document.addEventListener('DOMContentLoaded', function() {
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');

    if (mobileNavToggle && mobileNav && mobileNavOverlay) {
        function toggleMobileNav() {
            mobileNav.classList.toggle('is-open');
            mobileNavOverlay.classList.toggle('is-open');
            // Optional: Add/remove overflow hidden to body to prevent scrolling when nav is open
            document.body.classList.toggle('overflow-hidden');
        }

        mobileNavToggle.addEventListener('click', toggleMobileNav);
        mobileNavOverlay.addEventListener('click', toggleMobileNav); // Close when overlay is clicked
    }
});
