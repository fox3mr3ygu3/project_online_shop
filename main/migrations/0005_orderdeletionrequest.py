# Generated by Django 5.0.6 on 2024-10-30 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_rename_created_at_order_order_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDeletionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField()),
            ],
        ),
    ]
