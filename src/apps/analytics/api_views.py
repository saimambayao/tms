from django.http import JsonResponse
from django.db.models import Count
from apps.constituents.member_models import FahanieCaresMember
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate

def get_filtered_queryset(request):
    queryset = FahanieCaresMember.objects.all()
    province = request.GET.get('province')
    municipality = request.GET.get('municipality')
    sector = request.GET.get('sector')

    if province and province != 'All':
        queryset = queryset.filter(address_province=province)
    if municipality and municipality != 'All':
        queryset = queryset.filter(address_municipality=municipality)
    if sector and sector != 'All':
        queryset = queryset.filter(sector=sector)
        
    return queryset

def summary_data(request):
    queryset = get_filtered_queryset(request)
    total_members = queryset.count()
    
    # New members this month
    today = datetime.today()
    start_of_month = today.replace(day=1)
    new_this_month = queryset.filter(date_of_application__gte=start_of_month).count()
    
    # Active percentage (based on 'approved' status)
    approved_members = queryset.filter(status='approved').count()
    active_percentage = (approved_members / total_members * 100) if total_members > 0 else 0
    
    data = {
        'total_members': total_members,
        'new_this_month': new_this_month,
        'active_percentage': round(active_percentage, 2),
    }
    return JsonResponse(data)

def gender_distribution(request):
    queryset = get_filtered_queryset(request)
    data = queryset.values('sex').annotate(count=Count('id'))
    return JsonResponse(list(data), safe=False)

def age_distribution(request):
    queryset = get_filtered_queryset(request)
    data = queryset.values('age').annotate(count=Count('id')).order_by('age')
    return JsonResponse(list(data), safe=False)

def membership_status_distribution(request):
    queryset = get_filtered_queryset(request)
    data = queryset.values('status').annotate(count=Count('id'))
    # The 'status' field already contains the correct labels ('pending', 'approved', 'incomplete', 'archived')
    # No need to map from 'is_approved'
    return JsonResponse(list(data), safe=False)

def sector_distribution(request):
    queryset = get_filtered_queryset(request)
    data = queryset.values('sector').annotate(count=Count('id'))
    return JsonResponse(list(data), safe=False)

def registration_trend(request):
    queryset = get_filtered_queryset(request)
    data = queryset.annotate(date=TruncDate('date_of_application')).values('date').annotate(count=Count('id')).order_by('date')
    return JsonResponse(list(data), safe=False)

def sector_status_distribution(request):
    queryset = get_filtered_queryset(request)
    data = queryset.values('sector', 'status').annotate(count=Count('id')).order_by('sector', 'status')
    return JsonResponse(list(data), safe=False)
