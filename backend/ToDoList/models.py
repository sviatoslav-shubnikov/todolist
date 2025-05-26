from django.db import models
from ToDoListService.global_funcs import generate_custom_id


# Create your models here.
class User(models.Model):
    
    id = models.CharField(primary_key=True, default=generate_custom_id, editable=False, max_length=16)

    TelegramId = models.BigIntegerField(unique=True)
    
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.TelegramId)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
	

class Category(models.Model):

	id = models.CharField(primary_key=True, default=generate_custom_id, editable=False, max_length=16)

	Name = models.CharField(max_length=100)

	User = models.ForeignKey("User", on_delete=models.CASCADE, related_name='UserCategory')

	CreatedAt = models.DateTimeField(auto_now_add=True)
	UpdatedAt = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.Name)
	
	class Meta:
		verbose_name = "Категория"
		verbose_name_plural = "Категории"
	

class Task(models.Model):
		
	id = models.CharField(primary_key=True, default=generate_custom_id, editable=False, max_length=16)

	Title = models.CharField(max_length=100)
	Description = models.TextField()

	DueDate = models.DateTimeField(null=True, blank=True)

	class StatusChoices(models.TextChoices):
		PENDING = 'pending', 'Pending'
		COMPLETED = 'completed', 'Completed'
		OVERDUE = 'overdue', 'Overdue'

	Status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)

	IsNotified = models.BooleanField(default=False)

	User = models.ForeignKey("User", on_delete=models.CASCADE, related_name='UserTasks')
	Categories = models.ManyToManyField("Category", blank=True, related_name='TasksCategories')

	CreatedAt = models.DateTimeField(auto_now_add=True)
	UpdatedAt = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.Title)
	
	class Meta:
		verbose_name = "Задача"
		verbose_name_plural = "Задачи"