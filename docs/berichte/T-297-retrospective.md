STATUS: erledigt
AUFTRAG: T-297 — Retrospektive Zyklus 27 (Part 12, Stand `6467e06`)
GELESEN: GOAL.md (A22/A23), docs/state.md (`6467e06` und `c663573~1`), docs/lessons.md (Zyklus 26, NH-004..006), docs/tasks/T-287..T-297.md, docs/berichte/T-288-developer.md, T-290-qa-engineer.md (Fassungen `6f5c223` und `3b399c1`), T-290/293/294/295-release-manager-build.md, T-293-qa-engineer.md, T-295-qa-engineer.md, T-286-retrospective.md, qa/findings.md QA-282..285, DESIGN_REVIEW.md DR-032/033, UI_SPEC.md AK-313/314/317, .claude/hooks/enforce-data-redirect.ps1, .claude/settings.json, .github/workflows/release.yml, docs/release/RELEASE_BODY.md, ~/.claude/agents/_rahmen.md, qa-engineer.md, power-user.md, release-manager.md, commands/director.md, templates/task.md, hooks/require-task-file.ps1, hooks/limit-tool-calls.ps1, ~/.claude/settings.json, ~/.claude/state/zugschwelle.log, git log/for-each-ref `ae474c1..6467e06`, gh release view v1.13.2, Scratchpad 0c1b1951/T-293/qa-engineer/drv.ps1
GEÄNDERT: docs/lessons.md (Zyklus 27 angehaengt, Z. 1849-2191: Nummernraum, Gut gelaufen, Wirkungskontrolle, NH-007..NH-009, ein Muster ohne Massnahme, Beobachtungen), docs/berichte/T-297-retrospective.md (neu). Kein Commit.
ANNAHMEN: Der Dispatchtext zu T-290b ("Warten und Melden") liegt nicht auf Platte, Quelle ist das ANNAHMEN-Feld des QA-Berichts. Das Nutzerurteil zum Ingame-Test 1.13.2 vor dem Tag steht in keiner Datei (muendlich angenommen). Die Wirkung der Hook-Registrierung NH-006 ("griff sofort bei T-290 und T-297") ist nur ueber die Dateizaehlung belegt, nicht ueber ein protokolliertes `deny`.
NÄCHSTER: director — die drei Vorschlaege dem Nutzer vorlegen; Nebenfund QA-283 (P2, offen seit 17.09.) wird durch NH-007 geschlossen.
BLOCKIERT DURCH: nichts

# T-297 — Retrospektive Zyklus 27

Belege, Ursachen, Kosten und Erfolgskriterien stehen in `docs/lessons.md`
ab Z. 1851. Hier nur, was der Nutzer freigibt.

## Wirkungskontrolle

Acht geprueft, fuenf wirken (NH-006 Auftragsdatei-Hook 10/10, L-031, L-020
Budget, NH-002, NH-003), **NH-004 teilweise** (Reihenfolge 4/4, Riegel
angeschlossen; aber T-290b wartete ~20 min auf die Nutzerkopie — der Riegel
sitzt am Start, nicht am Dispatch), **NH-005 nicht messbar** (kein
power-user-Lauf; das Rezept kam beim `qa-engineer` nur ueber die
Berichtskette an), OF-43 einmal angewendet.

## Vorschlag 1 — NH-007: eine Maske statt zwei im Umlenkungs-Hook (Projekt, technisch)

`.claude/hooks/enforce-data-redirect.ps1`: Z. 75 (`$istExeStart`, jede
Nennung des EXE-Namens) streichen; den Block `$istExeKommando` (Z. 89-94,
nur Kommandoposition) vor das Umlenkungs-Gate ziehen; Z. 87 wird

```powershell
if (-not ($istQuellstart -or $istExeKommando -or $istFensterMessskript)) { exit 0 }
```

Nachweis: `ls`/`Get-FileHash` auf die EXE gehen durch; Start ohne
Variablen → `deny [datenumlenkung]`; Start bei laufender Kopie → `deny
[instanzsperre]`. QA-283 (P2, offen) bekommt die Abschlusszeile.
Sieben Fehlalarme 16.-17.09. (Heredocs, `grep run.py`, `tasklist`,
`certutil`, `ls`, zweimal `hashlib`-Umweg, einmal Fuellwerte in T-294b);
der Fix `986216d` schloss nur die `run.py`-Haelfte, obwohl T-289b beide
nannte. **Streichung:** `$istExeStart` samt Kommentar; kein neuer Text.

## Vorschlag 2 — NH-008: Riegel am Dispatch einer Fensterrolle (Projekt, technisch)

Neuer Hook `.claude/hooks/no-window-dispatch.ps1` (`PreToolUse`, Matcher
`Agent|Task`, Eintrag in `.claude/settings.json` nach dem Muster von
`require-task-file.ps1`): trifft der Prompt `qa-engineer|power-user|
clean-room|Fensterlauf|am Artefakt|am Fenster` und laeuft
`NightreignHelper` (oder `python`/`pythonw` mit Fenstertitel `Nightreign
Helper*`), `deny` mit PID/Startzeit und dem Satz "warte selbst oder gib
Arbeit ohne Programmstart; kein Auftrag verlangt 'warten'". Dritter
Wartefall (T-241d, T-285a, T-290b ~20 min auf die Nutzerkopie; Folge:
Fortsetzung an der Zugschwelle, EXE blieb laufen, Tag 1.13.2 mit QA
`teilweise`). **Streichung:** keine Textregel — Waechter statt Text
(`_rahmen.md:110-112`); ein Satz in `director.md` ist verworfen, weil der
CLAUDE.md-Absatz NH-004 schon stand und der Dispatch trotzdem kam. Wer
einbaut, zeigt einmal das `deny`.

## Vorschlag 3 — NH-009: Fenstertreiber ins Repo (Projekt, developer klein)

`<Scratchpad 0c1b1951>/T-293/qa-engineer/drv.ps1` (144 Zeilen, 27
Funktionen: Attach, Alt-Trick + `GetForegroundWindow`, Kaestchen +12 px,
`PrintWindow`, `CloseWin`, `Optimize`) als `scripts/drive_window.ps1`
committen, ORG als Parameter statt Literal; in `CLAUDE.md` unter
"Testbefehl" eine Zeile:

> Fensterlaeufe: `. scripts/drive_window.ps1` (UIA + echte Klicks; Rezept
> aus T-285/T-290b/T-293b). Nicht neu bauen; Luecken als Befund an den
> `developer`.

Das Rezept steht heute in 15 Berichten und wurde in T-290b erneut teuer
entdeckt (Zugschwelle); T-293b/T-295c kamen durch, weil sie den
Vorgaengerbericht von sich aus lasen. Der `qa-engineer` darf nichts im
Baum ablegen, der `power-user` hat kein `Write` — deshalb der `developer`.
**Streichung:** "Methodik-Nachtrag"-Abschnitte in Berichten entfallen.
Kosten: ~150 Zeilen `scripts/`.

## Zum Auftragspunkt (2), Tag 1.13.2 — keine Regel, Beobachtung

Ein Vorkommen (1.13.1 und 1.14.0 tragen den Tag auf dem damaligen HEAD);
das Rezept steht seit 17.09. in `docs/state.md`. Ein `release.yml`-Waechter
wurde geprueft und verworfen (haette den Tag auf `b0965e3` blockiert).
Falls der Nutzer trotzdem Text will: der Satz steht in `docs/lessons.md`,
Beobachtungen, erster Punkt.

## Zum Auftragspunkt (4), Nutzerbefunde — Muster, bewusst ohne Massnahme

AK-313, AK-314, AK-317-Nachtrag: drei Laienbefunde in vier Tagen, alle vom
Nutzer am gebauten Artefakt, keiner aus der Pruefkette; 1.13.2 und 1.14.0
liefen ohne `power-user`, und der letzte power-user-Lauf (1.13.1) traf 1 von
6 Zielen. NH-009 ist die Voraussetzung, damit die Rolle wieder Nachweise
liefern kann; ob sie danach zurueck in die Kette kommt oder der Ingame-Test
des Nutzers als A11-Gate in `docs/state.md` festgeschrieben wird, entscheidet
der Nutzer.

## Beobachtungen (kein Muster)

Halber Fix abgenommen (T-289b) · Fortsetzung nach `blockiert` teilt die
Zugschwelle (T-290b) · `docs/state.md` 48 Commits unangetastet, Zitate
"Stand (docs/state.md)" in T-288..T-294 nicht aus der Datei · Register lief
dem Retest voraus (T-294a, von T-295c korrigiert) · Auftraege in Kompaktform
ohne Vorlagenabschnitte · Tag 1.13.2 mit QA `teilweise` gegen die eigene
Scope-Grenze.

## Gut gelaufen, schuetzen

T-288: 948 Laeufe am echten Bestand, Ursache ausserhalb der vier
Hypothesen, Fix in 19 min · Sicherheitsblock als Vorlauf (T-292c → T-292d →
T-293c 0/0/0/0) · T-293b meldete QA-285 mit zwei Lesarten ohne eigene
Entscheidung, der Director entschied begruendet · T-295c Rot-vorher-Replik
und Registerkorrektur · Baubefund `.venv` wanderte ueber den Auftragstext
und hielt dreimal · 1.14.0 in 20 Minuten mit QA am Artefakt · T-296b liess
Pillow stehen, weil die Pixelgleichheit fehlte · T-290b stellte "EXE laeuft
noch, PIDs" an den Kopf des Berichts.
