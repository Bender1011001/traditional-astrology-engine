# Frontend Architecture

The frontend of Codex Caelestis is built with **Vanilla JavaScript**, **CSS Variables**, and **HTML5**. It is designed to be lightweight, fast, and easily hosted on static platforms like GitHub Pages or served directly by FastAPI.

## Directory Structure

*   `src/static/`: Contains all client-side assets.
    *   `basic.js`: Core application logic (Routing, API calls, State management).
    *   `style.css`: Global styles, themes, and responsive design.
    *   `landing.js`: Specific logic for the landing page marketing.

## Key Concepts

### 1. State Management
Authentication state and user preferences are managed via `localStorage`.
*   `cael_auth_token`: JWT for authenticated requests.
*   `cael_user`: Cached user profile data.
*   `cael_theme`: 'light' or 'dark' preference.

### 2. API Integration
All API calls are routed through the `apiUrl()` helper in `basic.js`, which determines the correct backend base URL (`window.CAEL_API_BASE` or localhost).

```javascript
// Example: Log a telemetry event
logEvent("page_view", { path: window.location.pathname });
```

### 3. Theme System
The application supports a toggleable Dark/Light mode using CSS variables.
*   **Root Variables**: Defined in `style.css` (`:root`).
*   **Switching**: `applyTheme()` in `basic.js` updates the `data-theme` attribute on the `<html>` element.

### 4. Viral Sharing
The `window.shareReading()` function allows users to generate a downloadable image of their chart audit.
*   **Mechanism**: It renders a hidden DOM element (`#socialCard`) and uses `html2canvas` to capture it as a PNG.

## Usage Guide

To work on the frontend:
1.  Open `src/static/index.html` in a browser (or via Live Server).
2.  Ensure local backend is running on `localhost:8000` for API calls to work.
