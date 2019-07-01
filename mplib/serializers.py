from rest_framework import serializers
from .models import User, LibUser, Notice, Activity, Advise


class LibUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibUser
        fields = ('libId',)


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ('url', 'urlEnable', 'title', 'contents', 'type', 'publishTime', 'pubUser')

    def get_pubUser(self, obj):
        return obj.pubUser.username


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('url', 'urlEnable', 'title', 'contents', 'publishTime', 'pubUser', 'imgUrl')

    def get_pubUser(self, obj):
        return obj.pubUser.username

    def get_imgUrl(self, obj):
        return 'https://system.lib.whu.edu.cn/mp/upload/' + obj.actImg


class AdviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advise
        fields = ('id', 'contents', 'tel', 'stats', 'solveUser', 'result', 'publishTime', 'solve_user')

    def get_solve_user(self, obj):
        return obj.solveUser.username


class UserSerializer(serializers.ModelSerializer):
    libAccount = LibUserSerializer()

    class Meta:
        model = User
        fields = ('wxSessionKey', 'id', 'session', 'openId', 'libAccount')
