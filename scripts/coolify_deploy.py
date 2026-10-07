#!/usr/bin/env python3
"""Deploy einer Coolify-Anwendung mit Smoke-Test und automatischem Rollback.

  coolify_deploy.py deploy --app UUID --url URL --keyword TEXT --sha SHA [--name NAME]
                           [--repo OWNER/REPO] [--branch main] [--timeout 900] [--attempts 10] [--delay 15]
  coolify_deploy.py notify --title TEXT --message TEXT [--priority 1-5]

Umgebung:
  COOLIFY_TOKEN   API-Token (Pflicht für deploy)
  COOLIFY_URL     Standard https://app.coolify.io
  NTFY_URL        https://ntfy.sh/<topic>; ohne Variable wird nur ausgegeben
  GITHUB_TOKEN    für die Prüfung, ob --sha noch der neueste Commit ist (nur mit --repo)
  GITHUB_API_URL  Standard https://api.github.com

Exit-Codes: 0 live oder übersprungen, 1 fehlgeschlagen (alte Version läuft, zurückgerollt
oder kein Vorgänger), 2 Rollback gescheitert oder Abbruch.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

USER_AGENT = "backsafe-deploy/1.0 (+https://github.com/kvnflx/github)"
STATUS_OK = {"finished"}
STATUS_FAILED = {"failed", "error", "cancelled", "cancelled-by-user"}


def _json_request(url, method="GET", body=None, headers=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if data is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return json.loads(raw) if raw else {}


class Coolify:
    def __init__(self, base_url, token, sleep=time.sleep):
        self.base = base_url.rstrip("/") + "/api/v1"
        self.auth = {"Authorization": f"Bearer {token}"}
        self.sleep = sleep

    def _call(self, method, path, body=None):
        return _json_request(self.base + path, method, body, self.auth)

    def deployments(self, app):
        return self._call("GET", f"/deployments/applications/{app}?take=20").get("deployments", [])

    def current_commit(self, app):
        for dep in self.deployments(app):
            if dep.get("status") in STATUS_OK:
                return dep.get("commit")
        return None

    def deploy(self, app):
        return self._call("POST", f"/deploy?uuid={app}")["deployments"][0]["deployment_uuid"]

    def rollback(self, app, commit):
        return self._call("POST", f"/applications/{app}/rollback", {"commit": commit})["deployment_uuid"]

    def status(self, app, deployment):
        try:
            return self._call("GET", f"/deployments/{deployment}").get("status")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
        # Bekannter Coolify-Fehler: gerade beendete Deployments liefern 404, dann in der Liste suchen
        for dep in self.deployments(app):
            if dep.get("deployment_uuid") == deployment:
                return dep.get("status")
        return None

    def wait(self, app, deployment, timeout=900, interval=10):
        waited = 0
        while True:
            st = self.status(app, deployment)
            if st in STATUS_OK:
                return True
            if st in STATUS_FAILED or waited >= timeout:
                return False
            self.sleep(interval)
            waited += interval


def is_latest(repo, branch, sha, token, api_url="https://api.github.com"):
    head = _json_request(f"{api_url.rstrip('/')}/repos/{repo}/commits/{branch}",
                         headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    return head.get("sha") == sha


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except OSError:  # deckt auch URLError ab
        return 0, ""


def smoke(url, keyword, sha, attempts=10, delay=15, sleep=time.sleep):
    """Seite antwortet 200 mit Schlüsselwort und version.txt enthält genau diesen Commit.

    Der Parameter v umgeht den Cloudflare-Cache, sonst könnte eine alte Kopie grün melden.
    """
    base = url.rstrip("/")
    for i in range(attempts):
        status, body = fetch(f"{base}/?v={sha}")
        vstatus, vbody = fetch(f"{base}/version.txt?v={sha}")
        if status == 200 and keyword in body and vstatus == 200 and vbody.strip() == sha:
            return True
        print(f"Smoke-Test {i + 1}/{attempts}: Seite {status}, version.txt {vstatus} '{vbody.strip()[:12]}'")
        if i < attempts - 1:
            sleep(delay)
    return False


def notify(ntfy_url, title, message, priority=3):
    if not ntfy_url:
        print(f"[ohne ntfy] {title}: {message}")
        return False
    base, topic = ntfy_url.rstrip("/").rsplit("/", 1)
    try:
        _json_request(base + "/", "POST", {"topic": topic, "title": title, "message": message, "priority": priority})
        return True
    except OSError as e:  # deckt auch URLError ab
        print(f"ntfy nicht erreichbar ({e}): {title}: {message}", file=sys.stderr)
        return False


def run_deploy(a, api, notify_fn, latest_fn=None, sleep=time.sleep):
    name = a.name or a.app
    short = a.sha[:7]
    if latest_fn and not latest_fn(a.sha):
        print(f"{short} ist nicht mehr der neueste Commit, ein späterer Lauf deployt. Übersprungen.")
        return 0
    previous = api.current_commit(a.app)
    print(f"Live vor dem Deploy: {previous or 'nichts'}")
    deployed = api.wait(a.app, api.deploy(a.app), a.timeout)
    if deployed and smoke(a.url, a.keyword, a.sha, a.attempts, a.delay, sleep):
        print(f"{name}: {short} ist live")
        return 0
    if not deployed and previous and smoke(a.url, a.keyword, previous, a.attempts, a.delay, sleep):
        notify_fn(f"Deploy fehlgeschlagen: {name}",
                  f"Build oder Deployment für {short} fehlgeschlagen. Die vorige Version {previous[:7]} läuft unverändert weiter.", 4)
        return 1
    reason = "Smoke-Test fehlgeschlagen" if deployed else "Build oder Deployment fehlgeschlagen"
    print(f"{name}: {reason}")
    if not previous or previous == a.sha:
        notify_fn(f"Deploy fehlgeschlagen: {name}", f"{reason} für {short}. Kein Vorgänger für einen Rollback vorhanden.", 4)
        return 1
    rolled = api.wait(a.app, api.rollback(a.app, previous), a.timeout)
    if rolled and smoke(a.url, a.keyword, previous, a.attempts, a.delay, sleep):
        notify_fn(f"Rollback: {name}", f"{reason} für {short}. Zurück auf {previous[:7]}, die Seite antwortet wieder.", 4)
        return 1
    notify_fn(f"Rollback fehlgeschlagen: {name}",
              f"{reason} für {short}, Rollback auf {previous[:7]} hat nicht geklappt. Sofort prüfen: {a.url}", 5)
    return 2


def main(argv=None):
    p = argparse.ArgumentParser(description="Coolify-Deploy mit Smoke-Test und Rollback")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("deploy")
    d.add_argument("--app", required=True)
    d.add_argument("--url", required=True)
    d.add_argument("--keyword", required=True)
    d.add_argument("--sha", required=True)
    d.add_argument("--name", default="")
    d.add_argument("--repo", default="")
    d.add_argument("--branch", default="main")
    d.add_argument("--timeout", type=int, default=900)
    d.add_argument("--attempts", type=int, default=10)
    d.add_argument("--delay", type=int, default=15)
    n = sub.add_parser("notify")
    n.add_argument("--title", required=True)
    n.add_argument("--message", required=True)
    n.add_argument("--priority", type=int, default=3)
    a = p.parse_args(argv)

    ntfy_url = os.environ.get("NTFY_URL", "")
    if a.cmd == "notify":
        notify(ntfy_url, a.title, a.message, a.priority)
        return 0

    token = os.environ.get("COOLIFY_TOKEN", "")
    if not token:
        print("COOLIFY_TOKEN fehlt", file=sys.stderr)
        return 2
    api = Coolify(os.environ.get("COOLIFY_URL", "https://app.coolify.io"), token)
    latest_fn = None
    if a.repo:
        gh_token = os.environ.get("GITHUB_TOKEN", "")
        gh_api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
        latest_fn = lambda sha: is_latest(a.repo, a.branch, sha, gh_token, gh_api)  # noqa: E731
    try:
        return run_deploy(a, api, lambda t, m, prio=3: notify(ntfy_url, t, m, prio), latest_fn)
    except Exception as e:  # jede unerwartete Lage muss gemeldet werden, nicht still enden
        notify(ntfy_url, f"Deploy abgebrochen: {a.name or a.app}",
               f"{type(e).__name__}: {e}. Zustand der Seite prüfen: {a.url}", 5)
        print(f"Abbruch: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
