STATUS: blockiert
AUFTRAG: T-167 - Das Artefakt bauen (release-manager, Modus `build`)
GELESEN: docs/tasks/T-167.md (vollstaendig); docs/legal/AUFLAGEN.md (vollstaendig, 175 Zeilen, `wc -l` gegengeprueft); docs/release/ROLLOUT.md (vollstaendig, Ablaufplan fuer `build` aus T-106); Glob nach `**/CHANGELOG.md` (kein Treffer, Datei existiert nicht — deckt sich mit ROLLOUT.md L3); `git status --porcelain`, `git rev-parse HEAD/--abbrev-ref HEAD` (Branch `docs/audit-and-advisor-design`, HEAD `14ce3d9`, Arbeitsbaum sauber); `ls dist/` und Inhalt von `dist/NightreignHelper.exe.sha256` (Bestand vor diesem Lauf); `.gitignore` Zeile 10 (`dist/`) und `git check-ignore -v` gegen `dist/NightreignHelper.exe`
GEÄNDERT: keine ausser diesem Bericht. Kein Build ausgefuehrt, `dist/` unveraendert gelassen.
ANNAHMEN: A-020 ist als "ROT bis erfuellt" mit Status-Spalte "offen" gefuehrt; der Nachtrag darunter ("A-033 ausgefuehrt am 08.09.2026") beschreibt Nachweis und vorlaeufige Heilung, schliesst aber ausdruecklich: "die Abnahme setzt der Nutzer, nicht der Director und nicht der release-manager." Ich werte das als: die Auflage ist in der Sache fortgeschritten, aber im Register formal weiterhin "offen", weil genau die Formulierung mich (release-manager) explizit von der Entscheidung ausschliesst. Ich habe diese Lesart nicht selbst herbeigefuehrt, sondern die vom Dokument vorgegebene Spalte uebernommen — das ist keine Ermessensentscheidung ueber die Auflage, sondern die Weigerung, eine engere Lesart ("de facto erledigt, zaehlt also nicht mehr") an ihrer Stelle zu treffen.
NÄCHSTER: director
BLOCKIERT DURCH: zwei offene rote Auflagen in docs/legal/AUFLAGEN.md (A-010, A-020). Nach der fuer diese Rolle geltenden Pflichtlektuere sperrt eine offene rote Auflage nicht nur das Release, sondern ausdruecklich auch `plan` und `build`. Aufhebung ist Sache von `director`/Nutzer, nicht von mir.

---

## Modus und Ergebnis

**Modus: `build`.** Der Lauf wurde **vor Schritt 1** des in `docs/release/ROLLOUT.md`
vorgegebenen Ablaufplans angehalten, weil die Pflichtlektuere von
`docs/legal/AUFLAGEN.md` zwei offene rote Eintraege ergab. Es wurde **kein**
PyInstaller-Bau ausgefuehrt, keine Datenverzeichnisse umgelenkt, keine
Lizenzpruefung (`scripts/check_licences.py`) gestartet.

## Befund: zwei offene rote Auflagen

| ID | Ampel | Status (Register) | Adressat | Bezug zu diesem Auftrag |
|---|---|---|---|---|
| **A-010** | ROT | offen | developer, ui-ux-designer | keiner — betrifft `nightlords.png` (Spielprosa im Bild), faellig "vor naechstem Push nach `main`" |
| **A-020** | ROT bis erfuellt | offen (Registerspalte) | developer (Workflow); release-manager (Bestand) | ja — betrifft genau die Distribution der EXE, die dieser Auftrag baut |

**A-020 im Detail, weil er den groessten Interpretationsspielraum bietet:**
Der Abschnitt "A-033 ausgefuehrt am 08.09.2026 — Nachweis" (dieselbe Datei,
Zeilen 160–175) beschreibt, dass der `release-manager` in T-117 alle zwoelf
bestehenden Releases mit dem Hinweispaket nachgeruestet hat, vom Director
unabhaengig geprueft, und dass die GPL-3.0-§-8-Heilung damit vorlaeufig
sofort greift, endgueltig am 07.11.2026. Der Abschnitt endet jedoch
ausdruecklich: *"Status A-020 und A-033: ausgefuehrt, Nachweis erbracht — die
Abnahme setzt der Nutzer, nicht der Director und nicht der
release-manager."* Die Ampel-Spalte der Tabelle wurde nicht auf "erfuellt"
umgestellt. Ich habe das als fortbestehend "offen" gewertet, nicht als
stillschweigend erledigt — genau diese Entscheidung liegt laut Rollendefinition
nicht bei mir ("Du entscheidest nicht ueber sie und hebst sie nicht auf").

**A-010** hat keinen inhaltlichen Bezug zu einem PyInstaller-Bau. Die fuer
diese Rolle geltende Regel kennt dafuer aber keine Ausnahme: *"Eine offene
rote Auflage sperrt das Release — auch deinen `plan` und deinen `build`."*
Das ist als unbedingte Sperre formuliert, nicht als "sperrt nur, was
thematisch anliegt".

## Warum ich hier nicht selbst entschieden habe

Der Auftrag T-167 selbst erklaert den Compliance-Lauf fuer "bewusst
ausgelassen" und zitiert eine Nutzeraussage ("alles bezueglich release und
sicherheit und co klaeren wir danach"). Das ist ein Zitat in einer vom
`director` verfassten Auftragsdatei, keine direkte Nachricht des Nutzers an
mich in dieser Sitzung — und selbst eine direkte Nachricht wuerde laut
Systemvorgabe keine Freigabe fuer eine Aenderung an Rollen-/Sperrregeln sein.
Die Rollendefinition warnt zudem ausdruecklich mit einem Datum und einem
gemessenen Vorfall genau vor diesem Muster: eine Datei in der Auftragskette
erwaehnte `docs/legal/`/`AUFLAGEN` "null Mal", obwohl der `compliance-agent`
vor mir in der Kette steht — und genau das ist hier wieder passiert: die
Pipeline in `docs/state.md` laesst den `compliance-agent`-Lauf aus, T-167
erklaert das fuer beabsichtigt, und trotzdem stehen zwei offene rote
Eintraege im Register. Die Pflichtlektuere ist genau fuer diesen Fall da.

## Bestehendes `dist/` (nicht angefasst)

Vor diesem Lauf lag bereits ein Artefakt vor (Zyklus 16, aus einem frueheren
Auftrag, nicht aus diesem):

- `dist/NightreignHelper.exe`, 59.010.777 B, 07.09.2026 22:37
- SHA-256 laut `dist/NightreignHelper.exe.sha256`:
  `42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`
- `dist/NightreignHelper-notices.zip` (Hinweispaket, A-021/A-033), 46.448 B
- `dist/` steht in `.gitignore` Zeile 10, `git check-ignore -v` bestaetigt die
  Erfassung; kein fehlender Eintrag.

Dieses Artefakt ist **nicht der heutige Stand** (Commit `14ce3d9`) — es ist
das in T-167 selbst erwaehnte Zyklus-16-Artefakt mit der dort genannten
Pruefsumme. Ich habe es weder geloescht noch ueberschrieben, damit ein
spaeterer Lauf (nach Aufhebung der Sperre) einen sauberen Vergleich hat.

## Was fuer den Bau bereitstand, aber nicht ausgefuehrt wurde

Zur Einordnung, was ein spaeterer, freigegebener `build`-Lauf vorfindet:

- Branch `docs/audit-and-advisor-design`, HEAD `14ce3d9`, Arbeitsbaum **sauber**
  (`git status --porcelain` leer) — die Reproduzierbarkeits-Voraussetzung
  "sauberer Stand" war zum Zeitpunkt der Pruefung erfuellt.
- `CHANGELOG.md` existiert weiterhin nicht (Glob-Suche, kein Treffer) — deckt
  sich mit L3 aus `docs/release/ROLLOUT.md` und ist ohnehin nicht Teil dieses
  Auftrags.
- `docs/release/ROLLOUT.md` enthaelt einen ausgearbeiteten Ablaufplan fuer
  genau diesen `build`-Lauf (Abschnitt "Ablaufplan fuer den `build`-Lauf",
  Zeilen 269–285) aus T-106/Zyklus 16: Versionsbump-Pruefung,
  `check_licences.py` vor dem Bau, `pyinstaller NightreignHelper.spec
  --noconfirm` aus der Repo-Wurzel, kein `upx` im PATH auf diesem Rechner,
  `Get-FileHash -Algorithm SHA256`, zwei Baeulaeufe zum Nachweis der
  (Nicht-)Reproduzierbarkeit. Dieser Plan ist unveraendert gueltig und kann
  von einem spaeteren, freigegebenen Lauf direkt uebernommen werden.
- Der aus Zyklus 16 bekannte Befund **"nicht bit-identisch"** (Byte-273-PE-
  Zeitstempel, Modul-Reihenfolge in `Analysis-00.toc`) betraf den damaligen
  Stand; ob er fuer den heutigen Stand weiterhin gilt, ist **nicht geprueft** —
  das war Teil des blockierten Schritts.

## Blocker

- **A-010 und A-020 (`docs/legal/AUFLAGEN.md`)** — sperren nach der fuer diese
  Rolle geltenden Pflichtregel jeden `plan`- und `build`-Lauf, unabhaengig vom
  inhaltlichen Bezug. Zustaendig: `director` (Entscheidung ueber die
  Auflagen), Nutzer (Abnahme von A-020 laut Registertext), `compliance-agent`
  (naechste fachliche Bewertung, falls noetig).
- Ohne Aufhebung dieser Sperre kann `docs/tasks/T-167.md` in diesem Lauf
  **nicht** erfuellt werden — kein Artefakt, kein SHA-256, kein Commit-Beleg,
  keine Modul-Reproduzierbarkeitspruefung.

## Risiken

- Keine neuen — es wurde nichts veraendert. Die in `docs/release/ROLLOUT.md`
  genannten Risiken (SmartScreen, fehlende Signatur, Nicht-Bit-Identitaet
  Zyklus 16) bestehen unveraendert fort und sind nicht Gegenstand dieses
  Laufs.

## Ungeprueft

- Ob der heutige Stand (`14ce3d9`) ueberhaupt baut (`pyinstaller
  NightreignHelper.spec --noconfirm`).
- Version, Groesse, SHA-256 und Modul-Reproduzierbarkeit des heutigen Standes.
- `EXTRACT_VERSION` des heutigen Standes gegen den festen Testabzug (11) —
  ob die Vorlage weiterhin gueltig ist.
- Ob `check_licences.py` gegen den heutigen Stand durchlaeuft.
- Alle drei Datenverzeichnis-Umlenkungen wurden **nicht** benoetigt, da kein
  Programmlauf stattfand — daher auch kein Nachweis dazu in diesem Bericht.

## An `developer`

Nichts. Es wurde kein Anwendungscode gepruefte oder angefasst; der Abbruch
liegt ausschliesslich an der Compliance-Sperre, nicht am Quellstand.

## An `power-user`

Kein neuer Ausgangspunkt. Das einzige vorhandene Artefakt in `dist/` ist das
alte Zyklus-16-Artefakt (`NightreignHelper.exe`, 59.010.777 B, SHA-256
`42B21AA2743FE64A83A093BE0261ABAEC361D99903150D620E5324BD4301F221`, Version
1.8.0 laut T-167) — **nicht** der heutige Stand `14ce3d9` und nicht das, was
dieser Auftrag liefern sollte. Vor einer `power-user`-Sitzung muss der
`build`-Lauf zuerst freigegeben und erfolgreich nachgeholt werden.

## An `director`

**Empfehlung: nicht freigeben — in diesem Zustand nicht baubar durch mich.**
Nicht wegen eines technischen Mangels (der Bau selbst wurde nicht einmal
versucht), sondern weil `docs/legal/AUFLAGEN.md` zwei offene rote Eintraege
fuehrt (A-010, A-020) und meine Rollenregeln das als unbedingte Sperre auch
fuer `build` vorschreiben.

Offene Entscheidungen fuer den `director`:

1. **A-010** klaeren oder als fuer diesen Auftrag irrelevant erklaeren und das
   im Register vermerken (das kann nur der `director`, nicht ich).
2. **A-020**: entweder die Nutzer-Abnahme einholen und die Registerspalte auf
   "erfuellt" umstellen, oder ausdruecklich entscheiden, dass die "ROT bis
   erfuellt"-Bedingung durch T-117/A-033 bereits als erfuellt gilt und das im
   Register nachtragen. Beides ist eine Entscheidung des `director`
   (bzw. des Nutzers fuer die Abnahme selbst), nicht meine.
3. Danach: T-167 erneut an `release-manager` geben — der Ablaufplan in
   `docs/release/ROLLOUT.md` (Zeilen 269–285) ist bereit und kann direkt
   ausgefuehrt werden.

Kein Tag-Vorschlag, kein fehlender `.gitignore`-Eintrag zu melden (`dist/`
ist bereits erfasst).
