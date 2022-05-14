# Generated by Django 3.0.3 on 2020-03-03 16:33

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields

import gnosis.eth.django.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0011_auto_20200303_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleTransaction',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('internal_tx', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='module_tx', serialize=False, to='history.InternalTx')),
                ('safe', gnosis.eth.django.models.EthereumAddressField(db_index=True)),
                ('module', gnosis.eth.django.models.EthereumAddressField(db_index=True)),
                ('to', gnosis.eth.django.models.EthereumAddressField(db_index=True)),
                ('value', gnosis.eth.django.models.Uint256Field()),
                ('data', models.BinaryField(null=True)),
                ('operation', models.PositiveSmallIntegerField(choices=[(0, 'CALL'), (1, 'DELEGATE_CALL'), (2, 'CREATE')])),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
