# Anthropic Design Language — Dashboard Brief

Researched: March 2026
Sources: anthropic.com CSS bundles, claude.com, platform.claude.com, support.claude.com

---

## Summary: The Design Philosophy

Anthropic's visual language is **warm minimalism with intellectual weight**. It is not clinical (no cool blue-grays), not playful (no gradients or illustrations as decoration), and not dense-technical (no cramped data tables). It reads as: trusted, calm, considered. The word "thoughtful" appears in their own copy constantly — their design reflects it.

The palette is built on **warm neutrals** (slate with yellow undertones, ivory backgrounds) anchored by a single terracotta/rust accent. Dark surfaces are almost-black with brown warmth, not blue-black. Light surfaces are cream, not white.

---

## Color System

### Primary Palette: The Slate Scale

Anthropic uses a custom warm-gray ("slate") scale with 21 stops. These are the foundation of every surface, text, border, and icon.

| Token | Hex | Use |
|-------|-----|-----|
| `--color-slate-1000` | `#0f0f0e` | Deepest black (rarely used) |
| `--color-slate-950` | `#141413` | Page background (dark mode), `<meta name="theme-color">` |
| `--color-slate-900` | `#1a1918` | Dark cards, elevated surfaces (dark) |
| `--color-slate-850` | `#1f1e1d` | Sidebar backgrounds (dark) |
| `--color-slate-800` | `#262624` | Secondary surfaces (dark) |
| `--color-slate-750` | `#30302e` | Borders, dividers (dark) |
| `--color-slate-700` | `#3d3d3a` | Muted icons, inactive states (dark) |
| `--color-slate-650` | `#4d4c48` | Placeholder text (dark) |
| `--color-slate-600` | `#5e5d59` | Secondary text (dark), borders (light) |
| `--color-slate-550` | `#73726c` | Tertiary text |
| `--color-slate-500` | `#87867f` | Disabled states, subtle text |
| `--color-slate-450` | `#9c9a92` | Muted labels |
| `--color-slate-400` | `#b0aea5` | Light mode: inactive/subtle |
| `--color-slate-350` | `#c2c0b6` | Light borders |
| `--color-slate-300` | `#d1cfc5` | Dividers, subtle borders (light) |
| `--color-slate-250` | `#dedcd1` | Light backgrounds, hover states |
| `--color-slate-200` | `#e8e6dc` | Card backgrounds (light) |
| `--color-slate-150` | `#f0eee6` | Page sections (light) |
| `--color-slate-100` | `#f5f4ed` | Secondary page bg (light) |
| `--color-slate-050` | `#faf9f5` | Primary page bg (light mode) |
| `--color-slate-000` | `#ffffff` | Pure white (rare, high contrast) |

### Semantic Aliases (What to Actually Use)

| Token | Hex | Meaning |
|-------|-----|---------|
| `--color-slate-dark` | `#141413` | Dark bg / dark text foundation |
| `--color-slate-medium` | `#3d3d3a` | Mid-dark, borders, icons |
| `--color-slate-light` | `#5e5d59` | Secondary text |
| `--color-cloud-dark` | `#87867f` | Muted/disabled |
| `--color-cloud-medium` | `#b0aea5` | Very subtle |
| `--color-cloud-light` | `#d1cfc5` | Dividers |
| `--color-ivory-dark` | `#e8e6dc` | Card backgrounds (light) |
| `--color-ivory-medium` | `#f0eee6` | Section fills |
| `--color-ivory-light` | `#faf9f5` | Page background (light) |

### Accent Color: Clay (The Brand Color)

`--color-clay: #d97757`

This is THE Anthropic brand color — a warm terracotta/rust. It appears on:
- Active navigation states
- CTA buttons (primary)
- Highlighted / selected elements
- Brand marks
- Icon accents in marketing

**Related tones from selection highlight:** `rgba(204, 120, 92, 0.5)` — a desaturated version of clay used for text selection backgrounds.

The heroes accent (marketing pages) is `#C46849` (slightly deeper clay).

### Extended Accent Palette

These are named accent colors used for categorical illustration backgrounds and tags:

| Token | Hex | Feel |
|-------|-----|------|
| `--color-clay` | `#d97757` | Terracotta (primary brand) |
| `--color-oat` | `#e3dacc` | Warm beige |
| `--color-olive` | `#788c5d` | Muted green |
| `--color-cactus` | `#bcd1ca` | Sage green |
| `--color-sky` | `#6a9bcc` | Slate blue |
| `--color-heather` | `#cbcadb` | Lavender-gray |
| `--color-fig` | `#c46686` | Dusty rose |
| `--color-coral` | `#ebcece` | Blush pink |

### Functional Colors

| Purpose | Hex |
|---------|-----|
| Focus ring | `#2c84db` |
| Error | `#bf4d43` |
| Error (lighter) | `#dc2626` |
| Success | `#10b981` |
| Dark tint overlay | `rgba(25, 25, 25, 0.1–0.2)` |
| Modal backdrop | 80% opacity slate-dark |

---

## Typography System

### Font Families

Anthropic has a custom-built type system. All fonts are proprietary WOFF2 files.

| CSS Variable | Font Family | Role |
|---|---|---|
| `--anthropic-sans` | AnthropicSans | Primary UI sans-serif |
| `--anthropic-serif` | AnthropicSerif | Editorial/marketing serif |
| `--anthropic-mono` | AnthropicMono | Code, terminal |
| `--copernicus` | Copernicus | Display serif (large headings) |
| `--styrene-a` | StyreneA | Geometric sans (secondary) |
| `--styrene-b` | StyreneB | Geometric sans (secondary, tighter) |
| `--tiempos-text` | TiemposText | Long-form reading (support, editorial) |
| `--jetbrains-mono` | JetBrainsMono | Developer code blocks |

**For a dashboard replica:** Use **Inter** as the closest publicly available match for AnthropicSans. Use **JetBrains Mono** directly (it's open-source and they use it). For editorial headings, **Libre Baskerville** approximates Copernicus.

The support site (support.claude.com) uses **Tiempos Text** as primary — a transitional serif that gives it a editorial-magazine feel distinct from the product UI.

### Type Scale

Uses `clamp()` for fluid responsive scaling:

| Level | Min | Max | Use |
|-------|-----|-----|-----|
| Display XXL | 3rem (48px) | 5rem (80px) | Hero headlines |
| Display XL | 2.5rem (40px) | 4rem (64px) | Section headlines |
| Display L | 2rem (32px) | 3rem (48px) | Sub-sections |
| Display M | ~1.75rem (28px) | ~2.25rem (36px) | Card titles |
| Paragraph L | ~1.25rem (20px) | ~1.5rem (24px) | Lead paragraphs |
| Paragraph M | 1.125rem (18px) | 1.25rem (20px) | Body text |
| Paragraph S | ~1rem (16px) | — | UI labels, captions |
| Detail | ~0.875rem (14px) | ~1rem (16px) | Metadata, timestamps |
| Mono | 0.875rem (14px) | 2rem (32px) | Code (fluid in terminal) |

### Typography Rules

- **Font smoothing:** `-webkit-font-smoothing: antialiased` everywhere
- **Line height:** 1.2–1.25 for headings, 1.5–1.6 for body
- **Letter spacing:** Tight to normal (no wide-tracked all-caps)
- **Text rendering:** All fonts use `font-display: swap` with carefully tuned fallback metrics

---

## Spacing System

An 8px base grid with a named token scale:

| Token | Value |
|-------|-------|
| `--sp-4` / `--gap-xs` | 4px |
| `--sp-8` / `--gap-sm` | 8px |
| `--sp-12` | 12px |
| `--sp-16` / `--gap-md` | 16px |
| `--sp-24` / `--gap-lg` | 24px |
| `--sp-32` / `--gap-xl` | 32px |
| `--sp-48` / `--gap-2xl` | 48px |
| `--sp-64` | 64px |

**Site margins:** `clamp(2rem, 3.9vw + 1rem, 5rem)` — extremely generous, never cramped
**Max content column:** 640px for text, 950px for media
**Container max width:** 1400px

---

## Border, Radius, and Shadow

### Border Radius

| Level | Value | Use |
|-------|-------|-----|
| xs | 4px | Tags, badges, inline elements |
| sm | 6px | Buttons, small inputs |
| md | 8px | Cards, modals, inputs |
| lg | 12px–14px | Large cards, panels |
| pill | 9999px | Rounded pill buttons |
| circle | 50% | Avatars |

### Borders

- `--border-subtle`: very light, almost invisible separation
- `--border-faint`: structural borders, card outlines
- `--border-strong`: emphasized borders, focused states
- Typical border: `1px solid` at slate-200/slate-700 for light/dark

### Shadows

Anthropic uses **minimal shadows**. The design separates elements primarily through color and spacing, not depth effects.

- Cards: `0 1px 2px 0 rgba(0,0,0,0.05)` (nearly invisible)
- Ambient card shadow: `var(--card-shadow-ambient-color)` (very subtle)
- NO multiple-layer box shadows, NO dramatic depth
- Modals: backdrop blur + dark overlay rather than hard shadows

---

## Component Patterns

### Buttons

**Primary Button:**
- Background: `--color-clay` (`#d97757`)
- Text: white
- Border-radius: 6px
- Padding: ~12px 20px
- No border
- Hover: slightly darker clay (~10%)
- Transition: 200ms ease

**Secondary Button:**
- Background: transparent
- Border: `1px solid --color-slate-300` (light) / `--color-slate-700` (dark)
- Text: primary text color
- Hover: `--color-slate-100` fill (light) / `--color-slate-850` fill (dark)

**Ghost/Tertiary:**
- No background, no border
- Text: secondary text color
- Hover: subtle fill

### Input Fields

- Border: 1px solid `#d1cfc5` (light) / `#3d3d3a` (dark)
- Border-radius: 6–8px
- Background: white (light) / `#1a1918` (dark)
- Focus: border color `#2c84db`, no glow/shadow
- Placeholder: slate-500 (`#87867f`)
- Padding: 10–12px 14–16px

### Cards

- Background: `#f0eee6` (ivory-medium) on light, `#1a1918` (slate-900) on dark
- Border: 1px solid `#e8e6dc` (light) / `#262624` (dark)
- Border-radius: 8–12px
- Padding: sm (16px), md (24px), lg (32px)
- Shadow: `0 1px 2px rgba(0,0,0,0.05)` only
- Hover (linked cards): image scales to 1.05 over 0.2s

### Navigation

- Height: 68px (desktop), 70px (mobile)
- Background: same as page background (not a visually distinct bar)
- No drop shadow on nav — very flat
- Active state: clay accent
- Transition: 400ms cubic-bezier(0.77, 0, 0.175, 1)

### Badges / Tags

- Border-radius: 4px (sharp) or 9999px (pill)
- Background: named accent color at low opacity, or ivory tones
- Text: small, 12–13px, medium weight
- No shadows

### Code Blocks / Terminal

- Background: dark slate (`#141413` or `#1a1918`)
- Text: ivory-light (`#faf9f5`) at 0.9 opacity
- Font: AnthropicMono / JetBrainsMono
- Border: 1px solid `#30302e`
- Border-radius: 8px
- Scrollbar: 6px wide, thumb at 30% white opacity
- Padding: 16–24px

### Tooltips

- Max-width: 17rem (272px)
- Background: dark slate
- Text: light
- Border-radius: `--radius-large` (~8px)
- Scale animation: 0.98 → 1.0 on appear
- No arrow/caret

---

## Motion & Animation

Anthropic uses deliberate, purposeful animation — not decorative.

| Element | Duration | Easing |
|---------|----------|--------|
| Dropdown open/close | 200ms | cubic-bezier(0.77, 0, 0.175, 1) |
| Menu open | 400ms | ease |
| Word/text entrance | 800ms | cubic-bezier(0.16, 1, 0.3, 1) |
| Modal fade | 400ms | ease-out |
| Image hover scale | 200ms | ease |
| Marquee scroll | 48s | linear infinite |
| Icon color | 300ms | ease |

**Easing tokens:**
- `--ease-in-quart`, `--ease-out-quart`
- `--ease-in-out-quart`, `--ease-in-out-expo`

**Accessibility:** All animations are completely disabled under `prefers-reduced-motion`.

---

## Light vs Dark Mode

### Light Mode (Marketing / Default)

- Page background: `#faf9f5` (ivory-light) — NOT white
- Secondary sections: `#f0eee6` or `#f5f4ed`
- Card fill: `#e8e6dc`
- Primary text: `#141413`
- Secondary text: `#5e5d59`
- Borders: `#d1cfc5`

### Dark Mode (Product / Developer)

- Page background: `#141413` (slate-950)
- Elevated surfaces: `#1a1918` (slate-900)
- Cards: `#1f1e1d` (slate-850)
- Primary text: `#faf9f5` (ivory-light)
- Secondary text: `#87867f` (cloud-dark)
- Borders: `#30302e` (slate-750)

**Key insight:** Anthropic's dark mode is warm-dark, not cool-dark. The blacks have brown undertones (`#141413` not `#111111`). This is intentional and distinctive.

**Mode behavior:** `data-mode="auto"` — follows system preference. Both modes are first-class.

---

## Platform-by-Platform Notes

### anthropic.com (Marketing)
- Primarily light mode (`#faf9f5` bg)
- Heavy use of Copernicus for large display headings
- Very generous whitespace — content is never crammed
- Lottie animations for product demos
- 12-column CSS grid
- Container max: 1400px
- Visual tone: **premium editorial**

### platform.claude.com (Developer Console)
- Primarily light with dark mode support
- `data-theme="claude"` custom theme layer
- Tailwind utility classes + CSS custom properties
- Moderate density — API console with data tables
- Font: AnthropicSans (Inter equivalent)
- Visual tone: **clean technical, professional**

### support.claude.com (Help Center)
- Light mode dominant
- Primary font: Tiempos Text (the editorial serif)
- Background: `rgb(240, 240, 235)` header (warm off-white)
- Collection cards: `rgb(204, 120, 92)` rust/terracotta accent
- Body text: `#1a1a1a`
- Border-radius: 14px on cards (more rounded than product UI)
- Visual tone: **approachable, editorial**

### claude.ai (Chat Interface)
- Supports both light and dark
- Gray-based swatch system for chat bubbles
- Accent: `#C46849` (slightly deeper clay)
- Very minimal chrome — content is the interface
- Visual tone: **conversational minimalism**

---

## Visual Tone: How It Should FEEL

A dashboard built in Anthropic's design language should feel:

1. **Warm, not clinical.** Backgrounds are cream, not white. Darks are brown-black, not blue-black.
2. **Spacious.** Padding errs generous. Content breathes.
3. **Flat with intention.** No gradients, no dramatic shadows. Separation comes from color, not depth.
4. **Typographically confident.** Large, clear headings. Good hierarchy. Type does the work.
5. **Accent-restrained.** Clay (`#d97757`) appears sparingly — for the ONE thing that matters on screen.
6. **Technically precise.** No decorative illustration. No stock photography. Data is data.

It should NOT feel:
- Bright or energetic (no saturated blues, no neons)
- Corporate cold (no grays with blue undertones)
- Dense or overwhelming (no tight line-height, no cramped padding)
- Trendy (no glassmorphism, no heavy gradients)

---

## Recommended Dashboard CSS Variables

Paste this into a `:root` block as your design token foundation:

```css
:root {
  /* === ANTHROPIC COLOR SYSTEM === */

  /* Slate scale (warm gray) */
  --slate-1000: #0f0f0e;
  --slate-950: #141413;
  --slate-900: #1a1918;
  --slate-850: #1f1e1d;
  --slate-800: #262624;
  --slate-750: #30302e;
  --slate-700: #3d3d3a;
  --slate-600: #5e5d59;
  --slate-500: #87867f;
  --slate-400: #b0aea5;
  --slate-300: #d1cfc5;
  --slate-250: #dedcd1;
  --slate-200: #e8e6dc;
  --slate-150: #f0eee6;
  --slate-100: #f5f4ed;
  --slate-050: #faf9f5;
  --slate-000: #ffffff;

  /* Brand accent */
  --clay: #d97757;
  --clay-dark: #c46849;
  --clay-muted: rgba(204, 120, 92, 0.15);

  /* Extended palette */
  --oat: #e3dacc;
  --olive: #788c5d;
  --cactus: #bcd1ca;
  --sky: #6a9bcc;
  --heather: #cbcadb;
  --fig: #c46686;
  --coral: #ebcece;

  /* Functional */
  --focus: #2c84db;
  --error: #bf4d43;
  --success: #10b981;

  /* === LIGHT MODE SEMANTIC TOKENS === */
  --bg-page: var(--slate-050);        /* #faf9f5 */
  --bg-section: var(--slate-150);     /* #f0eee6 */
  --bg-card: var(--slate-200);        /* #e8e6dc */
  --bg-input: var(--slate-000);       /* #ffffff */
  --bg-elevated: var(--slate-000);    /* #ffffff */

  --text-primary: var(--slate-950);   /* #141413 */
  --text-secondary: var(--slate-600); /* #5e5d59 */
  --text-muted: var(--slate-500);     /* #87867f */
  --text-disabled: var(--slate-400);  /* #b0aea5 */
  --text-on-accent: #ffffff;

  --border-subtle: var(--slate-250);  /* #dedcd1 */
  --border-default: var(--slate-300); /* #d1cfc5 */
  --border-strong: var(--slate-400);  /* #b0aea5 */

  --accent: var(--clay);              /* #d97757 */
  --accent-text: var(--clay-dark);    /* #c46849 */

  /* === SPACING === */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 12px;
  --sp-4: 16px;
  --sp-6: 24px;
  --sp-8: 32px;
  --sp-12: 48px;
  --sp-16: 64px;

  /* === RADIUS === */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-pill: 9999px;

  /* === TYPOGRAPHY === */
  --font-sans: "Inter", system-ui, sans-serif;    /* AnthropicSans substitute */
  --font-mono: "JetBrains Mono", monospace;        /* Exact match — they use it */
  --font-serif: "Libre Baskerville", Georgia, serif; /* Copernicus substitute */

  /* === SHADOW === */
  --shadow-card: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-elevated: 0 4px 12px rgba(0, 0, 0, 0.08);

  /* === MOTION === */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --duration-fast: 200ms;
  --duration-base: 300ms;
  --duration-slow: 400ms;
}

/* === DARK MODE === */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page: var(--slate-950);      /* #141413 */
    --bg-section: var(--slate-900);   /* #1a1918 */
    --bg-card: var(--slate-850);      /* #1f1e1d */
    --bg-input: var(--slate-900);     /* #1a1918 */
    --bg-elevated: var(--slate-800);  /* #262624 */

    --text-primary: var(--slate-050);  /* #faf9f5 */
    --text-secondary: var(--slate-500); /* #87867f */
    --text-muted: var(--slate-600);    /* #5e5d59 */
    --text-disabled: var(--slate-700); /* #3d3d3a */

    --border-subtle: var(--slate-800);  /* #262624 */
    --border-default: var(--slate-750); /* #30302e */
    --border-strong: var(--slate-700);  /* #3d3d3a */
  }
}
```

---

## What NOT to Do

- Do not use `#ffffff` pure white as a page background — use `#faf9f5`
- Do not use cool blue-gray for darks — use the warm slate scale
- Do not add heavy drop shadows — keep them at 1–2px, near invisible
- Do not use gradients as backgrounds — flat surfaces only
- Do not use saturated status colors (no electric green, no bright red) — muted tones
- Do not use clay for more than one primary action per view
- Do not use tight line-height or small padding — spaciousness is non-negotiable
- Do not add decorative elements (illustrations, patterns) to data surfaces

---

## Quick Reference: The Five Core Hex Values

If you can only remember five colors, these are the ones that make something look like Anthropic:

1. `#faf9f5` — page background (cream, not white)
2. `#141413` — dark text / dark mode bg (warm black)
3. `#d97757` — clay accent (THE brand color)
4. `#5e5d59` — secondary text (warm mid-gray)
5. `#e8e6dc` — card background (warm light gray)

---

*Brief compiled from direct CSS bundle analysis of anthropic.com, claude.com, platform.claude.com, and support.claude.com.*
