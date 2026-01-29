# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-01-29

### Added
- **Astrological Glossary**: New module and UI integration for defining traditional terms.
- **CSV Export**: Researchers can now export forensic reports to localized CSV files.
- **PDF Export**: Professional-grade PDF reporting via ReportLab.
- **Historical Figures**: Added Napoleon, Elizabeth I, Queen Victoria, and Abraham Lincoln to `example_charts.json`.

### Changed
- **License**: Changed project license from Proprietary to MIT.
- **Performance Index**: Replaced simple dignity labels with a 60/40 weighted "Performance Index".
- **Rule Source Attribution**: Added granular citations (e.g., Lilly CA p115) to 15+ core astrological rules.
- **Confidence Scoring**: Refined estimator considering source consensus and traditional divergence.
- **Probabilistic Framing**: Updated AI Oracle and Daily forecasts with symbolic vs deterministic disclaimers.


## [1.1.0] - 2026-01-28

### Added
- **Medical Disclaimer**: Prominent warnings added to medical modules and API responses.
- **License**: Explicit proprietary license to reserve all rights.
- **Example Charts**: Added historical birth data for William Lilly, Marsilio Ficino, and Isaac Newton.
- **API Documentation**: Enhanced FastAPI auto-docs with detailed descriptions.
- **Comprehensive Database**: Ingested 20 JSON files covering the full spectrum of pre-1700s astrology.
- **Forensic 5-Day Forecast**: Added "Epitasis" upgrade for short-term predictive modeling.
- **Generative AI Oracle**: Integrated Gemini Flash for plain-language chart synthesis.

### Changed
- **Chronocrator Upgrade**: Refined Firdaria and Profection logic for Rank 1 precision.
- **Dignity Engine**: Updated Egyptian Terms to include Sun/Moon as per the "Missing Codex" findings.

### Fixed
- **South Node Calculation**: Now correctly derived from North Node.
- **Vitality Safety**: Added floor to Hyleg/Alcocoden years to prevent negative results.
- **Delineation Gaps**: Filled missing Moon in Pisces delineations.

## [1.0.0] - 2026-01-20

### Initial Release
- Core chart calculation engine using Swiss Ephemeris.
- Essential Dignities (Ptolemaic).
- Basic Natal Delineations.
- FastAPI Backend / Vanilla JS Frontend.
