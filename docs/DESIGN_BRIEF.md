# Design and interaction contract

## Visual direction
Original Vizra identity with Apple-inspired restraint: photography first, disciplined spacing, strong hierarchy, quiet surfaces, limited accent color, readable type, subtle motion, and excellent light/dark modes. Use a system font stack or properly licensed web font. Do not distribute Apple fonts, logos, or SF Symbols by assumption. Avoid generic gradient dashboards, giant empty hero sections inside the app, and glass effects that reduce photo or text legibility.

Public exploration, personal library management, and administration need different densities within the same design system. Preserve the image's aspect ratio; do not default to destructive cropping. Viewer zoom/pan, keyboard navigation, captions, metadata, comments, and actions should remain understandable on small screens.

## Design deliverables
Start with the first working slice, not fifty speculative screens. Produce tokens, components, variants, interaction notes, and a control-to-action inventory for the shell, owner setup/sign-in, uploader, library, photo viewer, and album dialog. Expand to the remaining milestones after these work in the browser.

Document spacing/type/radii/shadows, semantic color roles, focus appearance, loading/empty/error/success/disabled states, light/dark modes, 200% zoom, reduced motion, keyboard navigation, and responsive behavior. Use 390px and 1440px as initial review viewports, with narrow-screen/zoom overflow checks; these are design targets, not a restriction on supported screens. Target WCAG 2.2 AA and verify with both automated checks and human keyboard/screen-reader review [WCAG].

Claude Design is for exploration. Approved Figma components/tokens, mirrored in repository artifacts, become the design source. Record node references and a design revision. Implement using available Figma design-context/screenshots rather than guessing from memory. A design change after acceptance needs a visible change record. Prototypes may use fixtures; shipping UI must use real APIs.

## Icons
Use one consistent licensed icon family, preferably Lucide, with attribution preserved [LUCIDE-LICENSE]. Use named, statically imported SVG components behind a typed semantic registry. Verify actual exports in the pinned package; do not invent icon names, accept arbitrary runtime strings, or load an entire icon library for a handful of controls [LUCIDE-REACT]. Custom Vizra brand marks are original vector assets and separately reviewed.

Specify purpose, accessible action label, visual states, size/stroke rules, RTL behavior when appropriate, tooltip behavior, and token usage. Examples of semantic purposes: upload, favorite, rating, comment, add-to-album, share, download, report, delete, search, filter, privacy, settings. Favorites and ratings must not be visually or semantically indistinguishable.

Label an icon-only button on the button; keep its redundant decorative SVG hidden from assistive technology [LUCIDE-A11Y]. Do not rely on hover-only tooltips, color alone, or an unlabeled clickable div. Use stable toggle labels plus programmatic pressed state where suitable. Provide visible labels when meaning is uncertain.

## Proof that a control works
Every visible interactive element maps to: route/component → action ID → API/real handler → allowed roles/visibility → expected persistence → loading/error/disabled behavior → browser test → screenshot/trace evidence.

For a Favorite control, prove authentication behavior, a single durable favorite on repeated/retried requests, displayed state after refresh and in a second tab, the actual favorites listing, correct reversal, permissions, keyboard operation, and recoverable server failure. A clicked animation or success toast is not proof.

Reject dead links, no-op handlers, decorative substitutes for controls, fake metrics, swallowed errors, missing mobile actions, horizontal overflow, inaccessible dialogs, and leaking private data in SSR/HTML/JSON. Screenshot differences need visual inspection; automated snapshots do not decide that a redesign is correct.
