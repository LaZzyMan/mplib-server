from django.db import models

# Create your models here.


class LibUser(models.Model):
    libId = models.CharField(verbose_name='lib id', max_length=30, primary_key=True)
    libPsw = models.CharField(verbose_name='lib password', max_length=30)
    name = models.CharField(verbose_name='name', max_length=20, null=True)
    department = models.CharField(verbose_name='name', max_length=100, null=True)
    readerType = models.CharField(verbose_name='name', max_length=20, null=True)
    registrationDate = models.DateField(verbose_name='registration date', null=True)
    expiryDate = models.DateField(verbose_name='expiry data', null=True)


class User(models.Model):
    openId = models.CharField(verbose_name='open id', max_length=100, null=True)
    wxSessionKey = models.CharField(verbose_name='wx session key', max_length=100, null=True)
    libAccount = models.ForeignKey(LibUser, on_delete=models.SET_NULL, verbose_name='lib account', blank=True, null=True, db_index=True, related_name='lib')
    session = models.CharField(verbose_name='session', max_length=100, null=True)
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



