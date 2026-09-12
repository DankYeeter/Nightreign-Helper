STATUS: erledigt
AUFTRAG: T-108 — C-003 auf dem richtigen Sachverhalt: es gibt schon zwoelf Releases (compliance-agent, Modus `klaeren`)
GELESEN: ~/.claude/agents/_rahmen.md; docs/tasks/T-108.md; docs/legal/C-003.md (vollstaendig); docs/legal/AUFLAGEN.md; docs/berichte/T-106-release-manager.md; docs/state.md (nur Treffer zu "Artefakt"/"Release", Z. 24–113). Extern (alle 2026-09-07): GitHub-API `releases`, `git/trees/v1.0.0`, `git/trees/v1.7.1`, Repo-Metadaten; Releases-Seiten 1 und 2; Rohdateien `THIRD_PARTY.md`, `LICENSE` bei `v1.0.0` und `v1.7.1`, `NightreignHelper.spec` und `.github/workflows/release.yml` bei `v1.0.0`; GPL-3.0 § 6(d), § 8 und LGPL-3.0 Eingangssatz, § 4 (spdx.org — gnu.org drosselte); §§ 97, 97a, 98, 102 UrhG, §§ 195, 199 BGB (gesetze-im-internet.de); GitHub-Doku "Managing releases", "About releases". Volltextsuche im Arbeitsbaum nach "Lesser General Public" / "GNU GENERAL PUBLIC LICENSE" / "LESSER GENERAL PUBLIC": kein Treffer.
GEÄNDERT: docs/legal/C-004.md (neu); docs/legal/AUFLAGEN.md (Kopfzeile des C-003-Abschnitts, Zeilen A-020, A-022, A-025 fortgeschrieben; neuer Abschnitt C-004 mit A-033 bis A-036; "Nicht geprueft" ergaenzt); docs/berichte/T-108-compliance-agent.md (dieser Bericht). Kein Commit, kein Git-Zustand veraendert (Rolle ohne Bash). Keine Datei ausserhalb docs/legal/ und docs/berichte/ angefasst; Scratchpad nicht benoetigt.
ANNAHMEN: (1) Jeder der zwoelf Builds folgte dem `requirements.txt` seines Tags — `THIRD_PARTY.md` bei `v1.0.0` und `v1.7.1` nennt identische Versionen, die Artefakte selbst habe ich nicht geladen; daran haengt "ein Hinweispaket fuer alle zwoelf". (2) "Immutable releases" ist fuer das Repo nicht aktiv (Opt-in, kein Anhaltspunkt; release-manager prueft vor A-033). (3) Die Tags `v1.1.0`–`v1.7.0` gleichen in Spec/Workflow/THIRD_PARTY den geprueften Enden der Reihe. (4) Aussagen zu Verjaehrungsbeginn bei Dauerhandlung und zu Verwirkung sind Einschaetzungen ohne Urteil, so gekennzeichnet.
NÄCHSTER: director — Entscheidungsvorlage (7 Fragen in C-004) an den Nutzer; danach technical-writer (T1 versionsunabhaengig, T2-Bestandsvariante — Anforderungen in C-004, Abschnitt "Anforderungen an T1 bis T4") und release-manager (A-033, vorab Pruefung "immutable releases").
BLOCKIERT DURCH: nichts fuer diesen Lauf. Die Umsetzung von A-033 haengt an T1 (T-107) und an der Nutzerentscheidung A-025 (W1/W2 vs. W3); A-035 und A-036 sind Tatsachenfragen, die nur der Nutzer beantworten kann.

---

# T-108 — Nachtrag zu C-003: zwoelf Releases seit dem 11.08.2026

**Ergebnis:** `docs/legal/C-004.md`. C-003 bleibt unveraendert stehen.

## Sachverhalt, unabhaengig bestaetigt

12 Releases `v1.0.0` (2026-08-11 20:22 UTC) bis `v1.7.1` (2026-08-24), je genau
ein hochgeladenes Asset `NightreignHelper.exe`, Downloads
2+2+1+3+3+1+3+2+2+3+2+1 = **25** — deckt sich mit T-106 B0 und dem Auftrag.
Repo angelegt 2026-08-11 19:47 UTC (35 Minuten vor `v1.0.0`), heute
oeffentlich, 1 Stern, 1 Fork. Keine der zwoelf Beschreibungen nennt Lizenz,
Qt, LGPL oder Nicht-Verbundenheit. In keinem Tag-Baum liegt ein LGPL-/GPL-
Volltext (Baeume vollstaendig gelesen, 1077 bzw. 1048 Eintraege). Die Spec bei
`v1.0.0` hatte dieselbe `datas`-Liste wie heute, aber **keine
Versionsressource** (kein `LegalCopyright`). GitHub haengt jedem Release das
Quellarchiv des Tags automatisch an — also reiste `THIRD_PARTY.md` mit, nur
nicht "mit jeder Kopie" der EXE.

*Hinweis zur Quelle:* Die Zusammenfassung des API-Abrufs nannte als Kopfzahl
einmal "15", einmal "16" Releases, listete aber beide Male genau zwoelf Tags
mit Datum. Die Liste ist die Primaerquelle; die Kopfzahl ist ein Fehler des
zusammenfassenden Werkzeugs, nicht der API.

## Die vier Antworten

1. **A-025 — unveraendert GRAU, Zeitform korrigiert.** Die Rechtslage ist
   durch zwoelf Releases nicht schlechter geworden; die Verbreitung ist eine
   Dauerhandlung, die seit 27 Tagen laeuft. Verjaehrung (3 Jahre ab
   Jahresende der Kenntnis, § 102 UrhG, §§ 195, 199 BGB) spielt keine Rolle;
   Duldung/Verwirkung entsteht in 27 Tagen bei 1 Stern nicht;
   Rueckabwicklung der 25 Kopien ist weder moeglich noch geschuldet (§ 98
   Abs. 2 ist ein Anspruch des Verletzten, Abs. 4 Verhaeltnismaessigkeit).
   Neu praezisiert: bei einer ersten Abmahnung deckelt § 97a Abs. 3 die
   Anwaltskosten des Abmahnenden auf einen Gegenstandswert von 1 000 Euro
   (Privatperson, nicht gewerblich). Vier Wege fuer den Nutzer: W1
   weitermachen + Bestand nachruesten; W2 nur `v1.7.1` behalten; W3 alle
   EXEs zurueckziehen (beseitigt das Risiko nur fuer die Zukunft, kostet A9);
   W4 anwaltlich klaeren. Die Entscheidung ist faktisch durch Handeln
   gefallen und muss jetzt bestaetigt oder revidiert werden.
2. **A-020 — fortdauernder Verstoss, heilbar.** LGPL-3.0 inkorporiert GPL-3.0;
   nach GPL § 8 sind die Qt-Rechte mit dem ersten nicht-konformen Convey
   automatisch erloschen und leben wieder auf, wenn *alle* Verletzung endet:
   vorlaeufig sofort, endgueltig 60 Tage danach ohne Anzeige (bzw. 30 Tage
   Heilung nach erster Anzeige). Nur das dreizehnte Release mit Paket heilt
   **nicht**, solange zwoelf alte EXEs ohne Paket abrufbar bleiben. Die 25
   heruntergeladenen Kopien: nicht heilbar, nicht zu heilen — § 8 letzter
   Absatz laesst die Rechte der Empfaenger unberuehrt. **Verhaeltnismaessig:**
   ein versionsunabhaengiges Hinweispaket an alle zwoelf Releases anhaengen,
   T2-Bestandsvariante mit Datum in die Beschreibung (kein Rueckdatieren).
   Loeschen alter Assets ist zulaessig, nicht geboten. GitHub erlaubt das
   Nachruesten, ausser "immutable releases" ist aktiv.
3. **A-022 — bestaetigt: bindet seit 2026-08-11** und ist nach pruefbarem
   Ist-Zustand erfuellt (Repo oeffentlich, 12 Tags, Quellarchive, Tag-Version-
   Pruefung im Workflow seit `v1.0.0`). Nicht pruefbar: ob das Repo
   zwischendurch privat war (A-036). Heute zu tun: Tags nie loeschen (A-034),
   Nutzer bestaetigt Sichtbarkeitsverlauf.
4. **Anders geschrieben haette ich:** Sachverhaltsaufnahme ("die Alternative
   ist der heutige Zustand" war falsch), Befund 2 (als laufender Verstoss mit
   GPL § 8 als Kernnorm — das Fehlen von § 8 ist ein Fehler von C-003, nicht
   des Auftrags), Befund 4 ("EXE-Metadaten leisten das bereits" gilt nicht
   fuer `v1.0.0`), Befund 5 (Zeitform der "wichtigsten Zeile"). Unveraendert:
   Befunde 1, 3, 6–10, "Anwaltlich zu klaeren".

## Register

A-020, A-022, A-025 in neuer Fassung; neu A-033 (Bestand nachruesten,
release-manager + technical-writer), A-034 (Tags nie loeschen, archivist),
A-035 (Beanstandung eingegangen?, Nutzer), A-036 (Repo durchgehend
oeffentlich?, Nutzer). Feld fuer das Datum der letzten Nachruestung und den
60-Tage-Stichtag angelegt.

## An andere Rollen — nicht mein Auftrag, aber gesehen

- **technical-writer (T-107):** T1 versionsunabhaengig benennen und mit dem
  Satz "gilt fuer v1.0.0 bis v1.7.1 und folgende" versehen; T2 braucht eine
  Bestandsvariante ohne Pruefsummen-Punkt, mit datiertem Nachruestungssatz.
  Inhalt von T1–T4 sonst unveraendert.
- **release-manager:** vor A-033 mit `gh` pruefen, ob "immutable releases"
  aktiv ist; keines der zwoelf Releases traegt eine Pruefsumme (kein
  Rechtsproblem, nur zur Kenntnis); die Versionsressource der EXE fehlte bei
  `v1.0.0` — ab welchem Tag sie kam, ist offen.
- **director:** die Zeile "EULA-Restrisiko bleibt offen … bewusst
  unentschieden" unter "Entscheidungen des Nutzers" in AUFLAGEN.md ist
  Nutzertext und von mir nicht angefasst; sie beschreibt einen Zustand, der
  seit dem 11.08. nicht mehr besteht. Fortschreibung liegt bei dir und beim
  Nutzer.

## Nicht geprueft

Tags `v1.1.0`–`v1.7.0` einzeln; die ausgelieferten EXEs selbst; Sichtbarkeits-
verlauf; "immutable releases"; GPL § 6(b); EULA-Heilungsklauseln; alles, was
C-003 bereits als nicht geprueft fuehrt (US-Recht, japanisches Recht,
Exportkontrolle, Arbeitsvertrag).
