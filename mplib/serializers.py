from rest_framework import serializers
from .models import User, LibUser, Notice


class LibUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibUser
        fields = ('libId',)


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('url', 'urlEnable', 'title', 'contents', 'type', 'publishTime', 'pubUser')


class UserSerializer(serializers.ModelSerializer):
    libAccount = LibUserSerializer()

    class Meta:
        model = User
        fields = ('wxSessionKey', 'id', 'session', 'openId', 'libAccount')
