"""Tests für scripts/coolify_deploy.py gegen einen Fake-Server.

Ein einziger lokaler HTTP-Server spielt Coolify-API, Webseite, GitHub-API und ntfy.
"""
import argparse
import os
import sys
import threading
import unittest
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
import coolify_deploy as cd  # noqa: E402

OLD = "a" * 40
NEW = "b" * 40


class World:
    def __init__(self):
        self.live = OLD
        self.keyword = "Barbershop"
        self.history = [{"deployment_uuid": "dep0", "status": "finished", "commit": OLD}]
        self.deploy_outcome = ("finished", NEW)
        self.broken_deploy = False
        self.rollback_outcome = "finished"
        self.status_404 = False
        self.head = NEW
        self.calls = []
        self.notifications = []
        self.user_agents = set()


def make_handler(world):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Testausgabe ruhig halten

        def _send(self, code, body, ctype="application/json"):
            if ctype == "application/json":
                data = json.dumps(body).encode()
            else:
                data = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n)) if n else {}

        def do_GET(self):
            world.user_agents.add(self.headers.get("User-Agent"))
            path = self.path.split("?")[0]
            if path.startswith("/api/v1/deployments/applications/"):
                return self._send(200, {"count": len(world.history), "deployments": world.history})
            if path.startswith("/api/v1/deployments/"):
                uuid = path.rsplit("/", 1)[1]
                if world.status_404:
                    return self._send(404, {"message": "Not found"})
                for dep in world.history:
                    if dep["deployment_uuid"] == uuid:
                        return self._send(200, dep)
                return self._send(404, {"message": "Not found"})
            if path.startswith("/repos/"):
                return self._send(200, {"sha": world.head})
            if path == "/version.txt":
                return self._send(200, (world.live or "") + "\n", "text/plain")
            if path == "/":
                return self._send(200, f"<html><title>{world.keyword}</title></html>", "text/html")
            return self._send(404, {})

        def do_POST(self):
            world.user_agents.add(self.headers.get("User-Agent"))
            path = self.path.split("?")[0]
            body = self._body()
            if path == "/api/v1/deploy":
                world.calls.append(("deploy",))
                status, commit = world.deploy_outcome
                uuid = f"dep{len(world.history)}"
                world.history.insert(0, {"deployment_uuid": uuid, "status": status, "commit": commit})
                if status == "finished":
                    world.live = commit
                    if world.broken_deploy:
                        world.keyword = "502 Bad Gateway"
                return self._send(200, {"deployments": [{"message": "queued", "resource_uuid": "app", "deployment_uuid": uuid}]})
            if path.endswith("/rollback"):
                world.calls.append(("rollback", body["commit"]))
                uuid = f"rb{len(world.history)}"
                world.history.insert(0, {"deployment_uuid": uuid, "status": world.rollback_outcome, "commit": body["commit"]})
                if world.rollback_outcome == "finished":
                    world.live = body["commit"]
                    world.keyword = "Barbershop"
                return self._send(200, {"message": "queued", "deployment_uuid": uuid})
            if path == "/":
                world.notifications.append(body)
                return self._send(200, {"id": "x"})
            return self._send(404, {})

    return Handler


class Base(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.world))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.api = cd.Coolify(self.url, "token", sleep=lambda s: None)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def args(self, **kw):
        a = {"app": "app", "url": self.url, "keyword": "Barbershop", "sha": NEW, "name": "cedre",
             "timeout": 30, "attempts": 2, "delay": 0}
        a.update(kw)
        return argparse.Namespace(**a)

    def deploy(self, latest_fn=None):
        notes = []
        code = cd.run_deploy(self.args(), self.api, lambda t, m, p=3: notes.append((t, m, p)),
                             latest_fn, sleep=lambda s: None)
        return code, notes


class DeployTests(Base):
    def test_erfolgreicher_deploy(self):
        code, notes = self.deploy()
        self.assertEqual(code, 0)
        self.assertEqual(notes, [])
        self.assertEqual(self.world.live, NEW)
        self.assertNotIn("rollback", [c[0] for c in self.world.calls])

    def test_smoke_scheitert_rollback(self):
        self.world.broken_deploy = True
        code, notes = self.deploy()
        self.assertEqual(code, 1)
        self.assertIn(("rollback", OLD), self.world.calls)
        self.assertEqual(self.world.live, OLD)
        self.assertTrue(notes[0][0].startswith("Rollback: cedre"))

    def test_build_scheitert_alte_version_laeuft(self):
        self.world.deploy_outcome = ("failed", NEW)
        code, notes = self.deploy()
        self.assertEqual(code, 1)
        self.assertNotIn("rollback", [c[0] for c in self.world.calls])
        self.assertIn("läuft unverändert weiter", notes[0][1])

    def test_timeout_alte_version_laeuft(self):
        self.world.deploy_outcome = ("in_progress", NEW)
        code, notes = self.deploy()
        self.assertEqual(code, 1)
        self.assertTrue(notes[0][0].startswith("Deploy fehlgeschlagen"))

    def test_erster_deploy_ohne_vorgaenger(self):
        self.world.history = []
        self.world.live = None
        self.world.broken_deploy = True
        code, notes = self.deploy()
        self.assertEqual(code, 1)
        self.assertNotIn("rollback", [c[0] for c in self.world.calls])
        self.assertIn("Kein Vorgänger", notes[0][1])

    def test_rollback_scheitert(self):
        self.world.broken_deploy = True
        self.world.rollback_outcome = "failed"
        code, notes = self.deploy()
        self.assertEqual(code, 2)
        self.assertEqual(notes[0][2], 5)
        self.assertTrue(notes[0][0].startswith("Rollback fehlgeschlagen"))

    def test_status_404_fallback(self):
        self.world.status_404 = True
        code, _ = self.deploy()
        self.assertEqual(code, 0)

    def test_ueberholter_commit_wird_uebersprungen(self):
        code, notes = self.deploy(latest_fn=lambda sha: False)
        self.assertEqual(code, 0)
        self.assertEqual(self.world.calls, [])
        self.assertEqual(notes, [])

    def test_user_agent_bei_jedem_aufruf(self):
        self.deploy()
        self.assertEqual(self.world.user_agents, {cd.USER_AGENT})


class SmokeTests(Base):
    def test_smoke_erkennt_alten_stand(self):
        self.assertFalse(cd.smoke(self.url, "Barbershop", NEW, attempts=1, delay=0, sleep=lambda s: None))

    def test_smoke_erkennt_fehlendes_schluesselwort(self):
        self.world.live = NEW
        self.world.keyword = "Fehlerseite"
        self.assertFalse(cd.smoke(self.url, "Barbershop", NEW, attempts=1, delay=0, sleep=lambda s: None))

    def test_smoke_gruen(self):
        self.world.live = NEW
        self.assertTrue(cd.smoke(self.url, "Barbershop", NEW, attempts=1, delay=0, sleep=lambda s: None))


class HelperTests(Base):
    def test_is_latest(self):
        self.assertTrue(cd.is_latest("kvnflx/x", "main", NEW, "t", self.url))
        self.assertFalse(cd.is_latest("kvnflx/x", "main", OLD, "t", self.url))

    def test_notify_json_mit_umlauten(self):
        self.assertTrue(cd.notify(f"{self.url}/topic123", "Größe", "Text", 4))
        self.assertEqual(self.world.notifications[0],
                         {"topic": "topic123", "title": "Größe", "message": "Text", "priority": 4})

    def test_notify_ohne_url(self):
        self.assertFalse(cd.notify("", "T", "M"))


class MainTests(Base):
    def test_api_nicht_erreichbar_meldet(self):
        env = {"COOLIFY_TOKEN": "t", "COOLIFY_URL": "http://127.0.0.1:9", "NTFY_URL": f"{self.url}/topic"}
        with mock.patch.dict(os.environ, env):
            code = cd.main(["deploy", "--app", "app", "--url", self.url, "--keyword", "Barbershop",
                            "--sha", NEW, "--name", "cedre", "--timeout", "30", "--attempts", "1", "--delay", "0"])
        self.assertEqual(code, 2)
        self.assertEqual(self.world.notifications[0]["priority"], 5)
        self.assertTrue(self.world.notifications[0]["title"].startswith("Deploy abgebrochen"))

    def test_ohne_token_abbruch(self):
        with mock.patch.dict(os.environ, {"COOLIFY_TOKEN": ""}):
            code = cd.main(["deploy", "--app", "a", "--url", self.url, "--keyword", "k", "--sha", NEW])
        self.assertEqual(code, 2)

    def test_cli_notify(self):
        with mock.patch.dict(os.environ, {"NTFY_URL": f"{self.url}/t"}):
            code = cd.main(["notify", "--title", "T", "--message", "M", "--priority", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(self.world.notifications[0]["priority"], 2)


if __name__ == "__main__":
    unittest.main()
