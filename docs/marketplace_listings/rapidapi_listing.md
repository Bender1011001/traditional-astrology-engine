# RapidAPI Listing — Codex Caelestis Traditional Astrology API

## Submission Checklist

- [ ] Create account at https://rapidapi.com/provider
- [ ] "Add New API" from Provider Dashboard
- [ ] Enter all fields below
- [ ] Upload OpenAPI spec (docs/openapi_marketplace.json)
- [ ] Set pricing tiers (see below)
- [ ] Test all endpoints in-browser
- [ ] Submit for review

---

## API Name
```
Traditional Astrology API — Codex Caelestis
```

## Short Description (≤200 chars — appears in search results)
```
Swiss Ephemeris-powered traditional Western astrology API. Natal charts, synastry, firdaria, dignities, ZR longevity. Every judgment cites Lilly, Bonatti, or Ptolemy.
```

## Long Description (Markdown, appears on API page)

```markdown
## Traditional Astrology Calculation Engine

The only production-grade API for **traditional (pre-1700) Western astrology**, powered by Swiss Ephemeris at sub-arcsecond precision.

### What Makes This Different

Most astrology APIs return planetary positions. Codex Caelestis returns **judgments** — with the source text that justifies each one.

| Feature | Other APIs | Codex Caelestis |
|---------|-----------|-----------------|
| Planetary positions | ✓ | ✓ |
| Essential dignities | Sometimes | ✓ Full table |
| Source citations (Lilly/Bonatti) | ✗ | ✓ Every judgment |
| ZR Longevity L1/L2 | ✗ | ✓ |
| Loosing of the Bond | ✗ | ✓ |
| Firdaria sequence | Rarely | ✓ With dates |
| Annual profections | Rarely | ✓ |
| Traditional synastry | ✗ | ✓ |
| Bulk PDF ZIP | ✗ | ✓ (50 charts/call) |
| Birth-time rectification | ✗ | ✓ |

### Use Cases

- **Astrology apps** — embed calculations in your mobile/web app
- **Etsy natal chart sellers** — automate PDF generation from customer orders
- **Astrology educators** — programmatic chart generation for course materials
- **Practitioners** — client intake automation, report pipelines
- **Researchers** — batch chart calculations for academic studies

### House Systems Supported
Whole Sign (default) · Alchabitius · Regiomontanus · Placidus · Porphyry · Koch

### Zodiac Systems
Tropical · Sidereal (all major ayanamsas: Lahiri, Fagan-Bradley, Krishnamurti, etc.)

### Response Format
Every natal chart response includes:
- Full planetary positions with degree, sign, house, dignity, speed, and retrograde flag
- Essential dignity table (domicile, exaltation, triplicity, term, face, detriment, fall, peregrine)
- Almuten figuris with score
- Chart sect (diurnal/nocturnal)
- Complete firdaria sequence with start/end dates
- Annual profection year and lord
- ZR Longevity indicators (Hyleg, Alcoccoden, L1/L2)
- Loosing of the Bond calculation
- Plain-language synthesis paragraph
- **Source citations array** — exact rule and book reference for every judgment

### Getting Started
1. Subscribe to a plan (Practitioner or Studio)
2. Generate an API key from your dashboard
3. Pass `X-API-Key: your_key` in the request header
4. POST to `/api/v1/charts/generate` with date, time, city

**Base URL**: `https://traditional-astrology.com`
**Full docs**: https://traditional-astrology.com/documentation.html
**Support**: api-support@traditional-astrology.com
```

## Category
```
Entertainment > Horoscopes
```
*(Also tag with: Science, Data)*

## Tags (comma-separated)
```
astrology, horoscope, natal chart, birth chart, zodiac, traditional astrology, swiss ephemeris, synastry, firdaria, dignities, planets, astrological calculation
```

## Website URL
```
https://traditional-astrology.com/developer.html
```

## Terms of Use URL
```
https://traditional-astrology.com/terms.html
```

## Base URL
```
https://traditional-astrology.com
```

---

## Pricing Tiers (set in RapidAPI Dashboard)

### Tier 1: Free / Test
- **Price**: $0/month
- **Quota**: 10 requests/day
- **Purpose**: Let developers test the API before subscribing
- **Throttle**: 1 request/second

### Tier 2: Practitioner
- **Price**: $29/month
- **Quota**: 100 requests/day
- **Throttle**: 5 requests/second
- **Features**: All endpoints except bulk PDF

### Tier 3: Studio
- **Price**: $99/month
- **Quota**: Unlimited
- **Throttle**: 20 requests/second
- **Features**: All endpoints including bulk PDF (50 charts/call)

### Tier 4: Enterprise
- **Price**: Custom (contact enterprise@traditional-astrology.com)
- **Quota**: Unlimited + SLA
- **Features**: White-label, dedicated instance, priority support

---

## Endpoints to Register

Register each endpoint manually in the RapidAPI dashboard:

| Name | Method | Path | Description |
|------|--------|------|-------------|
| Generate Natal Chart | POST | /api/v1/charts/generate | Full traditional natal chart |
| Calculate Chart (full) | POST | /api/v1/charts/calculate | Chart + 5-day forecast |
| Synastry Analysis | POST | /api/v1/synastry | Compatibility between two charts |
| World Dashboard | POST | /api/v1/world | Mundane/global astrological conditions |
| Bulk PDF Generation | POST | /api/v1/charts/bulk/pdf | ZIP of up to 50 PDF reports |
| Forensic Audit | POST | /api/v1/forensic/audit | Birth-time rectification |
| Get Usage Stats | GET | /api/v1/developer/usage | Daily API call count and quota |

---

## Sample Request (paste in RapidAPI's "Test" tab)

**Endpoint**: POST /api/v1/charts/generate
**Header**: X-API-Key: (your key)
**Body**:
```json
{
  "date": "1990-03-15",
  "time": "14:32",
  "city": "London",
  "state": "England",
  "name": "Test User",
  "house_system": "W",
  "zodiac_system": "tropical"
}
```

---

## SEO Optimization (RapidAPI-specific)

1. **API name** includes "Astrology API" — this is the primary search term
2. **Short description** front-loads the differentiator (Swiss Ephemeris + citations)
3. Tags include all common search terms developers use
4. Long description table format renders well in RapidAPI's markdown engine
5. **Respond to reviews** within 24h — RapidAPI surfaces highly-reviewed APIs
6. Link back from traditional-astrology.com/developer.html to the RapidAPI listing (helps RapidAPI SEO)

---

## Other Marketplaces — Priority Order

1. **RapidAPI** (primary — 3M developers, largest audience) — do this first
2. **APILayer** (https://apilayer.com/marketplace) — quality-focused, smaller but curated
3. **Zyla API Hub** (https://zylalabs.com) — astrology niche, worth listing
4. **AWS Marketplace** (enterprise only — requires ISV program) — long-term goal
5. **Postman Public API Network** (https://www.postman.com/explore) — discovery, not monetization, but drives inbound links; upload the Postman collection from docs/postman_collection.json
6. **APIs.guru** (https://apis.guru) — directory, free listing, SEO value from backlinks
