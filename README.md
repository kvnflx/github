# CI-Workflows

Zentrale, wiederverwendbare GitHub-Actions-Workflows für alle Repos unter `kvnflx`.

| Workflow | Zweck | Build scheitert bei |
|---|---|---|
| `dependency-check.yml` | OWASP Dependency-Check, bekannte CVEs in Abhängigkeiten | CVSS >= 7 (einstellbar) |
| `sonarqube.yml` | SonarQube auf https://sonar.backsafe.de, statische Codeanalyse, PR-Kommentare | rotem Quality Gate, nur mit `quality-gate: true` |

## Einbinden

`examples/security.yml` ins Projekt-Repo nach `.github/workflows/security.yml` kopieren. Das reicht für npm-, Python-, Go- und .NET-Projekte ohne weitere Anpassung.

```yaml
jobs:
  dependency-check:
    uses: kvnflx/github/.github/workflows/dependency-check.yml@v1
    secrets:
      NVD_API_KEY: ${{ secrets.NVD_API_KEY }}

  sonarqube:
    uses: kvnflx/github/.github/workflows/sonarqube.yml@v1
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

Damit ein Merge bei Funden blockiert wird, in den Branch-Protection-Regeln des Projekt-Repos die Checks `dependency-check / Dependency-Check` und `sonarqube / SonarQube` als Pflicht setzen.

## Secrets

| Secret | Pflicht | Woher |
|---|---|---|
| `NVD_API_KEY` | optional | Nur nötig, wenn `nvd-datafeed` leer ist und direkt die NVD-API benutzt wird. Kostenlos unter https://nvd.nist.gov/developers/request-an-api-key. |
| `SONAR_TOKEN` | für Sonar | Global Analysis Token von sonar.backsafe.de (KeePass auf MASTER: `sonarqube/Global Analysis Token github-actions`). Ohne Token wird der Sonar-Job mit Warnung übersprungen. |
| `OSS_INDEX_TOKEN` | optional | Sonatype Guide Personal Access Token. Ohne Token ist der OSS Index Analyzer aus. |

Die Secrets müssen im jeweiligen Projekt-Repo hinterlegt sein. Auf einem Personal Account gibt es keine kontoweiten Secrets.

## dependency-check.yml

| Input | Standard | Beschreibung |
|---|---|---|
| `scan-path` | `.` | Zu scannender Pfad |
| `exclude` | `.git`, `node_modules`, `.venv`, `venv` | Ant-Pattern, eines pro Zeile |
| `fail-on-cvss` | `7` | Schwellwert, `11` = nur berichten |
| `suppression-file` | leer | Leer = `dependency-check-suppressions.xml` im Repo-Root, falls vorhanden |
| `enable-experimental` | `true` | Experimentelle Analyzer, nötig u. a. für Python `requirements.txt` und Go |
| `npm-install` | `true` | `npm ci --ignore-scripts` vor dem Scan, für vollständige npm-Analyse |
| `skip-dev-dependencies` | `false` | devDependencies bei npm, yarn, pnpm ignorieren |
| `upload-sarif` | `false` | Funde im Security-Tab. Braucht `security-events: write` im Aufrufer und bei privaten Repos GitHub Advanced Security |
| `nvd-datafeed` | Mirror des Dependency-Check-Projekts | NVD-Daten als Feed, täglich aktualisiert, schnell und ohne Rate-Limit. Leer = NVD-API mit `NVD_API_KEY` (erster Lauf dauert dann über eine Stunde) |
| `extra-args` | leer | Weitere CLI-Argumente |
| `dc-version`, `dc-sha256` | `12.2.2` | CLI-Version mit gepinnter Prüfsumme. 13.0.0 bricht ohne NVD API Key ab (Issue #8715), Update sobald 13.0.1 erscheint |

Ergebnis: Tabelle in der Job-Zusammenfassung, HTML-, JSON- und SARIF-Report als Artefakt `dependency-check-report` (30 Tage).

Die NVD-Datenbank wird pro Repo und Tag im Actions-Cache gehalten. Nach dem ersten Lauf dauert ein Scan meist wenige Minuten.

False Positives: `examples/dependency-check-suppressions.xml` als `dependency-check-suppressions.xml` ins Projekt-Root legen und dort eintragen.

Für npm-Projekte führt der Workflow vor dem Scan in jedem Ordner mit `package-lock.json` ein `npm ci --ignore-scripts` aus. Ohne `node_modules` würde Dependency-Check das Lockfile nur über `npm audit` prüfen und den Abgleich gegen die NVD auslassen. Abschalten mit `npm-install: false`.

## sonarqube.yml

| Input | Standard | Beschreibung |
|---|---|---|
| `host-url` | `https://sonar.backsafe.de` | `https://sonarcloud.io` für SonarQube Cloud |
| `organization` | GitHub-Owner | Nur Cloud |
| `project-key` | `<owner>_<repo>` | Entspricht dem Schlüssel beim Import aus GitHub in SonarQube Cloud |
| `project-base-dir` | `.` | Basisverzeichnis |
| `args` | leer | Weitere `-Dsonar.*` Parameter |
| `coverage-artifact` | leer | Artefakt aus einem Test-Job, das vor dem Scan entpackt wird |
| `quality-gate` | `false` | `true` = Gate abwarten, rotes Gate lässt den Build scheitern. Vorerst aus, das Gate steht trotzdem im PR-Kommentar |
| `quality-gate-timeout` | `300` | Sekunden |

Liegt im Projekt eine `sonar-project.properties`, gelten deren Werte für Schlüssel und Organisation, solange die Inputs leer sind.

Coverage einbinden:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: npm ci && npm test -- --coverage
      - uses: actions/upload-artifact@v7
        with:
          name: coverage
          path: coverage/lcov.info

  sonarqube:
    needs: test
    uses: kvnflx/github/.github/workflows/sonarqube.yml@v1
    with:
      coverage-artifact: coverage
      args: -Dsonar.javascript.lcov.reportPaths=lcov.info
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### SonarQube-Server

Läuft seit 06.10.2026 als Coolify-Service `sonarqube` auf netcup-rs2000 unter https://sonar.backsafe.de: Community Build 26.5 mit dem Community-Branch-Plugin von mc1arke. Damit werden auch Branches und Pull Requests analysiert, und die GitHub App `sonarqube-kvnflx` schreibt das Ergebnis als Kommentar in den PR. Anmeldung ist Pflicht, Projekte sind privat.

Neues Repo anbinden:

1. Projekt `kvnflx_<repo>` in SonarQube anlegen (Hauptbranch = Default-Branch des Repos) und unter Project Settings > DevOps Platform Integration an `kvnflx/<repo>` binden (Konfiguration `github-kvnflx`)
2. `gh secret set SONAR_TOKEN -R kvnflx/<repo>` mit dem Global Analysis Token
3. `examples/security.yml` übernehmen

Die GitHub App muss Zugriff auf das Repo haben. Sie ist auf „All repositories" installiert, neue Repos sind damit automatisch drin.

Ein PR wird erst sauber kommentiert, wenn der Zielbranch einmal analysiert wurde. Nach dem Einbinden deshalb einmal auf main pushen oder den Workflow manuell starten.

SonarQube Cloud geht weiterhin mit `host-url: https://sonarcloud.io`.

## Versionierung

Aufrufer referenzieren `@v1`. Kompatible Änderungen: Tag `v1` nachziehen (`git tag -f v1 && git push -f origin v1`). Inkompatible Änderungen bekommen `v2`.

Die Actions sind auf Commit-SHAs gepinnt und werden von Dependabot aktualisiert. Die Dependency-Check CLI aktualisiert Dependabot nicht: neue Version in `dc-version` eintragen und `dc-sha256` neu berechnen, nachdem die GPG-Signatur des Release geprüft wurde.

## Selbsttest

`selftest.yml` läuft bei jedem Push: actionlint über alle Workflows, Dependency-Check gegen `test/fixtures/npm` (lodash 4.17.20 mit CVE-2021-23337) mit Prüfung, dass die Schwachstelle erkannt wird, und der Sonar-Workflow.
