# Prompt 12 — design fidelity, controls, and icon verification
Use with a fresh Opus or Codex session after implementation. This is an independent audit, not a redesign brief.

Read the accepted Figma/node references or actual exported designs, repository tokens/components, docs/DESIGN_BRIEF.md, and the UI-control inventory. Inspect the running production build with real seeded data and representative roles. Do not approve the builder's screenshots without checking the app.

For every in-scope route, enumerate visible links, buttons, menus, toggles, forms, upload affordances, modal controls, keyboard shortcuts, and icon actions. Map each to the expected action/API, authorization state, persistent outcome, loading/error/disabled state, and test evidence. Identify unlisted controls as inventory gaps. Test actual effects; clicking without observing the result is not verification.

Check the typed icon registry, actual exports in the pinned icon package, consistent family/style/size, correct selected states, label semantics, keyboard/touch behavior, and missing/broken assets. Put labels on interactive wrappers, not redundant decorative icons. Favorites and ratings must remain distinguishable. Check that icons are visible and understandable in light/dark, narrow screens, high contrast when supported, and 200% zoom. Avoid bundle-heavy unrestricted dynamic icon loading.

Inspect desktop/mobile screenshots against the accepted design, including empty/loading/error/full/long-content states. Examine alignment, spacing, typography, contrast, focus rings, image proportions, clipped controls, scrolling, touch targets, reduced motion, viewer/dialog focus return, and keyboard navigation. Run automated accessibility checks and preserve manual keyboard/screen-reader observations separately; automated green is not universal accessibility certification.

Test SSR/navigation/reload, direct route entry, multiple users, session expiry, failed mutations, browser console/network errors, and privacy-sensitive HTML/cache responses. Browser engine coverage must be accurately described; Chromium emulation is not real Safari/iPhone testing.

Deliver a defect list with screenshots/traces, affected requirement IDs, severity, exact reproduction, and narrow fixes. Do not change designs or bless new visual baselines solely to make diffs pass. If authorized to fix, implement focused corrections and rerun the affected checks; otherwise return findings with no false VERIFIED marks.
