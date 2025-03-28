# Generated by Django 5.1.7 on 2025-03-27 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lcwaikiki', '0003_auto_20250326_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='productsitemap',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
