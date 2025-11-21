/**
 * Mobile Navigation Menu Handler
 * Pure vanilla JavaScript implementation for BM Parliament mobile menu
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const hamburgerIcon = document.getElementById('hamburger-icon');
    const closeIcon = document.getElementById('close-icon');

    // Check if all required elements exist
    if (!mobileMenuButton || !mobileMenu || !hamburgerIcon || !closeIcon) {
        console.warn('Mobile navigation elements not found');
        return;
    }

    /**
     * Toggle mobile menu visibility
     */
    function toggleMobileMenu() {
        const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
        
        // Toggle aria-expanded attribute for accessibility
        mobileMenuButton.setAttribute('aria-expanded', String(!isExpanded));
        mobileMenu.setAttribute('aria-hidden', String(isExpanded));
        
        // Toggle menu visibility
        if (isExpanded) {
            // Close menu
            mobileMenu.classList.add('max-h-0');
            mobileMenu.classList.remove('max-h-screen');
            setTimeout(() => {
                mobileMenu.classList.add('hidden');
            }, 300); // Wait for transition to complete
        } else {
            // Open menu
            mobileMenu.classList.remove('hidden');
            // Force reflow
            mobileMenu.offsetHeight;
            mobileMenu.classList.remove('max-h-0');
            mobileMenu.classList.add('max-h-screen');
        }
        
        // Toggle icons
        hamburgerIcon.classList.toggle('hidden');
        hamburgerIcon.classList.toggle('block');
        closeIcon.classList.toggle('hidden');
        closeIcon.classList.toggle('block');
        
        // Prevent body scroll when menu is open
        document.body.classList.toggle('overflow-hidden');
    }

    /**
     * Close mobile menu
     */
    function closeMobileMenu() {
        const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
        if (isExpanded) {
            toggleMobileMenu();
        }
    }

    // Event listener for menu button
    mobileMenuButton.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMobileMenu();
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
            closeMobileMenu();
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });

    // Close menu when clicking on a link inside the menu
    const menuLinks = mobileMenu.querySelectorAll('a');
    menuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            closeMobileMenu();
        });
    });

    // Handle window resize - close menu if resized to desktop
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth >= 768) { // md breakpoint
                closeMobileMenu();
            }
        }, 250);
    });
});
