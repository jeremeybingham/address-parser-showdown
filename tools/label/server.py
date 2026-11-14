"""Local server for the blind labeling page (and the adjudication pass). Standard library only; binds to 127.0.0.1.

    uv run python -m tools.label.server label ROUND [--port 8765]
    uv run python -m tools.label.server adjudicate [--port 8765]
    uv run python -m tools.label.server review [--port 8765]   # queue from lint --queue
    uv run python -m tools.label.server revisit [--port 8765]  # every card marked `revisit`, over all rounds

Labels are appended to `local-data/labels/round-N.jsonl` (git-ignored). This module never imports an adapter.
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from schema import labels
from tools.label import store

PAGE = Path(__file__).with_name("page.html")


class App:
    def __init__(self, mode: str, rounds: list[int], log_dir: Path = store.LOG_DIR, rounds_dir: Path = store.ROUNDS):
        self.mode, self.log_dir, self.rounds_dir = mode, log_dir, rounds_dir
        self.rounds = rounds
        self.cards = {n: {c["id"]: c for c in store.load_round(n, rounds_dir)} for n in rounds}
        self.queue = self._load_queue() if mode in ("adjudicate", "review") else []

    def _load_queue(self) -> list[dict]:
        path = self.log_dir / ("review-queue.jsonl" if self.mode == "review" else "adjudication.jsonl")
        return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []

    def meta(self) -> dict:
        return {
            "mode": self.mode,
            "keys": store.key_map(),
            "labels": {n: labels()[n].doc for n in store.leaf_labels()},
        }

    def cards_payload(self) -> list[dict]:
        """Cards to show, in order, with any saved labels. Adjudication cards carry the questions (no parser names)."""
        out = []
        if self.mode == "revisit":
            for n in self.rounds:
                cards = store.gold_cards(n, self.rounds_dir, self.log_dir)
                out += [{**c, "round": n} for c in cards if c.get("revisit")]
        elif self.mode == "label":
            n = self.rounds[0]
            cards = [
                {**c, "round": n, "n": i + 1} for i, c in enumerate(store.gold_cards(n, self.rounds_dir, self.log_dir))
            ]
            # undone cards first (in round order), then the labeled ones for review
            out = [c for c in cards if not c["labeled"]] + [c for c in cards if c["labeled"]]
        else:
            for q in self.queue:
                n = q["round"]
                card = next(c for c in store.gold_cards(n, self.rounds_dir, self.log_dir) if c["id"] == q["id"])
                out.append(
                    {**card, "round": n}
                    | ({"rules": q["rules"]} if self.mode == "review" else {"questions": q["questions"]})
                )
        return out

    def save(self, payload: dict) -> dict:
        n, cid = payload["round"], payload["id"]
        card = self.cards[n][cid]  # KeyError for an unknown card
        phase = {"adjudicate": "adjudicate", "review": "review", "revisit": "review"}.get(self.mode, "label")
        return store.save_card(n, card, payload, phase=phase, log_dir=self.log_dir)


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str = "application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/api/meta":
                self._send(200, json.dumps(app.meta()).encode())
            elif self.path == "/api/cards":
                self._send(200, json.dumps(app.cards_payload()).encode())
            else:
                self._send(404, b"{}")

        def do_POST(self):
            if self.path != "/api/save":
                return self._send(404, b"{}")
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                rec = app.save(payload)
            except (store.CardError, KeyError, ValueError, TypeError, AttributeError) as e:
                return self._send(400, json.dumps({"error": type(e).__name__ + ": " + str(e)[:80]}).encode())
            self._send(200, json.dumps({"ok": True, "ts": rec["ts"]}).encode())

        def log_message(self, *a):  # keep request lines (card ids) out of the terminal
            pass

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["label", "adjudicate", "review", "revisit"])
    ap.add_argument("round", nargs="?", type=int)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--practice", action="store_true", help="use local-data/practice (round 0), not the real rounds")
    a = ap.parse_args()
    if a.mode == "label" and a.round is None:
        ap.error("label needs a round number")
    kw = {}
    if a.practice:
        base = store.ROOT / "local-data" / "practice"
        kw = {"log_dir": base / "labels", "rounds_dir": base}
    rounds = [a.round] if a.mode == "label" else list(range(1, 7 if a.mode == "adjudicate" else 12))
    if a.mode in ("review", "revisit"):  # only the rounds that exist
        rounds = [n for n in rounds if (kw.get("rounds_dir", store.ROUNDS) / f"round-{n}.jsonl").exists()]
    app = App(a.mode, rounds, **kw)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(app))
    print(f"{a.mode} on http://127.0.0.1:{a.port}/ (Ctrl-C to stop)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
