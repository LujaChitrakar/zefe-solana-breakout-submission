from django.db import models
from rest_framework.views import exception_handler
from rest_framework.permissions import SAFE_METHODS
from rest_framework.exceptions import ErrorDetail
from rest_framework.utils import encoders, json
from rest_framework.pagination import PageNumberPagination
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime
from django.core.files.base import ContentFile


class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super(BaseModelManager, self).get_queryset().filter(is_deleted=False)


class DateTimeAbstractModel(models.Model):
    created_date = models.DateTimeField(blank=True, auto_now_add=True)
    updated_date = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        abstract = True


class BaseModel(DateTimeAbstractModel):
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # this is for admin (to get all objects including those delete ones)
    admin_objects = models.Manager()

    objects = BaseModelManager()

    class Meta:
        abstract = True


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


def change_error_message(field, message):
    """
    Replacing This field word from the default error message to specific field name.
    """
    return message.replace("This field", field.replace("_", " "))




def compress_image(image_file, *args, **kwargs):
    image = Image.open(image_file)
    # Resize the image to a maximum size of 1024 x 1024 pixels
    image.thumbnail((1024, 1024))
    print(image_file.__str__().lower())
    # Compress the image
    if image_file.__str__().lower().endswith(
        "jpeg"
    ) or image_file.__str__().lower().endswith("jpg"):
        format = "JPEG"
        # Set the JPEG quality level to 80%
    elif image_file.__str__().lower().endswith("png"):
        format = "PNG"
        # Set the PNG compression level to 6 (out of 9)
        image = image.convert("P", palette=Image.ADAPTIVE, colors=256)
        options = {"compress_level": 6}
    else:
        # Unsupported image format
        raise ValueError("Unsupported image format: %s" % image.format)
        return image_file
    output = BytesIO()
    image.save(
        output,
        format=format,
        optimize=True,
        quality=70,
        **options if format == "PNG" else {},
    )
    compressed_image_file = ContentFile(output.getvalue(), name=image_file.__str__())
    return compressed_image_file
