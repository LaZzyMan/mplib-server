from django.contrib import admin
from mplib.models import Notice, LibUser, User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(LibUser)
class LibUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    pass
