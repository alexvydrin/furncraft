# Generated by Django 3.0.5 on 2020-04-25 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_calculation'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='passport_file',
            field=models.FileField(null=True, upload_to='passports/'),
        ),
    ]