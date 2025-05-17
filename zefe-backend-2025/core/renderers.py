from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import exception_handler
from rest_framework.utils import encoders, json
import requests
from datetime import datetime
import traceback
import json


DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1364695665590141121/DoYbgm3cqEGCOSlGsS1E3yGzjHaYG_o1ro642XbyiooWkiyf8TfzFFscv4Mw14T90m0J"
def send_discord_log(message, route, method="N/A", headers=None, status="SUCCESS", error_data=None):
    try:
        payload = {
            "username": "API Logger",
            "embeds": [{
                "title": f"{'✅' if status == 'SUCCESS' else '❌'} API {status}",
                "color": 3066993 if status == "SUCCESS" else 15158332,
                "fields": [
                    {"name": "Message", "value": message, "inline": False},
                    {"name": "Method", "value": method, "inline": True},
                    {"name": "Route", "value": route, "inline": False},
                    {"name": "Headers", "value": json.dumps(headers, indent=2)[:1000] if headers else "N/A", "inline": False},
                    {"name": "Error Data", "value": json.dumps(error_data, indent=2)[:1000] if error_data else "None", "inline": False}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)

    except Exception as e:
        print("⚠️ Failed to send Discord log:")
        print("Error message:", str(e))
        print("Stack trace:")
        traceback.print_exc()

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        request = renderer_context.get("request")
        method = request.method if request else "N/A"
        route = request.get_full_path() if request else "N/A"
        headers = dict(request.headers) if request else {}

        status_code = response.status_code if response else 200

        response_dict = {
            "status": "SUCCESS",
            "status_code": status_code,
            "message": "Successful",
            "data": request.data,
            "error_data": {},
            "error_message": "",
            "timestamp": datetime.utcnow().isoformat()
        }

        if isinstance(data, (dict, ReturnDict)):
            if "message" in data:
                response_dict["message"] = data.pop("message")

            if "results" in data and "count" in data:
                response_dict["data"] = data.pop("results")
                response_dict["meta"] = {
                    "count": data.pop("count"),
                    "next": data.pop("next", None),
                    "previous": data.pop("previous", None)
                }

            elif data.get("status") == "FAILURE" or status_code >= 400:
                response_dict["status"] = "FAILURE"
                response_dict["message"] = response_dict["message"] or "Unsuccessful"
                response_dict["data"] = data.get("data", {})
                response_dict["error_data"] = data.get("error_data", {})
                response_dict["error_message"] = data.get("error_message", "")
            else:
                if "detail" in data:
                    response_dict["message"] = str(data["detail"])
                    response_dict["status"] = "FAILURE"
                    response_dict["error_data"] = {"detail": data["detail"]}
                else:
                    response_dict["data"] = data
        else:
            if status_code >= 400:
                response_dict["status"] = "FAILURE"
                response_dict["message"] = str(data)
                response_dict["error_data"] = {"raw": data}
            else:
                response_dict["data"] = data

        # 🚀 Discord logging for all except GET
        if method != "GET":
            send_discord_log(
                message=response_dict["message"],
                route=route,
                method=method,
                headers=headers,
                status=response_dict["status"],
                error_data=response_dict["error_data"] if response_dict["status"] == "FAILURE" else None
            )

        return super().render(response_dict, accepted_media_type, renderer_context)

def send_discord_alert(exc, context, message, raw_data):
    request = context.get("request")
    route = request.get_full_path() if request else "N/A"
    
    # Se concentrer uniquement sur l'Authorization
    headers = {}
    if request and hasattr(request, "headers"):
        auth = request.headers.get("Authorization")
        if auth:
            headers["Authorization"] = auth

    # Préparer le corps de la requête
    request_body = {}
    if request and hasattr(request, "data"):
        try:
            request_body = request.data
        except Exception:
            request_body = "Unserializable request.data"

    # Préparer la stack trace de l'exception
    stack_trace = ""
    if exc:
        stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    payload = {
        "username": "API Exception Bot",
        "embeds": [
            {
                "title": "🚨 API Exception Occurred",
                "color": 16711680,
                "fields": [
                    {"name": "Message", "value": message, "inline": False},
                    {"name": "Route", "value": route, "inline": False},
                    {"name": "Method", "value": request.method if request else "N/A", "inline": True},
                    {"name": "Authorization Header", "value": json.dumps(headers, indent=2) if headers else "None", "inline": False},
                    {"name": "Request Body", "value": json.dumps(request_body, indent=2)[:1000], "inline": False},
                    {"name": "Error Data", "value": json.dumps(raw_data, indent=2)[:1000], "inline": False},
                    {"name": "Stack Trace", "value": stack_trace[:1000] if stack_trace else "None", "inline": False}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as discord_exc:
        print("⚠️ Failed to send Discord alert:", discord_exc)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    encoder_class = encoders.JSONEncoder
    request = context.get("request")

    if response is not None:
        raw_data = json.loads(json.dumps(response.data, cls=encoder_class))
        message = "Something went wrong."

        if isinstance(raw_data, dict):
            if "detail" in raw_data:
                message = str(raw_data["detail"])
            else:
                messages = []
                for key, value in raw_data.items():
                    if isinstance(value, list) and value:
                        messages.append(f"{key.title()}: {value[0]}")
                    elif isinstance(value, dict):
                        for subkey, subval in value.items():
                            messages.append(f"{subkey.title()}: {subval[0]}")
                    else:
                        messages.append(f"{key.title()}: {value}")
                if messages:
                    message = messages[0]
        elif isinstance(raw_data, list) and raw_data:
            message = str(raw_data[0])

        send_discord_alert(exc, context, message, raw_data)

        response.data = {
            "status": "FAILURE",
            "status_code": response.status_code,
            "message": message,
            "data": request.data,
            "error_data": raw_data,
            "error_message": "",
        }

    return response
