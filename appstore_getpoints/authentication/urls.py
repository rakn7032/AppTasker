from django.urls import path
from django.contrib.auth import views
from . import views

urlpatterns = [
    path('upload_image', views.UploadImage.as_view(http_method_names=['post']), name='Upload image for url'),
    path('create_user', views.RegisterUser.as_view(http_method_names=['post']), name='Create User'),
    path('updateuser_profile', views.RegisterUser.as_view(http_method_names=['put']), name='Update user Profile'),
    path('user_profile', views.RegisterUser.as_view(http_method_names=['get']), name='Get User Profile Info'),
    path('otp_request', views.OtpRequest.as_view(http_method_names=['get']), name='Requesting OTP'),
    path('verify_otp', views.OTPVerifyAndResetPassword.as_view(http_method_names=['get']), name='Otp Verification'),
    path('reset_password', views.OTPVerifyAndResetPassword.as_view(http_method_names=['post']), name='reset old password to new password'),
    path('login', views.CustomTokenObtainPairView.as_view(), name='token obtain pair'),
]
