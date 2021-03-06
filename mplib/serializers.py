from rest_framework import serializers
from .models import User, LibUser, Notice, Activity, Advise


class LibUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibUser
        fields = ('libId',)


class NoticeSerializer(serializers.ModelSerializer):
    pub_user = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ('url', 'urlEnable', 'title', 'contents', 'type', 'publishTime', 'pub_user')

    def get_pub_user(self, obj):
        return obj.pubUser.username


class TrainingSerializer(serializers.ModelSerializer):
    pub_user = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ('id', 'title', 'contents', 'type', 'place', 'start_time', 'end_time', 'speaker', 'pub_user')

    def get_pub_user(self, obj):
        return obj.pubUser.username


class ActivitySerializer(serializers.ModelSerializer):
    pub_user = serializers.SerializerMethodField()
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ('url', 'urlEnable', 'title', 'contents', 'publishTime', 'pub_user', 'img_url')

    def get_pub_user(self, obj):
        return obj.pubUser.username

    def get_img_url(self, obj):
        return 'https://system.lib.whu.edu.cn' + obj.actImg.url


class AdviseSerializer(serializers.ModelSerializer):
    solve_user = serializers.SerializerMethodField()

    class Meta:
        model = Advise
        fields = ('id', 'contents', 'tel', 'stats', 'solveTime', 'result', 'publishTime', 'solve_user')

    def get_solve_user(self, obj):
        if obj.solveUser is None:
            return None
        else:
            return obj.solveUser.username


class UserSerializer(serializers.ModelSerializer):
    libAccount = LibUserSerializer()

    class Meta:
        model = User
        fields = ('id', )
