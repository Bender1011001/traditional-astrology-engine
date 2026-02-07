# Static Assets

## Status
- **Working**: Landing page (index.html), about page (about.html), methodology page (methodology.html), pricing, services, booking, and FAQ pages. JavaScript logic for landing (landing.js) and basic functionality (basic.js). CSS styling (style.css).
- **In-Progress**: Ongoing minor UI refinements.

## Tech Stack
- HTML5, CSS3 (Vanilla)
- Vanilla JavaScript (ES6 Modules)
- Google Fonts (Cormorant Garamond, Inter, Sora, Space Mono)

## Key Files
- `index.html` — The main landing page.
- `style.css` — Global stylesheets with glassmorphism and responsive design.
- `js/landing.js` — Entry point for landing page interactivity.
- `basic.js` — Global utilities and core frontend logic.
- `og-card.png` — Open Graph preview image.

## Architecture Quirks
- CSS uses a global token system defined in `:root`.
- High degree of glassmorphism and subtle animations (background globes).
- Pricing and paywall modals are managed via JS triggers.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Modal overlap | Z-index conflict with background globes | Set modal z-index to 2000+ |
| Form submission hang | Missing error handling in basic.js | Added try/catch and user-facing error messages |

## Anti-Patterns (DO NOT)
- Do not use TailwindCSS; stick to the custom Vanilla CSS system.
- Do not add external JS dependencies if a vanilla solution is possible.
- Avoid inline styles; use the classes defined in `style.css`.

## Build / Verify
- Open `index.html` in a local browser or serve via FastAPI.
