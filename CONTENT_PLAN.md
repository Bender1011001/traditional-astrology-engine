# Content Strategy: The Codex Caelestis Articles
**Goal**: Drive traffic by "breaking open" the Binder. Demystify the "Forensic" approach and contrast it with modern pop-astrology.

## Series 1: The Physics of Fate (Philosophy & History)
**Hook**: "Why Ancient Kings Hired Bodyguards for the Stars."
**Source Material**: Binder Part 1 (Hierarchies of Causation) & Part 3 (Mesopotamian Substitute King).
- **Article 1: The Hierarchy of Causation.** 
    *   *Concept*: Universal Fate (War, Plague, Elections) > Particular Fate (Your Chart). Why "good vibes" can't stop a "bad eclipse".
- **Article 2: The Substitute King (Šar Pūḫi).** 
    *   *Concept*: Fate as a legal transaction. How Babylonian priests "tricked" the gods by dressing a peasant as the King during an eclipse, then executing the peasant to "pay" the debt.
- **Article 3: The "Omen" vs. The "Influence".**
    *   *Concept*: Stars don't *cause* events like billiard balls; they *signify* them like a clock face.

## Series 2: The Architecture of Sovereignty (Technical Delineation)
**Hook**: "You are not your Sun Sign. You are a Committee."
**Source Material**: Binder Part 8 Extended (Phase 2, 3, 4).
- **Article 4: The Doctrine of Sect (Team Day vs. Team Night).**
    *   *Concept*: Why Mars is constructive for some (Night births) and destructive for others (Day births).
- **Article 5: Essential Dignity (The Cosmic Credit Score).**
    *   *Concept*: A planet in Domicile is a homeowner. A planet in Exile is homeless. Why "weak" planets resort to crime (maleficence).
- **Article 6: The Almuten Figuris (The Captain of the Soul).**
    *   *Concept*: Ibn Ezra's algorithm to find the *one* planet that actually runs your life. It might be that quiet Mercury in the 12th house.

## Series 3: The Mechanics of Time (Predictive)
**Hook**: "The Landlord of Your Year."
**Source Material**: Binder Part 5 (Chronocrators, Profections).
- **Article 7: Annual Profections.**
    *   *Concept*: You don't live your whole chart at once. You live it one House at a time. The "Time Lord" logic.
- **Article 8: The Firdaria (The Chapters of Life).**
    *   *Concept*: Long-term planetary periods. Why your life changed drastically at age 10 (Moon period ends, Mercury begins) or 40.
- **Article 9: Zodiacal Releasing (The Loosing of the Bond).**
    *   *Concept*: Timing career peaks. The "Fore-shadowing" period.

## Series 4: The Physics of Illness (Medical)
**Hook**: "Why Surgeons Don't Cut on the Full Moon."
**Source Material**: Binder Part 6 (Medical Astrology).
- **Article 10: Zodiacal Melothesia.**
    *   *Concept*: The body as a microcosm. Aries = Head, Pisces = Feet.
- **Article 11: The Decumbiture Chart.**
    *   *Concept*: Casting a chart for the *moment you fell ill* to predict the outcome.
- **Article 12: Critical Days.**
    *   *Concept*: The Moon's 7-day hard aspect cycle as the rhythm of crisis and recovery.

## Series 5: The "Seven Maltreatments" (Forensic Audit)
**Hook**: "Is your Planet being Mugged?"
**Source Material**: Binder Part (The 7 Conditions of Kakosis).
- **Article 13: Overcoming (Kathuperteresis).**
    *   *Concept*: Why a square from the 10th house is a "dominant" strike.
- **Article 14: Besiegement & Enclosure.**
    *   *Concept*: Being trapped between Mars and Saturn. "Between a rock and a hard place" literally.
- **Article 15: Striking with a Ray.**
    *   *Concept*: Specific angular targeting.

---

# Code Audit Report: Missing Functionality
*Items found in Binder but missing or incomplete in current `src/engine`.*

### 1. Maltreatment Conditions (Kakosis)
The Binder lists 7 specific "Maltreatments". We are currently missing logic for:
- [ ] **Striking with a Ray (Aktinobolia)**: Distinct from simple aspect; involves specific angular logic often mentioned in Valens.
- [ ] **Overcoming (Kathuperteresis)**: We check standard squares, but we need a specific flag for "Right-side" vs "Left-side" dominance (10th sign relative to planet).
- [ ] **Adherence (Kollesis)**: We need to ensure looking at *applying* conjunctions specifically within restricted orbs.

### 2. Medical Modules
- [ ] **Decumbiture Calculations**: We have no module to input a "Date of Illness" separate from "Date of Birth".
- [ ] **Critical Days Calculator**: No logic to project the Moon's future hard aspects (7, 14, 21 days) from a specific date.

### 3. Predictive Nuance
- [ ] **Monthly Profection "Continuous" Count**: We implement the "Saltatory" (jump) count. We should check if "Continuous" (1 sign per 2.5 days approx?) is needed as an option.

### 4. Almuten Nuance
- [ ] **Compound Almuten**: The Almuten we calculate is likely the "Almuten Figuris" (chart ruler). Hyleg/Alcocoden logic appears to be implemented in `hyleg.py`, but we should ensure the interpretation layer correctly prioritizes the Alcocoden for longevity.

**Recommendation**: focusing on Series 1 & 2 for content first, while we implement the "Maltreatment" (Kakosis) logic in the backend to ensure the "Forensic Audit" product matches the marketing claims.
