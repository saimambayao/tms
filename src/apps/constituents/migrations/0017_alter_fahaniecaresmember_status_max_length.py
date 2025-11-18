# Generated manually to fix status field max_length for non_compliant status

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('constituents', '0016_constituentgroup_registrant_members_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fahaniecaresmember',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('incomplete', 'Incomplete'),
                    ('non_compliant', 'Non Compliant'),
                    ('archived', 'Archived')
                ],
                default='pending',
                max_length=15
            ),
        ),
    ]
