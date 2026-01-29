# Smart Socks - Design Assets

**ELEC-E7840 Smart Wearables — Aalto University**

> **Nordic Design Edition** · Minimalist · Professional · Functional

---

## Viewing SVG Diagrams

SVG diagrams must be opened directly in a browser (they won't render inline in markdown editors):

```bash
# Open all diagrams
open 01_Design/diagrams/*.svg

# Or open individually
open 01_Design/diagrams/system_architecture.svg
open 01_Design/diagrams/voltage_divider.svg
open 01_Design/diagrams/sensor_placement.svg
```

Or navigate to `01_Design/diagrams/` and double-click the SVG files.

---

## Brand Assets

### Logo
**File:** `assets/logo.svg`

![Logo](assets/logo.svg)

**Usage:**
- Presentation slides (top-left corner)
- Poster header
- Documentation headers
- Web dashboard favicon

**Colors:**
- Background: `#2E3440` (Nord0)
- Primary Text: `#ECEFF4` (Nord6)
- Accent: `#88C0D0` (Nord8)

---

## Presentation Templates

### Nordic Slides
**File:** `06_Presentation/templates/nordic_slides.html`

**Features:**
- 6 slide layouts included
- A4 landscape (1280×720)
- Print-ready CSS
- Responsive typography

**Slide Types:**
1. **Title Slide** - Project title with decorative circles
2. **Content Slide** - Two-column layout with text + visual
3. **Section Divider** - Clean transition slides
4. **Data Slide** - 4-column metrics grid
5. **Quote Slide** - Centered quote with attribution
6. **Full Content** - Single column with tables

**Usage:**
```bash
# Open in browser for presentation
open 06_Presentation/templates/nordic_slides.html

# Print to PDF (Chrome: Cmd+P → Save as PDF)
```

---

## Activity Icons

**File:** `assets/activity_icons.svg`

10 activity icons for real-time classification display:

| Icon | Activity | Description |
|------|----------|-------------|
| ➡️ | Walking Forward | Person with forward arrow |
| ⬅️ | Walking Backward | Person with backward arrow |
| ↗️ | Stairs Up | Person climbing stairs |
| ↘️ | Stairs Down | Person descending stairs |
| 🪑 | Sitting | Seated person |
| 🧍 | Standing | Upright standing |
| ⬅️ | Leaning Left | Tilted left |
| ➡️ | Leaning Right | Tilted right |
| ⬆️ | Sit→Stand | Transition up |
| ⬇️ | Stand→Sit | Transition down |

**Usage:**
- Real-time classifier UI
- Web dashboard activity indicators
- Presentation slides
- Analysis reports

---

## Research Poster

**File:** `06_Presentation/poster.html`

**Specifications:**
- Format: A0 Portrait (841mm × 1189mm)
- Resolution: 794 × 1123 pixels (96 DPI)
- Print-ready CSS

**Sections:**
1. **Header** - Logo, title, authors
2. **Abstract** - Project summary bar
3. **Introduction** - Problem statement
4. **System Architecture** - Hardware overview
5. **Sensor Placement** - Anatomical diagram
6. **Methodology** - ML approach
7. **Results** - Key metrics grid
8. **Applications** - Use cases
9. **Footer** - Contact info, QR code

**Usage:**
```bash
# Open in browser
open 06_Presentation/poster.html

# Print to PDF (scale: Fit to page)
# Recommended: Professional poster printing service
```

---

## Nordic Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Nord0** | `#2E3440` | Primary background |
| **Nord1** | `#3B4252` | Card backgrounds |
| **Nord2** | `#434C5E` | Borders, dividers |
| **Nord3** | `#4C566A` | Subtle elements |
| **Nord4** | `#D8DEE9` | Secondary text |
| **Nord5** | `#E5E9F0` | Light text |
| **Nord6** | `#ECEFF4` | Primary text |
| **Nord7** | `#8FBCBB` | Teal accent |
| **Nord8** | `#88C0D0` | **Primary accent** |
| **Nord9** | `#81A1C1` | Blue accent |
| **Nord10** | `#5E81AC` | Dark blue |
| **Nord11** | `#BF616A` | Red (alert/error) |
| **Nord12** | `#D08770` | Orange |
| **Nord13** | `#EBCB8B` | Yellow |
| **Nord14** | `#A3BE8C` | Green (success) |
| **Nord15** | `#B48EAD` | Purple |

---

## Typography

**Primary Font Stack:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

**Weights:**
- Headers: 300 (Light)
- Body: 400 (Regular)
- Labels: 500 (Medium)

**Sizing:**
- Title: 56px, letter-spacing: 8px
- H1: 42px, letter-spacing: 4px
- H2: 32px, letter-spacing: 2px
- Body: 14-16px
- Labels: 11-12px, uppercase, letter-spacing: 1-2px

---

## Design Principles

1. **Minimalism** - Only essential elements
2. **Whitespace** - Generous padding (60-80px)
3. **Muted Colors** - Never harsh or bright
4. **Functional** - Every element serves purpose
5. **Hierarchy** - Clear visual weight
6. **Consistency** - Same patterns throughout

---

## Circuit Diagrams

**File:** `01_Design/circuit_diagram.md`

**SVG Diagrams** (open directly in browser):

| Diagram | File | View Command |
|---------|------|--------------|
| System Architecture | `diagrams/system_architecture.svg` | `open 01_Design/diagrams/system_architecture.svg` |
| Voltage Divider | `diagrams/voltage_divider.svg` | `open 01_Design/diagrams/voltage_divider.svg` |
| PCB Layout | `diagrams/pcb_layout.svg` | `open 01_Design/diagrams/pcb_layout.svg` |

---

## Sensor Placement Guide

**File:** `01_Design/sensor_placement.md`

**SVG Diagram** (open directly in browser):

| Diagram | File | View Command |
|---------|------|--------------|
| Sensor Placement | `diagrams/sensor_placement.svg` | `open 01_Design/diagrams/sensor_placement.svg` |

**Contents:**
- Foot anatomy with sensor positions
- Left/right foot comparison  
- Zone explanations
- Placement procedure

---

## Usage Summary

| Asset | Used In | Format |
|-------|---------|--------|
| Logo | All docs, slides, poster | SVG |
| Activity Icons | Dashboard, classifier | SVG |
| Slide Template | Presentations | HTML |
| Poster | Conferences | HTML |
| Circuit Diagrams | Documentation | SVG |
| Sensor Placement | Documentation | SVG |

---

## Navigation

| Document | Description |
|----------|-------------|
| [[README]] | Project overview |
| [[INDEX]] | Documentation hub |
| [[circuit_diagram]] | Hardware schematics |
| [[sensor_placement]] | Assembly guide |

---

*Created: 2026-01-29 · Nordic Design System v1.0*
