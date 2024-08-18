from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError
import string, secrets, ipdb, os, re
from rest_framework import status
from datetime import datetime,timedelta
from django.utils import timezone
from django.conf import settings
# from rest_framework.serializers import Serializer
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
# from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .helpers import email_validator,password_validator,send_welcome_email,send_otp_email,url_validator
from .models import User,Permission,UserAuth
from appstore_getpoints.settings import MEDIA_ROOT
User = get_user_model()

class UploadImage(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        required_permissions = ["upload image"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        user_id = data.get('user_id')
        image_file = data.get('image')
        if not (user_id and user_id.isdigit() and image_file):
            return Response({"message": "The request data is invalid.", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id, is_active=True).exists():
            return Response({"message": "User not found or user is inactive.", 'status': False}, status=status.HTTP_400_BAD_REQUEST)
        
        upload_path = settings.MEDIA_ROOT
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        image_name = f"{user_id}_{image_file.name.replace(' ','')}"
        image_full_path = os.path.join(upload_path, image_name)
        with open(image_full_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        image_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{image_name}')
        return Response({'image_url': image_url, 'status': True}, status=status.HTTP_200_OK)

class RegisterUser(APIView):
    def post(self, request):
        data = request.data
        if not (type(data)==dict and len(data.keys())==7 and all(key in data for key in ["password", "first_name", "last_name", "email", "gender", "bio", "is_admin"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        first_name, last_name, email = data.get('first_name'), data.get('last_name'), data.get('email')
        gender, password = data.get('gender'), data.get('password')
        bio, is_admin = data.get('bio'), data.get('is_admin')
        if not(first_name and type(first_name)==str and email and type(email)==str and gender in ("Male", "Female", "Others") and type(is_admin)==bool):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if last_name and type(last_name)!=str:
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if bio and type(bio)!=str:
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if not email_validator(email):
            return Response({'message':'invalid email.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not password_validator(password):
            return Response({'message':'Password must Contain a special character,a number, and length must be more than 8 letters.','status':False},status=status.HTTP_400_BAD_REQUEST)
        
        user, created = User.objects.get_or_create(email=email,defaults={'first_name': first_name,'last_name': last_name,'username': email,'gender': gender,'bio': bio,'is_admin': is_admin})
        if not created:
            return Response({'message':'A user with the given email already exists; the email must be unique.','status':False},status=status.HTTP_400_BAD_REQUEST)
        elif created:
            user.set_password(password)
            user.save()
            if user.is_admin:
                permission_objects = Permission.objects.filter(admin=True)
                user_auth_obj = UserAuth.objects.create(user=user)
                user_auth_obj.permissions.set(permission_objects)
            elif not user.is_admin:
                permission_objects = Permission.objects.filter(user=True)
                user_auth_obj = UserAuth.objects.create(user=user)
                user_auth_obj.permissions.set(permission_objects)

            subject = "Welcome to AppStore! You are signed up!"
            send_welcome_email(to_email=user.email, subject=subject, user_name=user.first_name)
            return Response({"message":"user created Succesfully", "email":user.email, "user_id":user.pk, "status":True}, status=status.HTTP_201_CREATED)
    
    def put(self, request):
        required_permissions = ["update profile"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==9 and all(key in data for key in ["user_id", "first_name", "last_name", "email", "profile_pic_url", "gender", "bio", "is_admin", "is_active"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        first_name, last_name, email = data.get('first_name'), data.get('last_name'), data.get('email')
        profile_pic_url, gender = data.get('profile_pic_url'), data.get('gender')
        bio, is_admin, user_id, is_active = data.get('bio'), data.get('is_admin'), data.get('user_id'), data.get('is_active')
        if not(user_id and type(user_id)==int and first_name and type(first_name)==str and email and type(email)==str and gender in ("Male", "Female", "Others") and type(is_admin)==bool and type(is_active)==bool):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if last_name and type(last_name)!=str:
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if bio and type(bio)!=str:
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if profile_pic_url and not url_validator(profile_pic_url):
            return Response({"message": "Invalid profile pic url.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if not email_validator(email):
            return Response({'message':'invalid email.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.filter(id=user_id).first()
        if not user_obj: return Response({'message':'User not found.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exclude(id=user_id).exists(): return Response({'message':'A user with the given email already exists; the email must be unique.','status':False},status=status.HTTP_400_BAD_REQUEST)
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.email = email
        user_obj.username = email
        user_obj.profile_pic = profile_pic_url
        user_obj.gender = gender
        user_obj.bio = bio
        user_obj.is_admin = is_admin
        user_obj.is_active = is_active
        user_obj.save()
        return Response({"message":"User profile updated Succesfully.", "status":True}, status=status.HTTP_200_OK)

    def get(self, request):
        required_permissions = ["view profile"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request= request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.get('user_id')
        if not(user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        user_info = User.objects.filter(id=user_id).values("first_name", "last_name", "email", "profile_pic", "gender", "bio", "is_admin", "is_active").first()
        if user_info:return Response(user_info, status=status.HTTP_200_OK)
        if not user_info:return Response({"message":"No user found; Invalid user id."}, status=status.HTTP_400_BAD_REQUEST)

class OtpRequest(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        required_permissions = ["otp request"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request = request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["email"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        email = request.get('email')
        if not(email and email_validator(email=email)):
            return Response({'message':'Invalid email.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        characters = string.ascii_letters + string.digits
        otp = ''.join(secrets.choice(characters) for _ in range(6))
        user = User.objects.filter(email=email,is_active=True).first()
        if not user: return Response({'message':f'No user found with the email: {email}','status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_auth_obj = UserAuth.objects.filter(user__id=user.id).first()
        user_auth_obj.otp = otp
        user_auth_obj.otp_validated_upto = datetime.now()+timedelta(minutes=5)
        user_auth_obj.verified = False
        user_auth_obj.save()

        subject="OTP for AppStore Password Reset Request"        
        send_otp_email(to_email=email, user_name=user.first_name, subject=subject, otp=otp)
        return Response({'message':f"Hi {user.first_name}, OTP sent to given Email, please check",'user_id':user.pk,'status':True},status=status.HTTP_200_OK)

class OTPVerifyAndResetPassword(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        required_permissions = ["verify otp"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request = request.GET
        if not(len(request.keys())==2 and all(key in request for key in ["otp", "user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        otp, user_id = request.get('otp'), request.get('user_id')
        if not(otp and user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
       
        user_auth_obj = UserAuth.objects.filter(user__id=user_id, user__is_active=True).first()
        if not user_auth_obj: return Response({'message':'User Not Found/User is inactive','status':False},status=status.HTTP_400_BAD_REQUEST)
        if otp == user_auth_obj.otp:
            if not timezone.now() <= user_auth_obj.otp_validated_upto:
                return Response({'message':'The OTP has expired. Please request a new one.','status':False},status=status.HTTP_400_BAD_REQUEST)
            if user_auth_obj.verified==True:
                return Response({'message':'The OTP has already been verified. Please request a new one.','status':False},status=status.HTTP_400_BAD_REQUEST)
            user_auth_obj.verified = True
            user_auth_obj.save()
            return Response({'message':'OTP verified.','status':True},status=status.HTTP_200_OK)
        else: return Response({'message':'Incorrect OTP.','status':False},status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        required_permissions = ["reset password"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["password", "user_id"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        password, user_id = data.get('password'), data.get('user_id')
        if not(user_id and password and type(user_id)==int and type(password)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(pk=user_id,is_active=True).first()
        if not user: return Response({'message':'No user found with the request data.','status':False},status=status.HTTP_400_BAD_REQUEST)
        user_auth_obj = UserAuth.objects.filter(user__id=user.pk, user__is_active=True).first()

        if not user_auth_obj:
            return Response({'message':'No user found with the request data.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if not password_validator(password):
            return Response({'message':'Password must Contain a special character,a number, and length must be more than 8 letters.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if not user_auth_obj.verified:
            return Response({'message':'OTP not verified/ Do Request for Reset password.','status':False},status=status.HTTP_400_BAD_REQUEST)
        if user.check_password(password):
            return Response({'message':'Password should not be same like OLD password','status':False},status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user_auth_obj.verified = False
        user_auth_obj.otp = None
        user_auth_obj.save()
        user.save()
        return Response({'message':'password sucessfully changed.','status':True},status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    def get_token(self, user):
        token = RefreshToken.for_user(user)
        token['user_id'] = user.id
        token['admin'] = user.is_admin
        token['permissions'] = self.get_user_permissions(user)
        return token

    def get_user_permissions(self, user):
        try:
            user_auth = UserAuth.objects.get(user=user)
            permissions = user_auth.permissions.all()
            permission_names = [permission.name for permission in permissions]
            return permission_names
        except UserAuth.DoesNotExist:
            return []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not(email and password): return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user: return Response({"message": "Invalid credentials", "status":False}, status=status.HTTP_401_UNAUTHORIZED)
        elif not user.check_password(password): return Response({"message": "Invalid credentials", "status":False}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = self.get_token(user)
        access_token = refresh.access_token
        return Response({'refresh': str(refresh),'access': str(access_token),}, status=status.HTTP_200_OK)

def has_permission(user, required_permissions):
    if not user.is_authenticated:
        return (False, "Unauthorized User")

    user_permissions = UserAuth.objects.filter(user__id=user.pk, permissions__name__in=required_permissions).values_list("permissions__name", flat=True)
    missing_permissions = set(required_permissions) - set(user_permissions)
    if missing_permissions: return (False, f"Permission denied: Missing required permissions.")
    return (True, "Permission granted")
