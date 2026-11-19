# SonarQube und OWASP Dependency-Check in der Build-Pipeline

- [x] Versionen recherchieren (sonarqube-scan-action v8.3.0, Dependency-Check 12.2.2, Actions-SHAs)
- [x] GPG-Signatur des Dependency-Check-Release prüfen, SHA-256 pinnen
- [x] `dependency-check.yml` als Reusable Workflow
- [x] `sonarqube.yml` als Reusable Workflow, überspringt ohne Token
- [x] Selbsttest mit verwundbarem npm-Fixture, actionlint
- [x] Vorlage `examples/security.yml`, Suppression-Vorlage, README
- [x] Repo `kvnflx/github` angelegt (öffentlich, damit auch Public-Repos es aufrufen können), Tag `v1`
- [x] Selbsttest grün
- [x] NVD-Daten über den Feed-Mirror statt der NVD-API (API brauchte > 45 min)
- [x] `npm ci --ignore-scripts` vor dem Scan, sonst wird das Lockfile nicht vollständig analysiert
- [x] PRs `ci/security-scan` in 13 Repos mit package-lock.json, nur berichten (fail-on-cvss: 11), alle Scans grün
- [x] PRs gemergt (2026-10-06), alle Default-Branches grün
- [x] Funde behoben in 11 Repos (next, astro 7, postcss, vitest 4, nodemailer 10, react 19.2.8, sharp 0.35, Tailwind 4 in website-marketing), je Build/Tests/Smoke vorher und nachher
- [x] fail-on-cvss: 7 in allen 13 Repos, braces 3.0.3 und node-forge 1.4.0 (kein Fix) befristet bis 2027-04-01 unterdrückt
- [ ] Bis 2027-04-01: Suppressions für braces/node-forge neu bewerten
- [ ] Auf Dependency-Check 13.0.1 aktualisieren, sobald released (Issue #8715)
- [x] SonarQube-Server sonar.backsafe.de (netcup-Coolify), `SONAR_TOKEN` in allen Repos, Sonar-Job in den PRs `ci/security-scan` aller 29 Repos (06.10.2026)
- [ ] Quality Gate scharf schalten (`quality-gate` Standard auf true), sobald der Bestand gesichtet ist

## Runde 2 (2026-10-06/07): alles Rote und Auffällige beheben
- [x] pnpm/yarn-Unterstützung in dependency-check.yml, gehärtet gegen Codeausführung (feste Versionen, --ignore-pnpmfile, YARN_IGNORE_PATH, Install außerhalb des Repos)
- [x] Sonar-Gate "Backsafe" als Standard (ohne Coverage-Bedingung)
- [x] Sonar-Bugs/Vulnerabilities und alte rote Tests/Lint in 9 Repos behoben und gemergt, False Positives mit Begründung markiert
- [x] dealmeal: Gemini-Key aus dem Code (in KeePass dealmeal/Gemini API Key)
- [x] QR-Code-Wlan: echtes Praxis-WLAN-Passwort aus den Tests entfernt
- [x] Setup-Masterskript: CSP für die Tauri-App, Tailwind 4, npm audit 0, braces-Suppression entfernt
- [x] datedecoder: Auto-Deploy war seit 2026-09-01 tot (öffentliches Repo ohne GitHub-App), manuell deployt, GitHub-Webhook auf Coolify eingerichtet
- [x] echo und CheapFlightPro-Webversion archiviert, Sonar-Projekte gelöscht
- [ ] Gemini-Key rotieren (Kevin, Google AI Studio)
- [ ] Praxis-WLAN-Passwort ändern, falls noch aktiv (Kevin)
- [x] datedecoder: Auto-Deploy bestätigt (18.11.2026: Container mit Commit 32ca78a auf netcup-rs2000, healthy)
- [x] PRs ci/security-scan: alle 12 gemergt (siehe Runde 3)

## Runde 3 (2026-11-18/19): SonarQube und OWASP in allen Projekten wieder grün
Ausgangslage: Dependency-Check rot in kis-sinka, website-marketing, Setup-Masterskript, datedecoder, Coding. Sonar-Gate rot in dealmeal, github, sysops. 12 Repos nie gescannt. sysops auf Wunsch ausgeklammert.
- [x] github: 4 Sonar-Smells behoben (Cognitive Complexity im Deploy-Skript, Dockerfile-Fixture), Dependabot #5 gemergt, `v1` auf c08f23e gezogen
- [x] OWASP behoben: undici (kis-sinka), body-parser (datedecoder, website-marketing, dealmeal), zod (Setup-Masterskript, website-marketing, dealmeal), node-forge und vite (Coding), MCP-SDK (website-marketing)
- [x] Next.js-RCE GHSA-2464-fhr4-w9xw und DoS GHSA-p3m5-59mp-jv5r: website-marketing (15.5.29), dealmeal (16.4.6), devuniverse (15.5.29), alle live
- [x] dealmeal: Sonar-Gate auf master grün (26 Commits in 4 Schichten, 82 Hotspots einzeln mit Begründung, 1 als ACKNOWLEDGED, 1 False Positive), Mail-Vorlagen-Route live geprüft (Inhalt identisch zur alten Datei)
- [x] 12 Scan-PRs: alle 12 gemergt (bs-automation, vintguard, vintguard-friends, Zoom-AddOn, hotelblog, content-marekting, cisco-switch-konfigurator, hochzeit, mailcow-backsafe-config, backsafe-monitoring, devuniverse, backsafe), jeweils mit fail-on-cvss 7
- [x] bs-automation #1 (freigabe): Astro 6.4.8 und @astrojs/node 10.1.4 gegen GHSA-3rmj-9m5h-8fpv gemergt (4a36309), 487 Tests grün. **Noch nicht deployt:** auf dem VPS `deploy/deploy.sh` ausführen (Kevin)
- [x] sysops: separat erledigt, siehe Runde 4 unten
- [ ] Bis 2027-01-31: picomatch-Suppressions (GHSA-fc5q-39xc-vjpf, kein gepatchter Stand, npm latest 4.0.7) in 10 Repos neu bewerten: kis-sinka, website-marketing, Setup-Masterskript, Coding, dealmeal, backsafe, bs-automation, devuniverse und weitere, die nachziehen
- [ ] Altlast, die der erste Scan sichtbar machte: hochzeit (4x Cookie ohne secure-Flag in app/main.py und admin.py), vintguard (12x hartkodiertes Passwort in tests/, 1x SRI), devuniverse (26 Hotspots), content-marekting (7 Bugs)
- [ ] Scan-Abdeckung dünn: hotelblog ohne Lockfile, Zoom-AddOn ohne Manifest (Scan praktisch leer), content-marekting requirements.txt mit Inline-Kommentaren, cisco-switch-konfigurator und mailcow-backsafe-config ohne Abhängigkeiten
- [ ] dealmeal: Dockerfile-Hotspot (Container läuft als root wegen Playwright) im Coolify-Deployment prüfen und ggf. auf pwuser umstellen
- [ ] Quality Gate scharf schalten (`quality-gate: true` als Standard) erst, wenn sysops und bs-automation grün sind
- Server-Prüfung (18.11.2026, nur lesend): kein Hinweis auf Eindringlinge auf bs-automation, backsafe-prod-server, netcup-rs2000, mailcow und MASTER. Offen: Schlüssel `claude@backsafe-netcup-rs2000` auf dem rs2000 zuordnen, Altlast-Schlüssel `migration-hetzner-zu-netcup` entfernen, Coolify-Schlüssel rotieren und die Klartextdatei `~/.claude/secrets/netcup-rs2000.key` entfernen, Fremd-Images `ghcr.io/lesecuritae/traviorel-*` (fareweave) bestätigen, Fail2ban auf backsafe-prod-server
- MASTER: OneDrive deinstalliert und per Richtlinie gesperrt (hatte 16,5 GB Commit-Speicher reserviert), Remote Desktop ist für alle Quellen offen, Konto admin ohne Pflichtpasswort, vollständiger Defender-Scan ausstehend

## Runde 4 (2026-11-19): sysops, Sonar-Gate und govulncheck grün, ohne Verhaltensänderung
Ausgangslage: govulncheck rot (GO-2026-6859, `net/http`), Sonar-Gate rot (819 neue Verstöße, 48 Hotspots). Die Härtung vom Oktober hatte Funktionen zerschossen, deshalb zuerst ein Sicherheitsnetz, dann die Fixes.
- [x] Golden Masters (neue Tests) vor jeder Änderung: Befehlseinstufung (4963 Eingaben, 3.257.437 Kurzstrings, 150.000 Zufallsbefehle), Schwärzung, unsichtbare Zeichen (alle Codepoints gegen Referenz), Markdown-Parser, Verlaufsmodelle. Vier Gegenproben per Mutation.
- [x] PR #3 gemergt (120e8d7), Hub deployt am 19.11.2026: Go 1.26.11, 819 auf 75 neue Verstöße, Rest begründet geführt. Gate auf main OK (0 neue Verstöße, Hotspots 100 %, 0 Bugs, 0 Schwachstellen), alle fünf Pipeline-Jobs grün.
- [x] Geprüft: 772 Tests, Image-Build in CI (Node 22), Echtlauf Alt gegen Neu im Browser (17 Selektoren in 68 Kombinationen, ein Befund `.archive-caret` behoben), Diff-Prüfung auf Sicherheitsschutz (über 100 Hunks, kein Befund), Live-Prüfung mit dem Service-Token (22 Ziele, lesende Routen, Auslieferung).
- [x] Sonar-Entscheidungen (Kevin, 19.11.2026): 35 Komplexitäts-Funde (S3776) als Akzeptiert, 40 Einzelfälle und 38 Hotspots einzeln mit Begründung (SAFE oder ACKNOWLEDGED mit Messwerten).
- [ ] Komplexität je Funktion mit Test umbauen. Größte: `hubws.ts` handleFrame (61), `session.ts` (39, 24, 23), `config.ts` loadConfig (37), `attachments.ts` (35, 34), `api.ts` (33, 21). Go-Agent ohne Test: `runAgent`, `runSetup`, `resolveConfigAt` (Dienststart und Einrichtung auf den Kundenservern), dazu `service_linux.go`, `harden.go`, `client.go`, `stream.go`, `secure_windows.go`
- [ ] Akzeptierte ACKNOWLEDGED-Hotspots neu bewerten: `FAZIT` in `batch-logic.ts` (40.000 Leerzeilen 1,2 s), IP-Kandidaten in `groups.ts` (40.000 Doppelpunkte 2,9 s), Zeilen-Regexe im Markdown-Parser (nur mit U+2028/2029)
- [ ] Neun Dialoge als `<dialog>` und Chip-Kontrast `.wissen-chip.warn` im hellen Design (Sonar S6819, S7924) nur mit Design-Entscheidung
- [ ] Beobachtung: Der Strom-Schwärzer liefert in 49 von 400 Zufallsfällen nicht dasselbe wie `redactText` über den ganzen Text. Ursache nicht untersucht (Überlappung verschiedener Formen vermutet), Test hält den heutigen Stand fest
- [ ] Kevin: In der Leitstelle neu laden und je Haltung einen Befehl gegen ein Testziel geben (KI-Schleife, Freigabekarte, Not-Aus sind nur live prüfbar). Agents bei Gelegenheit per Knopf „Agent aktualisieren" auf das Go-1.26.11-Binary bringen, nichts ist erzwungen
- [ ] Kevins lokaler Klon `C:\Projekte\Tool` steht noch auf b452c47: `git pull`, die 12 unversionierten Dateien (Icons, `docs/security/`) kollidieren nicht
- Befund Einstufung: Die Härtung vom 22./23.10. hat `decideGate` und `classify` für Einzelchats nicht verändert (die Kern-Härtung M2 blieb zurückgestellt). Die neue Quellen-Schutz-Erkennung `changesExisting` greift nur in `session.ts` (Zeilen 519, 520), wenn eine Gruppe eine Quelle markiert hat und der Befehl sonst automatisch liefe. Das Verschieben im Autonom-Modus kam vom 16. bis 19.10. (Wortgrenzen der Zerstörer-Erkennung)
