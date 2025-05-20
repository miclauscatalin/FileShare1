from rest_framework import serializers
from .models import File, Share

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'upload']

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'file', 'message']
