# Generated manually for adding LGBTQ identity field

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('constituents', '0019_add_pwd_disability_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='fahaniecaresmember',
            name='lgbtq_identity',
            field=models.CharField(blank=True, choices=[('gay', 'Gay'), ('lesbian', 'Lesbian'), ('bisexual', 'Bisexual'), ('transgender', 'Transgender'), ('queer', 'Queer'), ('questioning', 'Questioning'), ('intersex', 'Intersex'), ('asexual', 'Asexual'), ('pansexual', 'Pansexual'), ('non_binary', 'Non-Binary'), ('genderfluid', 'Genderfluid'), ('two_spirit', 'Two-Spirit'), ('other', 'Other')], help_text='LGBTQ+ identity', max_length=30),
        ),
    ]
