# Generated by Django 4.2.4 on 2023-08-15 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_student_average_alter_student_totalquestionsanswered'),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='className',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
