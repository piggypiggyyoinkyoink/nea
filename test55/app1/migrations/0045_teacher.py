# Generated by Django 4.2.4 on 2023-11-01 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0044_alter_studentassignment_datecompleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('username', models.CharField(max_length=200)),
            ],
        ),
    ]
