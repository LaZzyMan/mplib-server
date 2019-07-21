from django.db import models
from django.contrib.auth.models import User as AdminUser

# Create your models here.


class LibUser(models.Model):
    libId = models.CharField(verbose_name='图书馆账号', max_length=30, primary_key=True)
    libBorId = models.CharField(verbose_name='lib bor id', max_length=50, null=True)
    libPsw = models.CharField(verbose_name='密码', max_length=200)
    name = models.CharField(verbose_name='姓名', max_length=20, null=True)
    department = models.CharField(verbose_name='院系', max_length=100, null=True)
    readerType = models.CharField(verbose_name='读者类型', max_length=20, null=True)
    registrationDate = models.DateField(verbose_name='注册时间', null=True)
    expiryDate = models.DateField(verbose_name='过期时间', null=True)

    class Meta:
        verbose_name = '图书馆用户管理'
        verbose_name_plural = '图书馆用户管理'

    def __str__(self):
        return self.libId


class User(models.Model):
    openId = models.CharField(verbose_name='open id', max_length=100, null=True)
    wxSessionKey = models.CharField(verbose_name='wx session key', max_length=100, null=True)
    libAccount = models.ForeignKey(LibUser, on_delete=models.SET_NULL, verbose_name='图书馆账户', blank=True, null=True, db_index=True, related_name='lib')
    session = models.CharField(verbose_name='session', max_length=100, null=True)
    sessionDate = models.DateTimeField(verbose_name='session更新时间', null=True)
    id = models.CharField(verbose_name='id', max_length=100, primary_key=True)
    nickName = models.CharField(verbose_name='昵称', max_length=100, null=True)
    avatarUrl = models.CharField(verbose_name='头像URL', max_length=200, null=True)
    gender = models.IntegerField(verbose_name='性别', null=True)
    province = models.CharField(verbose_name='省份', max_length=100, null=True)
    city = models.CharField(verbose_name='城市', max_length=100, null=True)
    country = models.CharField(verbose_name='国家', max_length=100, null=True)
    lastLoginTime = models.DateTimeField(verbose_name='最近登录', null=True)

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
    # id = models.CharField(verbose_name='ID', max_length=100, primary_key=True, null=False, auto_created=True)
    contents = models.TextField(verbose_name='投诉内容', null=True, blank=True)
    tel = models.CharField(verbose_name='联系方式', null=True, blank=True, max_length=100)
    publishTime = models.DateTimeField(verbose_name='投诉时间', null=False)
    solveTime = models.DateTimeField(verbose_name='受理时间', null=True)
    stats = models.BooleanField(verbose_name='受理状态', default=False)
    solveUser = models.ForeignKey(AdminUser, verbose_name='受理者', on_delete=models.SET_NULL, blank=True, null=True,
                                  db_index=True, related_name='solve_user')
    result = models.TextField(verbose_name='受理结果', null=True, blank=True)

    class Meta:
        verbose_name = '投诉受理'
        verbose_name_plural = '投诉受理'
        permissions = (('solve_advise', 'Can solve advise'),)

    def __str__(self):
        return str(self.id)


class IPKiller(models.Model):
    ip = models.CharField(verbose_name='IP地址', max_length=100, null=True)
    time = models.DateTimeField(verbose_name='上次访问时间', null=True)
    visit = models.IntegerField(verbose_name='访问频率', null=True)
    stats = models.BooleanField(verbose_name='IP状态', null=True, default=True)

    class Meta:
        verbose_name = 'IP封禁'
        verbose_name_plural = 'IP封禁'
        permissions = (('ip_kill', 'Can kill IP address'),)


class Training(models.Model):
    title = models.CharField(verbose_name='主题', max_length=200, null=False, blank=False)
    type = models.CharField(verbose_name='类别', max_length=10, choices=(('B', '毕业指导'), ('X', '学习助手'), ('S', '实用软件')), default='B')
    time = models.DateTimeField(verbose_name='时间', null=False)
    publishTime = models.DateTimeField(verbose_name='发布时间', null=False)
    pubUser = models.ForeignKey(AdminUser, verbose_name='发布者', on_delete=models.SET_NULL, blank=True, null=True,
                                db_index=True, related_name='training_pub_user')
    contents = models.TextField(verbose_name='简介', null=True, blank=True)
    place = models.CharField(verbose_name='地点', max_length=50)
    stats = models.BooleanField(verbose_name='发布状态')

    class Meta:
        verbose_name = '培训管理'
        verbose_name_plural = '培训管理'
        permissions = (('publish_training', 'Can publish trainings'),)

    def __str__(self):
        return self.title

