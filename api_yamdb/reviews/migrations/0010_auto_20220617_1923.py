# Generated by Django 2.2.16 on 2022-06-17 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0009_auto_20220617_1841'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='review',
            name='unique_author_review',
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('author', 'title'), name='unique_author_review'),
        ),
    ]
