# Generated by Django 2.2 on 2020-09-28 08:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('gricapi', '0002_auto_20200926_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='item_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
