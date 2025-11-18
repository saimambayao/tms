import os
import django
from django.utils import timezone
from datetime import date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.referrals.models import Agency, ServiceCategory, Service
from apps.constituents.models import Constituent, FahanieCaresMember
from apps.chapters.models import Chapter
from apps.services.models import MinistryProgram

def create_sample_data():
    # Create sample agencies
    print("Creating sample agencies...")
    
    moh = Agency.objects.get_or_create(
        name="Ministry of Health",
        defaults={
            'abbreviation': 'MOH',
            'ministry': 'Health',
            'description': 'The Ministry of Health is responsible for healthcare services, policies, and programs in the Bangsamoro region.',
            'contact_person': 'Dr. Amirel Usman',
            'contact_email': 'health@bangsamoro.gov',
            'contact_phone': '(123) 456-7890',
            'address': 'Health Complex, Cotabato City',
            'website': 'https://bangsamoro.gov.ph/health',
            'is_active': True
        }
    )[0]
    
    moe = Agency.objects.get_or_create(
        name="Ministry of Education",
        defaults={
            'abbreviation': 'MOE',
            'ministry': 'Education',
            'description': 'The Ministry of Education oversees the educational system in the Bangsamoro region.',
            'contact_person': 'Dr. Mohagher Iqbal',
            'contact_email': 'education@bangsamoro.gov',
            'contact_phone': '(123) 456-7891',
            'address': 'Education Building, Cotabato City',
            'website': 'https://bangsamoro.gov.ph/education',
            'is_active': True
        }
    )[0]
    
    mosw = Agency.objects.get_or_create(
        name="Ministry of Social Welfare",
        defaults={
            'abbreviation': 'MOSW',
            'ministry': 'Social Welfare',
            'description': 'The Ministry of Social Welfare provides social services and assistance to disadvantaged and vulnerable populations.',
            'contact_person': 'Raissa Jajurie',
            'contact_email': 'socialwelfare@bangsamoro.gov',
            'contact_phone': '(123) 456-7892',
            'address': 'Social Welfare Complex, Cotabato City',
            'website': 'https://bangsamoro.gov.ph/socialwelfare',
            'is_active': True
        }
    )[0]
    
    # Create sample service categories
    print("Creating sample service categories...")
    
    health_category = ServiceCategory.objects.get_or_create(
        name="Healthcare Services",
        defaults={
            'description': 'Medical and healthcare services for individuals and families',
            'icon': 'fas fa-heartbeat',
            'slug': 'healthcare-services',
            'order': 1
        }
    )[0]
    
    medical_assistance = ServiceCategory.objects.get_or_create(
        name="Medical Assistance",
        defaults={
            'description': 'Financial assistance for healthcare needs',
            'icon': 'fas fa-hand-holding-medical',
            'slug': 'medical-assistance',
            'parent': health_category,
            'order': 1
        }
    )[0]
    
    vaccination = ServiceCategory.objects.get_or_create(
        name="Vaccination Programs",
        defaults={
            'description': 'Immunization and vaccination services',
            'icon': 'fas fa-syringe',
            'slug': 'vaccination-programs',
            'parent': health_category,
            'order': 2
        }
    )[0]
    
    education_category = ServiceCategory.objects.get_or_create(
        name="Education Services",
        defaults={
            'description': 'Educational support and services for students',
            'icon': 'fas fa-graduation-cap',
            'slug': 'education-services',
            'order': 2
        }
    )[0]
    
    scholarship = ServiceCategory.objects.get_or_create(
        name="Scholarship Programs",
        defaults={
            'description': 'Financial assistance for education',
            'icon': 'fas fa-award',
            'slug': 'scholarship-programs',
            'parent': education_category,
            'order': 1
        }
    )[0]
    
    social_welfare_category = ServiceCategory.objects.get_or_create(
        name="Social Welfare",
        defaults={
            'description': 'Social assistance and welfare services',
            'icon': 'fas fa-hands-helping',
            'slug': 'social-welfare',
            'order': 3
        }
    )[0]
    
    financial_assistance = ServiceCategory.objects.get_or_create(
        name="Financial Assistance",
        defaults={
            'description': 'Financial support for individuals and families in need',
            'icon': 'fas fa-money-bill-wave',
            'slug': 'financial-assistance',
            'parent': social_welfare_category,
            'order': 1
        }
    )[0]
    
    # Create sample services
    print("Creating sample services...")
    
    # Health services
    Service.objects.get_or_create(
        name="Medical Assistance Program",
        defaults={
            'description': 'Financial assistance for medical expenses, hospitalization, and medicines for qualified residents.',
            'category': medical_assistance,
            'agency': moh,
            'eligibility_criteria': '- Bangsamoro resident\n- Monthly family income below poverty threshold\n- Has existing medical condition requiring treatment',
            'required_documents': '- Valid ID\n- Proof of residency\n- Medical certificate\n- Hospital bill or prescription\n- Income certificate',
            'application_process': '1. Submit application form with required documents\n2. Undergo assessment interview\n3. Wait for approval\n4. Receive assistance check or voucher',
            'processing_time': '5-7 working days',
            'fees': 'None',
            'contact_info': 'Medical Assistance Unit\nPhone: (123) 456-7890\nEmail: medical@bangsamoro.gov',
            'is_active': True,
            'slug': 'medical-assistance-program'
        }
    )
    
    Service.objects.get_or_create(
        name="Childhood Vaccination Program",
        defaults={
            'description': 'Free vaccination services for children to prevent diseases like measles, polio, diphtheria, tetanus, and more.',
            'category': vaccination,
            'agency': moh,
            'eligibility_criteria': '- Children aged 0-5 years\n- Bangsamoro resident',
            'required_documents': '- Child\'s birth certificate\n- Proof of residency\n- Vaccination card (if available)',
            'application_process': '1. Visit the nearest health center\n2. Register child for vaccination\n3. Complete vaccination schedule',
            'processing_time': 'Same day service',
            'fees': 'Free',
            'contact_info': 'Immunization Program\nPhone: (123) 456-7893\nEmail: vaccination@bangsamoro.gov',
            'is_active': True,
            'slug': 'childhood-vaccination-program'
        }
    )
    
    # Education services
    Service.objects.get_or_create(
        name="Bangsamoro Educational Assistance Program",
        defaults={
            'description': 'Scholarship grants for deserving students from low-income families to pursue higher education.',
            'category': scholarship,
            'agency': moe,
            'eligibility_criteria': '- Bangsamoro resident\n- High school graduate or currently enrolled in college\n- General weighted average of at least 85%\n- Family income below poverty threshold',
            'required_documents': '- School registration form\n- Grades/transcript of records\n- Birth certificate\n- Certificate of good moral character\n- Income certificate\n- Barangay certification of residency',
            'application_process': '1. Submit application form with required documents\n2. Take qualifying examination\n3. Undergo interview\n4. Wait for selection results\n5. Sign scholarship contract if selected',
            'processing_time': '30-45 days',
            'fees': 'None',
            'contact_info': 'Scholarship Office\nPhone: (123) 456-7894\nEmail: scholarship@bangsamoro.gov',
            'is_active': True,
            'slug': 'bangsamoro-educational-assistance-program'
        }
    )
    
    # Social welfare services
    Service.objects.get_or_create(
        name="Emergency Cash Assistance",
        defaults={
            'description': 'One-time cash assistance for families affected by disasters, calamities, or crisis situations.',
            'category': financial_assistance,
            'agency': mosw,
            'eligibility_criteria': '- Bangsamoro resident\n- Affected by disaster or crisis\n- Low-income household\n- Not a recipient of similar assistance within the last 6 months',
            'required_documents': '- Valid ID\n- Proof of residency\n- Barangay certification of indigency\n- Disaster/crisis certification\n- Photos of damage (if applicable)',
            'application_process': '1. Submit application form with required documents\n2. Undergo assessment interview\n3. Wait for approval\n4. Receive cash assistance',
            'processing_time': '3-5 working days',
            'fees': 'None',
            'contact_info': 'Crisis Intervention Unit\nPhone: (123) 456-7895\nEmail: crisis@bangsamoro.gov',
            'is_active': True,
            'slug': 'emergency-cash-assistance'
        }
    )

    # Create sample Constituents (Registered Members)
    print("Creating sample constituents...")
    Constituent.objects.get_or_create(
        first_name="Juan",
        last_name="Dela Cruz",
        defaults={
            'middle_name': 'Santos',
            'suffix_name': '',
            'birth_date': date(1990, 5, 15),
            'sex': 'male',
            'contact_number': '09171234567',
            'email': 'juan.delacruz@example.com',
            'region': 'BARMM',
            'province': 'Maguindanao del Norte',
            'municipality': 'Datu Odin Sinsuat',
            'barangay': 'Dalican',
            'complete_address': 'Purok 1, Dalican, Datu Odin Sinsuat, Maguindanao del Norte',
            'civil_status': 'single',
            'occupation': 'Farmer',
            'income_level': 'below_poverty',
            'sector': 'agriculture',
            'highest_education': 'high_school_graduate',
            'eligibility': 'indigent',
            'is_approved': True,
            'date_registered': timezone.now().date(),
        }
    )
    Constituent.objects.get_or_create(
        first_name="Maria",
        last_name="Santos",
        defaults={
            'middle_name': 'Reyes',
            'suffix_name': '',
            'birth_date': date(1988, 11, 22),
            'sex': 'female',
            'contact_number': '09179876543',
            'email': 'maria.santos@example.com',
            'region': 'BARMM',
            'province': 'Maguindanao del Sur',
            'municipality': 'Datu Piang',
            'barangay': 'Reina Regente',
            'complete_address': 'Sitio Centro, Reina Regente, Datu Piang, Maguindanao del Sur',
            'civil_status': 'married',
            'occupation': 'Teacher',
            'income_level': 'middle_income',
            'sector': 'education',
            'highest_education': 'college_graduate',
            'eligibility': 'general',
            'is_approved': True,
            'date_registered': timezone.now().date(),
        }
    )
    Constituent.objects.get_or_create(
        first_name="Ahmed",
        last_name="Abdullah",
        defaults={
            'middle_name': 'Ali',
            'suffix_name': '',
            'birth_date': date(1975, 3, 10),
            'sex': 'male',
            'contact_number': '09175551234',
            'email': 'ahmed.abdullah@example.com',
            'region': 'BARMM',
            'province': 'Lanao del Sur',
            'municipality': 'Marawi City',
            'barangay': 'Dansalan',
            'complete_address': 'Block 5, Dansalan, Marawi City, Lanao del Sur',
            'civil_status': 'married',
            'occupation': 'Businessman',
            'income_level': 'high_income',
            'sector': 'trade_and_industry',
            'highest_education': 'post_graduate',
            'eligibility': 'general',
            'is_approved': True,
            'date_registered': timezone.now().date(),
        }
    )

    # Create sample Chapters
    print("Creating sample chapters...")
    Chapter.objects.get_or_create(
        name="Datu Odin Sinsuat Chapter",
        defaults={
            'location': 'Datu Odin Sinsuat, Maguindanao del Norte',
            'tier': 'municipal',
            'status': 'active',
            'description': 'Active chapter serving the municipality of Datu Odin Sinsuat.',
            'coordinator_name': 'Aisha Khan',
            'contact_number': '09171112222',
            'email': 'dos.chapter@example.com',
            'established_date': date(2023, 1, 15),
        }
    )
    Chapter.objects.get_or_create(
        name="Cotabato City Chapter",
        defaults={
            'location': 'Cotabato City',
            'tier': 'city',
            'status': 'active',
            'description': 'Key chapter covering Cotabato City and surrounding areas.',
            'coordinator_name': 'Omar Hassan',
            'contact_number': '09173334444',
            'email': 'cotabato.chapter@example.com',
            'established_date': date(2022, 8, 1),
        }
    )

    # Create sample Ministry Programs (Community Events)
    print("Creating sample Ministry Programs (Community Events)...")
    MinistryProgram.objects.get_or_create(
        title="Community Health Caravan",
        defaults={
            'ministry': 'moh',
            'program_source': 'fahaniecares',
            'ppa_type': 'program',
            'status': 'active',
            'priority_level': 'high',
            'start_date': date(2024, 6, 1),
            'end_date': date(2024, 6, 30),
            'total_budget': 500000.00,
            'geographic_coverage': 'Various Barangays',
            'target_beneficiaries': 'All residents',
            'description': 'Providing free medical check-ups, consultations, and medicines to underserved communities.',
            'objectives': 'Improve health access in remote areas.',
            'expected_outcomes': 'Increased health awareness and reduced common illnesses.',
            'is_public': True,
            'is_featured': True,
            'slug': 'community-health-caravan',
        }
    )
    MinistryProgram.objects.get_or_create(
        title="Youth Leadership Summit",
        defaults={
            'ministry': 'mbasiced',
            'program_source': 'fahaniecares',
            'ppa_type': 'activity',
            'status': 'active',
            'priority_level': 'medium',
            'start_date': date(2024, 7, 10),
            'end_date': date(2024, 7, 12),
            'total_budget': 150000.00,
            'geographic_coverage': 'Regional',
            'target_beneficiaries': 'Youth leaders aged 18-30',
            'description': 'A summit to empower young leaders with skills in governance and community development.',
            'objectives': 'Develop leadership capabilities among Bangsamoro youth.',
            'expected_outcomes': 'More engaged and effective youth leaders.',
            'is_public': True,
            'is_featured': False,
            'slug': 'youth-leadership-summit',
        }
    )
    MinistryProgram.objects.get_or_create(
        title="Livelihood Training for Women",
        defaults={
            'ministry': 'mle',
            'program_source': 'fahaniecares',
            'ppa_type': 'program',
            'status': 'completed',
            'priority_level': 'high',
            'start_date': date(2023, 9, 1),
            'end_date': date(2023, 11, 30),
            'total_budget': 300000.00,
            'geographic_coverage': 'Selected Municipalities',
            'target_beneficiaries': 'Women from low-income households',
            'description': 'Skills training in various crafts to provide sustainable livelihood opportunities for women.',
            'objectives': 'Empower women economically.',
            'expected_outcomes': 'Increased household income and self-sufficiency.',
            'is_public': True,
            'is_featured': True,
            'slug': 'livelihood-training-women',
        }
    )
    
    print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()
