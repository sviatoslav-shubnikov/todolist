from django import forms
from .models import User, Task, Category


class CreateUserForm(forms.Form):

	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		return cleaned_data
	

class CreateTaskForm(forms.Form):

	Title = forms.CharField(max_length=100, required=True, label="Task Title")
	Description = forms.CharField(max_length=1000, required=False, label="Task Description")
	DueDate = forms.DateTimeField(required=False, label="Due Date")
	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		return cleaned_data
	

class CategoriesDataForm(forms.Form):
	
	CategoryId = forms.CharField(max_length=16, required=True, label="Category ID")


	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('CategoryId'):
			raise forms.ValidationError("Category ID is required.")
		
		if not Category.objects.filter(pk=cleaned_data.get('CategoryId')).exists():
			raise forms.ValidationError("Category with this ID does not exist.")
		
		return cleaned_data
	

class EditTaskForm(forms.Form):
	
	id = forms.CharField(max_length=16, required=True, label="Task ID")

	Title = forms.CharField(max_length=100, required=True, label="Task Title")
	Description = forms.CharField(max_length=1000, required=False, label="Task Description")

	DueDate = forms.DateTimeField(required=False, label="Due Date")
	Status = forms.ChoiceField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('overdue', 'Overdue')], required=False, label="Status")

	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('id'):
			raise forms.ValidationError("Task ID is required.")
		
		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		if not Task.objects.filter(pk=cleaned_data.get('id'), User=User.objects.get(TelegramId=cleaned_data.get('TelegramId'))).exists():
			raise forms.ValidationError("Task with this ID does not exist for the specified user.")
		
		return cleaned_data
	

class DeleteTaskForm(forms.Form):
	
	id = forms.CharField(max_length=16, required=True, label="Task ID")
	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('id'):
			raise forms.ValidationError("Task ID is required.")
		
		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		if not Task.objects.filter(pk=cleaned_data.get('id'), User=User.objects.get(TelegramId=cleaned_data.get('TelegramId'))).exists():
			raise forms.ValidationError("Task with this ID does not exist for the specified user.")
		
		return cleaned_data
	

class ChangeTaskStatusForm(forms.Form):
	
	id = forms.CharField(max_length=16, required=True, label="Task ID")

	Status = forms.ChoiceField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('overdue', 'Overdue')], required=True, label="Status")
	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('id'):
			raise forms.ValidationError("Task ID is required.")
		
		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		if not Task.objects.filter(pk=cleaned_data.get('id'), User=User.objects.get(TelegramId=cleaned_data.get('TelegramId'))).exists():
			raise forms.ValidationError("Task with this ID does not exist for the specified user.")
		
		return cleaned_data


class CreateCategoryForm(forms.Form):

	Name = forms.CharField(max_length=100, required=True, label="Category Name")

	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		return cleaned_data
	

class EditCategoryForm(forms.Form):

	id = forms.CharField(max_length=16, required=True, label="Category ID")

	Name = forms.CharField(max_length=100, required=True, label="Category Name")
	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('id'):
			raise forms.ValidationError("Category ID is required.")
		
		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		if not Category.objects.filter(pk=cleaned_data.get('id'), User=User.objects.get(TelegramId=cleaned_data.get('TelegramId'))).exists():
			raise forms.ValidationError("Category with this ID does not exist for the specified user.")
		
		return cleaned_data


class DeleteCategoryForm(forms.Form):

	id = forms.CharField(max_length=16, required=True, label="Category ID")
	TelegramId = forms.IntegerField(required=True, label="Telegram ID")

	def clean(self):

		cleaned_data = super().clean()

		if not cleaned_data.get('id'):
			raise forms.ValidationError("Category ID is required.")
		
		if not cleaned_data.get('TelegramId'):
			raise forms.ValidationError("Telegram ID is required.")
		
		if not User.objects.filter(TelegramId=cleaned_data.get('TelegramId')).exists():
			raise forms.ValidationError("User with this Telegram ID does not exist.")
		
		if not Category.objects.filter(pk=cleaned_data.get('id'), User=User.objects.get(TelegramId=cleaned_data.get('TelegramId'))).exists():
			raise forms.ValidationError("Category with this ID does not exist for the specified user.")
		
		return cleaned_data
	
