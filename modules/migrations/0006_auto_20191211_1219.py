# Generated by Django 2.2 on 2019-12-11 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0005_auto_20191210_1959'),
    ]

    operations = [
        migrations.AddField(
            model_name='undefinedmodule',
            name='academic_year',
            field=models.CharField(default='a', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='undefinedmodule',
            name='assessment_group_code',
            field=models.CharField(default='a', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='undefinedmodule',
            name='year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]