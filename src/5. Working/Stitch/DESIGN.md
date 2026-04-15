# Design System Strategy: The Luminous Workframe

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Luminous Workframe."** 

Standard SaaS platforms often feel like rigid spreadsheets—static, heavy, and boxed-in. This design system rejects that "template" feel in favor of a high-end editorial experience. We treat AI project management not as a series of rows and columns, but as a fluid, living workspace. By utilizing intentional asymmetry, expansive breathing room, and light-refracting surfaces, we create an environment that feels more like a digital studio than a database. The goal is "Precision through Softness": ultra-sharp typography paired with organic, diffused depth.

## 2. Colors & Surface Philosophy
The palette is rooted in a sophisticated "Deep Zinc" spectrum, punctuated by a vibrant Indigo primary that feels electric against the dark, muted background.

### The "No-Line" Rule
Standard UI relies on 1px borders to separate content. In this design system, **solid 1px borders for sectioning are strictly prohibited.** Boundaries are defined through tonal shifts. A side panel isn't "separated" by a line; it sits on a `surface-container-low` background while the main canvas utilizes the base `surface` (#131316). This creates a seamless, more architectural feel.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of semi-transparent layers.
*   **Base Layer:** `surface` (#131316) or `surface-dim`.
*   **In-set Content:** Use `surface-container-lowest` to create "wells" for secondary data.
*   **Elevated Elements:** Use `surface-container-high` or `highest` for cards and modals that need to "float" above the workspace.

### The "Glass & Gradient" Rule
To achieve the "Glimmer" aesthetic, floating elements (like command palettes or hover-state tooltips) should utilize Glassmorphism.
*   **Formula:** `surface-container` color at 70% opacity + `backdrop-blur: 24px`.
*   **Signature Texture:** Use a subtle linear gradient (from `primary` #c0c1ff to `primary-container` #8083ff) at 10% opacity as a background fill for active AI-generated sections. This provides a visual "soul" that distinguishes AI-assisted work from manual input.

## 3. Typography
We use a dual-typeface strategy to balance authority with utility.

*   **Editorial Authority (Manrope):** All `display` and `headline` tokens utilize Manrope. Its wide apertures and geometric construction provide a modern, premium feel. Use `display-lg` (3.5rem) with tight letter-spacing (-0.02em) for high-impact landing areas.
*   **Functional Precision (Inter):** All `title`, `body`, and `label` tokens utilize Inter. It is the workhorse of the system, ensuring maximum legibility at small sizes.
*   **The Contrast Rule:** To achieve an editorial look, pair a `display-sm` headline with a `label-sm` subtitle. The dramatic jump in scale creates a sophisticated hierarchy that feels intentional rather than "default."

## 4. Elevation & Depth
Depth is conveyed through **Tonal Layering** rather than traditional structural lines or heavy shadows.

*   **The Layering Principle:** Stack `surface-container` tiers to create hierarchy. A `surface-container-lowest` task card sitting on a `surface-container-low` board creates a soft, natural lift without a single pixel of stroke.
*   **Ambient Shadows:** If an element must float (e.g., a modal), use a high-spread, low-opacity shadow. Use a tint of `on-surface` (#e4e1e6) at 4-8% opacity. Avoid pure black shadows; the goal is to mimic natural light passing through frosted glass.
*   **The Ghost Border:** For high-density areas where separation is technically required for accessibility, use a "Ghost Border." This is an `outline-variant` (#464554) at 15% opacity. It should be felt, not seen.

## 5. Components

### Buttons & Interaction
*   **Primary:** Solid `primary` (#c0c1ff) with `on-primary` (#1000a9) text. Shape is `DEFAULT` (1rem) roundedness.
*   **Active States:** All active navigation or selection states must be **pill-shaped** (`full` roundedness) to contrast against the `DEFAULT` roundedness of the main containers.
*   **Glow State:** Primary buttons should have a subtle outer glow using the `primary` color at 20% opacity when hovered.

### Input Fields
*   **Style:** No background fill. Only a "Ghost Border" at the bottom or a subtle `surface-container-high` fill.
*   **Focus:** Transition the ghost border to 100% `primary` opacity and add a 2px `primary` outer "glow" with a heavy blur.

### Cards & Lists
*   **The Divider Ban:** Never use `<hr>` or border-bottom for lists. Use 16px to 24px of vertical whitespace or a alternating background shift of 2% brightness between items.
*   **Roundedness:** Content cards must use `DEFAULT` (1rem). Large layout containers (like the main workspace) use `lg` (2rem) to soften the overall frame.

### Specialized AI Components
*   **The "Glimmer" Pulse:** For AI processing states, use a non-linear animation of the `primary-container` color pulsing behind a glass-morphic container.
*   **Insight Chips:** Small, pill-shaped `tertiary-container` chips with `on-tertiary-container` text to highlight AI-suggested tags.

## 6. Do's and Don'ts

### Do
*   **Use Whitespace as a Tool:** Treat empty space as a structural element. If a layout feels cluttered, increase the gap before adding a line.
*   **Embrace Asymmetry:** Align primary actions to the right but keep descriptive headers to the left to create a dynamic, editorial flow.
*   **Subtle Motion:** Use 200ms "Ease-Out" transitions for all hover states to maintain the premium, "oil-damped" feel.

### Don't
*   **Don't Use Pure Black:** Even in dark mode, the "Zinc" grays are essential for depth. `#000000` is too harsh; stick to `surface` (#131316).
*   **Don't Use 100% Opacity Borders:** They break the "Luminous" effect. Always use the Ghost Border approach.
*   **Don't Mix Rounding:** Keep the hierarchy clear—`DEFAULT` for cards, `full` (pill) for active interaction states. Mixing these up destroys the system's "signature" look.