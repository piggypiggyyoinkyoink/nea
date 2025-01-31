# Generated by Django 4.2.4 on 2023-08-11 16:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app1', '0009_remove_student_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='first_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='last_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='noOfCorrectAnswers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='student',
            name='username',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_username', to=settings.AUTH_USER_MODEL),
        ),
    ]
