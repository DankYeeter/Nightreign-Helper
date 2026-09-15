# T-236 — developer, 14.09.2026: nichts reproduziert, nichts geaendert

Kontraktblock in der Antwort (STATUS: erledigt; Repo unveraendert). Suite
`pytest -n auto`: 1522 passed / 10 skipped (135 s) — Abweichung zu 1531/9:
`3110b4e` loeschte 9 Mutationen, `test_differential_track.py:478` skippt
seither mit leerer Parametermenge.

| Befund | Stand am Fenster (1536 px logisch, fusion, PrintWindow) | Fix-Commit |
|---|---|---|
| QA-140 | 11/11 Koepfe ganz | `6c5d895`, `49811a8` |
| DR-014 | `Effect` 353 px, `What it does` 287 px, breiteste Spalte; Rest per Tooltip (AK-77) | `0f270d8` |
| DR-013 | 10/10 Karten, Raster 4+4+2, kein H-Scroll | `d5b2035` |
| DR-015 | Deep of Night in `QScrollArea`, Fenster-Minimum 588 px logisch | `82cb18a` |
| QA-128 Pkt 4-10 | Bezugsgroessen genannt oder A7-Satz | `555d749`, `6f66267`, `d4ce7c7` |

Befund fuer den Director: QA-128 Punkt 10 (`eventstab.py:37`
`UNKNOWN_REFERENCE`) hat keinen Waechter. Bilder: Scratchpad `T-236/shots/`
(7 PNG). `DESIGN_REVIEW.md` DR-013/014/015 zieht der `ui-ux-designer` nach.
