from rest_framework import serializers


class TasksSerializer(serializers.Serializer):

	id = serializers.CharField(max_length=16)

	Title = serializers.CharField(max_length=255)
	Description = serializers.CharField(max_length=1000, allow_blank=True)

	DueDate = serializers.DateTimeField(allow_null=True)
	CreatedAt = serializers.DateTimeField()
	UpdatedAt = serializers.DateTimeField()

	Status = serializers.CharField()

	Categories = serializers.SerializerMethodField()

	def get_Categories(self, obj):
		return [category.Name for category in obj.Categories.all()]


class CategoriesSerializer(serializers.Serializer):

	id = serializers.CharField(max_length=16)

	Name = serializers.CharField(max_length=100)

	CreatedAt = serializers.DateTimeField()
	UpdatedAt = serializers.DateTimeField()

	