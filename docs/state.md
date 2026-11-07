# Stand

2026-11-07 23:45, **1.21.0 beim Nutzer installiert** (`dist\NightreignHelper.exe` aus `bb7f2cc`,
59 320 923 B, SHA-256 `add8ecd9…`, Update-Probe ueber v1.20.1 bestanden, erster Start rund 75 s
Neuaufbau ohne Fortschrittsanzeige). Neu: Zaehleffekte zaehlen nur einen Traeger, Stack-Grenzen je
Effekt (T-339, EMEVD-Lesart, keine Spielprobe), Ziel Balanced, echte Slot-Bilder und Spielsymbole
(T-340, v20/v5). Offen: QA-343, QA-344 (P4, zurueckgestellt), SEC-055 (Haertung); kein Tag.

2026-11-07, **T-336 fertig: Spalte Stacks im Effekt-Filter von Optimize, 0 bis 10
(`10e2c07`, Treiber `a56af52`), Nachtest T-336g im Fenster bestanden; Testabzug 1.21.0 aus `298a0c9` gebaut (T-336j,
59 300 781 B, SHA-256 `c5aa2e89…`), Nutzertest steht aus; kein Tag, kein Release, UI_SPEC AK-469 bis AK-473.** T-336h (`7886ba4`): QA-339 behoben, Zeilen gleich
hoch, ×-Zahl der Statistik-Seite bis 99 (erreicht Optimize bei leerem Filter weiter, bewusst so
gelassen: bis zum Vorschlag 2,85 bis 3,55 s); Nachtest T-336i bestanden. Offen: A6 am
Zielgeraet nicht gemessen (hier leer bis 2,27 s, Stacks 10 bis 3,67 s, auf dem Zielgeraet
hochgerechnet ueber 6 s auch ohne Stack-Wert, nur gerechnet). Registry-Vorfall
07.11.: `HKCU\Software` teilweise geloescht, aus der Schattenkopie von 08:23 wiederhergestellt,
Schluessel gegen die Liste geprueft (1348 von 1348).

2026-10-31 19:08, **Zyklus 34 (T-335) freigabebereit: Exe 1.19.0 aus `995039b`
(59 233 901 B, SHA-256 `b479a9bb…`), QA T-335qa4 PASS, Security PASS,
clean-room T-335cr PASS (`46b7b3c`); Tag `v1.19.0`, Release, PR folgen.**
Inhalt seit Zyklus 33: Ingame-Test-Fixes, Zauber-/Art-Wahl (Casting-Leiste,
AD-056, EXTRACT_VERSION 18), Zauber an der Puppe kalibriert; Details
`docs/tasks/T-335.md`, Restarbeiten `docs/plan-restarbeiten.md`. Branch
`docs/audit-and-advisor-design` (PR #18 gemerged 23.09. 19:15 `f45c98e`;
naechster PR am Zyklusende).
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` und Sitzung Part 12
(16.-19.09.) in `docs/tasks/T-281..T-296` · Befunde `qa/findings.md`,
`security/findings.md` · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (13.10., naechste freie, Abschrift — vor Vergabe zaehlen):
T **T-335** · QA **QA-302** · SEC **SEC-053** · AK **AK-395** · AD **AD-056**
· DR **DR-047** · C **C-008** · A **A-039** · P **P-005** · NH **NH-017**
(NH-014..016 vorgeschlagen)
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

1. **Ingame-Test `dist\NightreignHelper.exe` 1.19.0** (59 199 168 B, SHA-256
   `2DBFEDDF…E8BEB`, Bau `ed93e31`, Notes `0bc8f73`, Director gemessen
   14.10. 19:30; kein Code-Diff `ed93e31..HEAD`). Liste `docs/tasks/T-329.md`
   "Ingame-Test" (OF-54) plus Wylder/Optimize ohne Hammer+Great-Hammer-Paar
   plus QA-278. Danach Freigabe → Tag `v1.19.0` auf `0bc8f73` (oder spaeter
   reiner Doku-Commit), sync-out, PR.

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

## Zyklus 32 (T-333, 12.10.) — QA-299 PASS, Neubau `c5eaa41`, Laientest 2/2; Details `docs/tasks/T-333.md`

Fokusraub-Ursache **Hypothese**; Fensterlaeufe nur bei freiem PC (Nutzer 12.10. 21:05).

## Zyklus 33 (T-334, 13.-14.10.) — AM GATE 14.10. 19:30

QA-300/301 + Altbefunde (Triage 90 IDs, ~80 geschlossen/behoben) und QA-292
(Leiste zweizeilig, Fenster-Mindestbreite ~1190 px). QA T-334p CONCERNS ohne
P1/P2 (Suite `a5cd4eb` 2064/9), Security T-334q PASS, Bau `ed93e31`,
power-user T-334s 2/2, clean-room T-334t PASS (Erststart, Update 1.18.0→1.19.0,
Zweitstart; ohne Steam-Registry nicht pruefbar). Details `docs/tasks/T-334.md`.

## Naechster Zyklus (offen)

- QA-302 (Ordnerdialog Startort, P4), QA-303 (`drive_window.ps1:79`, P4),
  QA-304 (Save ueberdeckt Build-Feld bei schmalem Fenster, P3); Wortlaut
  Rescan vs. Find my save ohne Spielstand; Legende Durchstreichen fremder
  Nightfarer; `advisorbar.py:331` "No save was read" bei leerem Spielstand;
  lange Slotkarten (Flask-Zeilen); `relicpicker.py:922` (SEC-019).
- QA-030 dritter Punkt: leerer Slotsatz wird nie gespeichert, Build bleibt
  doppelt (P4, Speicherregel offen).
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
