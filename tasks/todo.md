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
- [ ] sysops separat (govulncheck: go 1.26.11 in agent/go.mod, Sonar-Gate 819 neue Verstöße)
- [ ] Bis 2027-01-31: picomatch-Suppressions (GHSA-fc5q-39xc-vjpf, kein gepatchter Stand, npm latest 4.0.7) in 10 Repos neu bewerten: kis-sinka, website-marketing, Setup-Masterskript, Coding, dealmeal, backsafe, bs-automation, devuniverse und weitere, die nachziehen
- [ ] Altlast, die der erste Scan sichtbar machte: hochzeit (4x Cookie ohne secure-Flag in app/main.py und admin.py), vintguard (12x hartkodiertes Passwort in tests/, 1x SRI), devuniverse (26 Hotspots), content-marekting (7 Bugs)
- [ ] Scan-Abdeckung dünn: hotelblog ohne Lockfile, Zoom-AddOn ohne Manifest (Scan praktisch leer), content-marekting requirements.txt mit Inline-Kommentaren, cisco-switch-konfigurator und mailcow-backsafe-config ohne Abhängigkeiten
- [ ] dealmeal: Dockerfile-Hotspot (Container läuft als root wegen Playwright) im Coolify-Deployment prüfen und ggf. auf pwuser umstellen
- [ ] Quality Gate scharf schalten (`quality-gate: true` als Standard) erst, wenn sysops und bs-automation grün sind
- Server-Prüfung (18.11.2026, nur lesend): kein Hinweis auf Eindringlinge auf bs-automation, backsafe-prod-server, netcup-rs2000, mailcow und MASTER. Offen: Schlüssel `claude@backsafe-netcup-rs2000` auf dem rs2000 zuordnen, Altlast-Schlüssel `migration-hetzner-zu-netcup` entfernen, Coolify-Schlüssel rotieren und die Klartextdatei `~/.claude/secrets/netcup-rs2000.key` entfernen, Fremd-Images `ghcr.io/lesecuritae/traviorel-*` (fareweave) bestätigen, Fail2ban auf backsafe-prod-server
- MASTER: OneDrive deinstalliert und per Richtlinie gesperrt (hatte 16,5 GB Commit-Speicher reserviert), Remote Desktop ist für alle Quellen offen, Konto admin ohne Pflichtpasswort, vollständiger Defender-Scan ausstehend
