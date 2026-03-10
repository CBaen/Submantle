# Substrate — Dashboard Design Specification

**Version**: 1.0
**Date**: 2026-03-10
**Purpose**: Visual and technical specification for the Substrate awareness dashboard prototype

---

## Brand Personality

Quiet confidence. Ambient awareness. The earth beneath everything.

Not a monitoring dashboard — an awareness layer. It doesn't shout alerts. It breathes. It knows. The UI should feel like the thing it represents: always present, always calm, deeply competent. The user should feel safe looking at it — like standing on solid ground.

Influences: Apple System Preferences (confidence through whitespace), Vercel dashboard (data density without clutter), Linear (typographic precision), Stripe (professional darkness without aggression).

---

## Color System

### Dark Mode (Primary)

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Background | Substrate Deep | `#0A0B0D` | Page background |
| Surface | Substrate Surface | `#111318` | Card backgrounds |
| Surface Raised | Substrate Elevated | `#171B23` | Hover states, dropdowns |
| Border | Substrate Border | `#1E2330` | Card outlines, dividers |
| Border Subtle | Substrate Border Subtle | `#161A22` | Inner separators |
| Text Primary | | `#E8EAF0` | Headlines, important values |
| Text Secondary | | `#8B90A0` | Labels, descriptions |
| Text Tertiary | | `#4A4F62` | Placeholders, muted |

### Status Colors

| State | Name | Hex | Usage |
|-------|------|-----|-------|
| Healthy | Substrate Green | `#2ECC8A` | Active/healthy processes |
| Healthy Glow | | `#2ECC8A1A` | Green card background tint |
| Caution | Substrate Amber | `#F5A623` | Medium importance, warnings |
| Caution Glow | | `#F5A6231A` | Amber card background tint |
| Critical | Substrate Red | `#E8504A` | Critical processes, do-not-kill |
| Critical Glow | | `#E8504A1A` | Red card background tint |
| Inert | Substrate Gray | `#4A4F62` | Unidentified, unknown |

### Brand Accent

| Role | Hex | Usage |
|------|-----|-------|
| Substrate Blue | `#4F8EF7` | Interactive elements, links, focus rings |
| Substrate Blue Dim | `#4F8EF71A` | Button backgrounds, hover states |
| Substrate Pulse | `#2ECC8A` | The awareness pulse indicator |

### Light Mode Overrides

| Role | Hex |
|------|-----|
| Background | `#F5F6F8` |
| Surface | `#FFFFFF` |
| Surface Raised | `#F0F1F4` |
| Border | `#E2E4EB` |
| Text Primary | `#0D0F14` |
| Text Secondary | `#5A5F72` |
| Text Tertiary | `#A0A5B8` |

---

## Typography

**Font Stack**: `"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

Load Inter from Google Fonts (weights: 300, 400, 500, 600, 700).

| Role | Weight | Size | Line Height | Tracking |
|------|--------|------|-------------|----------|
| Page Title | 600 | 24px | 1.2 | -0.02em |
| Section Header | 500 | 13px | 1.4 | 0.08em UPPERCASE |
| Card Title | 600 | 15px | 1.3 | -0.01em |
| Data Value (Large) | 700 | 32px | 1.0 | -0.03em |
| Data Value (Medium) | 600 | 20px | 1.2 | -0.02em |
| Body | 400 | 14px | 1.6 | 0 |
| Caption | 400 | 12px | 1.5 | 0.01em |
| Code / PID | 400 | 12px | 1.4 | 0 | Mono: `"SF Mono", "JetBrains Mono", "Fira Code", monospace` |

**Rule**: No text smaller than 12px. Numbers that matter use tabular figures (`font-variant-numeric: tabular-nums`).

---

## Spacing System

8px base grid. All spacing is a multiple of 4px.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, tight labels |
| sm | 8px | Inner card padding small |
| md | 16px | Standard element gap |
| lg | 24px | Card padding |
| xl | 32px | Section gap |
| 2xl | 48px | Major section gap |
| 3xl | 64px | Page top padding |

---

## Layout

### Grid

Single-page dashboard. Max width: **1440px**, centered, with 40px side padding (20px on mobile).

```
[ Topbar — full width ]
[ 40px padding ]
[ 2-column grid: 2fr / 1fr gap-24px ]
  Left column (wide):
    Overview Strip (4 stat cards)
    Process Categories (full width)
    What Would Break Query (full width)
  Right column (narrow):
    Awareness Pulse
    Critical Processes
    Connected Devices
[ 40px padding ]
```

Responsive breakpoint at 1024px: stack to single column, right column moves below.

### Topbar

Height: 56px. Sticky. Slightly blurred backdrop: `backdrop-filter: blur(20px)`.

Contents (left to right):
- Substrate wordmark (left): `SUBSTRATE` in weight 700, 15px, tracking 0.15em — with a 6px dot before it in `#2ECC8A` that breathes (the global pulse indicator)
- Tagline (left, after wordmark): "the ground beneath everything" — weight 300, 12px, `#4A4F62`
- Spacer
- Last scan timestamp: "scanned 3s ago" — weight 400, 12px, `#8B90A0`
- Light/dark mode toggle (right): sun/moon icon, 32x32 touch target
- Settings icon (right): 32x32 touch target

---

## Components

### 1. Stat Card (Overview Strip)

Four equal-width cards in a horizontal row. Each card:

- Background: `#111318`
- Border: `1px solid #1E2330`
- Border radius: 12px
- Padding: 24px
- Box shadow: `0 1px 3px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.03)`

Contents:
- Label: 12px, weight 500, uppercase, tracking 0.08em, color `#8B90A0`
- Value: 32px, weight 700, color `#E8EAF0`, tabular figures
- Sub-value or trend: 13px, weight 400, color varies by status

The four cards:
1. **Total Processes** — value: process count, sub: "on this machine"
2. **Identified** — value: identified count, sub: "X% recognized" (green if >50%, amber if <30%)
3. **Critical** — value: critical process count, sub: "must not be killed" (red tint if >0)
4. **Devices** — value: device count, sub: "on local network"

On hover: `background: #171B23`, transition 150ms ease.

### 2. Process Category Card

One card per category. Displayed in a responsive grid (2 or 3 columns at full width).

Card structure:
- Category header row: icon + category name (left), process count badge (right)
- Process list: each row has name, importance dot, PID in mono, memory usage
- Importance dot: 6px circle — green (low), amber (medium), red (critical/high)

Category icons (SVG inline, 16x16, `#8B90A0`):
- `creative.*` — sparkles/wand
- `development.*` — code brackets
- `infrastructure.*` — server/database
- `ai.*` — neural network nodes
- `browser` — globe

Card height: auto (no fixed height, no scroll within card).

### 3. Critical Processes Panel

Right column. Distinct visual weight — this is the "do not touch" zone.

- Background: `#111318` with a subtle red tint: `background: linear-gradient(135deg, #111318 0%, #180E0E 100%)`
- Left border: `3px solid #E8504A`
- Section label: "CRITICAL — DO NOT KILL" in `#E8504A`, 11px, uppercase, tracking 0.1em
- Each process row:
  - Name: 14px, weight 600, `#E8EAF0`
  - Description: 12px, `#8B90A0`, italic
  - PID badge: monospace, `#4A4F62`
  - Uptime: right-aligned, `#8B90A0`
  - Pulsing red dot: 6px, breathing animation, `#E8504A`

If no critical processes: show "All clear" state with soft green indicator.

### 4. Connected Devices Panel

Right column, below Critical Processes.

Each device row:
- Device icon (16x16, based on type): laptop, phone, server, router, unknown
- Device name: 14px, weight 500, `#E8EAF0`
- Manufacturer/type: 12px, `#8B90A0`
- Status dot: 6px green (online), amber (slow response), gray (idle)
- IP address: 12px mono, `#4A4F62`, right-aligned

Hover on row: `background: #171B23`, reveals a "→" chevron suggesting expandable detail (V2 feature placeholder).

### 5. What Would Break Query

Full-width card. This is the most interactive component.

Structure:
- Card header: "What Would Break?" title + "Ask Substrate" subtitle
- Search input:
  - Full width, height 48px
  - Background: `#0A0B0D` (one level darker than card)
  - Border: `1px solid #1E2330`, focus: `1px solid #4F8EF7` with `box-shadow: 0 0 0 3px rgba(79,142,247,0.15)`
  - Placeholder: "Type a process name — e.g., 'node', 'python', 'docker'"
  - Left icon: magnifying glass in `#4A4F62`
  - Right: keyboard shortcut hint "⌘K" in `#4A4F62` (desktop only)
  - Border radius: 10px
  - Font: 15px, weight 400

- Results panel (appears below input on query):
  - BLOCK state: red-tinted card, "BLOCK — High Risk" label, lists critical processes affected
  - CAUTION state: amber-tinted card, lists unidentified processes
  - SAFE state: green-tinted card, "Safe to proceed" message
  - Collateral damage section: "These would also stop:" list in amber
  - Empty state (no results): "No processes named 'X' are currently running."
  - Loading state: subtle shimmer on the results area (200ms)

### 6. Awareness Pulse

Right column, top. The most alive component.

A circular visualization — not a chart, a presence indicator.

Structure:
- Dark circle, ~140px diameter
- Center: the Substrate mark (a simple radiating dot pattern)
- Three concentric rings that pulse outward, staggered timing
- Ring 1 (innermost): opacity 0.6, 3s loop
- Ring 2: opacity 0.4, 3s loop, 1s delay
- Ring 3 (outermost): opacity 0.2, 3s loop, 2s delay

Below the circle:
- "AWARE" in `#2ECC8A`, 11px, uppercase, tracking 0.15em
- "Monitoring 342 processes" in `#8B90A0`, 12px
- Last scan: "3s ago" in `#4A4F62`, 11px

If Substrate loses connection to the backend: rings stop, dot dims to gray, label changes to "OFFLINE" in `#4A4F62`.

The pulse ring animation:
```css
@keyframes substrate-pulse {
  0% { transform: scale(1); opacity: var(--ring-opacity); }
  50% { transform: scale(1.15); opacity: calc(var(--ring-opacity) * 0.5); }
  100% { transform: scale(1); opacity: var(--ring-opacity); }
}
```

---

## Animations

**Philosophy**: Animations communicate system state, not decoration. Every motion means something.

| Animation | Duration | Easing | Purpose |
|-----------|----------|--------|---------|
| Card hover | 150ms | ease | Feedback |
| Result panel reveal | 250ms | ease-out | New information |
| Pulse rings | 3000ms | ease-in-out | System alive |
| Status dot breathe | 2000ms | ease-in-out | Active process |
| Scan flash | 800ms | ease | Scan just completed |
| Loading shimmer | 1200ms | ease-in-out | Fetching data |
| Mode toggle | 300ms | ease | Theme switch |
| Number count-up | 600ms | ease-out | Initial data load |

**Scan flash**: When a new scan completes, the overview stat values briefly highlight (background flashes from current to `#1E2330` and back). Subtle — the user should notice if watching, not be startled.

**Count-up**: On initial load, the four stat values count up from 0 to their actual values over 600ms. Uses easeOutExpo curve.

---

## Tech Stack Recommendation

### Frontend
- **Vanilla JS + CSS** — no framework overhead, loads instantly
- **Inter** via Google Fonts CDN
- **No charting library needed** — the pulse indicator is pure CSS/SVG, all other visualizations are CSS-driven

### Backend
- **Python FastAPI** — already in the project, familiar
- **psutil** — already used in prototype
- **uvicorn** — ASGI server, ships with FastAPI
- **CORS middleware** — for local development serving HTML from file:// or different port

### File Structure
```
prototype/
  substrate.py          (existing daemon logic)
  signatures.json       (existing)
  api.py                (NEW — FastAPI server wrapping substrate.py)
  dashboard.html        (NEW — single-file frontend)
```

---

## API Endpoints

All endpoints return JSON. All are GET except the query endpoint.

### `GET /api/status`
Returns the current awareness state. Polled every 5 seconds by the dashboard.

```json
{
  "timestamp": "2026-03-10 03:10:00",
  "scan_age_seconds": 3,
  "total_processes": 342,
  "identified_processes": 68,
  "identification_rate": 19.9,
  "critical_count": 3,
  "categories": {
    "ai.agent": [
      {
        "pid": 1184,
        "name": "Claude Code (AI Agent)",
        "importance": "medium",
        "uptime": "1h 19m",
        "memory_mb": 622.2
      }
    ]
  },
  "critical_processes": [
    {
      "pid": 1234,
      "name": "PostgreSQL Database",
      "description": "Production database — unclean shutdown risks data loss",
      "uptime": "4h 12m",
      "memory_mb": 340.1
    }
  ]
}
```

### `GET /api/devices`
Returns discovered devices on the local network.

```json
{
  "timestamp": "2026-03-10 03:10:00",
  "devices": [
    {
      "ip": "192.168.1.1",
      "hostname": "router.local",
      "mac": "AA:BB:CC:DD:EE:FF",
      "manufacturer": "ASUS",
      "type": "router",
      "status": "online",
      "response_ms": 2
    }
  ]
}
```

### `GET /api/query?process={name}`
The "What Would Break" query.

```json
{
  "query": "node",
  "recommendation": "CAUTION",
  "total_matching": 4,
  "critical_processes": [],
  "safe_to_kill": [
    { "pid": 4421, "identity": "Node.js Process" }
  ],
  "unidentified": [
    { "pid": 8823, "name": "node", "cmdline": "node server.js --port 3000" }
  ],
  "collateral_damage": []
}
```

Recommendation values: `"BLOCK"`, `"CAUTION"`, `"SAFE"`, `"NOT_FOUND"`

### `GET /api/health`
Simple liveness check.

```json
{ "status": "alive", "version": "0.1.0" }
```

---

## Key Interactions

### Auto-Refresh
- Dashboard polls `/api/status` every 5 seconds
- No full-page reload — DOM updates in place
- Stat values transition smoothly when numbers change
- Scan timestamp updates: "just now", "3s ago", "12s ago"
- If poll fails 3 consecutive times: Pulse goes offline state, banner appears: "Lost connection to Substrate daemon"

### What Would Break Query
- User types in the input field
- Query fires after 400ms debounce (not on every keystroke)
- Results slide down from the input with a 250ms ease-out
- BLOCK results: card has a brief red flash on appear (100ms)
- User can clear with Escape key — results slide back up
- Empty input: results hide

### Category Cards
- Each category is its own card
- Importance dots pulse if the process is `critical`
- Clicking a category card (V2): would expand to show all processes in that category — for now, clicking does nothing but shows a subtle hover state

### Devices
- Device rows have a hover state
- Clicking a device row (V2 placeholder): shows "Details coming in V2" tooltip
- Status dot for "online" devices has a slow 4s breathing animation

### Mode Toggle
- Clicking the sun/moon icon transitions all colors with `transition: background 300ms, color 300ms, border-color 300ms` on `:root`
- Preference saved to `localStorage`

---

## Visual Identity Details

### The Substrate Mark
Used in the Pulse component center. A simple radial pattern: a 6px center dot surrounded by 4 lines radiating outward at 45-degree offsets, each 8px long, 1px wide. Rendered in SVG. Color: `#2ECC8A` when alive, `#4A4F62` when offline.

### Process Category Color Mapping

| Category Prefix | Accent Color |
|-----------------|-------------|
| `creative.*` | `#B07EFF` (soft purple) |
| `development.*` | `#4F8EF7` (substrate blue) |
| `infrastructure.*` | `#F5A623` (substrate amber) |
| `ai.*` | `#2ECC8A` (substrate green) |
| `browser` | `#8B90A0` (neutral) |
| unknown | `#4A4F62` (inert) |

### Importance → Visual Weight Mapping

| Importance | Dot Color | Label Style |
|------------|-----------|-------------|
| `critical` | `#E8504A` + pulse | Name in weight 700 |
| `high` | `#F5A623` | Name in weight 600 |
| `medium` | `#4F8EF7` | Name in weight 500 |
| `low` | `#2ECC8A` | Name in weight 400 |

---

## Accessibility Notes

- All interactive elements have visible focus rings: `outline: 2px solid #4F8EF7; outline-offset: 2px`
- Color is never the only indicator — importance levels also use text labels
- Animations respect `prefers-reduced-motion` — all transitions cut to instant, pulse stops
- Minimum contrast ratio: 4.5:1 for body text against backgrounds (all colors above meet this)
- The What Would Break input is a real `<input>` element with proper label association

---

## What This Spec Does NOT Cover (V2+)

- Process detail drawer (click to expand full process info)
- Workflow graph visualization (the process relationship tree)
- Cross-device mesh view (connecting multiple Substrate instances)
- Historical timeline (how system state changed over time)
- Alert configuration (notify me if X stops running)
- Substrate Store integration
