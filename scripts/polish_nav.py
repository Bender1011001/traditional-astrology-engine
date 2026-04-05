import os
import re

STATIC_DIR = "src/static"
SW_FILE = os.path.join(STATIC_DIR, "sw.js")

STANDARD_NAV = """    <div class="nav-links">
      <a href="/#get-reading" class="nav-link">Get Your Reading</a>
      <a href="/horary.html" class="nav-link">Horary Oracle</a>
      <a href="/daily.html" class="nav-link">Daily Navigator</a>
      <a href="/#how-it-works" class="nav-link">How It Works</a>
      <a id="navLoginBtn" href="#" class="nav-link" aria-label="Log In">Sign In</a>
      <a id="navAccountBtn" href="/dashboard.html" class="nav-link hidden" aria-label="My Account">My Account</a>
    </div>"""

AUTH_MODAL_HTML = """
  <!-- Auth Modals -->
  <div id="authModalOverlay" class="modal-overlay hidden">
    <div class="modal-card">
      <button id="closeAuthModal" class="btn-close" aria-label="Close Modal">&times;</button>
      
      <!-- Login View -->
      <div id="loginView" class="auth-view">
        <h2 class="auth-title">Welcome Back</h2>
        <p class="auth-subtitle">Log in to view your chart history and active subscriptions.</p>
        <form id="loginForm" class="auth-form">
          <div class="form-field">
            <label for="loginEmail">Email</label>
            <input type="email" id="loginEmail" name="email" required placeholder="you@example.com">
          </div>
          <div class="form-field">
            <label for="loginPassword">Password</label>
            <input type="password" id="loginPassword" name="password" required placeholder="••••••••">
          </div>
          <div id="loginError" class="auth-error hidden"></div>
          <button type="submit" class="btn-primary auth-submit">
            <span class="btn-text">Sign In</span>
            <span class="btn-loading hidden">...</span>
          </button>
        </form>
        <p class="auth-switch">
          Don't have an account? <a href="#" id="showRegisterView">Sign up</a>
        </p>
      </div>

      <!-- Register View -->
      <div id="registerView" class="auth-view hidden">
        <h2 class="auth-title">Create Account</h2>
        <p class="auth-subtitle">Register to save your chart history moving forward.</p>
        <form id="registerForm" class="auth-form">
          <div class="form-field">
            <label for="regEmail">Email</label>
            <input type="email" id="regEmail" name="email" required placeholder="you@example.com">
          </div>
          <div class="form-field">
            <label for="regPassword">Password</label>
            <input type="password" id="regPassword" name="password" required placeholder="••••••••">
          </div>
          <div id="registerError" class="auth-error hidden"></div>
          <button type="submit" class="btn-primary auth-submit">
            <span class="btn-text">Register</span>
            <span class="btn-loading hidden">...</span>
          </button>
        </form>
        <p class="auth-switch">
          Already have an account? <a href="#" id="showLoginView">Sign in</a>
        </p>
      </div>
    </div>
  </div>
"""

AUTH_JS_TAG = '<script type="module" src="/js/auth.js?v=astro-v3"></script>'

def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Standardize Nav
    nav_pattern = re.compile(r'<div class="nav-links">.*?</div>', re.DOTALL)
    if nav_pattern.search(content):
        content = nav_pattern.sub(STANDARD_NAV, content)

    # 2. Add Auth Modal if missing
    if 'id="authModalOverlay"' not in content:
        # Insert right before </body>, 
        # but what if </body> isn't there? Try to find closing main or footer.
        if '</body>' in content:
            content = content.replace('</body>', f'{AUTH_MODAL_HTML}\n</body>')

    # 3. Add auth.js if missing
    if 'auth.js' not in content:
        # Insert before </body> as well
        if '</body>' in content:
            content = content.replace('</body>', f'  {AUTH_JS_TAG}\n</body>')
    else:
        # Update version string to bust cache
        content = re.sub(r'src="[/]?js/auth\.js[^\"]*"', 'src="/js/auth.js?v=astro-v3"', content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

# Process HTML files
for root, _, files in os.walk(STATIC_DIR):
    for filename in files:
        if filename.endswith(".html"):
            update_file(os.path.join(root, filename))

# Update sw.js version
with open(SW_FILE, "r", encoding="utf-8") as f:
    sw_content = f.read()

# bump CACHE_NAME = "astro-vX"
sw_content = re.sub(r'CACHE_NAME = "astro-v\d+"', 'CACHE_NAME = "astro-v3"', sw_content)
sw_content = re.sub(r'RUNTIME_CACHE = "astro-runtime-v\d+"', 'RUNTIME_CACHE = "astro-runtime-v3"', sw_content)

with open(SW_FILE, "w", encoding="utf-8") as f:
    f.write(sw_content)
print("Bumped service worker versions to v3.")

