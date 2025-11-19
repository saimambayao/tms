# BM Parliament UI Documentation

Welcome to the BM Parliament UI Design System documentation. This folder contains comprehensive guides for designing and implementing user interfaces for the BM Parliament platform.

## 📚 Documentation Files

### 1. [Primary Colors](./primary-colors.md)
**Complete reference for the BM Parliament color system**

- 10-shade green primary palette
- Bangsamoro gradient specification (#1e40af → #059669)
- CSS variables and Tailwind configuration
- Color contrast and accessibility compliance
- Implementation examples for all color usage patterns

**Key Sections:**
- Color Philosophy
- Primary Color Palette (10 shades)
- Bangsamoro Gradient Definition
- Secondary Colors & Status Colors
- Accessibility Compliance (WCAG AA)
- File References & Implementation

**Best for:** Developers implementing colors, designers choosing color combinations, accessibility audits

### 2. [Design Guidelines](./design-guidelines.md)
**Comprehensive design principles and patterns for the BM Parliament UI**

- Design principles (User-Centered, Consistent, Clear, Accessible, Bangsamoro-focused)
- Component patterns (Buttons, Cards, Forms, Navigation)
- Typography guidelines
- Spacing and layout systems
- Accessibility requirements
- Best practices and testing checklist

**Key Sections:**
- Design Principles
- Color System Usage
- Typography Scale
- Component Patterns
- Spacing & Layout
- Accessibility Requirements
- Testing Checklist
- Quick Reference

**Best for:** Designers creating new components, developers implementing UI patterns, QA testing, design reviews

---

## 🎨 Quick Start

### For Designers
1. Read **Design Guidelines** for overall design principles
2. Check **Primary Colors** for exact color specifications
3. Use the color palette for design mockups
4. Test contrast with WCAG guidelines

### For Developers
1. Reference **Primary Colors** for CSS variables and classes
2. Use **Design Guidelines** quick reference for component patterns
3. Copy code examples from both documents
4. Run accessibility checks before deployment

### For Project Managers
1. Review Design Principles in **Design Guidelines**
2. Use Testing Checklist to ensure quality
3. Reference documentation in design reviews
4. Share with team members for consistency

---

## 🎯 Key Concepts

### The Bangsamoro Gradient
The defining visual element of BM Parliament is a gradient from professional blue to emerald green.

```
#1e40af (Professional Blue) → #059669 (Bangsamoro Emerald)
Direction: 135° (diagonal bottom-right)
```

**Used for:**
- Hero sections across all major pages
- Feature backgrounds
- Primary call-to-action areas
- Gradient cards and special sections

**Tailwind Class:**
```html
<section class="bg-bangsamoro">
  <!-- Hero content -->
</section>
```

### 10-Shade Color System
The primary green palette provides flexibility for different use cases:

```
Primary 50-200   → Light backgrounds, subtle elements
Primary 300-500  → Interactive elements, accents
Primary 600-700  → Primary actions, navigation
Primary 800-900  → Text, high-contrast elements
```

### Accessibility Standards
All colors meet WCAG AA minimum (4.5:1 contrast for text)
- ✅ Sufficient color contrast
- ✅ Never color alone for meaning
- ✅ Keyboard navigation support
- ✅ Focus indicators required

---

## 📂 File Structure

```
docs/ui/
├── README.md                    # This file (index & overview)
├── primary-colors.md            # Complete color system reference
└── design-guidelines.md         # Design principles & patterns
```

**Related Files in Source Code:**
```
src/
├── tailwind.config.js           # Tailwind configuration (line 114)
├── templates/
│   └── components/
│       └── design-system/
│           └── color_palette.html  # CSS variables & classes
└── static/css/
    └── output.css               # Generated Tailwind CSS
```

---

## 🔗 Navigation

### By Role

**🎨 Designers**
→ [Design Guidelines](./design-guidelines.md) - Start here
→ [Primary Colors](./primary-colors.md) - For exact colors

**👨‍💻 Developers**
→ [Primary Colors](./primary-colors.md) - CSS & Tailwind info
→ [Design Guidelines](./design-guidelines.md) - Component patterns

**🔍 QA/Testers**
→ [Design Guidelines](./design-guidelines.md) - Testing Checklist
→ [Primary Colors](./primary-colors.md) - Accessibility section

### By Task

**Add a new component**
→ [Design Guidelines](./design-guidelines.md#components) - Component patterns
→ [Primary Colors](./primary-colors.md#usage-guidelines) - Color usage

**Update colors**
→ [Primary Colors](./primary-colors.md) - Full reference
→ File: `src/templates/components/design-system/color_palette.html`

**Audit accessibility**
→ [Primary Colors](./primary-colors.md#accessibility-compliance) - WCAG compliance
→ [Design Guidelines](./design-guidelines.md#accessibility) - Accessibility checklist

**Create hero section**
→ [Primary Colors](./primary-colors.md#bangsamoro-gradient) - Gradient specification
→ [Design Guidelines](./design-guidelines.md#hero-section) - Implementation example

---

## 📋 Color Quick Reference

### Primary Button
```html
<button class="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500">
  Action
</button>
```

### Hero Section
```html
<section class="bg-bangsamoro text-white py-20">
  <h1>Welcome</h1>
</section>
```

### Success Alert
```html
<div class="bg-success-50 text-success-700 border border-success-200 p-4 rounded">
  ✓ Success message
</div>
```

### Form Input
```html
<input class="px-4 py-2 border border-secondary-300 rounded focus:ring-2 focus:ring-primary-500" />
```

**See [Design Guidelines Quick Reference](./design-guidelines.md#quick-reference) for more patterns**

---

## 🛠️ Common Tasks

### Task: Change Hero Section Color
**File:** `src/templates/components/design-system/color_palette.html` (line 133)

Current:
```css
--gradient-hero: linear-gradient(135deg, #1e40af 0%, #059669 100%);
```

Update and rebuild:
```bash
npm run build-css  # or docker-compose exec web npm run build-css
```

### Task: Add New Primary Color Shade
**File:** `src/templates/components/design-system/color_palette.html`

1. Add CSS variable in `:root` section
2. Add corresponding Tailwind class `.bg-primary-XXX`
3. Rebuild Tailwind CSS

### Task: Check Accessibility Compliance
1. Review **Primary Colors** [Accessibility Compliance](./primary-colors.md#accessibility-compliance)
2. Check contrast ratios for your specific color combination
3. Test with colorblind simulator
4. Run through [Testing Checklist](./design-guidelines.md#testing-checklist)

### Task: Implement New Component
1. Review component patterns in [Design Guidelines](./design-guidelines.md#components)
2. Check [Primary Colors Usage Guidelines](./primary-colors.md#usage-guidelines)
3. Implement with appropriate colors
4. Test accessibility with focus indicators and contrast
5. Verify keyboard navigation

---

## 📊 Color Statistics

### Palette Size
- **Primary Shades:** 10 (50, 100, 200, 300, 400, 500, 600, 700, 800, 900)
- **Secondary Colors:** 10 shades (neutral blue-gray)
- **Status Colors:** 4 (Success, Warning, Error, Info)
- **Gradients:** 5+ (Primary, Hero, Success, Warning, Error)

### Accessibility Metrics
- **WCAG AA Compliance:** 100% ✅
- **Colorblind Safe:** Yes ✅
- **Contrast Ratios:** 4.5:1 to 15.2:1
- **Focus Indicators:** Required on all interactive elements

### Browsers/Platforms Tested
- Chrome/Chromium
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Android)

---

## 📞 Support & Questions

### For Color System Questions
→ See [Primary Colors Documentation](./primary-colors.md)

### For Design Pattern Questions
→ See [Design Guidelines](./design-guidelines.md)

### For Implementation Help
1. Check relevant documentation section
2. Review implementation examples
3. Check source files for actual usage
4. Review Git history for similar implementations

### To Report Issues
1. Document the issue with screenshots
2. Note which documentation section it relates to
3. Provide browser/platform information
4. Include accessibility testing results if relevant

---

## 📈 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0 | Nov 19, 2025 | Initial documentation release |
| | | Primary color system (10-shade green) |
| | | Bangsamoro gradient specification |
| | | Design guidelines and patterns |
| | | Accessibility guidelines and compliance |
| | | Component patterns and best practices |

---

## 🔄 Maintenance

### Regular Tasks
- **Monthly:** Review color usage for consistency
- **Quarterly:** Test accessibility compliance
- **Quarterly:** Update documentation with new patterns
- **Annually:** Audit design system against latest standards

### When to Update Documentation
- Add new component patterns
- Change color specifications
- Update accessibility guidelines
- Add new gradient definitions
- Implement design system changes

### Update Process
1. Edit relevant markdown file
2. Update version history
3. Test changes don't break links
4. Commit with clear message
5. Share update with team

---

## 📚 External Resources

### Accessibility
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Accessible Colors Tool](https://accessible-colors.com/)
- [Color Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)

### Design Systems
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Material Design System](https://material.io/design)
- [GOV.UK Design System](https://design-system.service.gov.uk/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

### Typography & Web Design
- [Typography on the Web](https://www.smashingmagazine.com/topics/typography/)
- [Responsive Design Patterns](https://www.smashingmagazine.com/topics/responsive-web-design/)
- [Web Accessibility](https://www.w3.org/WAI/)

---

**Last Updated:** November 19, 2025

**Maintained By:** BM Parliament Development Team

**Status:** Active & Current
