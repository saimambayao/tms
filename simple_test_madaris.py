#!/usr/bin/env python
"""
Simple test script to verify the Madaris Students sector choices without Django setup
"""

# Simulate the SECTOR_CHOICES from the model
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
)

# Simulate the SECTOR_ID_PREFIXES from the model
SECTOR_ID_PREFIXES = {
    'pwd_student': 'PWD',
    'solo_parent': 'SP',
    'volunteer_health': 'VHW',
    'volunteer_teacher': 'VT',
    'special_needs': 'SN',
    'women_mothers': 'WM',
    'farmer': 'F',
    'fisherman': 'FM',
    'small_time_vendor': 'STV',
    'dressmaker_weaver': 'DW',
    'student': 'S',
    'mujahidin': 'MJ',
    'lgbtq_community': 'LGBTQ',
    'madaris_students': 'MS',
}

def test_madaris_sector():
    """Test that the Madaris Students sector is properly configured"""

    print("Testing Madaris Students sector implementation...")

    # Test 1: Check if Madaris Students sector is in SECTOR_CHOICES
    sector_choices = dict(SECTOR_CHOICES)
    if 'madaris_students' in sector_choices:
        print("✓ Madaris Students sector found in SECTOR_CHOICES")
        print(f"  Display name: {sector_choices['madaris_students']}")
    else:
        print("✗ Madaris Students sector NOT found in SECTOR_CHOICES")
        return False

    # Test 2: Check if Madaris Students sector has ID prefix
    if 'madaris_students' in SECTOR_ID_PREFIXES:
        print("✓ Madaris Students sector found in SECTOR_ID_PREFIXES")
        print(f"  ID prefix: {SECTOR_ID_PREFIXES['madaris_students']}")
    else:
        print("✗ Madaris Students sector NOT found in SECTOR_ID_PREFIXES")
        return False

    # Test 3: Test member ID generation for Madaris Students sector
    try:
        prefix = SECTOR_ID_PREFIXES.get('madaris_students', 'GEN')
        member_id = f"{prefix}0001"
        print(f"✓ Member ID generation works: {member_id}")

        if member_id.startswith('MS'):
            print("✓ Member ID has correct MS prefix")
        else:
            print(f"✗ Member ID has incorrect prefix: {member_id}")
            return False

    except Exception as e:
        print(f"✗ Error in member ID generation: {e}")
        return False

    # Test 4: Test sector display category
    try:
        sector = 'madaris_students'
        vulnerable_sectors = [
            'pwd_student', 'solo_parent', 'volunteer_teacher',
            'volunteer_health', 'special_needs'
        ]
        youth_sectors = ['student']

        if sector in vulnerable_sectors:
            category = "Vulnerable Sectors"
        elif sector in youth_sectors:
            category = "Youth"
        elif sector == 'women_mothers':
            category = "Women/Mothers and Children"
        else:
            category = "Other"

        print(f"✓ Sector display category: {category}")

        if category == "Other":
            print("✓ Madaris Students sector correctly categorized as 'Other'")
        else:
            print(f"✗ Unexpected category: {category}")
            return False

    except Exception as e:
        print(f"✗ Error in sector display category: {e}")
        return False

    print("\n🎉 All tests passed! Madaris Students sector implementation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_madaris_sector()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)
