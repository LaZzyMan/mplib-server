from django.contrib import admin
from mplib.models import Notice, LibUser, User
import uuid
from django.contrib import messages
from django.contrib.auth.models import User as AdminUser
from mplib import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html


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


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    form = NoticeForm
    list_per_page = 30
    save_on_top = True
    view_on_site = False
    list_display = ('title', 'id', 'publishTime', 'pubUser', 'urlEnable', 'color_stats')
    # ordering = ('-publishTime')
    list_filter = ('type', 'urlEnable', 'stats', 'pubUser')
    search_fields = ('title', 'contents')
    date_hierarchy = 'publishTime'
    fields = ('title', 'type', 'urlEnable', 'url', 'contents', 'publishTime')
    actions = ['publish_notices']

    def publish_notices(self, request, queryset):
        queryset.update(stats=True)

    publish_notices.short_description = '发布选中的公告'
    publish_notices.allowed_permissions = ('publish', )

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(LibUser)
class LibUserAdmin(admin.ModelAdmin):
    pass
