# Generated by Django 4.1.7 on 2023-03-06 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_inventory_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='notes',
            field=models.TextField(null=True),
        ),
    ]
