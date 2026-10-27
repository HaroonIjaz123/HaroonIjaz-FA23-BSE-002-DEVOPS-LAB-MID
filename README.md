# Assignment Submission Portal with Automated Testing

CSC418 DevOps - Lab Midterm | Haroon Ijaz (FA23-BSE-002)

A small Flask web app where students submit an assignment link. Every push is
tested automatically by GitHub Actions and the test report is delivered to a
receiver running on the local computer.

## Requirements
- Python 3.10+ and Git
- ngrok (or cloudflared) to expose the local receiver to GitHub

## 1. Run the application
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## 2. Run the tests
```bash
python -m pytest -v
```

## 3. Start the report receiver
```bash
# terminal 1
python receiver.py                # listens on port 5050
# terminal 2
ngrok http 5050                   # copy the https forwarding URL
```
Add these repository secrets (Settings > Secrets and variables > Actions):

| Secret | Value |
|---|---|
| RECEIVER_URL | https://YOUR-TUNNEL-URL/report |
| REPORT_TOKEN | any shared password (also set it in the receiver terminal) |
| SMTP_USERNAME | Gmail address that sends the report (email bonus) |
| SMTP_PASSWORD | Gmail app password (email bonus) |
| EMAIL_TO | recipient, defaults to harooonijaz123@gmail.com |

After every push the report is saved next to `receiver.py` as `test-report.json`.

## Project layout
```
app.py                  Flask application
tests/test_app.py       automated tests
receiver.py             local HTTP receiver
scripts/send_report.py  builds and sends the JSON report
scripts/send_email.py   e-mails the report (bonus)
site/index.html         static demo published to GitHub Pages
.github/workflows/ci.yml  CI pipeline
```

