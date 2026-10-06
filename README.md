# CI-Workflows

Zentrale, wiederverwendbare GitHub-Actions-Workflows für alle Repos unter `kvnflx`.

| Workflow | Zweck | Build scheitert bei |
|---|---|---|
| `dependency-check.yml` | OWASP Dependency-Check, bekannte CVEs in Abhängigkeiten | CVSS >= 7 (einstellbar) |
| `sonarqube.yml` | SonarQube Cloud oder Server, statische Codeanalyse | rotem Quality Gate |

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
| `SONAR_TOKEN` | für Sonar | SonarQube Cloud: My Account > Security. Server: User > My Account > Security. Ohne Token wird der Sonar-Job mit Warnung übersprungen. |
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
| `host-url` | leer | Leer = SonarQube Cloud, sonst URL des eigenen Servers |
| `organization` | GitHub-Owner | Nur Cloud |
| `project-key` | `<owner>_<repo>` | Entspricht dem Schlüssel beim Import aus GitHub in SonarQube Cloud |
| `project-base-dir` | `.` | Basisverzeichnis |
| `args` | leer | Weitere `-Dsonar.*` Parameter |
| `coverage-artifact` | leer | Artefakt aus einem Test-Job, das vor dem Scan entpackt wird |
| `quality-gate` | `true` | Gate abwarten, rotes Gate lässt den Build scheitern |
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

### SonarQube einrichten

SonarQube Cloud (kostenlos für öffentliche Repos): auf https://sonarcloud.io mit GitHub anmelden, Organisation `kvnflx` importieren, Projekt anlegen, unter Administration > Analysis Method die automatische Analyse ausschalten (sonst kollidiert sie mit dem CI-Scan) und den Token als `SONAR_TOKEN` hinterlegen.

Eigener Server: Der Server muss aus dem Internet erreichbar sein, weil die GitHub-Runner von außen zugreifen. `host-url` als Repo-Variable `SONAR_HOST_URL` setzen und im Aufrufer `host-url: ${{ vars.SONAR_HOST_URL }}` eintragen.

## Versionierung

Aufrufer referenzieren `@v1`. Kompatible Änderungen: Tag `v1` nachziehen (`git tag -f v1 && git push -f origin v1`). Inkompatible Änderungen bekommen `v2`.

Die Actions sind auf Commit-SHAs gepinnt und werden von Dependabot aktualisiert. Die Dependency-Check CLI aktualisiert Dependabot nicht: neue Version in `dc-version` eintragen und `dc-sha256` neu berechnen, nachdem die GPG-Signatur des Release geprüft wurde.

## Selbsttest

`selftest.yml` läuft bei jedem Push: actionlint über alle Workflows, Dependency-Check gegen `test/fixtures/npm` (lodash 4.17.20 mit CVE-2021-23337) mit Prüfung, dass die Schwachstelle erkannt wird, und der Sonar-Workflow.
