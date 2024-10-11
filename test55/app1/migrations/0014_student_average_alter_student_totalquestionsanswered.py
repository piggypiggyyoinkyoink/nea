# Generated by Django 4.2.4 on 2023-08-14 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0013_student_totalquestionsanswered'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='average',
            field=models.FloatField(default=100),
        ),
        migrations.AlterField(
            model_name='student',
            name='totalQuestionsAnswered',
            field=models.IntegerField(default=0),
        ),
    ]
