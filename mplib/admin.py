from django.contrib import admin
from mplib.models import Notice, LibUser, User
import uuid
from django.contrib import messages
from django.contrib.auth.models import User as AdminUser
from django.utils.html import format_html


admin.site.site_header = '图书馆小程序后台管理系统'
admin.site.site_title = '武汉大学图书馆'
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(LibUser)
class LibUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_per_page = 30
    view_on_site = False
    list_display = ('id', 'title', 'publishTime', 'pubUser', 'urlEnable', 'color_stats')
    # ordering = ('-publishTime')
    list_filter = ('type', 'urlEnable', 'stats', 'pubUser')
    search_fields = ('title', 'contents')
    date_hierarchy = 'publishTime'
    fields = ('title', 'type', 'urlEnable', 'url', 'contents', 'publishTime')

    def color_stats(self, obj):
        return obj.stats
    color_stats.short_description = '状态'
    color_stats.boolean = True

    def save_model(self, request, obj, form, change):
        obj.pub_user = AdminUser.objects.get(username=request.user)
        messages.error(request, obj.pub_user.username)
        obj.id = uuid.uuid1()
        obj.stats = False
        if obj.title == '':
            messages.error(request, '标题不能为空.')
            return
        if obj.urlEnable:
            if obj.url == '':
                messages.error(request, '启用URL时，URL不能为空.')
                return
        elif obj.contents == '':
            messages.error(request, '不启用URL时，内容不能为空.')
        obj.save()
