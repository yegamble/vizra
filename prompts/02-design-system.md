# Prompt 02 — Claude Design / Figma brief
Use in Claude Design for exploration, then approve and maintain the chosen components in Figma.

Design Vizra, an original image-first, self-hosted photo community with Apple-inspired restraint. Read or attach docs/DESIGN_BRIEF.md, the first-slice specification, and any existing approved design tokens. Do not turn this into an Apple clone, a generic gradient SaaS dashboard, or a landing-page-only deliverable.

Design the first coherent workflow: setup/sign-in → upload → personal library → photo viewer → add to album → share/privacy controls. Public exploration, personal management, and administration should share a visual language but have suitable information densities. Prioritize real photography, legible metadata, balanced spacing, progressive disclosure, precise alignment, and small purposeful animations. Preserve aspect ratios; make zoom/pan and close/navigation controls easy to use.

Deliver original branding direction; semantic tokens; reusable components with meaningful variants; desktop and mobile frames; and interaction specifications. Include light/dark, loading, empty, error, offline/retry, disabled, long-content, unauthorized, and destructive-confirmation states. Define keyboard/focus behavior, 200% zoom, reduced-motion behavior, and screen-reader labels. Aim for WCAG 2.2 AA; the later implementation must be tested rather than assuming the design proves accessibility.

Use one consistent licensed SVG icon family such as Lucide. Keep a semantic icon inventory with the exact proposed component names to verify during coding, action labels, selected/unselected/disabled/loading states, size/stroke rules, tooltip behavior, and associated control IDs. Create an original Vizra brand mark separately. Do not distribute Apple fonts or SF Symbols by assumption; use a system font stack or suitably licensed font.

Every control must have an intended action, required role/state, success result, failure result, and persistence expectation. Specify Favorite and Rating as different concepts. A polished nonfunctional button is not an accepted design handoff. Mark unavailable future features rather than suggesting working functionality.

Produce a handoff containing token values, reusable component names/variants, Figma frame/node references when actually available, an interaction/control matrix, and a list of assets with provenance/license. Do not claim editable Figma layers or exports were created unless the available tool actually created them. Stop for design acceptance before proliferating unrelated screens.
