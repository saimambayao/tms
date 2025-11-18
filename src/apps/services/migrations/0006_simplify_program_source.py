# Generated manually for simplifying program_source choices

from django.db import migrations, models


def update_program_sources(apps, schema_editor):
    """Update existing program sources to simplified categories."""
    MinistryProgram = apps.get_model('services', 'MinistryProgram')
    
    # Update TDIF Infrastructure and Non-Infrastructure to just TDIF
    MinistryProgram.objects.filter(
        program_source__in=['tdif_infra', 'tdif_non_infra']
    ).update(program_source='tdif')


def reverse_program_sources(apps, schema_editor):
    """Reverse the update - split TDIF back into infra and non-infra."""
    # This is a simplified reverse - in reality you'd need to determine
    # which were infra vs non-infra based on other fields
    MinistryProgram = apps.get_model('services', 'MinistryProgram')
    
    # For reverse migration, we'll default all TDIF to tdif_infra
    # In a real scenario, you'd want to preserve the original distinction
    MinistryProgram.objects.filter(
        program_source='tdif'
    ).update(program_source='tdif_infra')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_add_program_source'),
    ]

    operations = [
        # First run the data migration to update existing values
        migrations.RunPython(update_program_sources, reverse_program_sources),
        
        # Then alter the field to use the new choices
        migrations.AlterField(
            model_name='ministryprogram',
            name='program_source',
            field=models.CharField(
                choices=[
                    ('fahaniecares', '#FahanieCares Program'),
                    ('tdif', 'TDIF Project'),
                    ('ministry', 'Ministry Program')
                ],
                default='ministry',
                help_text='Source/category of this program',
                max_length=20
            ),
        ),
    ]