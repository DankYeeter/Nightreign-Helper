# Stand

2026-10-12 21:30, **Zyklus 32 (T-333) autonom: Fix QA-299, dann Neubau
1.19.0; Ingame-Test des Nutzers offen**. Branch
`docs/audit-and-advisor-design` (PR #18 gemerged 23.09. 19:15 `f45c98e`;
naechster PR am Zyklusende).
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` und Sitzung Part 12
(16.-19.09.) in `docs/tasks/T-281..T-296` · Befunde `qa/findings.md`,
`security/findings.md` · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (23.09., naechste freie, Abschrift — vor Vergabe zaehlen):
T **T-333** · QA **QA-298** · SEC **SEC-053** · AK **AK-372** · AD **AD-056**
· DR **DR-047** · C **C-008** · A **A-039** · P **P-005** · NH **NH-014**
· R **R-012**.

**Zyklus 30 (T-330, 23.09. 16:40-16:45, Wiederanlauf) erledigt:**
a `700c629` Projekt-Hook NH-011 (Suite 1927 passed, 9 skipped); b
Agenten-Repo `9d0d22b` (Selbsttest 132 PASS, ungepusht); c `R-011`
P-003 **teilweise**: Relikt-Aenderungen im Snapshot, Grundwerte je
Nightfarer nicht (Kandidat ungelesene `EquipParamProtector` ueber
`CharaInitParam.equip_*`, ungeprueft); Verrechnung multiplikativ, nur
Community-belegt; Defense-Wert ohne Feld. Nebenfunde: `$istExeKommando`
weist Grep-Muster mit `|NightreignHelper.exe` ab (Textteile nicht
entfernt; Nutzer 16:46: sammeln); `bash -c "pytest ..."` zaehlt nicht
mehr (bekannt).

**T-331 (16:47-16:50, nur lesend) erledigt:** `docs/berichte/T-331-developer.md`.
Grund-Negation je Nightfarer steht in `EquipParamProtector`, nur in der
Koerperzeile (Helm/Hand/Bein 1,0) — interne Datenzeile, ingame keine
Ruestung (Nutzer 16:52: "Nightfarer haben keine Ruestung"); Garbs tragen dieselben Werte; Defense
nicht gefunden. Werte je Nightfarer verschieden (slash: Revenant 10 %,
Wylder 20 %, Guardian 28,75 %). **P-003 gestrichen (Nutzer 16:54: "wenn
nicht [dieselbe Negation], streichen wir es komplett")** — Status in
`docs/product/BACKLOG.md` beim naechsten `product-strategist`-Lauf nachtragen.

## Veroeffentlicht

| Version | Tag auf | Run | Assets | Inhalt |
|---|---|---|---|---|
| 1.13.1 | `798f808` | 35121936228 | 3 | A21 Effektfilter-Fenster, AK-312/313, A-008 Tests im Release-Lauf |
| 1.13.2 | `b0965e3` | 35267925982 | 3 | AK-314 Favorit auf gehaltenem Relikt genannt (T-288/289) |
| 1.14.0 | `ffac292` | 35427762335 | 3 | A22 Attribute ueber Startwaffe in die Schadenszahl (AD-038, AK-315/318), A23 Familien vermeiden + Allow (AD-039, AK-316/317), DR-032, QA-284/285 |
| 1.15.0 | `c536daa` | 35451242996 | 3 | A24 Unterbosse im Nightlords-Tab (AD-040..044, AK-319..326), QA-286 Red-variants-Beispielspalte, QA-288, Datenversion 15 |
| 1.16.0 | `a33e92b` | 35518272445 | 3 | A25 Schadensart im Berater (AD-045..049, AK-327..336), QA-289/290, Schadensart gemerkt |
| 1.17.0 | `28b7f1e` | 35560029819 | 3 | A26 Hit with x Damage type, Zauberzahl unkalibriert, EXTRACT_VERSION 16, Startbreite 0,9 x Bildschirm; QA-293/294 offen |
| 1.18.0 | `1ae6952` | 35633098282 | 3 | A27 Weapon art + Spell damage im Schadensblock, QA-293; QA-295 offen |

Beschreibung je Release aus `docs/release/RELEASE_BODY.md` (`body_path`,
A-023/A-024/A-037). Download: `releases/latest`.

## Stand gegen `GOAL.md` (19.09.2026, Artefakt 1.14.0)

| | | |
|---|---|---|
| A1, A2 | Audit, kritisch/hoch | erfuellt (Register; QA-237 zurueckgestellt) |
| A3-A9 | Berater, A6, A7, A8, QA am Artefakt | **erfuellt** (T-293b/T-295c am 1.14.0) |
| A10-A14 | Tabs, A11 Laie | A11 **teilweise** (power-user-Werkzeug, QA-282); Nutzer-Ingame-Tests 15.-19.09. |
| A15 | Erststart | erfuellt (clean-room T-285a) |
| A17-A21 | Bezugswaffe, Filter, Zweihand, Filterfenster | erfuellt am Artefakt |
| A22 | Attribute in die Schadenszahl | **erfuellt** (T-293b: Duchess 72 → 70, Why-Betrag; Nutzer "passt" 19.09.) |
| A23 | Familien + Allow | **erfuellt** (T-293b/T-295c; Allow immer klickbar AK-317 Nachtrag) |

## Befunde

Stand 23.09. aus den letzten Registerzeilen der Befunde dieses Zyklus: kein P1
offen. Geschlossen: QA-004, QA-016, QA-222 (mit echter Maus nicht
nachgestellt), QA-255, QA-294. Offen: QA-282 P3 (Werkzeug), OF-54
Zauberformel (nur ingame). SEC-051, SEC-052, QA-297 geschlossen (T-332);
Triage T-332 `72aeb8a`: 89 QA + 9 SEC ohne neuen Beleg weiter offen
(letzte Registerzeile je ID).
Debt: `upx=False` (C-006); 74 Hex-Literale in Stylesheet-Texten (AK-367ff.
Massstab je Fund).

## Beim Nutzer — offen

1. **Ingame-Test mit `dist\NightreignHelper.exe` 1.19.0 (Neubau 12.10.)**
   (59 186 282 B, SHA-256 `2306C5E0…1524610B`, Bau-Commit `7347908`,
   Director gemessen 22:33; Exe nie gestartet) — Liste `docs/tasks/T-329.md`
   Abschnitt "Ingame-Test" (OF-54 Zahlen) plus Wylder/Optimize: kein
   Hammer+Great-Hammer-Paar. Danach: Freigabe → `archivist` sync-out mit Tag
   `v1.19.0` auf dem Notes-Commit nach `7347908`, PR. Befunde → Fixzyklus.

2. **Retro Zyklus 32 (12.10., Empfehlung annehmen):** NH-014 Ursache nur mit
   Tauschprobe (`_rahmen.md:56-57`, `director.md:307-309`), NH-015 offene
   Spec-Fragen als Registerzeile (`qa-engineer.md:219-220`), NH-016 je
   Teilsatz des Kriteriums ein Testfall (`templates/task.md`, `_rahmen.md:52-53`).
   Wortlaut `docs/lessons.md` "Zyklus 32".

**Erledigt laut Nutzer 23.09. 19:14:** PR #18 auf `main` gemerged durch
den Director auf ausdruecklichen Nutzerauftrag ("merge es selbst"),
Merge-Commit `f45c98e`, Checks SUCCESS. Freundestest bestanden, keine
Probleme gemeldet. A-035 erledigt: keine Beschwerden. NH-011 umgesetzt
(T-330), P-003 gestrichen (T-331), P-001/002/004 nicht freigegeben; Audit-Rest
(`QFile.link`, `AttackRating`, `Weighting`, Relikt-`caption`) nicht umsetzen.

**Streichvorschlaege BACKLOG entschieden (Nutzer 19:20):**
1. Community-reported: **nicht streichen, als Fakt fuehren, Vermerk weg** —
   Deep of Night (`deeptab.py:419`, Kommentar `:43`), Red variants
   (`depthstab.py:117` "COMMUNITY-REPORTED: ..."), World Events (blaue
   Zeilen `eventstab.py:101`, Panel `:335`), Farbe `COMMUNITY`/Kommentar
   `bosstab.py:206` pruefen.
2. Why-Zeile "depends on the armaments you carry" (`explain.py:635`):
   **bleibt** (Beispiel "Improved Attack Power with 3+ Bows Equipped").
3. A11 power-user-Nachweis: **bleibt** (automatisierter Laientest).

## Zyklus 31 (T-332, 23.09.) — Bau 1.19.0 `7fc3e43`, QA/Security/clean-room PASS; Details `docs/tasks/T-332.md`

## Zyklus 32 (T-333, autonom ab 12.10. 21:28, Budget 6 h bis 03:28)

Nutzer 21:28: "arbeite 6 stunden autonom weiter oder bis dir nichts mehr
einfaellt". Warteschlange (keine neuen Kriterien): T-333f Fix QA-299 (hoechstens
eine Waffenart-Bedingung, Nutzer 21:15, AD-036.6-Nachtrag) → QA-Retest am
Quellstand → `release-manager` build+notes 1.19.0 neu → Gate: Ingame-Test des
Nutzers, kein Tag. Ende: sync-out Branch, Gate-Protokoll; PR erst nach
Ingame-Freigabe. Bisher: Treiber `05143d2` ohne Maus/SetForegroundWindow;
Fokusraub-Ursache **Hypothese** (UIA-Kern; Tauschprobe an Nicht-Qt-Fenster
und MSAA ungemessen, Retro 22:48), Umbau ruht — Fensterlaeufe nur bei freiem
PC (Nutzer 21:05). power-user T-333b 2/2 Ziele an Exe 1.19.0. QA-298
geschlossen (kein Fehler), QA-300 P3 / QA-301 P4 → naechster Zyklus.
Ergebnis 22:50: QA-299 `59a5f03`+`6ab0c4b` PASS, Neubau `c5eaa41`, Retro
NH-014..016 vorgeschlagen (`docs/lessons.md` "Zyklus 32").

## Naechster Zyklus (offen)

- QA-300 (Why-Fenster ueberladen, zwei Why-Knoepfe, Zielwahl ohne Namen) P3,
  QA-301 (Speichern ohne Bestaetigung, Einrichtung 50 s) P4; Why-Satz
  "you favourited it, so it always counts." fuer nicht gezaehlte Art
  (`explain.py:561`) P4.
- Treiber ohne Fokusraub: erst Tauschprobe (Nicht-Qt-Fenster), dann
  MSAA/LegacyIAccessible; Scratchpad-Werkzeuge T-333c/d sind sitzungsgebunden
  (Bericht T-333 als Quelle). Nur falls freie-PC-Regel stoert.
- **BACKLOG.md:** P-003 gestrichen und Streichvorschlaege-Entscheide
  nachtragen (`product-strategist`, nicht im Zyklus einer Umsetzung).
- Hook-Grenze: Blendung nur fuer Suchbefehle; Text mit `|…exe` in
  Anfuehrungszeichen ausserhalb von Suchbefehlen wird gesperrt (Absicht).
- Bau nicht byte-reproduzierbar (T-332j: PE-Zeitstempel + unbekannte Quelle).
- Audit-Fund 1 (35 ungelesene Snapshot-Felder) beim naechsten ohnehin
  noetigen EXTRACT_VERSION-Sprung mitnehmen.

## Beschlossen, nicht beauftragt

- **A25 abgeschlossen: Release 1.16.0 (20.09. 17:05, Tag `v1.16.0` auf `a33e92b`,
  Run 35518272445). PR #18 auf `main` offen (Nutzer mergt).** Rest: eigener
  Art-Regler im Picker (AK-336) beim Nutzer; Nightfarer wird nicht gemerkt
  (Bestand, Backlog); ROLLOUT.md ohne 1.16.0-Abschnitt.
- **A26 abgeschlossen: Release 1.17.0 (21.09. 06:10, Tag `v1.17.0` auf `28b7f1e`).**
  Pruefphase `docs/tasks/T-325.md` a-n: Sicherheit PASS, DR-038 gefixt
  `eaf9ea9`, QA T-325h/j PASS, clean-room PASS (Cache-Neubau 37 s),
  power-user 6/6 (QA-293 P3 Why-Zuordnung unter Schulwahl, QA-294 P4
  Nullzelle ohne Grund — beide offen, naechster Zyklus). Suite 1878/9.
  Offen: OF-54 Zauberformel unvermessen; performance-tuner Katalysator-Scan
  113 us; Nightfarer nicht gemerkt (Backlog); ROLLOUT.md ohne 1.16/1.17;
  Auflagen-Register seit 1.13.1 nicht fortgeschrieben (compliance).
- **A27 abgeschlossen: Release 1.18.0 (21.09. 19:35, Tag `v1.18.0` auf `1ae6952`,
  kurze Kette ohne clean-room/power-user — Nutzer 19:25).** Offen: QA-294
  zurueckgestellt (Pool-Meldung), OF-54 Zauberformel unvermessen,
  performance-tuner Katalysator-Scan. PR #18 offen (Nutzer mergt).
  Werkzeugbefund: Worktree-Sitzungen ohne PowerShell — Fensterlaeufe nur im
  Hauptbaum.
- **Zyklus 28 (21.09. 21:25-21:40, T-328, kein Release):** Nightfarer wird
  gemerkt (`a0ae6b7`, Schluessel `hero`, OF-55; Suite 1894/9 um 21:34;
  developer ueberschrieb die QA-155-Tests und stellte sie in `148a0de` selbst
  wieder her). QA-295 geschlossen per AK-355-Nachtrag (Delta kein Link).
  AUFLAGEN.md "Stand 1.18.0": keine neue Auflage, A-012/023/024/037 GRUEN,
  nichts ROT. ROLLOUT.md 1.15.0-1.18.0 nachgezogen; EXTRACT_VERSION je Tag
  gemessen 12/15/15/16/16. Nebenfunde: `check_licences.py` bewacht nur
  `requirements.txt` (PyInstaller-Zeile nicht mehr); Update-Pfade 1.14→1.15
  und 1.17→1.18 ohne clean-room. Ungeprueft am Fenster: Neustart waehlt den
  gemerkten Nightfarer (nur Test). Das naechste Release traegt es.
- **OF-43 (17.09.):** Fuenf-Dateien-Grenze weicht, wenn die Alternative
  Duplikat-Logik in der UI-Schicht ist (T-289b, sieben Dateien).
- **OF-34, OF-35 (13.09.):** Test-Umbenennungen zaehlen nicht; `MUTATIONS`
  loescht der `qa-engineer` im Pruefphasenlauf.
- **Senken-Waechter zu SEC-023:** nur Bauform des Befundtexts (T-202).
- **Kein Waechter haelt die Verlaufsdateien eingefroren** (T-183).
- **Pruefpunkt 13** in T-193 eingeengt; formaler Rueckzug offen.
- **Release-Rezept:** Tag auf dem Baustand (Commit mit Bericht), nie auf
  einem HEAD mit spaeterer Arbeit; `RELEASE_BODY.md` vorher nachziehen,
  sonst `gh release edit --notes-file` (17.09.).
