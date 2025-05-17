from core import boto3
from core.utils import compress_image
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, write_only=True)
    key = serializers.CharField(required=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    def validate_file(self, value):
        if (
            value.__str__().lower().endswith("jpeg")
            or value.__str__().lower().endswith("jpg")
            or value.__str__().lower().endswith("png")
        ):
            return compress_image(value)
        return value

    def get_file_url(self, obj):
        if not obj:
            return None
        if hasattr(obj, "key"):
            return obj.key
        if obj.get("key"):
            return boto3.get_presigned_url(obj.get("key"))
        return None

    def validate_key(self, value):
        if not value:
            raise serializers.ValidationError(_("Key is required"))
        return value

    def create(self, validated_data):
        file = validated_data.pop("file")
        print("File")
        key = validated_data.get("key")
        boto3.upload_temporary_file_to_s3(file, key)
        return validated_data