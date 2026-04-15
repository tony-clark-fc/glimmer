# Glimmer — Google Stitch Design Prompts

Each prompt below is ready to paste into [Google Stitch](https://stitch.withgoogle.com/) to generate design concepts for the corresponding Glimmer workspace page.

**Design system constants** shared across all pages:
- Primary accent: indigo (#6366f1 light / #818cf8 dark)
- Background: near-white #fafafa (dark: #09090b)
- Surface cards: white #ffffff (dark: #18181b)
- Borders: zinc-200 #e4e4e7 (dark: #27272a)
- Muted text: zinc-500 #71717a
- Font: Geist Sans (system fallback: -apple-system, sans-serif)
- Border radius: 12px cards, 8px buttons, full-round badges/pills
- Icons: Lucide stroke icons, 16px, stroke 1.75 inactive / 2.25 active

**Shared interaction pattern — "Ask Glimmer" contextual pop-up:**
Every data element (card, list item, badge, section) should have a small, subtle hover affordance — a tiny indigo sparkle icon (✦) or a "G" pill that appears on hover in the top-right corner of the element. Clicking it opens a compact floating popover anchored to that element, containing:
- A small Glimmer avatar (round, 32px, the 3D character with dark hair, tortoiseshell glasses, navy blazer, and name badge)
- A single-line text input: "Ask Glimmer about this…"
- A send button
This allows the operator to contextually ask Glimmer to update, explain, reprioritize, or act on any visible element without leaving the current view.

---

## 1. Navigation Bar

```
Design a sticky top navigation bar for a professional AI project management app called "Glimmer."

Layout:
- Fixed to the top of the viewport, 56px tall, full-width
- Frosted glass effect: semi-transparent white background with backdrop-blur
- Subtle 1px bottom border in zinc-200

Left side:
- An indigo (#6366f1) rounded-square logo mark with a bold white "G", 32×32px
- Next to it, the word "Glimmer" in 16px semibold, dark text

Center/right:
- 6 navigation tabs in a horizontal row with even spacing: Today, Portfolio, Triage, Drafts, Research, Review
- Each tab has a 16px Lucide stroke icon above or to the left of the label
- Icons: Sun (Today), LayoutGrid (Portfolio), Zap (Triage), PenLine (Drafts), Search (Research), CheckCircle (Review)
- Inactive tabs: zinc-500 text, no background
- Active tab: indigo-50 background pill, indigo-600 text, 2px indigo underline bar
- Hover on inactive: light zinc-100 background

Far right:
- A 32px round Glimmer persona avatar (the 3D character: young woman, dark hair, tortoiseshell glasses, navy blazer with name badge, silk scarf) — clicking this navigates to the Glimmer persona/chat page

Style: clean, minimal, professional. No heavy shadows. Feels like Linear or Vercel dashboard navigation.
```

---

## 2. Today Page (Daily Brief)

```
Design a "Today" daily brief dashboard page for Glimmer, an AI project chief-of-staff app.

Page header:
- Left: a 40px round Glimmer persona avatar (3D character: dark hair, tortoiseshell glasses, navy blazer, name badge)
- Right of avatar: "Today" as a large heading (24px bold) with a subtitle: "Your daily operating brief — priorities, deadlines, and what needs attention now."
- Far right of header: a small pill-shaped status chip showing "Research: Online" with a green dot, or "Research: Offline" with an amber dot

Content layout (single column, max-width 960px, centered):

Section 1 — Narrative summary:
- A soft indigo-tinted banner card (indigo-50 bg, indigo-600 left border accent, 12px rounded)
- Contains 2-3 sentences of Glimmer's daily narrative summary in 14px text
- Example: "Three items need your attention today. The Beta Migration validation is unblocked — Sarah confirmed staging disk space will be available by EOD. Budget submissions are still waiting on two departments."

Section 2 — Top Actions (full width card):
- White card with "Top Actions" header and a count badge (e.g., "4")
- Numbered list of action items, each row showing:
  - A numbered circle (1, 2, 3…) in indigo-50 with indigo text
  - Action title in 14px semibold
  - Below it: a rationale line in 12px muted text
  - Right side: a pill badge showing "Work Item" (blue) or "Pending Action" (amber)
  - A thin priority bar (red/amber/zinc fill) with a numeric score
- Each row has a subtle hover state and the "Ask Glimmer" sparkle icon (✦) appears on hover in the top-right corner

Section 3 — Two-column grid below:
- Left card: "High Risk" with a red-tinted header accent
  - Each risk item is a soft red-50 row with the risk description and a severity badge
- Right card: "Waiting On" with an amber-tinted header accent
  - Each waiting item shows who you're waiting on (bold), description, and expected-by date

Section 4 — Pressure indicators (two compact cards side by side):
- "Reply Debt" — zinc-bordered card with a short text summary
- "Calendar Pressure" — zinc-bordered card with a short text summary

Footer: "Generated 3:42 PM" in 12px muted text.

Overall feel: clean, scannable, not dense. Generous whitespace. The operator should understand their day in 10 seconds. Every card and list item has the "Ask Glimmer" hover affordance (✦ sparkle icon → popover with Glimmer avatar + "Ask Glimmer about this…" input).

Color palette: indigo accent, white surfaces, zinc borders, red for risk, amber for waiting/warnings. Dark mode support with inverted tokens.
```

---

## 3. Portfolio Page

```
Design a "Portfolio" page for Glimmer showing all active projects in a clean card grid.

Page header:
- "Portfolio" as a large heading (24px bold)
- Subtitle: "Compare active projects across urgency, health, and attention demand."

Content:
- A responsive grid of project cards: 1 column on mobile, 2 on tablet, 3 on desktop
- Max-width 960px, centered

Each project card:
- White surface card, 12px rounded corners, 1px zinc-200 border
- Subtle lift shadow on hover (translate-y -1px, soft shadow)
- Top row: project name (16px semibold, left) + status badge pill (right) — "active" in green, "paused" in amber
- Below name: 2-line summary in 14px muted text, line-clamped
- Bottom row: three compact metric indicators:
  - "3 Open" — number + label in zinc-500
  - "1 Blockers" — number + label, red-600 if > 0
  - "2 Pending" — number + label in zinc-500
- The entire card is clickable (navigates to project detail)
- On hover, the "Ask Glimmer" sparkle icon (✦) appears in the top-right corner of each card

Empty state:
- Centered icon (grid outline), message: "No projects yet. Create your first project to start building your portfolio view."

Style: clean grid, breathable spacing (16px gaps), cards feel tappable and lightweight. Think Notion database gallery view or Linear project cards.
```

---

## 4. Triage Page

```
Design a "Triage" page for Glimmer showing incoming signals that need the operator's review and classification.

Page header:
- "Triage" heading (24px bold)
- Subtitle: "Incoming signals, proposed classifications, and items awaiting review."

Content (single column, max-width 960px):

Section 1 — "Classifications Pending Review" card:
- White card with section header, count badge (e.g., "4")
- List of classification items, each row:
  - Top-left: a small "message" badge pill (neutral gray) + truncated source ID in monospace
  - Body: Glimmer's classification rationale in 14px text (e.g., "Message directly references Beta Migration staging environment…")
  - Bottom row: confidence percentage ("Confidence: 92%"), an amber "⚠ Ambiguous" badge if flagged, and review state
  - Right side: vertically stacked action buttons — green "Accept" and red "Reject" (small, pill-shaped)
  - Hover: "Ask Glimmer" sparkle affordance (✦)

Section 2 — "Extracted Actions Pending Review" card:
- Same card style with count badge
- Each action row:
  - Source provenance badge + ID
  - Action text in 14px (e.g., "Schedule cutover window once validation suite passes")
  - Urgency signal label + review state
  - Accept / Reject buttons on right
  - Hover: "Ask Glimmer" sparkle affordance (✦)

Empty state: lightning bolt icon, "No triage items yet. Signals will appear here once connectors are active."

Buttons: small pill-shaped, green for accept (emerald-600 bg), red for reject (red-600 bg), white text, 10px vertical padding.

Key UX principle: the operator should be able to rapid-fire accept/reject without friction. Make the action buttons prominent and easy to tap. Each card should feel like an inbox item to process.
```

---

## 5. Drafts Page

```
Design a "Drafts" page for Glimmer showing AI-generated communication drafts ready for operator review and copy-paste.

Page header:
- Left: a 32px Glimmer persona avatar (the 3D character)
- "Drafts" heading + subtitle: "Review and refine communication drafts — context, variants, and copy-ready output."

Important banner (below header):
- A soft blue-tinted info banner with a lock icon (🔒): "Drafts are review-only. Copy and send manually — Glimmer never sends on your behalf."
- This is a hard product safety rule (no-auto-send)

Content (single column, max-width 960px):
- Stack of draft cards, each one:
  - White surface card, 12px rounded, 1px border
  - Top row: intent label ("reply" in semibold), status badge ("draft" in amber, "reviewed" in green), channel badge ("email" in gray), tone label ("Tone: professional" in muted text)
  - Body area: the draft text in a slightly inset panel (zinc-50 background, 1px border, 12px rounded), 14px text, whitespace-preserved, line-clamped to 4 lines with expand option
  - Below body: italicized rationale in 12px muted text ("Rationale: Professional reply acknowledging the staging fix…")
  - Timestamp: "Created Apr 15, 2026 2:30 PM" in 12px muted
  - Right side: a prominent "Copy Draft" button (indigo-600 bg, white text). After copying, it briefly shows "Copied ✓" in green
  - Hover: "Ask Glimmer" sparkle affordance (✦) — lets operator ask Glimmer to revise tone, shorten, make more formal, etc.

Empty state: pencil icon, "No drafts yet."

Key UX: the copy button must be instantly accessible — this is a copy/paste workflow. Make the draft body text the visual hero of each card. The no-auto-send banner should always be visible.
```

---

## 6. Research & Expert Advice Page

```
Design a "Research & Expert Advice" page for Glimmer with two tab views: Research Runs and Expert Advice exchanges.

Page header:
- "Research & Expert Advice" heading
- Subtitle: "Deep research runs, expert advice consultations, and their review status."

Tab bar (below header):
- A segmented control / pill toggle with two options: "Research Runs" and "Expert Advice"
- Active tab: white background with subtle shadow, dark text
- Inactive tab: no background, muted text
- The tab bar sits in a zinc-100 rounded container (looks like iOS segmented control)

Tab 1 — Research Runs list:
- Stack of clickable cards, each showing:
  - Status badge ("completed" green, "in_progress" blue, "failed" red) + review state badge ("pending review" amber, "accepted" green)
  - Research query text in 14px, 2-line clamp
  - Metadata row: origin label, findings count, sources count, optional document name with 📄 icon
  - Timestamp on the right
  - Click opens a detail panel

Run detail panel (replaces list):
- "← Back to list" ghost button
- Header with status + review badges
- Provenance card: origin, query, document name, Google Doc link
- Summary card with indigo accent: summary text + Accept/Reject buttons if pending
- Findings list: each finding in a bordered card with type badge, confidence signal, content text, source URL link
- Sources list: each source with title, description, URL, relevance notes

Tab 2 — Expert Advice list:
- Similar card layout but shows: status, review state, Gemini mode badge ("fast"/"thinking"/"pro"), prompt text, origin, duration
- Click opens detail with prompt section and response section

"Ask Glimmer" sparkle (✦) on every card and detail section.

Empty states per tab with appropriate messages.

Style: feels like a research library / audit log. Clean, organized, easy to scan provenance information.
```

---

## 7. Review Page

```
Design a "Review" page for Glimmer showing all items that need the operator's judgment and approval.

Page header:
- "Review" heading
- Subtitle: "Items requiring your judgment — ambiguous classifications, memory updates, and approval-gated actions."

Alert banner:
- Amber-tinted banner showing pending count: "8 items pending review" with bold number

Content (single column, max-width 960px):

Section 1 — "Pending Classifications" card:
- Amber-accented section header with count badge
- Each classification item in an amber-50 tinted row:
  - "Pending" badge (amber)
  - Source provenance: type badge + truncated ID
  - Classification rationale text
  - Confidence percentage + "⚠ Ambiguous" badge if flagged
  - Accept / Reject buttons (stacked vertically, right side)
  - "Ask Glimmer" sparkle (✦) on hover

Section 2 — "Pending Extracted Actions" card:
- Same amber-accented style
- Each action item:
  - "Pending" badge
  - Source provenance
  - Action text
  - Urgency signal
  - Accept / Reject buttons
  - "Ask Glimmer" sparkle (✦) on hover

Empty state: checkmark icon, "Nothing to review right now."

Key UX: this is the operator's approval queue. It should feel like a focused todo list that you can clear quickly. Amber coloring signals "needs attention." The accept/reject buttons should be the most prominent interactive elements.
```

---

## 8. Project Detail Page

```
Design a "Project Detail" page for Glimmer showing the full view of a single project.

Top:
- "← Portfolio" breadcrumb link in muted text

Project header:
- Project name in 24px bold (e.g., "Beta Migration")
- Row of badge pills: status ("active" green), phase ("Phase: Execution" blue), priority band ("Priority: high" indigo)
- Objective: 16px text paragraph
- Short summary: 14px muted text below

Content (two-column grid, max-width 960px):

Card 1 — "Open Items" (top left):
- White card, count badge
- List of work items, each row: title + status badge + due date on the right
- Rows have subtle borders

Card 2 — "Active Blockers" (top right):
- Red-accented card header
- Each blocker in a red-50 tinted row with the blocker description

Card 3 — "Waiting On" (bottom left):
- Amber-accented card header
- Each item: bold name of who you're waiting on, description below, expected-by date

Card 4 — "Pending Actions (Review Required)" (bottom right):
- Amber-accented card header
- Each action in amber-50 row with action text and urgency badge

Every card and list item has the "Ask Glimmer" sparkle (✦) hover affordance so the operator can ask Glimmer to update a blocker, reprioritize a work item, draft a follow-up message, etc.

Style: organized dashboard for one project. The operator should quickly see health, blockers, and what's pending. Use the two-column layout to make it scannable.
```

---

## 9. Glimmer Persona Page (NEW — Chat + Mind Map)

```
Design a "Glimmer" persona page — the primary conversational interface where the operator chats directly with Glimmer, their AI chief-of-staff.

This is the most personal and immersive page in the app. It combines a chat interface with a dynamic visual mind-map that uses staged persistence — nothing commits to the database until the operator confirms.

Layout — split view (left 40% / right 60%):

LEFT PANEL — Glimmer Profile & Chat:
- Top: Large Glimmer persona image (the 3D character: young professional woman, dark bobbed hair, tortoiseshell glasses, freckles, navy blazer with name badge, silk paisley scarf — warm, competent, approachable). Display as a rounded-rectangle image, roughly 200×200px, centered, with a soft shadow.
- Below image: "Glimmer" in 20px semibold, and a subtitle: "Your AI Chief of Staff" in 14px muted text
- Below that: a compact status line showing "4 active projects · 8 pending items · 2 blockers"

- Chat area (fills remaining vertical space, scrollable):
  - Chat bubbles in a familiar messaging pattern
  - Glimmer's messages: left-aligned, indigo-50 background, small round Glimmer avatar (24px) to the left
  - Operator's messages: right-aligned, zinc-100 background
  - Messages use 14px text, 12px rounded corners, max-width 80% of chat area
  - Example conversation:
    - Operator: "I just got a new project — building an API gateway for the partner team. Can you set it up?"
    - Glimmer: "Of course. Let me map out what I understand so far. What's the timeline and who are the key stakeholders?"
    - Operator: "Launch is end of Q3. Main stakeholders are Jamie from engineering and the partner team lead, Priya."
    - Glimmer: "Got it. I've created the initial structure — take a look at the map. I'll need to know about any hard dependencies or existing blockers."
  - When the operator pastes content, show a special "pasted content" message bubble:
    - Slightly different styling: zinc-50 background with a 📋 clipboard icon and "Pasted content" label at the top
    - The pasted text shown in a collapsible preview (first 3 lines visible, expandable)
    - Glimmer responds with an extraction summary: "I found 3 stakeholders, 2 milestones, and 1 risk in that brief. I've added them to the map as candidates — review them on the right."

- Chat input bar (bottom, sticky):
  - Rounded text input with placeholder "Talk to Glimmer… (paste content anytime)"
  - A small 📎 attachment/paste indicator icon on the left side of the input
  - Microphone icon button (for voice input)
  - Send button (indigo arrow icon)
  - The input area has a soft border and 48px height
  - The input field should accept multi-line paste (auto-expand to ~120px when pasting long content)

RIGHT PANEL — Dynamic Mind Map Canvas:
- A visual mind-map / bubble diagram that Glimmer constructs in real-time as the conversation progresses
- IMPORTANT: All bubbles are in a DRAFT / TEMPORARY state until the operator confirms. This must be visually clear.

- Center bubble: the project name ("API Gateway") in a larger indigo circle (80px diameter), bold white text
- Connected bubbles fan outward in a radial layout:
  - "Jamie — Engineering Lead" (person icon, teal bubble)
  - "Priya — Partner Team" (person icon, teal bubble)
  - "Q3 Launch" (calendar icon, amber bubble for milestones)
  - "Partner API Requirements" (document icon, zinc bubble for work items)
  - "Security Review Needed" (shield icon, red-tinted bubble for risks/blockers)
- Connection lines: smooth curved lines connecting related bubbles to the center and to each other
- Line colors match the relationship: indigo for core connections, teal for stakeholder links, amber for timeline links
- Bubbles appear with a gentle scale-in animation as Glimmer mentions them in chat

- DRAFT STATE VISUAL TREATMENT:
  - All unconfirmed bubbles have a dashed border (2px dashed) instead of solid
  - A subtle pulsing glow or soft opacity (90%) to indicate "working / not yet saved"
  - A small "draft" pill label in the corner of the canvas: "⏳ Working draft — not yet saved"
  - Bubbles that came from pasted content have a small 📋 icon badge to show their provenance

- Each bubble is interactive:
  - Click to expand/see details in a small floating card
  - Hover shows "Ask Glimmer" sparkle (✦) for contextual questions
  - Each bubble has a tiny ✕ button on hover to remove it from the working map
  - Each bubble has a small ✏️ edit affordance to rename or adjust
  - Can be dragged to rearrange
- The canvas is zoomable and pannable (like Miro or FigJam)
- Background: very subtle dot grid pattern on white/zinc-50

- CONFIRMATION BAR (bottom of right panel, sticky):
  - A prominent bar that appears once the mind-map has content:
  - Left side: "12 items in working draft" (count of unconfirmed nodes)
  - Right side: two buttons:
    - "Confirm & Save" — indigo-600 primary button, bold. Commits everything to the database.
    - "Reset" — ghost/outline button, discards the working draft
  - When clicked, "Confirm & Save" shows a brief confirmation animation (checkmark, green flash), then the bubbles transition from dashed to solid borders, the draft pill disappears, and a success toast appears: "✓ Project structure saved"

Empty state (before conversation starts):
- The mind-map area shows a soft watermark: "Start a conversation and Glimmer will build your project map here"
- A few suggested conversation starters as clickable pills:
  - "What should I focus on today?"
  - "Tell me about a new project"
  - "Update me on Beta Migration"
  - "What's at risk this week?"
  - "I have a project brief to share" (paste-oriented starter)

Overall feel: this page should feel like sitting down with your chief-of-staff for a working session. The left side is conversational and personal. The right side is visual and structured — it's Glimmer showing her work as she builds understanding. The mind-map should feel alive and growing, not static. The staged persistence (draft → confirmed) should feel safe and controlled — the operator never worries that data is being saved behind their back.

Color palette: indigo for project bubbles, teal for people/stakeholders, amber for milestones/deadlines, red for risks/blockers, zinc for general work items. White canvas background with subtle dot grid. Dashed borders for draft state, solid for confirmed.

This is the heart of the Glimmer experience — where understanding is built collaboratively through conversation and visual structure.
```

---

## Design Notes for Stitch

When generating these in Google Stitch, consider requesting:
- **Desktop viewport** (1440×900) for the primary designs
- **Dark mode variants** for each page
- **Mobile responsive** versions (375px) showing how cards stack and nav collapses
- The persona image reference is a 3D-rendered character: young professional woman, dark bobbed hair, tortoiseshell glasses, freckles, navy blue blazer with a silver name badge, cream blouse, navy silk paisley scarf tied at the neck — warm, sharp, competent expression

The "Ask Glimmer" contextual affordance should be consistent across ALL pages — it's the primary interaction pattern that makes every piece of data actionable through Glimmer's intelligence.


