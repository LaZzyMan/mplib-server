from rest_framework import serializers
from .models import User, LibUser


class LibUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibUser
        fields = ('libId',)


class UserSerializer(serializers.ModelSerializer):
    libAccount = LibUserSerializer()

    class Meta:
        model = User
        fields = ('wxSessionKey', 'id', 'session', 'openId', 'libAccount')
