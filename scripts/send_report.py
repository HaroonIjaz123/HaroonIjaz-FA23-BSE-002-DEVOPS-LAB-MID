"""Build test-report.json from the JUnit XML and POST it to the receiver."""
import datetime
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

XML_PATH = os.getenv("JUNIT_XML", "results.xml")


def parse_tests(path):
    if not os.path.exists(path):
        return [{"name": "test-suite", "result": "failed",
                 "failure_message": "No results.xml was produced"}]
    tests = []
    for case in ET.parse(path).getroot().iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is not None:
            message = (problem.get("message") or problem.text or "").strip()
            tests.append({"name": case.get("name"), "result": "failed",
                          "failure_message": message})
        elif case.find("skipped") is not None:
            tests.append({"name": case.get("name"), "result": "skipped",
                          "failure_message": None})
        else:
            tests.append({"name": case.get("name"), "result": "passed",
                          "failure_message": None})
    return tests


def build_report():
    tests = parse_tests(XML_PATH)
    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)
    return {
        "repository": os.getenv("GITHUB_REPOSITORY", "local/repo"),
        "branch": os.getenv("GITHUB_REF_NAME", "local"),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "overall_status": "PASSED" if failed == 0 and tests else "FAILED",
        },
        "tests": tests,
    }


def email_body(report):
    s = report["summary"]
    lines = [
        f"Repository : {report['repository']}",
        f"Branch     : {report['branch']}",
        f"Commit     : {report['commit_sha']}",
        f"Run ID     : {report['run_id']}",
        f"Result     : {s['overall_status']}",
        f"Total/Passed/Failed : {s['total']}/{s['passed']}/{s['failed']}",
        "",
    ]
    for t in report["tests"]:
        line = f"- {t['name']}: {t['result']}"
        if t["failure_message"]:
            line += f" ({t['failure_message'][:200]})"
        lines.append(line)
    return "\n".join(lines)


def post_report(report, url, token):
    data = json.dumps(report).encode()
    headers = {"Content-Type": "application/json",
               "X-Report-Token": token,
               "ngrok-skip-browser-warning": "true"}
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=20) as resp:
                print("Receiver replied:", resp.status, resp.read().decode())
                return True
        except Exception as exc:                      # noqa: BLE001
            print(f"Attempt {attempt} failed: {exc}")
            time.sleep(3)
    return False


if __name__ == "__main__":
    report = build_report()
    with open("test-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    with open("email-body.txt", "w", encoding="utf-8") as f:
        f.write(email_body(report))
    print(json.dumps(report["summary"]))

    url = os.getenv("RECEIVER_URL")
    if not url:
        print("RECEIVER_URL is not set - report saved locally only.")
        sys.exit(0)
    if not post_report(report, url, os.getenv("REPORT_TOKEN", "")):
        sys.exit(1)
