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
- [ ] datedecoder: Auto-Deploy beim nächsten Push bestätigen
- [ ] 16 PRs ci/security-scan der Sonar-Session: Entscheidung Kevin (Re-Run zieht den pnpm-Fix)
