```markdown
# CODEX CAELESTIS MONETIZATION IMPLEMENTATION

## PROJECT CONTEXT
You are implementing a freemium paywall for Codex Caelestis, a traditional astrology 
engine that generates personalized natal chart readings. The system currently:

1. Takes birth data (date, time, location)
2. Calculates chart using pyswisseph
3. Generates 5 prose sections via Gemini Flash AI (~3000 words total)
4. Displays everything for free (unsustainable)

**Current tech stack:**
- Backend: Python 3.10+, FastAPI, Uvicorn
- Frontend: Static HTML/CSS/JS (served via GitHub Pages in demo mode)
- AI: Gemini Flash API for prose generation
- Database: JSON flat files for rules
- No user accounts currently
- No payment processing currently

**Business goal:**
Generate $400/month in first 30 days by converting 8-10% of free users to paid.

## OBJECTIVE
Implement a minimal viable paywall that:
1. Shows enough free content to hook users
2. Gates premium content behind payment
3. Prevents abuse/API cost bleeding
4. Captures emails for marketing
5. Processes payments via Stripe
6. Takes <40 hours of development time

## CURRENT READING STRUCTURE
The AI-generated reading has 5 sections:

**Section 1: "Your Natural Temperament"** (~500 words)
- Temperament type (Melancholic/Sanguine/etc.)
- Hot/Cold/Dry/Moist qualities
- Personality traits
- How they function best

**Section 2: "Your Soul's Purpose: The Sovereign Communicator"** (~600 words)
- Almuten (soul guardian planet)
- Life's work theme
- Key players/teams in chart
- Health indicators

**Section 3: "Your Current Life Chapter"** (~700 words)
- Current age analysis
- Annual profection (Lord of the Year)
- Daily oracle
- Sub-period timing (Firdaria)

**Section 4: "Your Life Path: The Balsamic Soul"** (~600 words)
- Lunar phase personality
- Social dynamics (11th house)
- Hidden strengths (12th house)
- Current timing (Saturn return, etc.)

**Section 5: "Hidden Architecture"** (~600 words)
- Lots (Fortune, Spirit, Victory, Nemesis)
- Sect status and teams
- Advanced timing (Firdaria periods)
- Family/financial blueprint

## PAYWALL STRATEGY

### FREE TIER (No email required initially)
**Show immediately:**
- Section 1: "Your Natural Temperament" (FULL)
- Section 2: "Your Soul's Purpose" (FIRST 200 WORDS ONLY)

**Teaser display:**
```
Your reading continues with:
✓ Your Current Life Chapter (including Saturn Return analysis)
✓ Your Life Path & Social Dynamics  
✓ Hidden Architecture (Lots, Timing, Financial Blueprint)

[Unlock Full Reading - $9.99]
[or Subscribe for $4.99/month - Unlimited Readings]
```

### PAID TIER
**One-time purchase ($9.99):**
- Unlock all 5 sections for THIS chart
- PDF export of full reading
- Valid for 30 days (can re-download)

**Monthly subscription ($4.99/month):**
- Unlimited chart readings
- All 5 sections always unlocked
- PDF export
- Save up to 10 charts
- Priority generation (no artificial delay)

### EMAIL CAPTURE (After free reading)
After user views free sections, show modal:
```
Want to save your reading?
Enter your email to receive a copy + weekly astrology insights.

[Email input]
[Send Me My Reading]

[Skip for now] ← Still allow, but track as lower-intent user
```

**Email flow:**
- Immediate: PDF of free sections + "Unlock full reading" CTA
- Day 3: "Still curious? Here's what you're missing" + testimonials
- Day 7: "Last chance: 20% off full reading" ($7.99)

## ABUSE PREVENTION

### Rate Limiting (Free Tier)
**Without email verification:**
- 1 reading per IP per day
- Max 3 readings per IP per month
- Cookie tracking for browser fingerprinting

**With email verification:**
- 3 readings per email per month (free tier)
- Lift limits entirely for paid users

### API Cost Protection
**For free tier:**
- Only generate Sections 1 + partial Section 2 (~2000 tokens)
- Cost: ~$0.0005 per free reading
- Cache aggressively (same birth data = same reading)

**For paid tier:**
- Generate all 5 sections (~5000 tokens)
- Cost: ~$0.0012 per paid reading
- Still cache, but full reading

**Caching strategy:**
```python
cache_key = hash(f"{date}_{time}_{location}_{tier}")
# Tier = 'free' or 'paid'
# Cache for 30 days
# 90% of requests should hit cache (common birth dates)
```

### Bot Protection
- Add simple CAPTCHA before chart calculation
- Require JavaScript (no headless scrapers)
- Track and block IPs making >10 requests/hour
- Add honeypot fields in forms

## TECHNICAL IMPLEMENTATION REQUIREMENTS

### Phase 1: Payment Infrastructure (Priority 1 - Week 1)

**Stripe Integration:**
1. Create Stripe account + get API keys (test mode first)
2. Implement two payment flows:
   - One-time purchase: Stripe Checkout Session
   - Monthly subscription: Stripe Subscription + Customer Portal
3. Webhook endpoint to handle payment confirmations
4. Generate access tokens on successful payment

**Access Token System:**
- On payment success: Generate JWT token with expiry
- Store: `{chart_hash: token, expires: timestamp, tier: 'onetime'|'subscription'}`
- One-time tokens: Valid 30 days
- Subscription tokens: Valid while subscription active

**Frontend changes:**
```javascript
// After user enters birth data, before calculation:
1. Check if user has valid access token for this chart
2. If yes: Calculate full reading (all 5 sections)
3. If no: Calculate free reading (sections 1-2 only)
4. Display paywall modal after free content
5. On payment: Redirect to success page → Regenerate with full access
```

### Phase 2: Email Capture (Priority 2 - Week 1)

**Email collection flow:**
1. User views free reading
2. Show modal (not blocking, can dismiss)
3. Collect email via simple form
4. Send confirmation email with:
   - Link to download free reading PDF
   - Explanation of what's in paid version
   - CTA button to upgrade

**Email service integration:**
Options in order of simplicity:
1. SendGrid (free tier: 100 emails/day)
2. Mailgun (pay-as-you-go)
3. AWS SES (cheapest, but setup complexity)

**Required endpoints:**
```
POST /api/capture-email
  Body: {email, chart_id}
  Returns: {success, message}

GET /api/send-reading-pdf
  Params: {email, chart_id, tier}
  Sends email with PDF attachment
```

### Phase 3: Reading Generation Logic (Priority 1 - Week 1)

**Modify existing chart calculation endpoint:**
```python
@app.post("/api/calculate")
def calculate_chart(birth_data: BirthData, access_token: Optional[str] = None):
    # Calculate chart data (always do this)
    chart = calculate_chart_data(birth_data)
    
    # Determine tier
    if access_token and validate_token(access_token):
        tier = 'paid'
        sections_to_generate = [1, 2, 3, 4, 5]
    else:
        tier = 'free'
        sections_to_generate = [1, 2]  # Section 2 truncated
    
    # Check cache first
    cache_key = generate_cache_key(birth_data, tier)
    cached_reading = get_from_cache(cache_key)
    if cached_reading:
        return cached_reading
    
    # Generate reading via Gemini
    reading = generate_ai_reading(chart, sections_to_generate)
    
    # Cache for 30 days
    set_cache(cache_key, reading, expire=2592000)
    
    return {
        'chart_data': chart,
        'reading': reading,
        'tier': tier,
        'sections_available': sections_to_generate
    }
```

### Phase 4: Frontend Paywall UI (Priority 1 - Week 1)

**Required UI components:**

**1. Paywall Modal** (shows after free content):
```html
<div id="paywall-modal" class="modal">
  <div class="modal-content">
    <h2>Your Reading Continues...</h2>
    <p>You've seen your Natural Temperament and Soul's Purpose.</p>
    
    <div class="locked-sections">
      <h3>Unlock Now:</h3>
      <ul>
        <li>✓ Your Current Life Chapter (Saturn Year Analysis)</li>
        <li>✓ Your Life Path & Hidden Strengths</li>
        <li>✓ Advanced Timing & Financial Blueprint</li>
      </ul>
    </div>
    
    <div class="pricing">
      <div class="option">
        <h4>One-Time Access</h4>
        <p class="price">$9.99</p>
        <p>Full reading for this chart</p>
        <button onclick="checkout('onetime')">Unlock Now</button>
      </div>
      
      <div class="option recommended">
        <span class="badge">BEST VALUE</span>
        <h4>Monthly Unlimited</h4>
        <p class="price">$4.99/month</p>
        <p>Unlimited readings + saved charts</p>
        <button onclick="checkout('subscription')">Subscribe</button>
      </div>
    </div>
    
    <p class="guarantee">30-day money-back guarantee</p>
  </div>
</div>
```

**2. Checkout function:**
```javascript
async function checkout(tier) {
  const response = await fetch('/api/create-checkout', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      tier: tier,
      chart_data: currentChartData,
      success_url: window.location.origin + '/success',
      cancel_url: window.location.href
    })
  });
  
  const {checkout_url} = await response.json();
  window.location.href = checkout_url;
}
```

**3. Success page:**
- Thank you message
- "Generating your full reading..." spinner
- Auto-redirect to reading with access token in URL
- "Download PDF" button

### Phase 5: PDF Export (Priority 2 - Week 2)

**PDF generation:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_reading_pdf(chart_data, reading_sections):
    """
    Generate professional PDF of reading
    Include:
    - Title: "Your Natal Chart Reading"
    - Birth data (date, time, location)
    - Chart wheel image (if available)
    - All 5 sections formatted nicely
    - Footer: "Generated by Codex Caelestis"
    """
    # Implementation details...
    return pdf_bytes

# Endpoint
@app.get("/api/download-pdf")
def download_pdf(chart_id: str, access_token: str):
    if not validate_token(access_token):
        raise HTTPException(401, "Invalid access token")
    
    chart_data = get_chart_from_cache(chart_id)
    reading = get_reading_from_cache(chart_id, tier='paid')
    
    pdf = generate_reading_pdf(chart_data, reading)
    
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=reading_{chart_id}.pdf"}
    )
```

### Phase 6: Analytics & Tracking (Priority 3 - Week 2)

**Minimal analytics to track:**
```python
# Simple event logging
events = {
    'chart_calculated_free': 0,
    'chart_calculated_paid': 0,
    'paywall_shown': 0,
    'checkout_started': 0,
    'payment_completed': 0,
    'email_captured': 0,
    'pdf_downloaded': 0
}

# Log to file or simple database
def log_event(event_name, metadata={}):
    timestamp = datetime.now()
    write_to_log({
        'event': event_name,
        'timestamp': timestamp,
        'metadata': metadata
    })
```

Track conversion funnel:
1. Landing page views → Chart calculated (free)
2. Chart calculated (free) → Paywall shown
3. Paywall shown → Checkout started
4. Checkout started → Payment completed
5. Payment completed → PDF downloaded

**Goal: Optimize worst-performing step**

## EDGE CASES TO HANDLE

### Payment Failures
- Stripe checkout fails → User returns to site
- Show: "Payment failed. Please try again."
- Don't regenerate reading (cached)
- Allow retry without re-entering birth data

### Subscription Cancellations
- User cancels subscription mid-month
- Access continues until period end
- Stripe webhook handles this automatically
- After expiry: Revert to free tier

### Refund Requests
- 30-day money-back guarantee
- Process via Stripe dashboard manually
- Revoke access token on refund
- Track refund rate (goal: <5%)

### Multiple Charts
- Free users: Can calculate different charts, but each limited
- Paid one-time: Access token tied to SPECIFIC chart
- Paid subscription: Can calculate unlimited different charts

### Sharing/Abuse
- One-time purchase tokens: Not transferable (tied to payment email)
- If user shares token → It works, but you still got paid
- If abuse detected (token used 1000x) → Revoke and investigate
- Not worth heavy DRM for $10 product

## SUCCESS METRICS (Week 1-4)

### Week 1 Goals:
- [x] Payment button live
- [x] Stripe processing works (test mode)
- [x] Paywall shows after free content
- [x] PDF export functional
- [ ] Track: 10+ free readings generated

### Week 2 Goals:
- [ ] Switch Stripe to live mode
- [ ] First paying customer
- [x] Email capture working
- [ ] Track: 50+ free readings, 1-5 paid conversions

### Week 3 Goals:
- [ ] Reddit post live + driving traffic
- [ ] Email drip sequence sending
- [ ] Track: 200+ free readings, 10-20 paid conversions

### Week 4 Goals:
- [ ] Testimonials collected and displayed
- [ ] A/B test pricing ($4.99 vs $9.99 vs $14.99)
- [ ] Track: 500+ free readings, 40+ paid conversions
- [ ] **Revenue: $400+**

## IMPLEMENTATION PRIORITY QUEUE

**DO FIRST (Weekend 1):**
1. Stripe account setup + test mode
2. Create checkout endpoints (one-time + subscription)
3. Modify reading generation to check access tokens
4. Add paywall modal to frontend
5. Test end-to-end: Free reading → Paywall → Checkout → Success → Full reading

**DO NEXT (Week 1):**
6. Email capture modal + SendGrid integration
7. PDF generation + download endpoint
8. Cache implementation (Redis or file-based)
9. Rate limiting (IP-based)
10. Switch Stripe to live mode

**DO LATER (Week 2+):**
11. Email drip sequence (Day 3, Day 7)
12. Analytics dashboard
13. A/B testing framework
14. Testimonials page
15. Referral program ("Share for 20% off")

## TECHNOLOGY DECISIONS

### Caching Layer
**Option 1: Redis** (recommended if deploying to server)
- Fast, battle-tested
- Easy to expire keys
- Heroku/Railway/Render all support Redis

**Option 2: File-based cache** (fine for MVP)
```python
import hashlib
import json
import os
from datetime import datetime, timedelta

CACHE_DIR = '/tmp/chart_cache'

def get_from_cache(cache_key):
    filepath = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if not os.path.exists(filepath):
        return None
    
    with open(filepath) as f:
        data = json.load(f)
    
    # Check expiry
    if datetime.fromisoformat(data['expires']) < datetime.now():
        os.remove(filepath)
        return None
    
    return data['reading']

def set_cache(cache_key, reading, expire_seconds=2592000):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filepath = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    data = {
        'reading': reading,
        'expires': (datetime.now() + timedelta(seconds=expire_seconds)).isoformat()
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f)
```

### Session Management
**No user accounts needed yet.** Use stateless tokens:

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('JWT_SECRET')

def create_access_token(chart_hash, tier, expires_days=30):
    payload = {
        'chart_hash': chart_hash,
        'tier': tier,
        'exp': datetime.utcnow() + timedelta(days=expires_days)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### Payment Processing
**Use Stripe Checkout** (not custom payment form):
- Stripe hosts the payment page (you don't handle card data)
- Automatic PCI compliance
- Built-in fraud detection
- Webhook for payment confirmation

```python
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@app.post("/api/create-checkout")
def create_checkout(request: CheckoutRequest):
    if request.tier == 'onetime':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Full Natal Chart Reading'},
                    'unit_amount': 999,  # $9.99 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.success_url + f'?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.cancel_url,
            metadata={'chart_hash': request.chart_data['hash']}
        )
    else:  # subscription
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_XXXXX',  # Create price in Stripe dashboard
            }],
            mode='subscription',
            success_url=request.success_url + f'?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.cancel_url,
        )
    
    return {'checkout_url': session.url}

@app.post("/api/stripe-webhook")
def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    event = stripe.Webhook.construct_event(
        payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
    )
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        chart_hash = session['metadata']['chart_hash']
        
        # Generate access token
        token = create_access_token(chart_hash, 'paid')
        
        # Store token (database or cache)
        store_token(chart_hash, token)
        
        # Send confirmation email
        send_confirmation_email(session['customer_email'], token, chart_hash)
    
    return {'status': 'success'}
```

## DEPLOYMENT CONSIDERATIONS

### Current Setup (GitHub Pages)
- Static frontend only
- Can't process payments or run Python backend
- **Need to deploy backend separately**

### Recommended Deployment:
**Option 1: Railway.app** (easiest)
- Deploy FastAPI backend in <5 minutes
- Built-in PostgreSQL + Redis
- Auto-scaling
- Free tier: 500 hours/month (enough for MVP)

**Option 2: Render.com**
- Similar to Railway
- Generous free tier
- Easy Stripe webhook setup

**Option 3: Heroku** (most established)
- Reliable but more expensive
- Free tier ended, starts at $7/month

### Environment Variables Needed:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
GEMINI_API_KEY=...
JWT_SECRET=<random-string>
SENDGRID_API_KEY=...
DATABASE_URL=postgresql://...  (if using database)
REDIS_URL=redis://...  (if using Redis)
```

## TESTING CHECKLIST

### Before Launch:
- [ ] Test free reading generation (verify only sections 1-2 show)
- [ ] Test paywall modal appears correctly
- [ ] Test Stripe checkout (test mode) - one-time purchase
- [ ] Test Stripe checkout (test mode) - subscription
- [ ] Test webhook receives payment confirmation
- [ ] Test access token generation on payment
- [ ] Test full reading generation with valid token
- [ ] Test PDF download with valid token
- [ ] Test email capture and confirmation email
- [ ] Test rate limiting (try generating 4 readings quickly)
- [ ] Test cache (same birth data should hit cache)
- [ ] Mobile responsive check (paywall modal, checkout)

### After Launch (Monitor Daily):
- [ ] Check Stripe dashboard for payments
- [ ] Check error logs for failed API calls
- [ ] Check cache hit rate (should be >50%)
- [ ] Check email delivery rate
- [ ] Check conversion funnel (free → paid %)
- [ ] Respond to support emails within 24h

## SECURITY CONSIDERATIONS

### API Key Protection:
- Never commit API keys to Git
- Use environment variables
- Rotate keys if accidentally exposed

### Rate Limiting:
- Prevent DDOS (max 100 requests/hour per IP)
- Prevent AI cost bleed (max 3 free readings per IP/day)

### Input Validation:
- Validate birth dates (1900-2100)
- Validate coordinates (lat: -90 to 90, lon: -180 to 180)
- Sanitize city names (prevent SQL injection even though you use JSON)

### Payment Security:
- Use Stripe's hosted checkout (never store card details)
- Verify webhook signatures (prevent fake payment events)
- Log all payment events for audit trail

## SUPPORT & DOCUMENTATION

### User-Facing FAQ:
- "What's included in the free reading?"
- "What's the difference between one-time and subscription?"
- "Can I get a refund?" (Yes, 30-day guarantee)
- "How accurate is this?" (Based on traditional astrology techniques)
- "Do you store my birth data?" (Only temporarily for calculation)

### Error Messages:
- Payment failed → "Payment could not be processed. Please try again or contact support@codexcaelestis.com"
- Rate limit → "You've reached the free tier limit. Upgrade for unlimited readings."
- Invalid birth data → "Please check your birth date and location."

## LAUNCH COMMUNICATION PLAN

### Reddit Post Template:
```
Title: "I rebuilt traditional astrology from 492 historical sources - 
here's what it found in my chart [OC]"

Body:
I spent 6 months building a rule-based astrology engine using only
pre-modern sources (Ptolemy, Lilly, Valens, etc.). No modern psychology,
just pure traditional techniques with source citations.

[Screenshot of YOUR reading - the impressive parts]

The system calculates:
- Classical temperament (humoral theory)
- Almuten Figuris (soul guardian)
- Zodiacal Releasing (life chapters)
- Firdaria + Profections (timing)
- Medical astrology (melothesia)

I'm curious if this resonates with other traditional astrology folks.
The first section is free at [yoursite.com] if you want to try it.

[Be genuine, not salesy. Let people ask questions.]
```

### Landing Page Copy:
```
Traditional Astrology. Rebuilt from Primary Sources.

Get a forensic-grade natal chart reading based on 492 historical texts.
No modern psychology. No vague platitudes. Just pure traditional technique.

[See Free Sample] [Get Full Reading - $9.99]

✓ Source-cited delineations (Ptolemy, Lilly, Bonatti)
✓ Classical temperament & humoral analysis
✓ Life timing techniques (Profections, Firdaria, Zodiacal Releasing)
✓ Medical astrology with anatomical governance
✓ 3,000+ word personalized analysis

[Testimonials]
[Example reading sections]
[FAQ]
```

## FINAL SANITY CHECKS

### Before you start coding:
1. Do you have a Stripe account? (Create one - 10 min)
2. Do you have $20 to test real payments? (Need to verify it works)
3. Can you deploy the backend somewhere? (Railway/Render)
4. Do you have time to respond to support emails? (Expect 5-10/week)

### Red flags that would indicate "don't launch yet":
- Backend isn't stable (crashes, slow)
- AI readings are incoherent or factually wrong
- You can't explain what the product does in one sentence
- You're not willing to give refunds

### Green lights that mean "ship it now":
- ✓ You've shown 5 people and 3+ said "I'd pay for this"
- ✓ The free reading is compelling enough to want more
- ✓ You can process a test payment end-to-end
- ✓ You have 10 hours to monitor the launch

## YOUR SPECIFIC IMPLEMENTATION TASKS

Based on your codebase (FastAPI backend, JSON rules, Gemini AI), here's what YOU need to build:

### 1. Modify `/api/calculate` endpoint:
```python
# Current: Always generates full reading
# New: Check for access_token parameter
# If no token or invalid → Generate sections 1-2 only
# If valid token → Generate all 5 sections
# Return tier info in response
```

### 2. Create new endpoints:
```python
POST /api/create-checkout  # Create Stripe session
POST /api/stripe-webhook   # Handle payment confirmations
POST /api/capture-email    # Store email + send confirmation
GET /api/download-pdf      # Generate and return PDF
GET /api/verify-token      # Check if token is valid (for frontend)
```

### 3. Add to frontend (index.html or advanced.html):
```javascript
// After reading renders:
if (response.tier === 'free') {
    showPaywallModal();
}

function showPaywallModal() {
    // Display modal with pricing options
    // On click: Call /api/create-checkout
    // Redirect to Stripe checkout URL
}

// On success page:
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id');
// Exchange session_id for access_token
// Re-run calculation with access_token
// Show full reading
```

### 4. Add caching:
```python
# In chart_calculator.py or equivalent
# Before calling Gemini API:
cache_key = hashlib.md5(f"{date}{time}{location}{tier}".encode()).hexdigest()
cached = get_from_cache(cache_key)
if cached:
    return cached

# After generating reading:
set_cache(cache_key, reading, expire=2592000)
```

### 5. Add rate limiting:
```python
# In api.py middleware or decorator
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/calculate")
@limiter.limit("3/day")  # Free tier limit
async def calculate(request: Request, ...):
    # Check if user has paid access token
    # If yes: Skip rate limit
    # If no: Enforce limit
```

## TIMELINE ESTIMATE

**Weekend 1 (8-12 hours):**
- Stripe integration
- Payment endpoints
- Paywall UI
- Test mode end-to-end

**Week 1 (5-10 hours):**
- Email capture
- PDF generation
- Caching implementation
- Switch to live mode

**Week 2 (5 hours):**
- Reddit post
- Monitor and respond
- Fix bugs
- Add testimonials

**Week 3-4 (5 hours):**
- Optimize conversion
- A/B test pricing
- Scale what works

**Total: 25-30 hours to launch + $400/month**

## QUESTIONS TO ANSWER BEFORE STARTING

1. **Where will you deploy the backend?**
   - Railway? Render? Heroku? Your own server?

2. **How will users access paid readings?**
   - URL with token? Account login? Email link?
   - Recommendation: URL with token (simplest, no accounts needed)

3. **What happens after 30 days for one-time purchases?**
   - Token expires, must repurchase
   - Token stays valid forever
   - Recommendation: 30-day expiry, then offer "refresh for $4.99"

4. **Do you want to offer trials/discounts?**
   - First 50 users: 50% off ($4.99 instead of $9.99)
   - Email subscribers: 20% off
   - Recommendation: Yes, launch discount to build momentum

5. **Who handles support emails?**
   - You, manually (fine for <100 customers)
   - Recommendation: Create support@codexcaelestis.com, check daily

## SUCCESS CRITERIA

**You know this is working when:**
- ✅ 10+ people voluntarily enter their credit card
- ✅ 50%+ of paying customers say "this is accurate"
- ✅ <5% refund rate
- ✅ You make $400+ in month 1
- ✅ You want to keep building it

**You know this isn't working when:**
- ❌ Nobody clicks "unlock reading" button
- ❌ People pay but immediately request refunds
- ❌ You get angry emails about inaccuracy
- ❌ You make <$50 in month 1
- ❌ It feels like a chore, not exciting

If it's working: Scale up (more features, more marketing, hire help)
If it's not: Pivot or quit (don't waste 6 more months)

## GO LAUNCH

You have everything you need. The product is good. The market exists. 
The only thing left is execution.

Start with Stripe integration (2 hours), add the paywall (1 hour), 
and post on Reddit (30 min). That's 3.5 hours to find out if this can work.

Stop planning. Start shipping. You'll know within 48 hours if people will pay.

Good luck. 🚀
```