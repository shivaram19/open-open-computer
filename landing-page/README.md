# Sukha Landing Page

A multi-page, research-backed landing page for the open-open-computer project.

## Quick Start

```bash
# Preview locally (required — JS uses modern browser features)
python serve.py

# Or on a custom port
python serve.py 3000
```

Then open http://localhost:8000 in your browser.

## File Structure

```
landing-page/
├── css/
│   ├── design-system.css    # Variables, reset, typography, dark mode
│   ├── layout.css           # Grid, container, spacing utilities
│   ├── components.css       # Nav, cards, buttons, FAQ, footer
│   ├── motion.css           # Scroll reveals, entrance animations
│   ├── parallax.css         # Parallax depth layers
│   └── responsive.css       # Mobile-first breakpoints
├── js/
│   ├── core.js              # Utilities ($, $$, throttle, reduced motion)
│   ├── motion.js            # IntersectionObserver scroll reveals
│   ├── parallax.js          # Parallax scrolling
│   ├── navigation.js        # Mobile menu, focus trap, active page
│   └── faq.js               # Accessible accordion
├── index.html               # Homepage (relief, uses, trust, CTA)
├── features.html            # Detailed use cases (problem → solution)
├── philosophy.html          # SOLID principles, research methodology
├── faq.html                 # FAQ with Schema.org structured data
├── serve.py                 # Local development server
└── README.md                # This file
```

## Design Principles

1. **No AI slop** — Distinctive typography (Bricolage Grotesque + Inter), semantic colors, human copy
2. **SOLID architecture** — Each file has one responsibility
3. **Mobile-first** — Breakpoints at 640px, 768px, 1024px
4. **Accessibility** — Skip links, ARIA, focus-visible, reduced motion, high contrast
5. **SEO/GEO** — Schema.org JSON-LD, Open Graph, semantic HTML, FAQPage markup
6. **Performance** — CSS `contain`, IntersectionObserver, passive event listeners
7. **Dark mode** — `prefers-color-scheme` with full palette swap

## Deployment

Deployed automatically to **GitHub Pages** via `.github/workflows/deploy-landing-page.yml`.

Live URL: `https://shivaram19.github.io/open-open-computer/`

To regenerate the social preview image:

```bash
python3 generate_og_image.py
```

This writes `og-image.png` (1200×630) and updates Open Graph / Twitter Card tags in every HTML page.

To enable:
1. Push the workflow file to `main`.
2. Go to **Settings → Pages** in the GitHub repo.
3. Under **Build and deployment → Source**, select **GitHub Actions**.
4. The workflow runs on every push to `landing-page/**`.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Same as open-open-computer — open source.
