# Generated by Django 4.1.7 on 2023-03-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_amazonorder_is_business_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySales',
            fields=[
                ('sku', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('daily_average', models.FloatField()),
            ],
            options={
                'db_table': 'sales_daily_quantity_30avg',
                'managed': False,
            },
        ),
    ]