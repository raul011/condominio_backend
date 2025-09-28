# serializers.py
from rest_framework import serializers
from usuarios.models import User 
from .models import DeviceToken



class DeviceTokenSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DeviceToken
        fields = ['id', 'user', 'token', 'is_active', 'created_at']
        read_only_fields = ['id', 'user', 'is_active', 'created_at']

class UserTokensSerializer(serializers.Serializer):
    tokens = serializers.ListField(child=serializers.CharField())

class NotificationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=500)
    notification_type = serializers.CharField(max_length=50)
   