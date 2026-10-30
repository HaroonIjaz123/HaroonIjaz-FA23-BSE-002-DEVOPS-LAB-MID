# Assignment Submission Portal

CSC418 DevOps Lab Midterm | Haroon Ijaz (FA23-BSE-002)

This project uses React for the portal and Node.js for the submission API, CI report sender, email sender, and local report receiver. The API stores submissions in `submissions.json`. GitHub Pages is static, so its build stores submissions in the visitor's browser.

## Requirements

- Node.js 22 or newer and npm
- ngrok installed and connected to an ngrok account for GitHub Actions to reach your local report receiver

## Run the portal locally

```bash
npm ci
npm start
```

Open http://localhost:5000. The API saves submissions in `submissions.json`. Set `PORT` to change the app port or `SUBMISSIONS_FILE` to choose another data file.

For frontend development with Vite, run `npm start` in one terminal and `npm run dev` in another, then open http://localhost:5173.

## Test and build

```bash
npm test
npm run build
```

The existing valid submission, missing registration number, and invalid URL cases remain covered. Additional tests cover required fields, whitespace, URL variants, trimming, JSON persistence, and CI report summaries.

## Send GitHub Actions reports to your computer with ngrok

GitHub-hosted Actions cannot reach `localhost` on your computer directly. Keep the report receiver and ngrok tunnel running while a GitHub Actions run is sending its report.

1. In your ngrok account, get an authtoken and configure the ngrok agent:

   ```bash
   ngrok config add-authtoken "YOUR_NGROK_AUTHTOKEN"
   ```

2. Start the report receiver in a terminal. Use the same long random token in the receiver and GitHub secret:

   ```bash
   REPORT_TOKEN="your-long-random-report-token" npm run receiver
   ```

   The receiver listens on port 5050 and saves reports as `test-report.json` in the project directory. You can set `RECEIVER_PORT` and `REPORT_FILE` to change those defaults.

3. In a second terminal, expose the receiver port:

   ```bash
   ngrok http 5050
   ```

   Copy the HTTPS forwarding address printed by ngrok and append `/report`, for example `https://example.ngrok-free.app/report`.

4. In the GitHub repository, open **Settings → Secrets and variables → Actions** and add:

   | Secret | Value |
   | --- | --- |
   | `RECEIVER_URL` | Your ngrok HTTPS URL ending in `/report` |
   | `REPORT_TOKEN` | The exact token used to start the local receiver |
   | `SMTP_USERNAME` | Sender email address (optional) |
   | `SMTP_PASSWORD` | Sender app password (optional) |
   | `EMAIL_TO` | Report recipient (optional) |

Push to GitHub while both local processes are running. Actions runs the tests and React build, creates a JSON report, posts it through the ngrok tunnel, and stores the report as an Actions artifact. If ngrok gives you a new URL, update `RECEIVER_URL`. If the receiver or tunnel is offline, report delivery fails and the report remains available as an artifact. Email is skipped unless SMTP credentials are set.

## GitHub Pages

The workflow deploys the static React build on pushes to `main`. Enable GitHub Pages using the `github-pages` environment if the repository has not used Pages before. The Pages version uses browser storage; the Node API is not hosted by GitHub Pages.

## Project layout

```text
src/main.jsx               React portal
src/validation.js          Submission validation
src/styles.css             Portal styling
server.js                  Express submission API and JSON persistence
receiver.js                Node report receiver
scripts/build-report.js    Creates detailed CI JSON report
scripts/send-report.js     Posts the report to the ngrok receiver
scripts/send-email.js      Optional SMTP email with JSON attachment
test/server.test.js        Node test suite
.github/workflows/ci.yml  Tests, report delivery, email, and Pages deployment
```
