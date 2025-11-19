# Generated migration to rename related_name from fahanie_cares_member to bm_parliament_member
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('constituents', '0022_alter_bmparliamentmember_sector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bmparliamentmember',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bm_parliament_member',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
