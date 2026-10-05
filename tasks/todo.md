# SonarQube und OWASP Dependency-Check in der Build-Pipeline

- [x] Versionen recherchieren (sonarqube-scan-action v8.3.0, Dependency-Check 12.2.2, Actions-SHAs)
- [x] GPG-Signatur des Dependency-Check-Release prüfen, SHA-256 pinnen
- [x] `dependency-check.yml` als Reusable Workflow
- [x] `sonarqube.yml` als Reusable Workflow, überspringt ohne Token
- [x] Selbsttest mit verwundbarem npm-Fixture, actionlint
- [x] Vorlage `examples/security.yml`, Suppression-Vorlage, README
- [ ] Repo `kvnflx/github` anlegen, pushen, Tag `v1`, Actions-Zugriff für eigene Repos freigeben
- [ ] Selbsttest auf GitHub grün
- [ ] NVD API Key beantragen und als Secret hinterlegen
- [ ] SonarQube Cloud oder Server einrichten, `SONAR_TOKEN` hinterlegen
- [ ] `examples/security.yml` in die Projekt-Repos übernehmen
