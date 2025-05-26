from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.db import models
import pytz
from datetime import datetime

from .models import User, Task, Category
from ToDoListService.global_funcs import standard_response
from .serializers import TasksSerializer, CategoriesSerializer
from .forms import CreateCategoryForm, EditCategoryForm, DeleteCategoryForm, CreateTaskForm, CategoriesDataForm, EditTaskForm, DeleteTaskForm, ChangeTaskStatusForm, CreateUserForm


class CreateUserView(APIView):

	def post(self, request):

		form = CreateUserForm(request.data)

		if form.is_valid():

			if User.objects.filter(TelegramId=form.cleaned_data.get('TelegramId')).exists():
                
				return standard_response(message="User already exists")


			User.objects.create(
				TelegramId=form.cleaned_data.get('TelegramId')
			)

			return standard_response(message="User created successfully")
		
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)


class TasksView(APIView):
    def get(self, request, tg_id: int):
        if not User.objects.filter(TelegramId=tg_id).exists():
            return standard_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

        user = User.objects.get(TelegramId=tg_id)
        tasks = Task.objects.filter(User=user).order_by('-CreatedAt')

        adak_tz = pytz.timezone('America/Adak')
        current_time_adak = datetime.now(adak_tz)
        
        for task in tasks:
            if task.DueDate:

                if not timezone.is_aware(task.DueDate):
                    task.DueDate = timezone.make_aware(task.DueDate, pytz.UTC)
                    task.save()
                
                due_date_adak = task.DueDate.astimezone(adak_tz)
                
                
                if due_date_adak < current_time_adak and task.Status != Task.StatusChoices.COMPLETED:
                    task.Status = Task.StatusChoices.OVERDUE
                    task.save()

        return standard_response(data=TasksSerializer(tasks, many=True).data, message="Tasks retrieved successfully")


class TasksOnTodayView(APIView):

	def get(self, request, tg_id:int):

		if not User.objects.filter(TelegramId=tg_id).exists():
			return standard_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

		user = User.objects.get(TelegramId=tg_id)

		today = timezone.now().date()
		tomorrow = today + timedelta(days=1)

		tasks = Task.objects.filter(
			User=user,
			DueDate__gte=today,
			DueDate__lt=tomorrow
		).order_by('-CreatedAt')

		return standard_response(data=TasksSerializer(tasks, many=True).data, message="Today's tasks retrieved successfully")


class TaskView(APIView):

	def get(self, request, task_id:str, tg_id:int):
		
		if not User.objects.filter(TelegramId=tg_id).exists():
			return standard_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
		
		if not Task.objects.filter(id=task_id, User=User.objects.get(TelegramId=tg_id)).exists():
			return standard_response(message="Task not found", status_code=status.HTTP_404_NOT_FOUND)

		user = User.objects.get(TelegramId=tg_id)

		tasks = Task.objects.get(pk=task_id, User=user)

		return standard_response(data=TasksSerializer(tasks).data, message="Task retrieved successfully")
	
	def post(self, request):


		form = CreateTaskForm(request.data)

		if form.is_valid():


			categories = request.data.get('Categories', [])

			categories_items = []

			for category in categories:

				formdata = CategoriesDataForm({'CategoryId': category})

				if formdata.is_valid():
					
					if Category.objects.filter(id=formdata.cleaned_data.get('CategoryId'), User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId'))).exists():
						categories_items.append(formdata.cleaned_data.get('CategoryId'))

			

			task = Task.objects.create(
				Title=form.cleaned_data.get('Title'),
				Description=form.cleaned_data.get('Description'),
				DueDate=form.cleaned_data.get('DueDate'), 
				User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId')),
			)

			task.Categories.add(*Category.objects.filter(id__in=categories_items, User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId'))))
			task.save()

			return standard_response(message="Task created successfully")			


		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)

	def patch(self, request):
		form = EditTaskForm(request.data)

		if form.is_valid():
			
			task = Task.objects.get(id=form.cleaned_data.get('id'), 
								User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId')))

			task.Title = form.cleaned_data.get('Title')
			task.Description = form.cleaned_data.get('Description')
			
			task.DueDate = form.cleaned_data.get('DueDate')
			
			if form.cleaned_data.get('Status'):
				task.Status = form.cleaned_data.get('Status')

			categories = request.data.get('Categories', [])

			if categories:
				categories_items = []
				for category in categories:
					formdata = CategoriesDataForm({'CategoryId': category})
					if formdata.is_valid():
						if Category.objects.filter(id=formdata.cleaned_data.get('CategoryId'), 
												User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId'))).exists():
							categories_items.append(formdata.cleaned_data.get('CategoryId'))

				task.Categories.set(Category.objects.filter(id__in=categories_items, 
									User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId'))))
			else:
				task.Categories.clear()

			task.save()

			return standard_response(message="Task updated successfully")    
			
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)
	
	def delete(self, request):

		form = DeleteTaskForm(request.data)

		if form.is_valid():

			task = Task.objects.get(id=form.cleaned_data.get('id'), User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId')))
			task.delete()

			return standard_response(message="Task deleted successfully")
		
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)



class CategoriesView(APIView):

	def get(self, request, tg_id:int):
		
		if not User.objects.filter(TelegramId=tg_id).exists():
			return standard_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)

		user = User.objects.get(TelegramId=tg_id)


		categories = Category.objects.filter(User=user).order_by('-CreatedAt')

		return standard_response(data=CategoriesSerializer(categories, many=True).data, message="Categories retrieved successfully")


class CategoryView(APIView):

	def get(self, request, category_id:str, tg_id:int):
		
		if not User.objects.filter(TelegramId=tg_id).exists():
			return standard_response(message="User not found", status_code=status.HTTP_404_NOT_FOUND)
		
		if not Category.objects.filter(id=category_id, User=User.objects.get(TelegramId=tg_id)).exists():
			return standard_response(message="Category not found", status_code=status.HTTP_404_NOT_FOUND)

		user = User.objects.get(TelegramId=tg_id)

		category = Category.objects.get(pk=category_id, User=user)

		return standard_response(data=CategoriesSerializer(category).data, message="Category retrieved successfully")

	def post(self, request):

		form = CreateCategoryForm(request.data)

		if form.is_valid():

			Category.objects.create(
				Name=form.cleaned_data.get('Name'),
				User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId'))
			)

			return standard_response(message="Category created successfully")
		
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)
	
	def patch(self, request):

		form = EditCategoryForm(request.data)

		if form.is_valid():
			
			category = Category.objects.get(id=form.cleaned_data.get('id'), User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId')))
	
			category.Name = form.cleaned_data.get('Name')
			category.save()

			return standard_response(message="Category updated successfully")
		
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)
	
	def delete(self, request):

		form = DeleteCategoryForm(request.data)

		if form.is_valid():

			category = Category.objects.get(id=form.cleaned_data.get('id'), User=User.objects.get(TelegramId=form.cleaned_data.get('TelegramId')))
			category.delete()

			return standard_response(message="Category deleted successfully")
		
		return standard_response(message="Invalid data", status_code=status.HTTP_400_BAD_REQUEST, errors=form.errors)
		
	

