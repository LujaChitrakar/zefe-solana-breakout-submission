from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views


urlpatterns = [
    path("upload/file/", views.UploadImageView.as_view(), name="upload_files"),
]
