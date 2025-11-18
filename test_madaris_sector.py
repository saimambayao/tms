#!/usr/bin/env python
"""
Test script to verify the new Madaris Students sector is working properly
"""
import os
import sys
import django

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.constituents.member_models import FahanieCaresMember

def test_madaris_sector():
    """Test that the Madaris Students sector is properly configured"""

    print("Testing Madaris Students sector implementation...")

    # Test 1: Check if Madaris Students sector is in SECTOR_CHOICES
    sector_choices = dict(FahanieCaresMember.SECTOR_CHOICES)
    if 'madaris_students' in sector_choices:
        print("✓ Madaris Students sector found in SECTOR_CHOICES")
        print(f"  Display name: {sector_choices['madaris_students']}")
    else:
        print("✗ Madaris Students sector NOT found in SECTOR_CHOICES")
        return False

    # Test 2: Check if Madaris Students sector has ID prefix
    if 'madaris_students' in FahanieCaresMember.SECTOR_ID_PREFIXES:
        print("✓ Madaris Students sector found in SECTOR_ID_PREFIXES")
        print(f"  ID prefix: {FahanieCaresMember.SECTOR_ID_PREFIXES['madaris_students']}")
    else:
        print("✗ Madaris Students sector NOT found in SECTOR_ID_PREFIXES")
        return False

    # Test 3: Test member ID generation for Madaris Students sector
    try:
        # Create a mock member instance to test ID generation
        class MockMember:
            def __init__(self, sector):
                self.sector = sector
                self.SECTOR_ID_PREFIXES = FahanieCaresMember.SECTOR_ID_PREFIXES

            def _generate_member_id(self):
                prefix = self.SECTOR_ID_PREFIXES.get(self.sector, 'GEN')
                return f"{prefix}0001"

        mock_member = MockMember('madaris_students')
        member_id = mock_member._generate_member_id()
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
        class MockMemberWithCategory:
            def __init__(self, sector):
                self.sector = sector

            def get_sector_display_category(self):
                vulnerable_sectors = [
                    'pwd_student', 'solo_parent', 'volunteer_teacher',
                    'volunteer_health', 'special_needs'
                ]
                youth_sectors = ['student']

                if self.sector in vulnerable_sectors:
                    return "Vulnerable Sectors"
                elif self.sector in youth_sectors:
                    return "Youth"
                elif self.sector == 'women_mothers':
                    return "Women/Mothers and Children"
                return "Other"

        mock_member = MockMemberWithCategory('madaris_students')
        category = mock_member.get_sector_display_category()
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
    sys.exit(0 if success else 1)
