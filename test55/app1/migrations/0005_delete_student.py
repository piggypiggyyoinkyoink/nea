# Generated by Django 4.2.4 on 2023-08-11 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_student_delete_person'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Student',
        ),
    ]