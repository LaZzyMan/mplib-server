# Generated by Django 2.2.1 on 2019-05-31 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mplib', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libuser',
            name='department',
            field=models.CharField(max_length=100, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='libuser',
            name='expiryDate',
            field=models.DateField(null=True, verbose_name='expiry data'),
        ),
        migrations.AddField(
            model_name='libuser',
            name='name',
            field=models.CharField(max_length=20, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='libuser',
            name='readerType',
            field=models.CharField(max_length=20, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='libuser',
            name='registrationDate',
            field=models.DateField(null=True, verbose_name='registration date'),
        ),
    ]
