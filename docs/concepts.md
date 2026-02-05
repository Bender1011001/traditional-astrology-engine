# Core Concepts & Methodology

Codex Caelestis is a **rule-based** system, treating astrological judgment as a structured, auditable process. This page outlines the philosophical and technical foundations of the engine.

## Why This Approach?

Modern astrology often relies on intuitive synthesis or psychological archetypes. While valuable, this approach lacks the reproducibility required for forensic analysis. Codex Caelestis prioritizes:

1.  **Source-First Governance**: Every algorithm is tied to a specific textual source (e.g., Ptolemy's *Tetrabiblos*, Valens' *Anthology*).
2.  **Deterministic Logic**: The same inputs always produce the same outputs. There is no "AI hallucination" in the calculation layer.
3.  **Hierarchical Causation**: Mundane factors (eclipses, ingress charts) can override natal promises, reflecting traditional doctrine.

## Key Techniques

### 1. Temperament Analysis
We calculate the Native's humoral balance (Choleric, Melancholic, Sanguine, Phlegmatic) using the method of **William Lilly** and **John Gadbury**.
*   **Inputs**: Ascendant Sign, Moon's Sign/Phase, Lord of the Geniture, Planets in the First House.
*   **Weighted Scoring**: Each factor contributes to Hot/Cold/Wet/Dry scores.

### 2. Almuten Figuris (Soul Guardian)
The "Ruler of the Chart" is determined using the 12-point scoring system of **Ibn Ezra**.
*   **Candidates**: Planets differntiated by 5 levels of dignity at 5 key hylegical points (Sun, Moon, Ascendant, Lot of Fortune, Syzygy).
*   **Winner**: Information is aggregated to find the planet with the most authority over the life.

### 3. Kakosis (Maltreatment)
A rigorous audit of planetary condition based on **Bonatti's 146 Considerations**.
*   **Besiegement**: Being trapped between two malefics (Mars/Saturn) by body or ray.
*   **Combustion**: Proximity to the Sun (within 8.5 degrees).
*   **Void of Course**: Lack of applying aspects before leaving the sign.

## Tradition vs. Modernity

| Feature | Codex Caelestis (Traditional) | Modern Psychological |
| :--- | :--- | :--- |
| **Philosophy** | Deterministic, External, Fate-oriented | Archetypal, Internal, Choice-oriented |
| **Primary Technique** | Dignity, Sect, House Rulership | Aspects, Signs, Outer Planets |
| **Planets Used** | 7 Visible Planets (Septener) | 10+ Planets (Uranus, Neptune, Pluto) |
| **House System** | Whole Sign (Principal) | Placidus / Quadrant |
| **Outcome Focus** | Concrete Events | Personality Drives |
