# Footer Styling Documentation

**Last Updated:** 2025-11-19

**Scope:** Footer component styling for consistent implementation

---

## Overview

A clean, professional footer design with a dark background, centered content, and subtle color variations for visual hierarchy. Perfect for government, corporate, or professional websites.

---

## Exact Color Specification

### Background & Text Colors

| Element | Property | Color Code | Tailwind Class | Description |
|---------|----------|------------|----------------|-------------|
| **Footer Background** | `background` | `#1f2937` | `bg-gray-800` | Dark charcoal gray |
| **Primary Text** | `color` | `#ffffff` | `text-white` | Pure white |
| **Secondary Text** | `color` | `#d1d5db` | `text-gray-300` | Light gray |
| **Tertiary/Copyright** | `color` | `#9ca3af` | `text-gray-400` | Medium gray |
| **Accent Icon** | `color` | `#4ade80` | `text-green-400` | Bright green |

---

## Complete Footer Structure

### HTML Implementation

```html
<!-- Footer -->
<footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
            <div class="flex justify-center items-center space-x-2 mb-2">
                <i class="fas fa-mosque text-xl text-green-400"></i>
                <p class="text-lg font-semibold">YOUR TAGLINE HERE</p>
            </div>
            <p class="text-sm text-gray-300">Your Organization Name</p>
            <p class="text-sm text-gray-300">Department or Division</p>
            <p class="text-sm text-gray-300">Location or Region</p>
            <div class="mt-4 text-xs text-gray-400">
                <p>&copy; 2025 Your Organization - All rights reserved</p>
            </div>
        </div>
    </div>
</footer>
```

---

## Spacing & Layout

### Padding & Margins

- **Vertical Padding:** `py-8` (2rem / 32px top & bottom)
- **Top Margin:** `mt-8` (2rem / 32px from main content)
- **Container:** `max-w-7xl mx-auto` (centered, max-width 1280px)
- **Responsive Padding:** `px-4 sm:px-6 lg:px-8` (responsive horizontal padding)

### Content Alignment

- **Main Container:** Centered text (`text-center`)
- **Icon + Tagline:** Flexbox centered (`flex justify-center items-center`)
- **Spacing:** `space-x-2` between icon and tagline, `mb-2` bottom margin

---

## Typography

### Text Sizes & Weights

```css
/* Tagline */
font-size: 1.125rem;     /* text-lg */
font-weight: 600;        /* font-semibold */

/* Organization Lines */
font-size: 0.875rem;     /* text-sm */
font-weight: 400;        /* normal */

/* Copyright */
font-size: 0.75rem;      /* text-xs */
font-weight: 400;        /* normal */

/* Icon */
font-size: 1.25rem;      /* text-xl */
```

---

## Variations

### Footer with Links

```html
<footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <!-- Column 1 -->
            <div>
                <h3 class="text-lg font-semibold mb-4">About</h3>
                <ul class="space-y-2 text-sm text-gray-300">
                    <li><a href="#" class="hover:text-green-400 transition-colors">Our Mission</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">Our Team</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">Contact</a></li>
                </ul>
            </div>

            <!-- Column 2 -->
            <div>
                <h3 class="text-lg font-semibold mb-4">Resources</h3>
                <ul class="space-y-2 text-sm text-gray-300">
                    <li><a href="#" class="hover:text-green-400 transition-colors">Documentation</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">Support</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">FAQs</a></li>
                </ul>
            </div>

            <!-- Column 3 -->
            <div>
                <h3 class="text-lg font-semibold mb-4">Legal</h3>
                <ul class="space-y-2 text-sm text-gray-300">
                    <li><a href="#" class="hover:text-green-400 transition-colors">Privacy Policy</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">Terms of Service</a></li>
                    <li><a href="#" class="hover:text-green-400 transition-colors">Accessibility</a></li>
                </ul>
            </div>
        </div>

        <div class="border-t border-gray-700 pt-8">
            <div class="text-center">
                <div class="flex justify-center items-center space-x-2 mb-2">
                    <i class="fas fa-building text-xl text-green-400"></i>
                    <p class="text-lg font-semibold">YOUR ORGANIZATION</p>
                </div>
                <p class="text-xs text-gray-400 mt-4">&copy; 2025 Your Organization - All rights reserved</p>
            </div>
        </div>
    </div>
</footer>
```

### Footer with Social Media

```html
<footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
            <div class="flex justify-center items-center space-x-2 mb-4">
                <i class="fas fa-globe text-xl text-green-400"></i>
                <p class="text-lg font-semibold">Your Organization</p>
            </div>

            <!-- Social Media Icons -->
            <div class="flex justify-center space-x-4 mb-4">
                <a href="#" class="text-gray-400 hover:text-green-400 transition-colors">
                    <i class="fab fa-facebook text-2xl"></i>
                </a>
                <a href="#" class="text-gray-400 hover:text-green-400 transition-colors">
                    <i class="fab fa-twitter text-2xl"></i>
                </a>
                <a href="#" class="text-gray-400 hover:text-green-400 transition-colors">
                    <i class="fab fa-linkedin text-2xl"></i>
                </a>
                <a href="#" class="text-gray-400 hover:text-green-400 transition-colors">
                    <i class="fab fa-instagram text-2xl"></i>
                </a>
            </div>

            <p class="text-sm text-gray-300">Department Name</p>
            <p class="text-sm text-gray-300">City, Country</p>
            <div class="mt-4 text-xs text-gray-400">
                <p>&copy; 2025 Your Organization - All rights reserved</p>
            </div>
        </div>
    </div>
</footer>
```

### Minimal Footer

```html
<footer class="bg-gray-800 text-white py-6 mt-8">
    <div class="max-w-7xl mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <p>&copy; 2025 Your Organization. All rights reserved.</p>
            <div class="flex space-x-4 mt-2 md:mt-0">
                <a href="#" class="hover:text-green-400 transition-colors">Privacy</a>
                <a href="#" class="hover:text-green-400 transition-colors">Terms</a>
                <a href="#" class="hover:text-green-400 transition-colors">Contact</a>
            </div>
        </div>
    </div>
</footer>
```

---

## Color Palette Reference

### Tailwind Colors Used

```css
/* Background */
--gray-800: #1f2937;

/* Text Colors */
--white: #ffffff;
--gray-300: #d1d5db;
--gray-400: #9ca3af;

/* Accent */
--green-400: #4ade80;
```

### Hex Codes for Non-Tailwind Projects

```css
.footer {
    background-color: #1f2937;
    color: #ffffff;
}

.footer-secondary-text {
    color: #d1d5db;
}

.footer-tertiary-text {
    color: #9ca3af;
}

.footer-accent {
    color: #4ade80;
}
```

---

## Accessibility

### Contrast Ratios

- **White on Gray-800:** 12.63:1 (AAA - Excellent)
- **Gray-300 on Gray-800:** 7.59:1 (AAA)
- **Gray-400 on Gray-800:** 5.22:1 (AA)
- **Green-400 on Gray-800:** 8.21:1 (AAA)

All color combinations meet WCAG 2.1 AA standards (minimum 4.5:1 for normal text).

### Best Practices

- Ensure links have visible focus states
- Use semantic HTML (`<footer>` element)
- Provide sufficient contrast for all text
- Include skip navigation links if needed

---

## Integration Examples

### Tailwind CSS Projects

```html
<footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
            <p class="text-lg font-semibold mb-2">Your Organization</p>
            <p class="text-sm text-gray-300">Supporting text</p>
            <p class="text-xs text-gray-400 mt-4">&copy; 2025 All rights reserved</p>
        </div>
    </div>
</footer>
```

### Vanilla CSS

```css
.footer {
    background-color: #1f2937;
    color: #ffffff;
    padding: 2rem 0;
    margin-top: 2rem;
}

.footer-container {
    max-width: 80rem;
    margin: 0 auto;
    padding: 0 1rem;
    text-align: center;
}

.footer-tagline {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.footer-text {
    font-size: 0.875rem;
    color: #d1d5db;
}

.footer-copyright {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 1rem;
}

.footer-icon {
    color: #4ade80;
    font-size: 1.25rem;
}
```

```html
<footer class="footer">
    <div class="footer-container">
        <p class="footer-tagline">Your Organization</p>
        <p class="footer-text">Department Name</p>
        <p class="footer-text">Location</p>
        <p class="footer-copyright">&copy; 2025 All rights reserved</p>
    </div>
</footer>
```

---

## Framework-Specific Implementations

### React/Next.js

```jsx
const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8 mt-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="flex justify-center items-center space-x-2 mb-2">
            <i className="fas fa-building text-xl text-green-400"></i>
            <p className="text-lg font-semibold">Your Organization</p>
          </div>
          <p className="text-sm text-gray-300">Department Name</p>
          <p className="text-sm text-gray-300">Location</p>
          <div className="mt-4 text-xs text-gray-400">
            <p>&copy; {new Date().getFullYear()} Your Organization - All rights reserved</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
```

### Vue.js

```vue
<template>
  <footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <div class="flex justify-center items-center space-x-2 mb-2">
          <i class="fas fa-building text-xl text-green-400"></i>
          <p class="text-lg font-semibold">Your Organization</p>
        </div>
        <p class="text-sm text-gray-300">Department Name</p>
        <p class="text-sm text-gray-300">Location</p>
        <div class="mt-4 text-xs text-gray-400">
          <p>&copy; {{ currentYear }} Your Organization - All rights reserved</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
</script>
```

### Angular

```typescript
// footer.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {
  currentYear = new Date().getFullYear();
}
```

```html
<!-- footer.component.html -->
<footer class="bg-gray-800 text-white py-8 mt-8">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center">
      <p class="text-lg font-semibold mb-2">Your Organization</p>
      <p class="text-sm text-gray-300">Department Name</p>
      <p class="text-sm text-gray-300">Location</p>
      <div class="mt-4 text-xs text-gray-400">
        <p>&copy; {{ currentYear }} Your Organization - All rights reserved</p>
      </div>
    </div>
  </div>
</footer>
```

---

## Responsive Design

### Mobile Considerations

The footer is fully responsive with:

- **Padding adjustments:** `px-4 sm:px-6 lg:px-8`
- **Centered content:** Works well on all screen sizes
- **Flexible text:** Scales appropriately on mobile devices

### Multi-column Responsive Footer

For footers with multiple columns, use responsive grid:

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
    <!-- Automatically stacks on mobile, 2 columns on tablet, 4 on desktop -->
</div>
```

---

## Quick Copy-Paste

### Basic Footer

```html
<footer class="bg-gray-800 text-white py-8 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
            <p class="text-lg font-semibold">Your Organization</p>
            <p class="text-sm text-gray-300">Your Department</p>
            <p class="text-xs text-gray-400 mt-4">&copy; 2025 All rights reserved</p>
        </div>
    </div>
</footer>
```

### CSS Only

```css
background-color: #1f2937;
color: #ffffff;
padding: 2rem 0;
margin-top: 2rem;
text-align: center;
```

---

## License & Usage

This footer styling specification is provided as-is for use in any project. Attribution is appreciated but not required.
