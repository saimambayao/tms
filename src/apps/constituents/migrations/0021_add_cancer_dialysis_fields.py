# Generated manually for adding cancer/dialysis patient fields

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('constituents', '0020_add_lgbtq_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='fahaniecaresmember',
            name='cancer_patient',
            field=models.BooleanField(default=False, help_text='Is a cancer patient'),
        ),
        migrations.AddField(
            model_name='fahaniecaresmember',
            name='dialysis_patient',
            field=models.BooleanField(default=False, help_text='Is a dialysis patient'),
        ),
    ]
