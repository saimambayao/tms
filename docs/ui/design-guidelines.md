# BM Parliament UI Design Guidelines

## Table of Contents
1. [Design Principles](#design-principles)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Components](#components)
5. [Spacing & Layout](#spacing--layout)
6. [Accessibility](#accessibility)
7. [Best Practices](#best-practices)

---

## Design Principles

### 1. User-Centered Design
- Prioritize user needs and accessibility
- Design for all abilities and backgrounds
- Test with real users regularly
- Iterate based on feedback

### 2. Consistency
- Use the established color system consistently
- Follow component patterns throughout
- Maintain visual hierarchy
- Use standardized spacing and sizing

### 3. Clarity
- Clear navigation and information architecture
- Descriptive labels and error messages
- Visual feedback for all interactions
- Logical content organization

### 4. Accessibility First
- WCAG AA compliance minimum
- Sufficient color contrast (4.5:1 for text)
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators for all interactive elements

### 5. Bangsamoro Identity
- Reflect cultural values in design choices
- Use colors that represent Bangsamoro heritage
- Inclusive language and imagery
- Community-focused interactions

---

## Color System

### Primary Colors: Bangsamoro Gradient

The defining visual element of BM Parliament is the Bangsamoro gradient.

**Gradient Specification:**
- Direction: 135° (diagonal bottom-right)
- Start: #1e40af (Professional Blue)
- End: #059669 (Bangsamoro Emerald)

**Usage:** Hero sections, feature backgrounds, primary CTAs

### Green Palette (Primary)

**10-Shade System for flexibility:**
- 50-200: Light backgrounds and subtle elements
- 300-500: Interactive elements and accents
- 600-700: Primary buttons and navigation
- 800-900: Text and high-contrast elements

**Application:**
```
Buttons:        Primary 600 (default) → Primary 700 (hover)
Links:          Primary 600 text, Primary 200 hover background
Badges:         Primary 100 background, Primary 800 text
Cards:          Primary 50 background
Active States:  Primary 700 or Primary 400
Disabled:       Primary 100 background, Primary 300 text
```

### Status Colors

Use semantic colors for user feedback:

**Success (Green)**: Positive outcomes
```html
<div class="bg-success-50 text-success-700 border border-success-200">
  ✓ Action completed successfully
</div>
```

**Warning (Orange)**: Caution required
```html
<div class="bg-warning-50 text-warning-700 border border-warning-200">
  ⚠ Please verify before proceeding
</div>
```

**Error (Red)**: Critical issues
```html
<div class="bg-error-50 text-error-700 border border-error-200">
  ✗ Error: Please correct and try again
</div>
```

**Info (Blue)**: Informational messages
```html
<div class="bg-info-50 text-info-700 border border-info-200">
  ℹ Information for your reference
</div>
```

### Secondary Colors

**Blue-Gray**: Professional, neutral backgrounds
- Use for secondary content areas
- Borders and dividers
- Muted text and inactive elements

**When to use:** Backgrounds, secondary navigation, borders, disabled states

---

## Typography

### Font Family
- **Default**: Inter (sans-serif) for modern, clean appearance
- **Fallback**: system-ui, -apple-system, sans-serif
- **Serif**: Merriweather for special content (optional)

### Font Scale

**Headings** (using Tailwind sizing):
```
h1: text-3xl md:text-4xl lg:text-5xl font-bold
h2: text-2xl md:text-3xl lg:text-4xl font-bold
h3: text-xl md:text-2xl lg:text-3xl font-semibold
h4: text-lg md:text-xl font-semibold
h5: text-base md:text-lg font-semibold
h6: text-sm md:text-base font-semibold
```

**Body Text**:
```
Base:     text-base (1rem)
Small:    text-sm (0.875rem)
Tiny:     text-xs (0.75rem)
Large:    text-lg (1.125rem)
```

### Text Colors

**Primary Text**:
```css
color: var(--color-secondary-900);  /* #0f172a */
```

**Secondary Text**:
```css
color: var(--color-secondary-700);  /* #334155 */
```

**Muted Text**:
```css
color: var(--color-secondary-500);  /* #64748b */
```

**Inverse (on primary background)**:
```css
color: #ffffff;
```

---

## Components

### Buttons

**Primary Button (Uses Bangsamoro Gradient)**
Primary buttons use the Bangsamoro gradient to match the brand identity:
```html
<button style="background: linear-gradient(135deg, #1e40af 0%, #059669 100%);" 
        onmouseover="this.style.background='linear-gradient(135deg, #1e3a8a 0%, #047857 100%)';" 
        onmouseout="this.style.background='linear-gradient(135deg, #1e40af 0%, #059669 100%)';"
        class="text-white px-6 py-3 rounded-lg shadow-md transition-all duration-300">
  Action
</button>
```

**Alternative: Using Button Component**
```html
{% include 'components/atoms/button.html' with variant='primary' text='Action' %}
```

**Secondary Button**
```html
<button class="bg-secondary-200 text-secondary-900 px-6 py-3 rounded-lg hover:bg-secondary-300 focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2 transition-all duration-200">
  Secondary
</button>
```

**Outline Button**
```html
<button class="border-2 border-primary-600 text-primary-600 px-6 py-3 rounded-lg hover:bg-primary-50 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200">
  Outline
</button>
```

**Disabled State**
```html
<button disabled class="bg-primary-100 text-primary-300 px-6 py-3 rounded-lg cursor-not-allowed">
  Disabled
</button>
```

### Cards

**Default Card**
```html
<div class="bg-white rounded-lg shadow-md p-6 border border-secondary-200">
  <h3 class="text-lg font-semibold text-secondary-900 mb-2">Card Title</h3>
  <p class="text-secondary-700">Card content goes here.</p>
</div>
```

**Hero Card**
```html
<div class="bg-gradient-hero rounded-lg p-8 text-white shadow-lg">
  <h3 class="text-xl font-bold mb-2">Featured Item</h3>
  <p class="text-white/90">Description of featured content</p>
</div>
```

**Elevated Card**
```html
<div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
  <h3 class="font-semibold text-secondary-900">Card Title</h3>
</div>
```

### Forms

**Input Field**
```html
<input
  type="text"
  class="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
  placeholder="Enter text..."
>
```

**Label + Input**
```html
<div class="mb-4">
  <label class="block text-secondary-700 font-medium mb-2">
    Field Label
  </label>
  <input
    type="text"
    class="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500"
  >
</div>
```

**Error State**
```html
<div class="mb-4">
  <label class="block text-secondary-700 font-medium mb-2">Email</label>
  <input
    type="email"
    class="w-full px-4 py-2 border-2 border-error-500 rounded-lg focus:ring-2 focus:ring-error-500"
    value="invalid-email"
  >
  <p class="text-error-600 text-sm mt-1">Please enter a valid email</p>
</div>
```

### Navigation

**Navbar Link - Active**
```html
<a href="/about" class="text-primary-700 font-semibold border-b-2 border-primary-700">
  About
</a>
```

**Navbar Link - Inactive**
```html
<a href="/about" class="text-secondary-600 hover:text-primary-600 transition-colors">
  About
</a>
```

---

## Spacing & Layout

### Spacing Scale
```
xs: 0.25rem (4px)
sm: 0.5rem (8px)
md: 1rem (16px)
lg: 1.5rem (24px)
xl: 2rem (32px)
2xl: 3rem (48px)
3xl: 4rem (64px)
4xl: 6rem (96px)
```

### Layout Patterns

**Container**
```html
<div class="container mx-auto px-4 max-w-7xl">
  <!-- Content with consistent max width and padding -->
</div>
```

**Grid Layout**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

**Section Spacing**
```html
<section class="py-12 md:py-20 lg:py-24">
  <div class="container mx-auto">
    <!-- Content -->
  </div>
</section>
```

---

## Accessibility

### Color Contrast
All text must have sufficient contrast:
- **Body text**: Minimum 4.5:1 contrast ratio
- **Large text (18pt+)**: Minimum 3:1 contrast ratio
- **UI components**: Minimum 3:1 contrast ratio

**Approved Combinations:**
- Primary 900 on Primary 50: 15.2:1 ✅ AAA
- White on Primary 600: 5.8:1 ✅ AA
- Primary 700 on Primary 100: 8.1:1 ✅ AAA

### Focus Management

**Focus Indicators** (always visible):
```css
focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

**Skip to Content Link:**
```html
<a href="#main-content" class="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Tab order should follow visual flow
- Focus should be visible and obvious
- Avoid keyboard traps

### Screen Readers

**Semantic HTML:**
```html
<!-- Use semantic elements -->
<button>Click Me</button>
<nav>Navigation</nav>
<main id="main-content">Main Content</main>
<article>Article</article>

<!-- Avoid -->
<div onclick="...">Click Me</div>
<div role="navigation">Navigation</div>
```

**ARIA Labels (when needed):**
```html
<button aria-label="Close menu">×</button>
<div aria-live="polite" aria-atomic="true">
  <!-- Live region updates -->
</div>
```

---

## Best Practices

### 1. Color Usage
- ✅ Use color with purpose and meaning
- ✅ Always provide text with sufficient contrast
- ✅ Use status colors consistently (green=success, red=error)
- ✅ Test with colorblind simulators
- ❌ Don't rely on color alone to convey information
- ❌ Don't use more than 3 primary colors in one section

### 2. Typography
- ✅ Use hierarchy: h1 → h2 → h3 → body
- ✅ Keep line length 50-75 characters for readability
- ✅ Use proper font sizes for different screen sizes
- ✅ Maintain consistent font weight usage
- ❌ Don't use too many different font sizes
- ❌ Don't mix serif and sans-serif for body text

### 3. Spacing
- ✅ Use consistent spacing throughout (use scale)
- ✅ Add breathing room around elements
- ✅ Align elements to a grid system
- ✅ Use whitespace to organize content
- ❌ Don't overcrowd content
- ❌ Don't use arbitrary spacing values

### 4. Responsive Design
- ✅ Design mobile-first
- ✅ Test at multiple breakpoints
- ✅ Use Tailwind breakpoints (sm, md, lg, xl, 2xl)
- ✅ Make touch targets at least 44×44 pixels
- ❌ Don't hide important content on mobile
- ❌ Don't assume fixed widths

### 5. Performance
- ✅ Optimize images for web
- ✅ Use lazy loading for below-the-fold content
- ✅ Minimize CSS and JavaScript
- ✅ Use system fonts when possible
- ❌ Don't use heavy animations on mobile
- ❌ Don't load unoptimized images

---

## Testing Checklist

### Visual Design
- [ ] Colors match primary color palette
- [ ] Text has sufficient contrast (4.5:1 minimum)
- [ ] Spacing follows the scale
- [ ] Typography is consistent
- [ ] Bangsamoro gradient used appropriately

### Functionality
- [ ] All buttons are clickable
- [ ] Form validation works correctly
- [ ] Links navigate properly
- [ ] Responsive at all breakpoints
- [ ] Mobile layout is usable

### Accessibility
- [ ] All images have alt text
- [ ] Focus indicators are visible
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color not sole indicator of meaning
- [ ] Form labels are associated correctly

### Performance
- [ ] Page loads in <3 seconds
- [ ] No layout shifts on load
- [ ] Images are optimized
- [ ] CSS is minified
- [ ] Animations perform smoothly

---

## Quick Reference

### Color Classes
```html
<!-- Backgrounds -->
<div class="bg-primary-600">Primary button background</div>
<div class="bg-gradient-hero">Hero section gradient</div>
<div class="bg-bangsamoro">Bangsamoro gradient</div>

<!-- Text -->
<p class="text-secondary-900">Primary text</p>
<p class="text-secondary-700">Secondary text</p>
<p class="text-primary-600">Accent text</p>

<!-- Borders -->
<div class="border border-secondary-200">Light border</div>
<div class="border-2 border-primary-600">Accent border</div>
```

### Common Patterns
```html
<!-- Card -->
<div class="bg-white rounded-lg shadow-md p-6 border border-secondary-200">
  Content
</div>

<!-- Button -->
<button class="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500">
  Click
</button>

<!-- Form Group -->
<div class="mb-4">
  <label class="block text-secondary-700 font-medium mb-2">Label</label>
  <input class="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500">
</div>

<!-- Alert -->
<div class="bg-success-50 border border-success-200 rounded-lg p-4 text-success-700">
  Success message
</div>
```

---

## Resources

- [Primary Colors Documentation](./primary-colors.md)
- [Tailwind CSS](https://tailwindcss.com/)
- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Accessible Colors](https://accessible-colors.com/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | November 19, 2025 | Initial design guidelines document |

---

Last Updated: November 19, 2025
