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
