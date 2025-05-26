"""
URL configuration for ToDoListService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('create_user/', views.CreateUserView.as_view(), name='create_user'),

	path('get_user_tasks/<int:tg_id>/', views.TasksView.as_view(), name='user_tasks'),
	
	path('get_user_tasks_on_today/<int:tg_id>/', views.TasksOnTodayView.as_view(), name='user_tasks_on_today'), # not use
	
    path('get_user_task/<str:task_id>/<int:tg_id>/', views.TaskView.as_view(), name='user_task'),
    path('create_task/', views.TaskView.as_view(), name='create_task'),
    path('edit_task/', views.TaskView.as_view(), name='edit_task'),
    path('delete_task/', views.TaskView.as_view(), name='delete_task'),

	
    path('get_task_categories/<int:tg_id>/', views.CategoriesView.as_view(), name='task_categories'),
	path('get_task_category/<str:category_id>/<int:tg_id>/', views.CategoryView.as_view(), name='task_category'),
    path('create_task_category/', views.CategoryView.as_view(), name='create_task_category'),
    path('edit_task_category/', views.CategoryView.as_view(), name='edit_task_category'),
    path('delete_task_category/', views.CategoryView.as_view(), name='delete_task_category'),

]
