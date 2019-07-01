from django.db import models
from django.contrib.auth.models import User as AdminUser

# Create your models here.


class LibUser(models.Model):
    libId = models.CharField(verbose_name='lib id', max_length=30, primary_key=True)
    libBorId = models.CharField(verbose_name='lib bor id', max_length=50, null=True)
    libPsw = models.CharField(verbose_name='lib password', max_length=200)
    name = models.CharField(verbose_name='name', max_length=20, null=True)
    department = models.CharField(verbose_name='name', max_length=100, null=True)
    readerType = models.CharField(verbose_name='name', max_length=20, null=True)
    registrationDate = models.DateField(verbose_name='registration date', null=True)
    expiryDate = models.DateField(verbose_name='expiry data', null=True)

    class Meta:
        verbose_name = '图书馆用户管理'
        verbose_name_plural = '图书馆用户管理'


class User(models.Model):
    openId = models.CharField(verbose_name='open id', max_length=100, null=True)
    wxSessionKey = models.CharField(verbose_name='wx session key', max_length=100, null=True)
    libAccount = models.ForeignKey(LibUser, on_delete=models.SET_NULL, verbose_name='lib account', blank=True, null=True, db_index=True, related_name='lib')
    session = models.CharField(verbose_name='session', max_length=100, null=True)
    sessionDate = models.DateTimeField(verbose_name='session used time', null=True)
    id = models.CharField(verbose_name='id', max_length=100, primary_key=True)
    nickName = models.CharField(verbose_name='nick name', max_length=100, null=True)
    avatarUrl = models.CharField(verbose_name='avatar url', max_length=200, null=True)
    gender = models.IntegerField(verbose_name='gender', null=True)
    province = models.CharField(verbose_name='province', max_length=100, null=True)
    city = models.CharField(verbose_name='city', max_length=100, null=True)
    country = models.CharField(verbose_name='country', max_length=100, null=True)
    lastLoginTime = models.DateTimeField(verbose_name='last login time', null=True)

    def __str__(self):
        return self.nickName

    class Meta:
        verbose_name = '小程序用户管理'
        verbose_name_plural = '小程序用户管理'


class Notice(models.Model):
    id = models.CharField(verbose_name='ID', max_length=100, primary_key=True, null=False)
    url = models.CharField(verbose_name='URL', max_length=200, null=True, blank=True)
    urlEnable = models.BooleanField(verbose_name='使用URL')
    title = models.CharField(verbose_name='标题', max_length=200, null=False, blank=False)
    contents = models.TextField(verbose_name='内容', null=True, blank=True)
    type = models.CharField(verbose_name='公告分类', max_length=10, choices=(('N', '通知公告'), ('Z', '资源动态'), ('P', '培训活动')))
    publishTime = models.DateTimeField(verbose_name='发布时间', null=False)
    stats = models.BooleanField(verbose_name='发布状态')
    pubUser = models.ForeignKey(AdminUser, verbose_name='发布者', on_delete=models.SET_NULL, blank=True, null=True,
                                db_index=True, related_name='notice_pub_user')

    class Meta:
        verbose_name = '通知公告管理'
        verbose_name_plural = '通知公告管理'
        permissions = (('publish_notice', 'Can publish notices'),)

    def __str__(self):
        return self.title


class Activity(models.Model):
    id = models.CharField(verbose_name='ID', max_length=100, primary_key=True, null=False, auto_created=True)
    url = models.CharField(verbose_name='URL', max_length=200, null=True, blank=True)
    urlEnable = models.BooleanField(verbose_name='使用URL')
    title = models.CharField(verbose_name='标题', max_length=200, null=False, blank=False)
    contents = models.TextField(verbose_name='内容', null=True, blank=True)
    publishTime = models.DateTimeField(verbose_name='发布时间', null=False)
    stats = models.BooleanField(verbose_name='发布状态')
    pubUser = models.ForeignKey(AdminUser, verbose_name='发布者', on_delete=models.SET_NULL, blank=True, null=True,
                                db_index=True, related_name='act_pub_user')
    actImg = models.ImageField(verbose_name='活动图片', upload_to='activity_img')

    class Meta:
        verbose_name = '活动信息管理'
        verbose_name_plural = '活动信息管理'
        permissions = (('publish_activity', 'Can publish activities'),)

    def __str__(self):
        return self.title


class Advise(models.Model):
    id = models.CharField(verbose_name='ID', max_length=100, primary_key=True, null=False, auto_created=True)
    contents = models.TextField(verbose_name='投诉内容', null=True, blank=True)
    tel = models.CharField(verbose_name='联系方式', null=True, blank=True, max_length=100)
    publishTime = models.DateTimeField(verbose_name='投诉时间', null=False)
    stats = models.BooleanField(verbose_name='受理状态')
    solveUser = models.ForeignKey(AdminUser, verbose_name='受理者', on_delete=models.SET_NULL, blank=True, null=True,
                                  db_index=True, related_name='solve_user')
    result = models.TextField(verbose_name='受理结果', null=True, blank=True)

    class Meta:
        verbose_name = '投诉受理'
        verbose_name_plural = '投诉受理'

    def __str__(self):
        return self.id




