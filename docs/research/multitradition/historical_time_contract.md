# Shared historical birth-time and calendar contract

Status: implementation specification, not yet implemented  
Updated: 2026-07-31

## Why this is a release blocker

All proposed engines start from the same human input, but they do not necessarily start their day, month, year, or astronomical reckoning at the same instant. A single normalized UTC timestamp is not enough. The platform must preserve the reported civil statement and produce one or more explicitly sourced time candidates for each tradition.

This is especially important before standardized time zones, near daylight-saving transitions, near midnight or Zi hour, near solar terms, for lunar-calendar dates, and in ancient epochs where Earth-rotation uncertainty moves apparent phenomena in longitude.

## Authoritative limitations

- IANA's time-zone database is designed primarily around clocks that agree after 1970. It includes pre-1970 transitions, but its own theory document says those data are incomplete, sometimes unreliable, and not authoritative for all historical civil time.
- IANA does not encode uncertainty. The application must add it.
- NASA's historical Delta-T material explains that converting uniform ephemeris time to Earth-rotation-based Universal Time becomes increasingly uncertain in the past. Around 400 BCE, the cited uncertainty is on the order of several minutes and roughly two degrees of longitude; ancient eclipse locality cannot be treated as exact.
- Swiss Ephemeris distinguishes UT from ET/TT calculations, exposes Delta-T functions, and requires an explicit Julian-versus-Gregorian calendar flag for calendar conversion.
- The US Naval Observatory demonstrates that the 1582 Gregorian reform contains a civil-date gap but no discontinuity in Julian Date. Actual local adoption dates varied by jurisdiction and must not be replaced globally with the papal 1582 date.

Sources:

- [IANA time-zone theory and accuracy limits](https://data.iana.org/time-zones/theory.html)
- [NASA historical Delta T](https://eclipse.gsfc.nasa.gov/SEcat5/deltat.html)
- [NASA eclipse-path uncertainty from Earth rotation](https://eclipse.gsfc.nasa.gov/SEhelp/rotation.html)
- [Swiss Ephemeris date/time and Delta-T API](https://www.astro.com/ftp/swisseph/doc/swephprg.2.10.htm)
- [USNO Julian Date converter and 1582 example](https://aa.usno.navy.mil/data/JulianDate)

## Immutable reported input

The database must retain what the user said, not only a converted timestamp.

```json
{
  "reported_date": "YYYY-MM-DD or structured historical date",
  "reported_time": "HH:MM:SS or null",
  "reported_time_precision": "second|minute|quarter_hour|hour|part_of_day|unknown",
  "reported_calendar_label": "gregorian|julian|local_named_calendar|unknown",
  "reported_place_text": "verbatim place",
  "reported_time_qualifier": "exact|approximate|family_record|rectified|unknown",
  "source_note": "optional user provenance",
  "input_locale": "BCP-47 tag"
}
```

Do not overwrite this object after geocoding, timezone resolution, calendar conversion, or rectification.

## Resolved place

```json
{
  "place_id": "stable internal ID",
  "display_name": "resolved historical/modern label",
  "latitude_deg": 0.0,
  "longitude_deg_east": 0.0,
  "coordinate_uncertainty_km": 0.0,
  "elevation_m": null,
  "jurisdiction_at_date": null,
  "geocoder_provider": "name and dataset version",
  "resolution_method": "user_coordinates|gazetteer|manual_review",
  "evidence": []
}
```

Longitude is always degrees east in the canonical layer. Adapters may convert sign conventions only at their boundary and must test that conversion.

## Time candidates, not one asserted instant

```json
{
  "candidate_id": "timecand-...",
  "local_datetime_interpretation": "ISO-like proleptic representation",
  "calendar_system": "named and versioned",
  "calendar_adoption_policy": "jurisdictional|proleptic|source_specific",
  "utc_offset_seconds": null,
  "timezone_id": null,
  "timezone_database_version": null,
  "ut1_jd": null,
  "tt_jd": null,
  "delta_t_seconds": null,
  "delta_t_uncertainty_seconds": null,
  "earliest_ut1_jd": null,
  "latest_ut1_jd": null,
  "confidence": "high|medium|low|indeterminate",
  "basis": [],
  "warnings": []
}
```

A modern unambiguous timestamp may yield one high-confidence candidate. A skipped/repeated DST time, local-mean-time record, unknown time, historical calendar ambiguity, or ancient date yields multiple candidates or an interval.

## Required time layers

Do not use one `datetime` object to stand for all of these:

| Layer | Purpose |
|---|---|
| reported wall time | preserve the human record |
| legal/civil time | offset and clock rules applicable to the place/date |
| local mean solar time | longitude correction from the relevant meridian |
| local apparent solar time | mean solar time plus equation of time, when a tradition explicitly requires it |
| UT1 | Earth-rotation angle and horizon phenomena |
| UTC | modern civil interchange after its historical applicability |
| TT/ET | ephemeris calculations |
| tradition day index | boundary-specific ritual/astrological day |

The report must say which layer each calculation uses.

## Calendar policy

Each candidate has a named calendar converter and adoption policy.

- **Jurisdictional civil mode** uses the calendar legally/local-historically in force where evidence exists.
- **Source-specific mode** follows the calendar assumed by a source corpus or worked example.
- **Proleptic mode** is allowed only when clearly labelled and never silently substitutes for historical civil dating.
- BCE years use astronomical year numbering internally (`1 BCE = 0`) while the UI retains human-era labels.
- Invalid or skipped civil dates are rejected or represented as an explicit ambiguity; they are not silently normalized.
- Lunisolar calendars preserve leap/intercalary month identity, day start, observational/computed status, and conversion provenance.

## Tradition boundary adapters

The shared contract supplies candidate instants and astronomical facts. Each tradition adapter chooses boundaries under a versioned convention pack.

Examples:

- Western: civil birth instant, house-system/horizon calculation, historical calendar policy.
- Jyotisha: sunrise/day convention, tithi/nakshatra transitions, sidereal-mode and ayanamsha version.
- BaZi: year/month solar-term boundaries, day rollover, Zi hour, civil versus solar time, luck commencement.
- Tibetan: calendrical school, repeated/skipped day and month handling.
- Maya: correlation constant, Long Count/Calendar Round conversion, day-start convention if relevant to the selected source.
- Babylonian: Babylonian calendar/intercalation, sunset/day reckoning where source-specific, Delta-T interval for ancient horizon/eclipsing phenomena.
- Islamicate/Persian: local horizon/time, calendar conversion, source-specific day start and astronomical tables.

No adapter may mutate the shared input or hide the convention ID.

## Boundary fan-out

If uncertainty crosses a chart-changing boundary, calculate every materially distinct result.

```text
reported birth statement
  -> one or more time candidates / interval
  -> enumerate relevant tradition boundaries
  -> partition interval at every crossed boundary
  -> calculate one chart fact set per partition
  -> deduplicate identical fact sets
  -> label stable facts and variant facts
  -> suppress judgments whose predicates are not stable, or show alternatives
```

Examples of material boundaries include Ascendant/house-cusp changes, sign/nakshatra changes, sunrise, tithi, solar terms, pillar rollover, lunar-day changes, and eclipse/visibility contact.

## Cache identity

The cache key must include at least:

- reported input hash;
- resolved place/version;
- every time candidate or interval;
- calendar converter and adoption policy;
- IANA/tzdata version where used;
- Delta-T model/version;
- ephemeris/version/files;
- atmospheric/refraction policy for apparent phenomena;
- tradition, school, source pack, and convention versions.

Changing any of these invalidates a result. A city name plus birth date is not a valid calculation cache key.

## Golden boundary tests

The validation suite must include:

1. both sides of a modern DST gap and repeated hour;
2. a pre-1970 locality where historical offset evidence is strong;
3. a locality where IANA pre-1970 history is explicitly insufficient, yielding low confidence;
4. 4 October / 15 October 1582 under papal-reform policy, plus jurisdictions with later adoption;
5. BCE year conversion across astronomical year zero;
6. longitude sign tests east and west of Greenwich;
7. UT versus TT calculations with a locked Delta-T value;
8. ancient Delta-T lower/central/upper values that move a horizon event;
9. unknown-time full-day interval crossing Ascendant, nakshatra, tithi, pillar, and lunar-day boundaries;
10. BaZi births around Li Chun, a month `jie`, midnight, and 23:00 Zi hour;
11. Jyotisha birth around sunrise and a nakshatra/tithi boundary;
12. Tibetan repeated/skipped calendar days;
13. Babylonian sunset/calendar and eclipse-watch boundaries;
14. a place-resolution uncertainty large enough to change local solar time.

For every vector, store expected facts, allowed uncertainty, source, and independent recomputation result.

## Failure policy

- Never invent a historical offset.
- Never present IANA data as authoritative for a poorly documented historical locality.
- Never collapse an ambiguous local time to the earlier or later offset without telling the user.
- Never treat `UTC` as the name of a pre-1960 civil standard.
- Never report horizon-sensitive ancient results more precisely than the Delta-T/place uncertainty allows.
- Never let a language model choose a calendar, offset, or boundary.
- When evidence is insufficient, return a bounded set/interval and explain exactly which readings remain stable.

## Implementation gate

Before any non-Western engine reaches consumer output, the project must implement this contract as a shared service and pass the golden boundary suite. Tradition engines should consume immutable resolved candidates and return fact variants; they should not each reinvent timezone and calendar logic.
