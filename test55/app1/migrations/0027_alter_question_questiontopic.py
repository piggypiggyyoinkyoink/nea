# Generated by Django 4.2.4 on 2023-08-23 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0026_questioncategory_question_questioncategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='questionTopic',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
