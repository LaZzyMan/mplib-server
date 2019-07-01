from rest_framework import serializers
from .models import User, LibUser, Notice, Activity, Advise


class LibUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibUser
        fields = ('libId',)


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('url', 'urlEnable', 'title', 'contents', 'type', 'publishTime')

    def get_pub_user(self, obj):
        return obj.pubUser.username


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('url', 'urlEnable', 'title', 'contents', 'type', 'publishTime', 'actImg')

    def get_pub_user(self, obj):
        return obj.pubUser.username


class AdviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advise
        fields = ('id', 'contents', 'tel', 'stats', 'solveUser', 'result', 'publishTime')

    def get_solve_user(self, obj):
        return obj.solveUser.username


class UserSerializer(serializers.ModelSerializer):
    libAccount = LibUserSerializer()

    class Meta:
        model = User
        fields = ('wxSessionKey', 'id', 'session', 'openId', 'libAccount')
