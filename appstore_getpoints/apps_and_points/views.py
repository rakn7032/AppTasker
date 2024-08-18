from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import json,os, ipdb, re
from django.db.models import F,Q,Count,Avg,FloatField
from django.db.models.functions import Cast
from django.db import transaction
from .models import AppCategory,SubCategory,App,UserAppPoints
from authentication.helpers import url_validator
from authentication.models import User, UserAuth
from rest_framework.permissions import IsAuthenticated
from authentication.views import has_permission
from django.core.exceptions import PermissionDenied

class AppCategories(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        required_permissions = ["view categories"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        resp = AppCategory.objects.all().annotate(category_id=F("id"), category=F("name")).values("category_id", "category")
        return Response(resp, status=status.HTTP_200_OK)
        
    def post(self, request):
        required_permissions = ["create categories"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["user_id", "category"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_id, category = data.get('user_id'), data.get('category')
        if not(user_id and type(user_id)==int and category and type(category)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if not User.objects.filter(id=user_id, is_active=True):
            return Response({"message": "User not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = AppCategory.objects.get_or_create(name=category.lower())
        if created: return Response({"category":obj.name, "category_id":obj.id}, status=status.HTTP_201_CREATED)
        elif not created: return Response({"category":obj.name, "category_id":obj.id}, status=status.HTTP_200_OK)

class SubCategories(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        required_permissions = ["view subcategories"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        resp = SubCategory.objects.all().annotate(sub_category_id=F("id"), sub_category=F("name")).values("sub_category_id", "sub_category")
        return Response(resp, status=status.HTTP_200_OK)
        
    def post(self, request):
        required_permissions = ["create subcategories"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["user_id", "sub_category"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        user_id, sub_category = data.get('user_id'), data.get('sub_category')
        if not(user_id and type(user_id)==int and sub_category and type(sub_category)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if not User.objects.filter(id=user_id, is_active=True):
            return Response({"message": "User not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = SubCategory.objects.get_or_create(name=sub_category.lower())
        if created: return Response({"sub_category":obj.name, "sub_category_id":obj.id}, status=status.HTTP_201_CREATED)
        elif not created: return Response({"sub_category":obj.name, "sub_category_id":obj.id}, status=status.HTTP_200_OK)


class AppConfigurations(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        required_permissions = ["view apps"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        resp = App.objects.filter(active=True).annotate(app_id=F("id"), app_name=F("name"), category_id=F("appcategory__id"), category=F("appcategory__name"), sub_category=F("subcategory__name"), sub_category_id=F("subcategory__id")).values("app_id", "app_name", "link", "category","category_id", "sub_category", "sub_category_id", "app_logo", "points")
        return Response(resp, status=status.HTTP_200_OK)
        
    def post(self, request):
        required_permissions = ["add apps", "assign points to apps"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==7 and all(key in data for key in ["user_id", "sub_category_id", "category_id", "app_name", "link", "app_logo", "points"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)

        user_id, sub_category_id, category_id = data.get('user_id'), data.get('sub_category_id'), data.get('category_id')
        app_name, link, app_logo, points = data.get('app_name'), data.get('link'), data.get('app_logo'), data.get('points')
        if not(user_id and type(user_id)==int and sub_category_id and type(sub_category_id)==int and category_id and type(category_id)==int
            and app_name and type(app_name)==str and link and type(link)==str and app_logo and type(app_logo)==str and points and type(points)==int):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if not url_validator(app_logo): return Response({"message": "Invalid app logo.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if not User.objects.filter(id=user_id, is_active=True):
            return Response({"message": "User not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        category_obj = AppCategory.objects.filter(id=category_id, active=True).first()
        sub_category_obj = SubCategory.objects.filter(id=sub_category_id, active=True).first()
        if not(category_obj and sub_category_obj):
            return Response({"message": "Category/ SubCategory not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
       
        obj, created = App.objects.get_or_create(name=app_name.lower(), defaults={"appcategory":category_obj, "subcategory":sub_category_obj, "link":link, "app_logo":app_logo, "points":points})
        if created: return Response({"app_id":obj.pk, "app_name":obj.name, "category":obj.appcategory.name,"category_id":obj.appcategory.pk, "sub_category":obj.subcategory.name,"sub_category_id":obj.subcategory.id, "link":obj.link, "app_logo":obj.app_logo, "points":obj.points, "active":obj.active}, status=status.HTTP_201_CREATED)
        elif not created: return Response({"message":"An app exists with the given app name.", "status":False}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        required_permissions = ["update apps"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==9 and all(key in data for key in ["app_id","active", "user_id", "sub_category_id", "category_id", "app_name", "link", "app_logo", "points"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id, sub_category_id, category_id = data.get('user_id'), data.get('sub_category_id'), data.get('category_id')
        app_name, link, app_logo = data.get('app_name'), data.get('link'), data.get('app_logo')
        points, app_id, active = data.get('points'), data.get('app_id'), data.get('active')
        if not(user_id and type(user_id)==int and sub_category_id and type(sub_category_id)==int and category_id and type(category_id)==int
            and app_name and type(app_name)==str and link and type(link)==str and app_logo and type(app_logo)==str and points and type(points)==int and app_id and type(app_id)==int and type(active)==bool):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if not url_validator(app_logo): return Response({"message": "Invalid app logo.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id, is_active=True): return Response({"message": "User not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        category_obj = AppCategory.objects.filter(id=category_id, active=True).first()
        sub_category_obj = SubCategory.objects.filter(id=sub_category_id, active=True).first()
        if not(category_obj and sub_category_obj):
            return Response({"message": "Category/ SubCategory not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        if App.objects.filter(name=app_name.lower()).exclude(id=app_id).exists():
            return Response({"message":"An app exists with the given app name.", "status":False}, status=status.HTTP_400_BAD_REQUEST)
        obj = App.objects.filter(id=app_id).first()
        if not obj:
            return Response({"message":"App not found.", "status":False}, status=status.HTTP_400_BAD_REQUEST)
        
        obj.appcategory=category_obj
        obj.subcategory=sub_category_obj
        obj.name=app_name
        obj.link=link
        obj.app_logo=app_logo
        obj.points=points
        obj.active=active
        obj.save()
        return Response({"app_id":obj.pk, "app_name":obj.name, "category":obj.appcategory.name,"category_id":obj.appcategory.pk, "sub_category":obj.subcategory.name,"sub_category_id":obj.subcategory.id, "link":obj.link, "app_logo":obj.app_logo, "points":obj.points, "active":obj.active}, status=status.HTTP_200_OK)

class UserTasksConfiguration(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        required_permissions = ["view tasks", "view points"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request= request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["user_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.get('user_id')
        if not(user_id and user_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(id=user_id, is_active=True):
            return Response({"message": "User not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)

        resp = UserAppPoints.objects.filter(user__id=user_id).annotate(task_id=F("id"), app_name=F("app__name"),app_logo=F("app__app_logo"),app_link=F("app__link"),screen_shot=F("task"),app_points=F("app__points"))\
            .values("task_id", "app_name", "app_logo", "app_link", "screen_shot", "verified", "app_points")
        
        final_resp = [{"verified_tasks":[]}, {"unverified_tasks":[]}]
        for rec in resp:
            if rec["verified"]==True: final_resp[0]["verified_tasks"].append(rec)
            else: final_resp[1]["unverified_tasks"].append(rec)
        return Response(final_resp, status=status.HTTP_200_OK)

    def post(self, request):
        required_permissions = ["create tasks"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["user_id","app_id"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)

        user_id, app_id = data.get('user_id'), data.get('app_id')
        if not(user_id and type(user_id)==int and app_id and type(app_id)==int):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST)    
        
        user_obj = User.objects.filter(id=user_id, is_active=True).first()
        app_obj = App.objects.filter(id=app_id).first()
        if not(user_obj and app_obj): return Response({"message": "User/ App not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = UserAppPoints.objects.get_or_create(user=user_obj, app=app_obj)
        if created : return Response({"message":"Task created successfully.", "status":True}, status=status.HTTP_201_CREATED)
        if not created : return Response({"message":"A task exists for the given user and app.", "status":False}, status=status.HTTP_200_OK)

    def put(self, request):
        required_permissions = ["update tasks"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not (type(data)==dict and len(data.keys())==2 and all(key in data for key in ["task_id", "screen_short"])):
            return Response({"message": "The request data is invalid.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        
        task_id, screen_short = data.get('task_id'), data.get('screen_short')
        if not(task_id and type(task_id)==int and screen_short and type(screen_short)==str):
            return Response({"message": "Invalid or missing required request data.",'status':False}, status=status.HTTP_400_BAD_REQUEST) 
        if not url_validator(screen_short): return Response({"message": "Invalid screen short.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        task_obj = UserAppPoints.objects.filter(id=task_id).first()
        if not task_obj: return Response({"message": "Task not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        task_obj.task = screen_short
        task_obj.save()
        return Response({"message":"Task updated successfully.", "status":True}, status=status.HTTP_200_OK)
    
    def delete(self, request):
        required_permissions = ["delete tasks"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request= request.GET
        if not(len(request.keys())==1 and all(key in request for key in ["task_id"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        task_id = request.get('task_id')
        if not(task_id and task_id.isdigit()):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)
        
        task_obj = UserAppPoints.objects.filter(id=task_id).first()
        if not task_obj: return Response({"message": "Task not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        task_obj.delete()
        
        return Response({"message":"Task deleted successfully.", "status":True}, status=status.HTTP_200_OK)
    
class VerifyTaskSreenshot(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        required_permissions = ["verify task"]
        has_perm, message = has_permission(request.user, required_permissions)
        if not has_perm: return Response({'message': message, "status": False}, status=status.HTTP_403_FORBIDDEN)

        request= request.GET
        if not(len(request.keys())==2 and all(key in request for key in ["task_id", "verified"])):
            return Response({"message": "The request data is invalid.", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        task_id, verified = request.get('task_id'), request.get('verified')
        if not(task_id and task_id.isdigit() and verified in ("True", "False")):
            return Response({'message':'Invalid or missing required request data.', "status":False},status=status.HTTP_400_BAD_REQUEST)

        task_obj = UserAppPoints.objects.filter(id=task_id, task__isnull=False).first()
        if not task_obj: return Response({"message": "Task not found.",'status':False}, status=status.HTTP_400_BAD_REQUEST)
        task_obj.verified=eval(verified)
        task_obj.save()
        return Response({"message": "Task updated.",'status':True}, status=status.HTTP_200_OK)