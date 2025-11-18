# Generated manually for adding PWD disability type field

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('constituents', '0018_add_college_student_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='fahaniecaresmember',
            name='pwd_disability_type',
            field=models.CharField(blank=True, choices=[('physical', 'Physical Disability'), ('mental', 'Mental/Intellectual Disability')], help_text='Type of disability', max_length=20),
        ),
    ]
