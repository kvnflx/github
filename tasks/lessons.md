# Lessons

Regeln aus Fehlern und Funden. Vor Sicherheits- und CI-Arbeit lesen.

## Prüfen, was ein grünes Häkchen wirklich aussagt
- Ein grüner Dependency-Check bei `fail-on-cvss: 11` sagt nichts, er berichtet nur. Alle Repos laufen mit 7, die Scan-PRs der Vorrunde standen auf 11 und mussten zurückgesetzt werden.
- Ein grüner SonarQube-Job im CI sagt nichts über das Quality Gate, solange `quality-gate` auf `false` steht. Das Gate immer in der Sonar-API prüfen (`/api/qualitygates/project_status`).
- Die Sonar-PR-Analyse bewertet nur geänderte Zeilen. Nach dem Merge zeigt `master` zusätzlich Verstöße in nicht angefassten Zeilen und neue Hotspots. Ein Gate "OK" im PR heißt nicht "OK" auf `master`, nach dem Merge immer neu abfragen.
- Der GitHub-Check "SonarQube Code Analysis" ist eine Momentaufnahme. Setzt man Hotspots danach auf SAFE, bleibt er rot, bis die Analyse neu läuft.

## Advisories ohne CVSS-Wert nicht übersehen
- GHSA-2464-fhr4-w9xw (Next.js, unauthentifizierte RCE) und GHSA-p3m5-59mp-jv5r haben bei GitHub keinen Score. Filter nach `baseScore >= 7` übersehen sie, der Dependency-Check zählt sie trotzdem. Maßgeblich ist der Exit-Code des Checks, nicht ein eigener Score-Filter. Immer auch nach `severity` (HIGH, CRITICAL) filtern.
- Der Fund erscheint nicht in jedem Lauf und nicht in jedem Repo (picomatch: kleiderschrank grün, kis-sinka rot, gleiche Version). Nach Änderungen an Suppressions oder Abhängigkeiten alle JS-Repos erneut laufen lassen.
- Ein zweites Advisory für dasselbe Paket ist keine Wiederholung des ersten. `@astrojs/node` war für CVE-2026-54299 nicht betroffen, für CVE-2026-29772 schon. Jede Annahme "ist nicht betroffen" gilt nur für die genannte ID.

## Suppressions
- Nur befristet (`until`), nur für eine GHSA, nur wenn nachweislich kein gepatchter Stand existiert (`gh api advisories/<GHSA>` und `npm view <paket> versions`), und mit repo-spezifischem Beleg: `npm ls <paket> --omit=dev` und eine Suche, ob Muster oder Eingaben von außen in das Paket laufen.
- Lockfile-Funde heißen `pkg:npm/<name>` ohne Version. Das Muster muss `^pkg:npm/<name>(@.*)?$` sein, mit festem `@` greift es nicht.
- Nicht auf eine Eigenschaft hin "reparieren", die nur die Detektion umgeht (z. B. Google-Fonts per `@import` statt `<link>`, um S5725 zu entgehen). Entweder den Code wirklich ändern oder die Meldung einzeln mit Begründung als False Positive markieren.

## Arbeit mit Teammates
- Vor dem Absenden eines Auftrags nach unaufgelösten Platzhaltern suchen (`{{REGELN}}`, `<SCRATCH>`). Ein Auftrag mit Platzhalter hat keine Regeln.
- Eine Nachricht an einen laufenden Teammate kann untergehen. Bei Prioritätsaufträgen den Zustand (PR vorhanden?) prüfen und notfalls selbst übernehmen.
- Berichte, die über 16.000 Zeichen kommen, werden abgeschnitten. Von Teammates kompakte Berichte (höchstens 30 Zeilen) verlangen.
- Ein leeres Ergebnis ist kein Beleg. Zwei leere Ausgabedateien sind "gleich". Vor jedem Vergleich prüfen, dass beide Seiten nicht leer sind.

## Windows und Werkzeuge
- pnpm baut unter Windows einen sehr tiefen `node_modules/.pnpm`-Baum. Im Scratchpad-Pfad bricht er an MAX_PATH ab (fehlende Dateien, `ERR_MODULE_NOT_FOUND`). Für pnpm-Projekte einen kurzen Arbeitspfad wie `C:\\tmpw\\<name>` nehmen.
- Git Bash wandelt Pfade um (`gh api /advisories/...` wird zu `C:/Program Files/Git/...`). Endpunkte ohne führenden Schrägstrich schreiben (`advisories/...`).
- Die Sonar-API und Cloudflare blocken den Python-Standard-User-Agent mit 403. Header `User-Agent: curl/8.5.0` setzen.
- Bei `Exit 134` (`heap out of memory`) und `WebAssembly.Memory(): could not allocate memory` zuerst das Commit-Limit der Maschine prüfen, nicht den Code. Ursache war ein `OneDrive.Sync.Service` mit 16,5 GB reserviertem Speicher (`Get-Process | Sort PrivateMemorySize64`).
- Parallel laufende Test- und Build-Läufe (PGlite, Next) nicht gleichzeitig starten, sie reservieren je mehrere GB.
- Hintergrundjobs und Test-Worker nach einem Neustart der Sitzung prüfen (`Get-CimInstance Win32_Process`), hängengebliebene beenden.

## Server
- Fail2ban sperrt nach wenigen Fehlversuchen. Für jeden Server genau einen Versuch mit dem passenden Schlüssel, vorher Fingerprints abgleichen.
- Hetzner `set_rules` ersetzt die komplette Regelliste. Vor jeder Änderung die Originalregeln sichern und nach dem Zurücksetzen per Vergleich bestätigen.
- Privaten Schlüssel nie auf die Platte schreiben: `keepassxc-cli attachment-export --stdout | ssh-add -` in einem temporären `ssh-agent`.

## Sonar-Funde beheben, ohne Verhalten zu ändern (sysops, 19.11.2026)
- Wenn eine frühere Härtung Funktionen zerstört hat, kommt vor jeder Änderung ein Golden Master: feste Eingaben, Ergebnis aus dem unveränderten Stand, danach nie neu erzeugt. Ein Korpus allein reicht nicht: Eine Gegenprobe per Mutation (eine Bedingung absichtlich ändern) zeigte eine Lücke. Erst die Prüfsumme über alle Kurzstrings (3,3 Mio.) und über deterministische Zufallseingaben schloss sie. Jedes Netz mit mindestens zwei Mutationen testen.
- Feste Prüfsummen über Unicode-abhängige Ergebnisse (alle Codepoints) hängen von der Laufzeit ab. Das Image baut mit Node 22, lokal lief Node 24. Stattdessen alle Codepoints gegen eine unabhängige Referenz im selben Lauf vergleichen und die Tests auch unter der Image-Version laufen lassen.
- Sonar-Textbereiche (Zeile, Offset) gelten für den analysierten Stand. Nach dem ersten Edit an derselben Zeile (oder einer eingefügten Importzeile) passen sie nicht mehr. Funde immer aus dem Stand vor der ersten Änderung lesen, das Literal dort ausschneiden und in der heutigen Zeile exakt wiederfinden, Zeilenverschiebung mitrechnen. Texttreffer ohne Eindeutigkeit überspringen.
- Sonar kennt die Node-Typen nicht: S4325 (überflüssige Zusicherung) ist oft falsch, `server.address() as AddressInfo` wird gemeldet, obwohl tsc die Zusicherung braucht. tsc ist der Schiedsrichter: alles anwenden, Zeilen mit tsc-Fehler zurückstellen, wiederholen.
- Fixes, die gleich aussehen, sind es nicht immer: `charCodeAt` zu `codePointAt` (UTF-16-Einheiten sind gewollt), `.sort()` zu `localeCompare` (ändert die Reihenfolge, stattdessen Vergleich nach Codeeinheit), `!(x > 0)` zu `x <= 0` (NaN, undefined), `[...map.keys()]` ohne Spread (Momentaufnahme beim Löschen in der Schleife), `a && a.b` zu `a?.b` (0, "", false). Vor dem Umbau die Ausnahme prüfen, im Zweifel als begründete Ausnahme führen.
- ReDoS messen statt raten: Eingabe mit dem verdächtigen Zeichen in Länge n, 2n, 4n zeitlich messen, Faktor 4 je Verdopplung heißt quadratisch. Beim Umbau einer Regex dieselbe Sprache mit mehreren Millionen Zufallsstrings gegen die alte prüfen (nicht nur Beispiele).
- Zweistufige Funde: Nach `replace` zu `replaceAll` meldet Sonar bei festem Zeichen ein zweites Mal (Text statt Regex). Die PR-Analyse zeigt nur geänderte Zeilen. Was auf main zusätzlich sichtbar wird, vorher abschätzen: alte Funde auf die neuen Zeilennummern abbilden und die in unberührten Zeilen zählen.
- Werkzeug-Fallen auf diesem Rechner: In Edit- und Write-Eingaben wird eine Backslash-u-Folge zu einem echten Zeichen (Dateien dann verfälscht), in Python-Heredocs (`python - <<EOF`) werden doppelte Backslashes zu einem. Ersetzungen mit Backslashes immer als Skriptdatei mit dem Write-Werkzeug schreiben, den Backslash bei Bedarf mit `chr(92)` bauen, und jede Ersetzung mit `assert text.count(alt) == n` absichern.
- Nie `git commit` hinter einen Testlauf ketten, ohne den Testlauf zur Bedingung zu machen (`if npm test; then git commit ...`). Ein roter Test mit Commit musste zurückgesetzt werden.
- CSS-Regeln mit gleichem Selektor zusammenzuführen ist nicht neutral: Das Element trägt oft weitere Klassen, deren Regeln dazwischen liegen (`.archive-caret` mit `.ic`). Dazwischen nicht nur nach dem Selektor suchen, sondern nach allem, was dasselbe Element trifft, und die Wirkung im echten Browser vergleichen (berechnete Stile, alt gegen neu). Der Echtlauf fand genau das.
- Ein Vergleich zweier Programmstände kann an der Reihenfolge der Läufe scheitern (der Agent legt beim ersten Start seinen Ordner geschützt an und startet danach nicht mehr ohne Adminrechte). Vor dem Schluss "Verhalten geändert" beide Stände in gleicher Reihenfolge und aus frischem Zustand laufen lassen.
- `gofmt -l` listet unter Windows jede Datei (CRLF im Arbeitsverzeichnis, LF im Repo). Kein echter Fund.
- Teammates: Fundliste als Datei mit Text der Zeile, Regeln samt Fallen im Brief, eigener Worktree je Teammate. Berichte nicht abwarten, sondern die Commits im Worktree prüfen. Den Diff selbst lesen und unklare Stellen belegen (z. B. Zeichenfolge des System-Prompts alt gegen neu vergleichen).
