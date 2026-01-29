=== HIGH PRIORITY (Core Functionality Gaps) ===

1. EXPORT & PERSISTENCE
   - Add PDF export for professional reports (use reportlab or weasyprint)
   - CSV export for research datasets
   - Chart caching option (even session-based) to reduce redundant calculations
   - "Save Chart" feature for registered users

2. PERFORMANCE OPTIMIZATION
   - Implement ephemeris caching for date ranges (Swiss Ephemeris is fast, but batch 
     operations would benefit)
   - Redis/memcached layer for frequently requested charts
   - Async task queue (Celery) for batch rectification/electional scans

3. USER ACCOUNTS & HISTORY
   - Optional user registration to save chart library
   - Chart comparison history (track revisions for rectification work)
   - Personal notes/annotations on charts

4. VISUALIZATION
   - SVG chart wheel generator (even basic bi-wheel for synastry)
   - Timeline visualization for profections/firdaria/releasing overlap
   - Aspect grid display
   - Dignity table visualization (color-coded strengths)

5. DOCUMENTATION
   - API documentation (Swagger/OpenAPI auto-generated from FastAPI)
   - Tutorial series: "Your first natal chart" → "Understanding the rule ledger"
   - Video walkthrough of each module
   - Case study library with historical examples

=== MEDIUM PRIORITY (Enhanced Functionality) ===

6. CALCULATION ENHANCEMENTS
   - Primary directions: Add planet-to-planet (you noted this limitation)
   - Solar arc directions (mentioned in UI but implementation unclear)
   - Continuous profections option alongside saltatory
   - Minor aspects option (quincunx, semi-sextile) as opt-in for research
   - Custom orb configuration for research purposes

7. MEDICAL ASTROLOGY DEPTH
   - Decumbiture chart module (separate from natal)
   - Critical days calculator (Galen's 7/14/21 + Hippocratic crisis)
   - Herbal correspondences (Culpeper integration)
   - Full humoral analysis with dietary recommendations
   - Medical source citations prominent in surgery constraints

8. TIMING TOOLS
   - Transit search: "When does Mars conjunct my Sun in next 5 years?"
   - Aspect perfection exact dates/times
   - Combined time-lord view (when multiple techniques agree = high confidence)
   - Historical event correlation tool (test techniques against known events)

9. ELECTIONAL IMPROVEMENTS
   - Show top 5 windows ranked by quality (not just single best)
   - Constraint customization (what's negotiable vs. fixed)
   - Save electional searches with results
   - Electional chart comparison tool

10. HORARY ENHANCEMENTS
    - Testimonies checklist display (perfection, prohibition, refranation)
    - Strictures against judgment explicit display
    - Save questions + outcomes for personal learning database
    - Statistical tracking of horary accuracy over time

=== LOWER PRIORITY (Polish & Reach) ===

11. UX REFINEMENTS
    - Glossary tooltips (epitasis, chronocrator, etc.)
    - Progress indicators for long calculations
    - Dark mode consistency check across all views
    - Mobile responsive optimization
    - Keyboard shortcuts for power users

12. EDUCATIONAL FEATURES
    - Interactive tutorial/wizard
    - Example chart library (Napoleon, Elizabeth I, etc.)
    - Source text excerpts linked from rules
    - "Why this rule?" explanations
    - Technique comparison guides

13. RESEARCH FEATURES
    - Batch CSV processing UI (you have backend capability)
    - Statistical aggregation across charts
    - A/B testing: compare rule sets side-by-side
    - Research mode: raw calculations only, no interpretation
    - Data export for statistical software (SPSS, R formats)

14. COMMUNITY & VALIDATION
    - Enhanced feedback: "which parts accurate?" granular rating
    - User testimonials collection
    - Forum/discussion integration
    - Academic partnership outreach (Culture and Cosmos journal)
    - Conference presentation materials

15. ADVANCED FEATURES
    - Custom rule builder for advanced users
    - Plugin system for community modules
    - Natural language query parsing ("next good time to start business")
    - Multi-language support (at least chart labels)

=== INFRASTRUCTURE & DEPLOYMENT ===

16. PRODUCTION READINESS
    - Rate limiting (you rely on Cloudflare; add app-level backup)
    - Comprehensive error logging (Sentry integration?)
    - Health check endpoint for monitoring
    - Automated backup of user data (when accounts added)
    - Load testing for concurrent users

17. SECURITY & PRIVACY
    - Privacy policy page (especially important for user accounts)
    - GDPR compliance if EU users
    - Data retention policy
    - Anonymization option for research data sharing

18. OPEN SOURCE STRATEGY
    - Choose license (AGPL for research community? MIT for permissive?)
    - Contributor guidelines document
    - Code of conduct
    - Issue templates for bug reports/feature requests
    - Clear "how to contribute" documentation

=== SPECIFIC TECHNICAL QUESTIONS ===

19. CALCULATION CLARIFICATIONS NEEDED
    - Solar arcs: Implementation status? (UI mentions it but unclear in docs)
    - Firdaria: Which tradition? (Persian? Arabic? Which author?)
    - Zodiacal Releasing: Valens only or Schmidt refinements included?
    - Muntha: Which calculation method?
    - Topocentric houses: Why included? (Very modern system)

20. RULE ENGINE SPECIFICS
    - Combustion distance: Within 8.5° (Lilly) or variable by planet?
    - Under the beams: Included separately from combustion?
    - Via Combusta: 15° Libra to 15° Scorpio traditional bounds?
    - Besiegement: Applied when malefics on both sides within X degrees?
    - Collection of light: Implemented in horary module?

21. LOT CALCULATIONS
    - How many lots total? (You mention Fortune/Spirit/Eros/Necessity/Victory/Nemesis)
    - All 97 Paulus lots? Or curated subset?
    - Lot of Marriage calculation (controversy on formula)
    - Display lots in chart wheel or table only?

22. SYNASTRY SPECIFICS
    - Which traditional synastry factors? (Dignity in partner's chart?)
    - Composite vs. Davison options?
    - Relationship timing through composite profections?
    - Compatibility scoring algorithm details?

23. WORLD/MUNDANE
    - Eclipse visibility path calculation?
    - Aries ingress for which capital city?
    - Historical great conjunctions database extent?
    - Current planetary year ruler display?

=== MARKETING & POSITIONING ===

24. AUDIENCE DEVELOPMENT
    - Beta tester recruitment from traditional astrology communities
    - Partnership with schools (Kepler College, STA, NCGR)
    - Academic research collaboration (offer free API for studies)
    - Conference presence (NORWAC, ISAR, UAC, ARHAT)

25. CONTENT STRATEGY
    - Blog: "How Codex Caelestis calculated X historical event"
    - YouTube: Chart readings demonstrating rule engine
    - Published papers on methodology
    - Case study PDFs for download

26. LICENSING & MONETIZATION
    - Free tier: Basic natal readings
    - Pro tier: All timing techniques, batch processing, exports
    - Research tier: API access, no rate limits, bulk data
    - Institutional tier: Multi-user accounts, white-label option

=== IMMEDIATE ACTIONABLE ITEMS ===

MUST DO NOW:
1. Add prominent medical disclaimer on medical modules
2. Choose and add open-source license file
3. Create CHANGELOG.md tracking rule updates
4. Document API endpoints (FastAPI auto-docs are free)
5. Add example charts (at least 3 historical figures)

SHOULD DO NEXT SPRINT:
6. PDF export (even basic text formatting)
7. Chart wheel visualization (SVG, simple design)
8. Tooltip glossary for technical terms
9. Save chart to browser localStorage as stopgap
10. Progress indicators for rectification/electional scans

NICE TO HAVE SOON:
11. User accounts with saved charts
12. Mobile responsive refinement
13. Enhanced electional: show top 5 options
14. Transit search functionality
15. Dark mode consistency audit

=== VALIDATION & TESTING REQUESTS ===

Can you provide:
- Sample output from rule_ledger for a specific judgment?
- Screenshot of "dignity_conflicts" display?
- Example of Mundane Hierarchy override in action?
- Sample forensic trace showing source attribution?
- Typical calculation time for full natal + timing analysis?

=== STRATEGIC QUESTIONS ===

POSITIONING:
- Do you want to be: Academic research tool? Professional practitioner software? 
  Educational platform? All three?
- Competition: How do you differentiate from Morinus, Delphic Oracle, 
  Solar Fire traditional module?
- Target geography: English-speaking only or multilingual ambitions?

SUSTAINABILITY:
- Personal project or seeking team/funding?
- Timeline for "1.0 release"?
- Plan for long-term maintenance as ephemeris/rule research evolves?

COMMUNITY:
- Open to outside contributors or maintaining tight control for quality?
- Willing to moderate forums/Discord if you build community features?
- Interest in academic partnerships (might require IRB approval for research)?
