# Generated by Django 4.2.4 on 2024-01-31 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0045_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentquestionassignment',
            name='questionID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app1.question'),
        ),
    ]