from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.constituents.member_models import FahanieCaresMember

@login_required
def dashboard(request):
    # Get unique provinces and municipalities, excluding null/empty values
    provinces = sorted(list(
        FahanieCaresMember.objects
        .exclude(address_province__isnull=True)
        .exclude(address_province__exact='')
        .values_list('address_province', flat=True)
        .distinct()
    ))

    municipalities = sorted(list(
        FahanieCaresMember.objects
        .exclude(address_municipality__isnull=True)
        .exclude(address_municipality__exact='')
        .values_list('address_municipality', flat=True)
        .distinct()
    ))

    # Ensure uniqueness by converting to set and back to list
    provinces = sorted(list(set(provinces)))
    municipalities = sorted(list(set(municipalities)))

    # Get all sectors from the model choices, not from database
    sectors = sorted([choice[0] for choice in FahanieCaresMember.SECTOR_CHOICES])
    # Get sector display names for the dropdown
    sector_display_names = sorted([choice[1] for choice in FahanieCaresMember.SECTOR_CHOICES])

    context = {
        'provinces': provinces,
        'municipalities': municipalities,
        'sectors': sectors,
        'sector_display_names': sector_display_names,
    }
    return render(request, 'analytics/dashboard.html', context)
