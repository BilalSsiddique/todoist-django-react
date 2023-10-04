from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password']
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return value
    def validate_username(self, value):
        existing_user = User.objects.filter(username=value)
        if existing_user.exists():
            raise serializers.ValidationError('Username must be unique.')
        return value


class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields= ['list_title','id']
    
    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError('Title cannot be empty.')
        return value

    def create(self,validated_data):
        user = self.context['request'].user
        list_title = validated_data.get('title')
        new_list = List.objects.create(title=list_title, user_id=user)
        return new_list

class TaskSerializer(serializers.ModelSerializer):
    list_title = serializers.ReadOnlyField(source='list_id.list_title')
    user_name = serializers.ReadOnlyField(source='list_id.user_id.user_name')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'is_Completed', 'created_at', 'updated_at', 'priority','list_id','list_title','user_name']
    
    # called when performing serialization (converting data to python data types). It is getting override.
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['due_date'] = instance.due_date.strftime('%A, %d %b %Y')
        representation['updated_at'] = instance.updated_at.strftime('%I:%M %p')
        representation['created_at'] = instance.created_at.strftime('%A, %d %b %Y %I:%M %p')
        return representation

    def create(self,validated_data):
        user = self.context['request'].user
        user = get_object_or_404(User, email=user.email)
        list_obj = get_object_or_404(List, id=self.context['request'].data['list_id'], user_id=user)
        task = Task.objects.create(
        list_id=list_obj,
        title=validated_data.get('title'),
        description=validated_data.get('description'),
        due_date=validated_data.get('due_date'),
        is_Completed=validated_data.get('is_Completed', False),
        priority=validated_data.get('priority')
        )
        return task


