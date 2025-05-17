import requests

TELEGRAM_BOT_TOKEN = "7768362707:AAEnVm1DYxeKoFgkaVOxfcFyng_vVTNY2og"
CHAT_ID = "6070467278"

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChat?chat_id={CHAT_ID}"

response = requests.get(url)
data = response.json()

if data.get("ok"):
    user = data["result"]
    print(f"User ID: {user['id']}")
    print(f"First Name: {user['first_name']}")
    print(f"Last Name: {user.get('last_name', 'N/A')}")
    print(f"Username: {user.get('username', 'N/A')}")
else:
    print("Failed to fetch user data:", data)
