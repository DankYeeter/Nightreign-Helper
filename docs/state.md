# Stand

2026-09-23 01:40, **Zyklus 29: Restposten + autonomer Lauf (T-329 a-u), gesammelt,
kein Release; QA T-329s PASS am Quellstand, Ingame-Test des Nutzers offen**. Branch
`docs/audit-and-advisor-design` (PR #18 gemerged 23.09. 19:15 `f45c98e`;
naechster PR am Zyklusende).
Verlauf `docs/archiv/state-bis-2026-09-12-zyklus19.md` und Sitzung Part 12
(16.-19.09.) in `docs/tasks/T-281..T-296` · Befunde `qa/findings.md`,
`security/findings.md` · Register `UI_SPEC_REGISTER.md`,
`ARCHITECTURE_REGISTER.md` · Reihenfolge `docs/plan-restarbeiten.md`.

**Nummernkreise** (23.09., naechste freie, Abschrift — vor Vergabe zaehlen):
T **T-332** · QA **QA-297** · SEC **SEC-052** · AK **AK-372** · AD **AD-056**
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

## Autonomer Lauf 22.09. 23:50 bis 23.09. ~01:45 (Budget 6 h, vorzeitig leer)

Endete, weil die Warteschlange leer lief (`director-autonom.md`), nicht am
Budget. Erledigt: QA-Fensterlauf T-329k + Retests p/s (PASS), Security T-329l
PASS, Farbrollen AK-367..371, Snapshot-Leser, `.gitignore` (SEC-051),
unsicherer Test selbsterklaerend, Ponytail-Audit (12 Funde umgesetzt, 2 mit
Leser behalten), Retrospektive (`docs/lessons.md`), discover
(`docs/product/BACKLOG.md`, P-001..004 `vorgeschlagen`). Suite `05dbfed`:
1914 passed, 9 skipped. Kein Merge, kein Release.

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

## HIER WEITERMACHEN

**Zyklus 27 abgeschlossen 19.09. 10:00.** T-296: README 769 → 94 Zeilen,
Guide `docs/anleitung/guide.md` (`25aa6ad`, SEC-019 geschlossen); Audit
net -421 Zeilen (`561e2ff`, `45217ef`, `122ec39`), PyInstaller nach dev;
**Pillow bleibt** (Qt-Skalierung: 820/839 Icons weichen ab). Ponytail-Debt:
1 Eintrag (`search.py:169`, bleibt). T-297 Retrospektive, T-298 umgesetzt
(NH-007 Hook-Maske `efa52fd`, NH-008 `no-window-dispatch.ps1` `b14fb4d`,
NH-009 `scripts/drive_window.ps1` `6633fca`). Kein neues Release: der
Anwendungscode seit 1.14.0 ist nur Bereinigung (Tag `v1.14.0` = `ffac292`).
**Naechster Schritt:** sync-out, PR auf `main` (Nutzer mergt). **A24** (Unterbosse, GOAL.md Nachtrag 19.09.) als naechster Zyklus: T-299 erledigt 13:05 (Bericht: beide Stufen belegt, QA-286 Extraktor liest Orte als Figuren); T-300 Entwurf AD-040/041 fertig 13:21; OF-45 (60 s) und OF-46 (nur Feld- und Nachtbosse) entschieden; T-301 gemessen 13:33 (Zusatz 21 ms bei Archiv-Wiederverwendung, Schranke eingehalten); T-302 Spec fertig 13:39 (AK-319..326, OF-47: Beispielspalte faellt); T-303 committet `3114100` 14:00 (subbosses, EXTRACT_VERSION 13, Testabzug 841 Dateien 20 913 184 B; Zaehlung single 11/group 1/ambiguous 1/unresolved 16 — Schranke INFERRED_MIN_HP); T-304 AD-042 14:15 (hoechste HP auf der Ortsroute, kein Forschungsauftrag, OF-48 Float-Kante offen); T-305 committet `25f8958` 14:29 (29/29 single, Testabzug 20 953 085 B; zwei Karten ohne Namen in den Dateien: 4654 c3252, 4688 c4021); T-306 committet `1859c57`+`7f12d5f` 14:50 (Baum, Panel HP/Beute, Beispielspalte weg, QA-144-Geometrietest entfernt, abgenickt; Suite 1797 passed); T-307 14:57: Namen belegt ueber EMEVD 90015000 (c3252 Royal Carian Knight, c4021 Royal Revenant); T-308 committet `262c7a2` 15:05 (Nachtkarten, EXTRACT_VERSION 14, Testabzug 21 012 433 B; Nachtkarten single 16/group 3/unresolved 16 — Arena-Regel zu streng, an T-309 nachgereicht); T-309 AD-043/044 15:19 (Balkenname per EMEVD mit Vorrang, Ortsregel auf allen 64 Karten, float32-Toleranz; OF-49 Nutzer-Balken offen); T-310 committet `f184b06`+`79b3ecb` 15:46 (64 single, 59 Namen, EXTRACT_VERSION 15, Testabzug 21 131 645 B, Suite 1807); T-311 Guide `e73727e`; T-312a Bau 1.15.0 `cf4c7df` (59.152.448 B, SHA E2F614F8…8405A); T-312b PASS (SEC-049/050 Niedrig, Haertung); T-312c 16:27: A24-Nachweis live bestaetigt, AK-319..326 bis auf nicht ausloesbares AK-322; QA-287 Fehldeutung (geschlossen), QA-288 P3 Beute-Toggle reagiert nicht auf UIA-Toggle; Nutzer 16:35: QA-288 fixen, dann Release; OF-49 (1) bestaetigt; T-313 fertig 16:56: a Fix `6edab2e`, b Bau `47b4330` (59.151.716 B, SHA 1D4197DF…BBDF0), c Retest PASS `8b54898`, d Notes `c536daa`; **Release 1.15.0 veroeffentlicht 17:05** (Tag `v1.15.0` auf `c536daa`, Run 35451242996, 3 Assets; Branch gepusht); naechster Schritt PR auf main (Nutzer mergt); Nebenfund: QA-286-Zeile noch "offen", Fix in `7f12d5f` — Abschlusszeile beim Zyklusende; OF-49 (drei Balken ingame) beim Nutzer; danach guide.md Abschn. 6 (technical-writer) und QA am Artefakt; AK-324.3 entschieden 13:42 (fuenf offen, Rest Toggle, seltenste zuerst). Backlog
leer laut Nutzer 19.09.; naechster Zyklus nur auf Nutzer-/Freundesbefund.

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
Zauberformel (nur ingame). SEC-051 behoben, SEC-019 Klasse offen; Retest
Security im naechsten Release-Lauf (`nrdata/savefile.py`, `param.py`,
`tpf.py`, `extract.py`, `paths.py`, `gamepath.py` geaendert). **Retrospektive:
135 QA-IDs ohne Abschlusszeile, SEC-049/050 ohne Abschluss** — Triage offen.
Debt: `upx=False` (C-006); 74 Hex-Literale in Stylesheet-Texten (AK-367ff.
Massstab je Fund).

## Beim Nutzer — offen

1. **Ingame-Test T-329** (Liste `docs/tasks/T-329.md`, Abschnitt
   "Ingame-Test", OF-54 Zahlen) — **Nutzer 19:14: "machen wir am Ende"**,
   also nach dem naechsten Zyklus, vor dessen Release.

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

## Zyklus 31 (T-332, autonom ab 23.09. 19:35)

Nutzer 19:35: autonom ohne Zeitgrenze bis die Exe gebaut ist; Stopp nur bei
Sicherheit, Datenverlust, Blocker. Warteschlange = die Punkte unten, keine
neuen Kriterien. Ende: Gate mit gebauter Exe, Nutzer testet ingame, erst dann
Veroeffentlichung (Tag, PR). GOAL.md-Nicht-Ziel "Wiki-Daten" geaendert
(Nutzerfreigabe 19:35). Reihenfolge: a Community + b Hook + Register-Triage
parallel → Ponytail-Audit/Debt → ein Fixauftrag → QA (Quelle) + Security →
Fixes → technical-writer → release-manager build+notes → power-user → Gate.

## Naechster Zyklus (alles Offene, Nutzer 19:14)

- **Community-Vermerke entfernen:** T-332a.
- **A11:** Freundestest bestanden; Kriterium bleibt "teilweise", bis der
  automatisierte Laientest (QA-282 Werkzeug) laeuft.
- **Register-Triage:** 135 QA-IDs ohne Abschlusszeile, SEC-049/050 ohne
  Abschluss.
- **Hook `$istExeKommando`:** Textteile vor dem Abgleich entfernen (T-330a
  Nebenfund).
- **Security-Retest** im Release-Lauf (`savefile.py`, `param.py`, `tpf.py`,
  `extract.py`, `paths.py`, `gamepath.py` geaendert).
- **BACKLOG.md:** P-003 gestrichen und Streichvorschlaege-Entscheide
  nachtragen (`product-strategist`).
- **Release** am Zyklusende (gesammelt seit 1.18.0: Nightfarer gemerkt,
  Bereinigung), danach Ingame-Test.

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
