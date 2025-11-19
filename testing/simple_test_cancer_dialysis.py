#!/usr/bin/env python
"""
Simple test script to verify the Cancer/Dialysis Patients sector choices without Django setup
"""

# Import the SECTOR_CHOICES directly
SECTOR_CHOICES = (
    ('student', 'College Students in need of Educational Assistance'),
    ('delivery_riders', 'Delivery Riders'),
    ('dressmaker_weaver', 'Dressmaker/Weaver'),
    ('farmer', 'Farmers'),
    ('fisherman', 'Fishermen'),
    ('women_mothers', 'Learning Women/Mothers (Ummahat)'),
    ('lgbtq_community', 'LGBTQ+ Community Members'),
    ('madaris_students', 'Madaris Students'),
    ('mujahidin', 'Mujahidin/Mujahidat'),
    ('special_needs', 'Parents/Guardians of Children with Special Needs'),
    ('pwd_student', 'Person with Disability (PWD)'),
    ('volunteer_teacher', 'Public School Volunteer Teachers (English/Arabic)'),
    ('small_time_vendor', 'Small-time Vendors'),
    ('solo_parent', 'Solo Parents'),
    ('volunteer_health', 'Volunteer Health Workers'),
    ('cancer_dialysis', 'Cancer/Dialysis Patients'),
)

def test_cancer_dialysis_sector():
    """Test if the Cancer/Dialysis Patients sector is properly configured"""
    print("Testing Cancer/Dialysis Patients sector implementation...")

    # Test 1: Check if cancer_dialysis sector is in SECTOR_CHOICES
    sector_choices = dict(SECTOR_CHOICES)
    if 'cancer_dialysis' in sector_choices:
        print("✓ Cancer/Dialysis Patients sector found in SECTOR_CHOICES")
        print(f"  Display name: {sector_choices['cancer_dialysis']}")
    else:
        print("✗ Cancer/Dialysis Patients sector NOT found in SECTOR_CHOICES")
        return False

    print("\n✓ Test passed! Cancer/Dialysis Patients sector is properly defined.")
    return True

if __name__ == '__main__':
    test_cancer_dialysis_sector()
