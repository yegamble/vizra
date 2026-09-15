from core import *

req("VZ-DESIGN-001","Design system: tokens, components, typed icon registry, light/dark, accepted first-slice screens",
    "Everyone: approved tokens (spacing/type/radii/shadows/semantic colors), components with variants and states, Lucide icons behind a typed registry with verified exports, brand mark; mirrored from Figma into the repo with revision references.",
    "design", SAFE, [{"source":"DESIGN-BRIEF"},{"source":"LUCIDE-REACT","note":"lucide-react 1.46.0 ISC"}],
    deps=["VZ-FOUND-001"], success=["Token file + component catalog + icon registry test that every name exists in the pinned package"], negative=["Unknown icon name fails typecheck"], evidence=["design handoff record with node references"])
req("VZ-A11Y-001","WCAG 2.2 AA across shell, auth, uploader, library, viewer, album dialog with automated and manual evidence",
    "Everyone: keyboard operability, visible focus, focus trap/return, labels on icon-only controls, aria-live for upload/processing, 200% zoom, reflow at 320px, reduced motion, contrast ≥ 4.5:1 text / 3:1 UI over real backings.",
    "design", SAFE, [{"source":"WCAG","note":"2.2 REC 2024-12-12"},{"source":"DESIGN-BRIEF"}],
    deps=["VZ-DESIGN-001"], success=["axe serious/critical zero on first-slice routes + recorded manual keyboard/screen-reader review"], negative=["Drag-only interaction without alternative is a failing check"], evidence=["axe report + manual review record with reviewer and setup"])
req("VZ-RESPONSIVE-001","Responsive behavior at 390px and 1440px with no horizontal overflow, touch targets and mobile viewer actions",
    "Everyone: every first-slice route reviewed at both viewports in both themes; no overflow; viewer actions reachable on phones.",
    "design", SAFE, [{"source":"DESIGN-BRIEF","note":"390/1440"}],
    deps=["VZ-DESIGN-001"], success=["Screenshot matrix inspected by a human"], evidence=["screenshot matrix + review notes"])
req("VZ-CONTROLS-001","UI-control inventory kept in sync with implemented routes",
    "QA: docs/quality/ui-controls.json lists every visible interactive control with route, action, API, access, persistence, states, tests and evidence; an audit compares it with the running app.",
    "design", SAFE, [{"source":"DESIGN-BRIEF","note":"proof that a control works"}],
    deps=["VZ-DESIGN-001"], success=["Inventory audit finds no unlisted control and no dead control"], evidence=["audit report per milestone"])
