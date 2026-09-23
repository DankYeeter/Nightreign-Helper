# T-332b — Bericht developer: Hook `$istExeKommando`

**Fix:** `.claude/hooks/enforce-data-redirect.ps1` maskiert vor dem Abgleich
von `$istExeKommando` alle Grenzzeichen `;&|(`, die zwischen zwei gleichen
Anfuehrungszeichen liegen (einfache Zaehl-Zustandsmaschine je Zeichen). Ein
Grep- oder Select-String-Muster wie `"foo|NightreignHelper.exe"` blockt damit
nicht mehr; ein in Anfuehrungszeichen stehender Exe-Pfad an der
Befehlsstelle (`& "C:\x\NightreignHelper.exe"`) bleibt erkannt, weil das
Grenzzeichen dort ausserhalb der Anfuehrungszeichen steht. Alle vier
"weiterhin gesperrt"-Faelle und beide "jetzt frei"-Faelle aus dem Kriterium
als Tests in `tests/test_redirect_hook_masks.py` (`NOT_A_START`/`A_START`),
19 Faelle gruen.

## Befund: Zustandsmaschine kennt keine Heredocs/Subshells

Beim Commit dieser Aenderung wies der Hook den eigenen `git commit`-Aufruf ab
(`STATUS: deny`, obwohl alle drei Umlenkungsvariablen irrelevant sind — echter
Exe-Start war es nicht). Ursache: die Commit-Message stand in einem
`$(cat <<'EOF' ... EOF)`-Heredoc; die aeussere `"` vor `$(` bleibt fuer den
Hook (er kennt nur `"`/`'` als Zeichen, keine Heredoc-Syntax) "offen", bis er
zufaellig auf ein weiteres `"` im Heredoc-Text trifft (dort stand ein
Beispiel `"foo|NightreignHelper.exe"` aus diesem Auftrag selbst) — das
schliesst die Anfuehrung fuer den Scanner vorzeitig, der `|` danach zaehlt
wieder als Grenze, `$istExeKommando` schlaegt an.

**Risiko:** dieselbe Verwechslung kann auch andersherum wirken — ein
Grenzzeichen, das eigentlich ausserhalb jeder Anfuehrung steht (echter
Exe-Start), landet durch ein vorangehendes unausgeglichenes Anfuehrungszeichen
in einem `$(...)`- oder Heredoc-Kontext "faelschlich innerhalb" und wird
maskiert — der Hook wuerde einen echten Start dann *nicht* erkennen. Nicht
reproduziert (kein Testfall in `A_START` dafuer), aber aus der Mechanik
ableitbar.

**Ort:** `.claude/hooks/enforce-data-redirect.ps1`, neue Maskierungs-Schleife
vor `$istExeKommando`. **Aufwand fuer eine vollstaendige Loesung:** ein echter
Shell-Tokenizer (Heredoc-/Subshell-Grenzen erkennen) — deutlich groesser als
der jetzige Umfang; **nicht umgesetzt** (Kriterium verlangte nur die vier
gelisteten Faelle, das ist eine Naeherung, nicht die einzig moegliche). Als
`ponytail:`-Kommentar im Hook vermerkt (keine Escape-Behandlung). Empfehlung:
im Bericht belassen, bis ein echter Vorfall (ein Startbefehl mit `$(...)`
oder Heredoc, der uebersehen wird) das noetig macht — bis dahin YAGNI.

**An director:** kein Blocker fuer T-332b (Kriterium erfuellt, Tests gruen),
aber ein Wissenstand, der in `docs/plan-restarbeiten.md` oder `qa/findings.md`
festgehalten werden sollte, falls kuenftige Rollen Startbefehle mit
Heredoc/Subshell-Konstrukten bauen.
