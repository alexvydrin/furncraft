# Generated by Django 3.0.5 on 2020-04-06 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20200405_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, null=True)),
                ('waste_percent', models.FloatField(blank=True, null=True)),
                ('cost_add', models.FloatField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('cost_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.Cost')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
    ]
