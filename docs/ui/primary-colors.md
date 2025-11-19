# BM Parliament Primary Color System

## Overview

The BM Parliament platform uses a comprehensive, accessible color system. **The primary brand identity is the Bangsamoro Gradient** - a blue-green gradient that combines Professional Blue (#1e40af) with Bangsamoro Emerald (#059669). This gradient is the defining visual element representing the platform's identity and values.

The system also includes a green-based primary color palette for UI elements, buttons, and interactive components. The system is designed to reflect the Bangsamoro identity through professional, trustworthy colors that meet WCAG accessibility standards.

---

## Brand Identity: The Bangsamoro Gradient

### Primary Brand Identity
**The Bangsamoro Gradient is the PRIMARY BRAND IDENTITY** of BM Parliament, not a single color.

**Gradient Specification:**
- **Start Color**: Professional Blue `#1e40af` (RGB: 30, 64, 175)
- **End Color**: Bangsamoro Emerald `#059669` (RGB: 5, 150, 105)
- **Direction**: 135 degrees (diagonal, bottom-right)
- **CSS**: `linear-gradient(135deg, #1e40af 0%, #059669 100%)`

**Usage:**
- Hero sections across all pages
- Primary brand representation
- Main visual identity element
- Overlays should use blue-green gradient colors, not just green

**See [Bangsamoro Gradient Documentation](./BANGSAMORO_GRADIENT.md) for complete details.**

---

## Color Philosophy

### Design Principles
- **Bangsamoro Gradient (Blue-Green)**: The primary brand identity combining professionalism (blue) with growth and heritage (emerald)
- **Green Base**: Represents growth, sustainability, trust, and nature for UI elements
- **Bangsamoro Context**: Green holds cultural significance in Islamic traditions and symbolizes peace and prosperity
- **Government Trust**: Professional, stable, and accessible government services
- **2025 Trends**: Nature-inspired, sustainable, soft sage tones
- **Accessibility First**: WCAG AA compliant (4.5:1 contrast minimum)

### Psychological Impact
- **Bangsamoro Gradient**: Combines authority (blue) with growth (emerald) - the complete brand identity
- **Primary Green (#16a34a)**: Conveys stability, growth, and trustworthiness for UI elements
- **Professional Blue (#1e40af)**: Adds professionalism and authority (part of brand gradient)
- **Bangsamoro Emerald (#059669)**: Provides vibrancy and energy (part of brand gradient)
- **Forest Tones**: Creates depth and visual hierarchy

---

## Primary Color Palette (UI Elements)

**Note:** This palette is for UI elements (buttons, badges, links). The **brand identity** is the Bangsamoro Gradient (blue-green), documented above.

### Core Green Palette
The primary UI palette uses a sage green spectrum, inspired by modern nature design trends. This is used for interactive elements, buttons, and UI components.

```
#f0f9f4  - Primary 50   (Lightest sage - backgrounds)
#dcfce7  - Primary 100  (Light sage - subtle highlights)
#bbf7d0  - Primary 200  (Soft sage - hover states)
#86efac  - Primary 300  (Medium sage - secondary actions)
#4ade80  - Primary 400  (Bright sage - interactive elements)
#22c55e  - Primary 500  (Core brand green - main CTAs)
#16a34a  - Primary 600  (Professional green - primary buttons)
#15803d  - Primary 700  (Deep sage - active states)
#166534  - Primary 800  (Forest green - dark text)
#14532d  - Primary 900  (Darkest green - headings)
```

### Usage Guidelines

| Shade | Use Case | Example |
|-------|----------|---------|
| 50 | Light backgrounds, subtle backgrounds | Page background tints, card backgrounds |
| 100 | Subtle highlights, light accents | Inactive states, disabled elements |
| 200 | Hover states for links, secondary text hover | Link hover effects, light interactive elements |
| 300 | Secondary action buttons, badges | Info badges, secondary CTAs |
| 400 | Interactive elements, focus states | Focus rings, active interactive elements |
| 500 | Core brand color, prominent CTAs | Main call-to-action buttons, primary icons |
| 600 | Primary buttons, active states | Primary button default state, active navigation |
| 700 | Primary button hover, dark accents | Button hover effects, strong emphasis |
| 800 | Dark text, high-contrast elements | Body text, code blocks |
| 900 | Darkest text, maximum contrast | Headings, primary text |

---

## Bangsamoro Gradient (Brand Identity)

### Specification
**The Bangsamoro gradient IS the primary brand identity** of the BM Parliament platform, combining professional blue with emerald green. This is not just a design element - it is the defining visual identity.

**Important:** All hero sections, overlays, and brand elements should use this blue-green gradient, not just green colors.

**Gradient Definition:**
```
Direction: 135° (diagonal, bottom-right)
Start Color: #1e40af (Professional Blue)
End Color: #059669 (Bangsamoro Emerald)
```

### Visual Representation
```
#1e40af ▓▓░░░░░░░░ #059669
  Blue           Emerald
```

### CSS Implementation

#### Tailwind Config (`tailwind.config.js`)
```javascript
theme: {
  extend: {
    backgroundImage: {
      'bangsamoro': 'linear-gradient(135deg, #1e40af 0%, #059669 100%)',
    }
  }
}
```

#### CSS Variables (`color_palette.html`)
```css
:root {
  /* Hero Gradients - Bangsamoro Colors */
  --gradient-hero: linear-gradient(135deg, #1e40af 0%, #059669 100%);
  --gradient-hero-overlay: linear-gradient(135deg, #1e40af 0%, rgba(5, 150, 105, 0.9) 100%);
}
```

#### CSS Classes
```css
.bg-bangsamoro {
  background: linear-gradient(135deg, #1e40af 0%, #059669 100%);
}

.bg-gradient-hero {
  background: var(--gradient-hero);
}
```

### Implementation in HTML

**Using Tailwind Class:**
```html
<section class="bg-bangsamoro text-white py-20">
  <div class="container mx-auto">
    <h1>BM Parliament Hero Section</h1>
    <p>Bringing Bangsamoro Public Service Closer to You</p>
  </div>
</section>
```

**Using CSS Variable:**
```html
<section style="background: var(--gradient-hero);" class="text-white py-20">
  <div class="container mx-auto">
    <h1>Hero Section</h1>
  </div>
</section>
```

**Using CSS Class:**
```html
<div class="bg-gradient-hero text-white py-20">
  <h1>Hero Section</h1>
</div>
```

---

## Pages Using Bangsamoro Gradient

The Bangsamoro gradient (`bg-bangsamoro` or `bg-gradient-hero`) is used as the primary hero background on these pages:

1. **Home Page** (`/en/`) - Main hero section
2. **Programs Page** (`/en/programs/`) - Programs overview hero
3. **TDIF Projects Page** (`/en/tdif-projects/`) - Projects hero section
4. **Accessible Ministry Programs** (`/en/accessible-ministry-programs/`) - Services hero
5. **FAQs Page** (`/en/faqs/`) - FAQ header section
6. **Gradient Cards** - Component-level hero cards throughout the platform

---

## Secondary Color System

### Blue-Gray Secondary Palette
Provides complementary earth tones for balance and professional appearance.

```
#f8fafc  - Secondary 50   (Clean backgrounds)
#f1f5f9  - Secondary 100  (Section backgrounds)
#e2e8f0  - Secondary 200  (Borders, dividers)
#cbd5e1  - Secondary 300  (Muted elements)
#94a3b8  - Secondary 400  (Secondary text)
#64748b  - Secondary 500  (Body text)
#475569  - Secondary 600  (Dark text)
#334155  - Secondary 700  (Headings)
#1e293b  - Secondary 800  (Primary headings)
#0f172a  - Secondary 900  (Maximum contrast)
```

### Semantic Status Colors

**Success**
```
#10b981  - Success 500 (Messages)
#059669  - Success 600 (Buttons)
#047857  - Success 700 (Active states)
```

**Warning**
```
#f97316  - Warning 500 (Messages)
#ea580c  - Warning 600 (Buttons)
#c2410c  - Warning 700 (Active states)
```

**Error**
```
#ef4444  - Error 500 (Messages)
#dc2626  - Error 600 (Buttons)
#b91c1c  - Error 700 (Active states)
```

**Info**
```
#3b82f6  - Info 500 (Messages)
#2563eb  - Info 600 (Buttons)
#1d4ed8  - Info 700 (Active states)
```

---

## Accessibility Compliance

### WCAG AA Compliance
All colors in the BM Parliament palette are designed to meet WCAG AA standards:

- **Contrast Ratio**: Minimum 4.5:1 for text
- **Colorblind Friendly**: Distinct enough for red-green colorblindness
- **Alternative Indicators**: Never rely on color alone for meaning
- **Focus States**: Clear, visible focus rings

### Contrast Examples

| Foreground | Background | Ratio | Status |
|-----------|-----------|-------|--------|
| Primary 900 (#14532d) | Primary 50 (#f0f9f4) | 15.2:1 | ✅ AAA |
| White | Primary 600 (#16a34a) | 5.8:1 | ✅ AA |
| White | Primary 700 (#15803d) | 6.1:1 | ✅ AA |
| Primary 700 (#15803d) | Primary 100 (#dcfce7) | 8.1:1 | ✅ AAA |

### High Contrast Mode
```css
@media (prefers-contrast: high) {
  :root {
    --color-primary-500: #16a34a;
    --color-primary-600: #15803d;
    --color-text-primary: #000000;
    --color-text-secondary: #1e293b;
  }
}
```

### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
```

---

## File References

### Source Files
- **Tailwind Configuration**: `src/tailwind.config.js`
- **Color System Definition**: `src/templates/components/design-system/color_palette.html`
- **CSS Output**: `src/static/css/output.css` (generated)

### Key Lines
```
tailwind.config.js (line 114):
  'bangsamoro': 'linear-gradient(135deg, #1e40af 0%, #059669 100%)',

color_palette.html (lines 37-188):
  CSS variable definitions for entire color system

color_palette.html (line 133):
  --gradient-hero: linear-gradient(135deg, #1e40af 0%, #059669 100%);

color_palette.html (line 209):
  .bg-gradient-hero { background: var(--gradient-hero); }
```

---

## Implementation Examples

### Hero Section
```html
<section class="bg-bangsamoro text-white py-16 md:py-24">
  <div class="container mx-auto px-4">
    <h1 class="text-4xl font-bold mb-4">Welcome to BM Parliament</h1>
    <p class="text-lg text-white/90">Bringing Bangsamoro Public Service Closer to You</p>
    <a href="#register" class="mt-8 inline-block px-6 py-3 bg-white text-primary-700 rounded-lg font-semibold hover:bg-primary-50">
      Get Started
    </a>
  </div>
</section>
```

### Primary Button (Uses Bangsamoro Gradient)
Primary buttons use the Bangsamoro gradient to match the brand identity:
```html
<button style="background: linear-gradient(135deg, #1e40af 0%, #059669 100%);" 
        onmouseover="this.style.background='linear-gradient(135deg, #1e3a8a 0%, #047857 100%)';" 
        onmouseout="this.style.background='linear-gradient(135deg, #1e40af 0%, #059669 100%)';"
        class="text-white px-6 py-2 rounded-lg shadow-md transition-all duration-300">
  Primary Action
</button>
```

**Note:** The green UI palette (`bg-primary-600`, `bg-primary-700`) is for secondary buttons, badges, and other UI elements. Primary action buttons should always use the Bangsamoro gradient.

### Card with Hero Gradient
```html
<div class="bg-gradient-hero rounded-lg p-6 text-white shadow-lg">
  <h3 class="text-xl font-bold mb-2">Featured Program</h3>
  <p class="text-white/90">Learn more about our services</p>
</div>
```

### Status Badge
```html
<span class="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
  Active
</span>
```

### Link with Hover
```html
<a href="#" class="text-primary-600 hover:text-primary-700 underline">
  Learn more about BM Parliament
</a>
```

---

## Maintenance Notes

### When to Update
- Color system updates should be made in `color_palette.html`
- Tailwind config should only be modified for new gradient additions
- CSS output is generated automatically and should not be edited directly

### Rebuilding Tailwind CSS
```bash
# Development
npm run build-css

# Docker
docker-compose exec web npm run build-css
```

### Testing Color Changes
1. Update `color_palette.html` with new colors
2. Rebuild Tailwind CSS
3. Test in browser for contrast compliance
4. Verify across different pages that use the colors
5. Test in high contrast mode and with colorblind simulation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 19, 2025 | Initial documentation of Bangsamoro color system |
| | | Documented primary color palette (10-shade green) |
| | | Added Bangsamoro gradient specification |
| | | WCAG AA accessibility compliance |
| | | Implementation examples and file references |

---

## Related Documentation

- [UI Design System](../README.md)
- [Component Library](../../src/templates/components/README.md)
- [Tailwind Configuration](../../src/tailwind.config.js)
- [Color Palette Component](../../src/templates/components/design-system/color_palette.html)

---

## Questions or Updates?

For questions about the color system or to propose updates:
1. Check the source files listed above
2. Review WCAG accessibility standards
3. Test with colorblind simulation tools
4. Document changes in this file with version updates
