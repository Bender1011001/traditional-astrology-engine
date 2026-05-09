Swiss Ephemeris runtime data
============================

`sefstars.txt` is the fixed-star catalogue required by Swiss Ephemeris fixed-star
functions such as `swe.fixstar2_ut()`.

Source: https://github.com/aloistr/swisseph/blob/master/ephe/sefstars.txt
Downloaded: 2026-05-08
SHA256: 18b0dcafbe5b7240773daba2c038a325f5b3fc4163f61e0a7f4e92abd4f517c6

Keep this file in the container ephemeris path. The Cloud Run Docker image sets
`SE_EPHE_PATH=/app/src/ephe:/usr/share/swisseph:/usr/local/share/swisseph`.
