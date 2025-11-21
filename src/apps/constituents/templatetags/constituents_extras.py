from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def get_sector_color(sector_code):
    """
    Return CSS classes for sector-specific colors with better visibility
    """
    color_map = {
        'student': 'bg-blue-500 text-white',
        'delivery_riders': 'bg-green-500 text-white',
        'dressmaker_weaver': 'bg-purple-500 text-white',
        'farmer': 'bg-yellow-500 text-white',
        'fisherman': 'bg-cyan-500 text-white',
        'women_mothers': 'bg-pink-500 text-white',
        'mujahidin': 'bg-indigo-500 text-white',
        'special_needs': 'bg-orange-500 text-white',
        'pwd_student': 'bg-red-500 text-white',
        'volunteer_teacher': 'bg-teal-500 text-white',
        'small_time_vendor': 'bg-lime-500 text-white',
        'solo_parent': 'bg-emerald-500 text-white',
        'volunteer_health': 'bg-sky-500 text-white',
        'lgbtq_community': 'bg-gradient-to-r from-red-500 via-yellow-500 via-green-500 via-blue-500 to-purple-500 text-white font-bold shadow-lg',
    }

    return color_map.get(sector_code, 'bg-gray-500 text-white')

@register.simple_tag
def get_sector_badge_html(sector_code, sector_display_name):
    """
    Return complete HTML for sector badge with appropriate colors
    """
    css_classes = get_sector_color(sector_code)
    return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {css_classes}">{sector_display_name}</span>')
