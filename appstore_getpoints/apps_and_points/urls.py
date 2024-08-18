from django.urls import path, re_path
from . import views

urlpatterns = [
    path('categories_dropdown', views.AppCategories.as_view(http_method_names=['get']), name='DropDown for App Categories'),
    path('create_category', views.AppCategories.as_view(http_method_names=['post']), name='Create Category'),
    path('subcategory_dropdown', views.SubCategories.as_view(http_method_names=['get']), name='DropDown for SubCategories'),
    path('create_subcategory', views.SubCategories.as_view(http_method_names=['post']), name='Create SubCategory'),
    path('apps_dropdown', views.AppConfigurations.as_view(http_method_names=['get']), name='get all Apps in dropdown'),
    path('create_app', views.AppConfigurations.as_view(http_method_names=['post']), name='Register app'),
    path('update_app', views.AppConfigurations.as_view(http_method_names=['put']), name='update app data'),
    path('user_tasks', views.UserTasksConfiguration.as_view(http_method_names=['get']), name='get all tasks of user'),
    path('create_task', views.UserTasksConfiguration.as_view(http_method_names=['post']), name='create user tasks'),
    path('update_task', views.UserTasksConfiguration.as_view(http_method_names=['put']), name='update user tasks'),
    path('delete_task', views.UserTasksConfiguration.as_view(http_method_names=['delete']), name='delete user tasks'),
    path('verify_task', views.VerifyTaskSreenshot.as_view(http_method_names=['get']), name='Verify user tasks'),
    
]