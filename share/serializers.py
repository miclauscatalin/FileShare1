from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import File, Share

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'upload']

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'file', 'message', 'recipient']

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
