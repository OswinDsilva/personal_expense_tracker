# Kharcha Dashboard - Design Specification

## Overview
The Kharcha Dashboard uses "The Obsidian Architect" design system, a dark-mode fintech editorial aesthetic. It is command-center inspired, moving away from bright SaaS norms to a high-stakes, sophisticated environment. A minimalistic and highly interactive frontend.

## Design System Tokens

### Colors
- **Background / Surface Empty Void:** `#0e0e0f` (Base layer)
- **Surface Low:** `#131314` (Section backgrounds)
- **Surface Highest:** `#262627` (Interactive cards)
- **Primary (Neon Mint):** `#b1ffce` (Success, Main CTAs, Growth)
  - Primary Container: `#00ffa3`
  - Gradient CTA: Linear gradient from `#b1ffce` to `#00ffa3`
- **Secondary (Purple):** `#d674ff` (Alternative categories, deep data viz)
- **Tertiary (Orange):** `#ff9249` (Warnings, high-energy spend categories)
- **Text:** 
  - Standard (On Surface): `#ffffff`
  - Muted (On Surface Variant): `#adaaab`

### Typography
- **Headlines & Display (The Architectural font):** `Space Grotesk`
  - Used for large balances (`display-lg` / 3.5rem) and section headers.
- **Body & Titles (The Functional font):** `Inter`
  - Used for lists, descriptions, clean layout.
- **Labels (The Technical font):** `Manrope`
  - Used for timestamps, small data points (`0.6875rem`).

### Layout & Spacing
- **No-Line Rule:** Zero 1px borders for layout. Rely on tonal background differences (`#131314` on `#0e0e0f`).
- **Glassmorphism:** `surface_variant` at 60% opacity with 20-40px backdrop blur for floating elements.
- **Elevation:** Ambient shadows using neon reflection (32px blur at 8% opacity with primary/secondary tint). No gray drop shadows.
- **Spacing:** Large asymmetrical paddings.

## Key Screens to Implement
1. **Refined Kharcha Dashboard (v3):** The main landing page with large typography, balances, and quick actions.
2. **Refined Kharcha Transactions (v2):** Transaction list utilizing white space and no dividers.
3. **Reports: Financial Excel Grid:** Data grid for intensive reporting, likely using secondary dim colors for data viz.

## Components (React)
- `GradientButton`: Primary action button with the signature mint gradient.
- `GlassWidget`: A container with `backdrop-blur` and soft semi-transparent surface.
- `DataCard`: Stat container with large Space Grotesk typography.
- `TransactionRow`: Divider-less row for list items with tonal hover states.

## Interactions
- Smooth micro-interactions on hover (scale, glow effects).
- Interactive charts (e.g. using `recharts` with neon glow effects).
- Soft transitions between pages or states.
