# Generated by Django 4.2.4 on 2023-09-01 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0031_student_noofquizzescompleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='TargetGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=200)),
                ('percentage', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('grade',)},
            },
        ),
    ]
