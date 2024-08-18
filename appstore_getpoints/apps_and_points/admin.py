from django.contrib import admin
from . import models

class AppCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active")
    fields = ("name", "active", "created_at","updated_at")
    readonly_fields = ("created_at","updated_at")

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "active")
    fields = ("name", "active", "created_at","updated_at")
    readonly_fields = ("created_at","updated_at")

class AppAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "appcategory", "subcategory", "points", "active")
    fields = ("appcategory", "subcategory", "name", "link", "app_logo", "points", "active", "created_at","updated_at")
    readonly_fields = ("created_at","updated_at")

class UserAppPointsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "app", "task", "verified")
    fields = ("user", "app", "task", "verified", "created_at","updated_at")
    readonly_fields = ("created_at","updated_at")

admin.site.register(models.AppCategory, AppCategoryAdmin)
admin.site.register(models.SubCategory, SubCategoryAdmin)
admin.site.register(models.App, AppAdmin)
admin.site.register(models.UserAppPoints, UserAppPointsAdmin)
