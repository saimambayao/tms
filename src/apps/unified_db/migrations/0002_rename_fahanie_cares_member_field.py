# Generated migration to rename PersonLink field from fahanie_cares_member to bm_parliament_member
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('constituents', '0023_rename_fahanie_cares_member_to_bm_parliament_member'),
        ('unified_db', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personlink',
            old_name='fahanie_cares_member',
            new_name='bm_parliament_member',
        ),
    ]
