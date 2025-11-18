from django.core.management.base import BaseCommand
from django.db import transaction
from apps.constituents.member_models import FahanieCaresMember

class Command(BaseCommand):
    help = 'Backfills member_id for existing approved FahanieCaresMember instances that do not have one.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting backfill of member IDs...'))
        
        # Find approved members without a member_id
        approved_members_to_update = FahanieCaresMember.objects.filter(
            is_approved=True,
            member_id__isnull=True
        )
        
        # Find pending members without a member_id
        pending_members_to_update = FahanieCaresMember.objects.filter(
            is_approved=False,
            member_id__isnull=True
        )
        
        total_approved_to_update = approved_members_to_update.count()
        total_pending_to_update = pending_members_to_update.count()
        
        total_to_update = total_approved_to_update + total_pending_to_update

        if total_to_update == 0:
            self.stdout.write(self.style.SUCCESS('No members found without a member ID. Exiting.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {total_approved_to_update} approved members and {total_pending_to_update} pending members without a member ID.'))

        updated_count = 0
        with transaction.atomic():
            # Process approved members first
            for member in approved_members_to_update:
                original_member_id = member.member_id
                member.save() # This will trigger the custom save method to generate permanent member_id
                
                if member.member_id and member.member_id != original_member_id:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated approved member {member.get_full_name()} (ID: {member.id}) with permanent member_id: {member.member_id}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped approved member {member.get_full_name()} (ID: {member.id}) - member_id was not generated or already existed.'))

            # Process pending members
            for member in pending_members_to_update:
                original_member_id = member.member_id
                # Manually call _generate_member_id with is_temporary=True and save
                member.member_id = member._generate_member_id(is_temporary=True)
                member.save(update_fields=['member_id']) # Only update member_id to avoid side effects
                
                if member.member_id and member.member_id != original_member_id:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated pending member {member.get_full_name()} (ID: {member.id}) with temporary member_id: {member.member_id}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped pending member {member.get_full_name()} (ID: {member.id}) - temporary member_id was not generated or already existed.'))

        self.stdout.write(self.style.SUCCESS(f'Successfully backfilled member IDs for {updated_count} members.'))
        self.stdout.write(self.style.SUCCESS('Backfill process completed.'))
