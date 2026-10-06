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
- [ ] PRs mergen
- [ ] Kritische Funde abarbeiten (next, astro, postcss, vitest, proxy-addr, react), danach fail-on-cvss: 7
- [ ] Auf Dependency-Check 13.0.1 aktualisieren, sobald released (Issue #8715)
- [ ] SonarQube Cloud oder Server einrichten, `SONAR_TOKEN` hinterlegen, Sonar-Job in die Repos aufnehmen
