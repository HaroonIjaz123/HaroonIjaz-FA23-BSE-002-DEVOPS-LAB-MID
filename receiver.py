"""Local HTTP receiver: saves the CI test report as test-report.json."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.getenv("PORT", "5050"))
TOKEN = os.getenv("REPORT_TOKEN", "")          # optional shared secret
OUTPUT = os.getenv("REPORT_FILE", "test-report.json")


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, message):
        body = json.dumps({"message": message}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._reply(200, "Receiver is running. POST reports to /report")

    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, "Not found")
        if TOKEN and self.headers.get("X-Report-Token") != TOKEN:
            return self._reply(401, "Invalid token")
        length = int(self.headers.get("Content-Length", 0))
        try:
            report = json.loads(self.rfile.read(length))
        except ValueError:
            return self._reply(400, "Body is not valid JSON")
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        summary = report.get("summary", {})
        print(f"[receiver] saved {OUTPUT}: commit={report.get('commit_sha', '')[:7]} "
              f"status={summary.get('overall_status')} "
              f"passed={summary.get('passed')}/{summary.get('total')}")
        self._reply(200, "Report saved")


if __name__ == "__main__":
    print(f"[receiver] listening on http://localhost:{PORT}/report")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
