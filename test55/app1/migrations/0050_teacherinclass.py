# Generated by Django 4.2.4 on 2024-02-24 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0049_alter_student_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherInClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.class')),
                ('teacherID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.teacher')),
            ],
            options={
                'unique_together': {('teacherID', 'classID')},
            },
        ),
    ]