# Generated by Django 4.2.4 on 2023-08-16 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0016_assignment_alter_student_average_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questioninassignment',
            unique_together={('questionID', 'assignmentID')},
        ),
    ]
