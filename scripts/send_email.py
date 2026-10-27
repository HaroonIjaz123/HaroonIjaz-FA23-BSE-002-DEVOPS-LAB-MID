"""Bonus: e-mail the test report (body + attached test-report.json).

Credentials come from environment variables (GitHub secrets), never from code.
"""
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

USER = os.getenv("SMTP_USERNAME", "")
PASSWORD = os.getenv("SMTP_PASSWORD", "")
TO = os.getenv("EMAIL_TO", "")
HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
PORT = int(os.getenv("SMTP_PORT", "465"))


def build_message():
    with open("test-report.json", encoding="utf-8") as f:
        report = json.load(f)
    with open("email-body.txt", encoding="utf-8") as f:
        body = f.read()
    summary = report["summary"]
    msg = EmailMessage()
    msg["Subject"] = (f"[CI {summary['overall_status']}] {report['repository']} "
                      f"@ {report['commit_sha'][:7]} "
                      f"({summary['passed']}/{summary['total']} passed)")
    msg["From"] = USER
    msg["To"] = TO
    msg.set_content(body)
    with open("test-report.json", "rb") as f:
        msg.add_attachment(f.read(), maintype="application",
                           subtype="json", filename="test-report.json")
    return msg


def send(msg):
    if PORT == 465:
        with smtplib.SMTP_SSL(HOST, PORT, context=ssl.create_default_context(),
                              timeout=30) as server:
            server.login(USER, PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(HOST, PORT, timeout=30) as server:
            if PORT == 587:
                server.starttls(context=ssl.create_default_context())
                server.login(USER, PASSWORD)
            server.send_message(msg)


if __name__ == "__main__":
    if not (USER and PASSWORD and TO):
        print("SMTP_USERNAME / SMTP_PASSWORD / EMAIL_TO not set - e-mail skipped.")
        sys.exit(0)
    send(build_message())
    print(f"Report e-mailed to {TO}")
