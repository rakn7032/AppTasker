from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "username", "is_admin", "is_active")
    fields = ("first_name", "last_name", "email", "username", "profile_pic", "gender", "bio", "is_admin", "is_active", "is_superuser", "created_at","updated_at")
    readonly_fields = ("created_at","updated_at")

class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id","name", "admin", "user")
    fields = ("name", "admin", "user", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

class UserAuthAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "otp", "otp_validated_upto", "verified")
    fields = ("user", "permissions", "otp", "otp_validated_upto", "verified", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at")

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Permission, PermissionAdmin)
admin.site.register(models.UserAuth, UserAuthAdmin)