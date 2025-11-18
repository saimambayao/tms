from django.contrib import admin
from .models import Cooperative, CooperativeMembership

@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooperative_type', 'status', 'municipality', 'province')
    list_filter = ('cooperative_type', 'status', 'province', 'municipality')
    search_fields = ('name', 'registration_number')

@admin.register(CooperativeMembership)
class CooperativeMembershipAdmin(admin.ModelAdmin):
    list_display = ('cooperative', 'fahaniecares_member', 'position', 'is_active')
    list_filter = ('position', 'is_active')
    search_fields = ('cooperative__name', 'fahaniecares_member__last_name', 'fahaniecares_member__first_name')
