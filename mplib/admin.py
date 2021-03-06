from django.contrib import admin
from mplib.models import Notice, LibUser, User, Activity, Advise, IPKiller, Training
import uuid
from django.contrib import messages
from django.contrib.auth.models import User as AdminUser
from mplib import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone


admin.site.site_header = '图书馆小程序后台管理系统'
admin.site.site_title = '武汉大学图书馆'
admin.site.empty_value_display = '-empty-'
# Register your models here.


class NoticeForm(forms.ModelForm):
    class Meta:
        model = models.Notice
        fields = ['title', 'type', 'urlEnable', 'url', 'contents', 'publishTime']

    def clean(self):
        urlEnable = self.cleaned_data['urlEnable']
        if urlEnable:
            if self.cleaned_data['url'] is None:
                raise ValidationError('使用URL时，URL不能为空')
        else:
            if self.cleaned_data['contents'] is None:
                raise ValidationError('请填写公告内容')
        super().clean()


class TrainingForm(forms.ModelForm):
    class Meta:
        model = models.Training
        fields = ['title', 'type', 'time', 'place', 'contents']

    def clean(self):
        if self.cleaned_data['title'] is None:
            raise ValidationError('请填写培训主题')
        if self.cleaned_data['contents'] is None:
            raise ValidationError('请填写培训简介')
        if self.cleaned_data['start_time'] is None:
            raise ValidationError('请填写培训开始时间')
        if self.cleaned_data['end_time'] is None:
            raise ValidationError('请填写培训结束时间')
        if self.cleaned_data['place'] is None:
            raise ValidationError('请填写培训地点')
        if self.cleaned_data['speaker'] is None:
            raise ValidationError('请填写主讲人')
        super().clean()


class AdviseForm(forms.ModelForm):
    class Meta:
        model = models.Advise
        fields = ['publishTime', 'tel', 'contents', 'result', 'solveTime', 'stats']
        help_texts = {
            'stats': '填写受理结果和时间后完成受理'
        }

    def clean(self):
        solve = self.cleaned_data['stats']
        print(solve)
        print(self.cleaned_data['result']=='')
        if solve:
            if self.cleaned_data['result'] == '':
                raise ValidationError('请填写投诉受理结果')
        super().clean()


class ActivityForm(forms.ModelForm):
    class Meta:
        model = models.Activity
        fields = ['title', 'urlEnable', 'url', 'contents', 'publishTime', 'actImg']
        help_texts = {
            'actImg': '上传图片最佳尺寸为731*295，尽量保证图片比例一致'
        }

    def clean(self):
        urlEnable = self.cleaned_data['urlEnable']
        img = self.cleaned_data['actImg']
        img.name = str(uuid.uuid1()) + '.' + img.name.split('.')[-1]
        if urlEnable:
            if self.cleaned_data['url'] is None:
                raise ValidationError('使用URL时，URL不能为空')
        else:
            if self.cleaned_data['contents'] is None:
                raise ValidationError('请填写公告内容')
        super().clean()


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    form = NoticeForm
    list_per_page = 50
    # save_on_top = True
    view_on_site = False
    list_display = ('title', 'id', 'publishTime', 'pubUser', 'urlEnable', 'color_stats')
    # ordering = ('-publishTime')
    list_filter = ('type', 'urlEnable', 'stats', 'pubUser')
    search_fields = ('title', 'contents')
    date_hierarchy = 'publishTime'
    fields = ('title', 'type', 'urlEnable', 'url', 'contents', 'publishTime')
    actions = ['publish_notices', 'unpublish_notices']

    def publish_notices(self, request, queryset):
        queryset.update(stats=True)

    publish_notices.short_description = '发布公告'
    publish_notices.allowed_permissions = ('publish', )

    def unpublish_notices(self, request, queryset):
        queryset.update(stats=False)

    unpublish_notices.short_description = '撤下公告'
    unpublish_notices.allowed_permissions = ('publish', )

    def has_publish_permission(self, request):
        opts = self.opts
        return request.user.has_perm('%s.%s' % (opts.app_label, 'publish_notice'))

    def color_stats(self, obj):
        return obj.stats
    color_stats.short_description = '状态'
    color_stats.boolean = True

    def save_model(self, request, obj, form, change):
        obj.pubUser = AdminUser.objects.get(username=request.user)
        obj.id = uuid.uuid1()
        obj.stats = False
        super(NoticeAdmin, self).save_model(request, obj, form, change)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    form = ActivityForm
    list_per_page = 30
    # save_on_top = True
    view_on_site = False
    list_display = ('title', 'id', 'publishTime', 'pubUser', 'urlEnable', 'stats')
    # ordering = ('-publishTime')
    list_filter = ('urlEnable', 'stats', 'pubUser')
    search_fields = ('title', 'contents')
    date_hierarchy = 'publishTime'
    fields = ('title', 'urlEnable', 'url', 'contents', 'publishTime', 'actImg')
    actions = ['publish_activity', 'unpublish_activity']

    def publish_activity(self, request, queryset):
        queryset.update(stats=True)

    publish_activity.short_description = '发布活动'
    publish_activity.allowed_permissions = ('publish',)

    def unpublish_activity(self, request, queryset):
        queryset.update(stats=False)

    unpublish_activity.short_description = '撤下活动'
    unpublish_activity.allowed_permissions = ('publish',)

    def has_publish_permission(self, request):
        opts = self.opts
        return request.user.has_perm('%s.%s' % (opts.app_label, 'publish_activity'))

    def save_model(self, request, obj, form, change):
        obj.pubUser = AdminUser.objects.get(username=request.user)
        obj.id = uuid.uuid1()
        obj.stats = False
        super(ActivityAdmin, self).save_model(request, obj, form, change)


@admin.register(Advise)
class AdviseAdmin(admin.ModelAdmin):
    form = AdviseForm
    list_per_page = 50
    # save_on_top = True
    view_on_site = False
    list_display = ('id', 'publishTime', 'contents', 'solveUser', 'result', 'stats')
    # ordering = ('-publishTime')
    list_filter = ('stats', 'solveUser')
    search_fields = ('contents', )
    date_hierarchy = 'publishTime'
    fields = ('publishTime', 'tel', 'contents', 'result', 'solveTime', 'stats')

    def get_readonly_fields(self, request, obj=None):
        opts = self.opts
        if request.user.has_perm('%s.%s' % (opts.app_label, 'solve_advise')):
            return ('publishTime', 'tel', 'contents')
        else:
            return ('publishTime', 'tel', 'contents', 'result', 'solveTime', 'stats')

    def save_model(self, request, obj, form, change):
        obj.solveUser = AdminUser.objects.get(username=request.user)
        super(AdviseAdmin, self).save_model(request, obj, form, change)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 50
    view_on_site = False
    list_display = ('nickName', 'libAccount', 'gender_name', 'country', 'province', 'city', 'lastLoginTime')
    list_filter = ('gender', 'province', 'city')
    search_fields = ('nickName', )
    date_hierarchy = 'lastLoginTime'
    fields = ('nickName', 'libAccount', 'gender', 'country', 'province', 'city', 'avatarUrl', 'lastLoginTime')

    def gender_name(self, obj):
        if obj.gender == 2:
            return '女'
        elif obj.gender == 1:
            return '男'
        else:
            return '未知'
    gender_name.short_description = '性别'


@admin.register(LibUser)
class LibUserAdmin(admin.ModelAdmin):
    list_per_page = 50
    view_on_site = False
    list_display = ('libId', 'name', 'department', 'readerType')
    list_filter = ('department', 'readerType')
    search_fields = ('libId', )
    fields = ('libId', 'name', 'department', 'readerType', 'registrationDate', 'expiryDate')


@admin.register(IPKiller)
class IPKillerAdmin(admin.ModelAdmin):
    list_per_page = 50
    # save_on_top = True
    view_on_site = False
    list_display = ('ip', 'time', 'visit', 'stats')
    # ordering = ('-publishTime')
    list_filter = ('stats',)
    search_fields = ('ip', )
    date_hierarchy = 'time'
    fields = ('ip', 'time', 'visit', 'stats')
    readonly_fields = ('ip', 'time', 'visit', 'stats')

    actions = ['ban_ip', 'unban_ip']

    def ban_ip(self, request, queryset):
        queryset.update(stats=False)

    ban_ip.short_description = '封禁IP'
    ban_ip.allowed_permissions = ('ban',)

    def unban_ip(self, request, queryset):
        queryset.update(stats=True)

    unban_ip.short_description = '解封IP'
    unban_ip.allowed_permissions = ('ban',)

    def has_ban_permission(self, request):
        opts = self.opts
        return request.user.has_perm('%s.%s' % (opts.app_label, 'ip_kill'))


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    form = TrainingForm
    list_per_page = 50
    # save_on_top = True
    view_on_site = False
    list_display = ('title', 'type', 'start_time', 'place', 'speaker', 'publishTime', 'pubUser', 'stats')
    # ordering = ('-publishTime')
    list_filter = ('type', 'stats', 'pubUser', 'speaker')
    search_fields = ('title', 'contents')
    date_hierarchy = 'start_time'
    fields = ('title', 'type', 'start_time', 'end_time', 'speaker', 'place', 'contents')
    actions = ['publish_training', 'unpublish_training']

    def publish_training(self, request, queryset):
        queryset.update(stats=True)
        queryset.update(publishTime=timezone.now())

    publish_training.short_description = '发布培训'
    publish_training.allowed_permissions = ('publish', )

    def unpublish_training(self, request, queryset):
        queryset.update(stats=False)

    unpublish_training.short_description = '撤下培训'
    unpublish_training.allowed_permissions = ('publish', )

    def has_publish_permission(self, request):
        opts = self.opts
        return request.user.has_perm('%s.%s' % (opts.app_label, 'publish_training'))

    def save_model(self, request, obj, form, change):
        obj.pubUser = AdminUser.objects.get(username=request.user)
        obj.publishTime = timezone.now()
        obj.stats = False
        super(TrainingAdmin, self).save_model(request, obj, form, change)
