import json
import os
from urllib.parse import urlparse


from flask import Flask, redirect, render_template_string, request, url_for

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Assignment Submission Portal</title>
  <style>
    :root {
      --navy: #1f3864; --blue: #2e5597; --bg: #f2f5fb; --card: #ffffff;
      --text: #1d2433; --muted: #667085; --line: #e3e8f2;
      --err-bg: #fdecea; --err: #b71c1c; --ok: #1b7f4b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; background: var(--bg); color: var(--text);
      font-family: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
      line-height: 1.5;
    }
    header {
      background: linear-gradient(135deg, var(--navy), var(--blue));
      color: #fff; padding: 36px 16px 70px; text-align: center;
    }
    header h1 { margin: 0 0 6px; font-size: clamp(1.5rem, 4vw, 2.2rem); }
    header p { margin: 0; opacity: .85; font-size: .95rem; }
    main { max-width: 980px; margin: -44px auto 40px; padding: 0 16px; }
    .card {
      background: var(--card); border-radius: 14px; padding: 24px;
      box-shadow: 0 6px 24px rgba(31, 56, 100, .10); margin-bottom: 24px;
    }
    .card h2 { margin: 0 0 16px; font-size: 1.2rem; color: var(--navy); }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .full { grid-column: 1 / -1; }
    label { display: block; margin-bottom: 6px; font-weight: 600; font-size: .9rem; }
    input {
      width: 100%; padding: 11px 12px; font-size: 1rem;
      border: 1px solid #cfd7e6; border-radius: 8px; background: #fbfcff;
      transition: border-color .15s, box-shadow .15s;
    }
    input:focus {
      outline: none; border-color: var(--blue); background: #fff;
      box-shadow: 0 0 0 3px rgba(46, 85, 151, .18);
    }
    button {
      margin-top: 20px; width: 100%; padding: 13px 20px; font-size: 1rem;
      font-weight: 600; color: #fff; border: 0; border-radius: 8px; cursor: pointer;
      background: linear-gradient(135deg, var(--blue), var(--navy));
      transition: transform .1s, box-shadow .15s;
    }
    button:hover { box-shadow: 0 6px 16px rgba(31, 56, 100, .30); }
    button:active { transform: translateY(1px); }
    .errors { margin-bottom: 16px; }
    .error {
      background: var(--err-bg); color: var(--err); padding: 10px 14px;
      border-left: 4px solid var(--err); border-radius: 6px; margin-bottom: 8px;
      font-size: .93rem;
    }
    .badge {
      display: inline-block; margin-left: 8px; padding: 1px 10px; font-size: .8rem;
      color: #fff; background: var(--blue); border-radius: 999px; vertical-align: middle;
    }
    .table-wrap { overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th {
      background: var(--navy); color: #fff; text-align: left; padding: 11px 12px;
      font-size: .88rem; white-space: nowrap;
    }
    th:first-child { border-radius: 8px 0 0 0; }
    th:last-child { border-radius: 0 8px 0 0; }
    td { padding: 11px 12px; border-bottom: 1px solid var(--line); word-break: break-word; }
    tbody tr:nth-child(even) { background: #f8faff; }
    tbody tr:hover { background: #eef3fc; }
    td[data-label="Reg. No"] { white-space: nowrap; }
    td a { color: var(--blue); text-decoration: none; }
    td a:hover { text-decoration: underline; }
    .empty { text-align: center; color: var(--muted); padding: 28px 8px; }
    footer { text-align: center; color: var(--muted); font-size: .82rem; padding-bottom: 28px; }

    @media (max-width: 640px) {
      header { padding: 28px 16px 60px; }
      .card { padding: 18px; }
      .grid { grid-template-columns: 1fr; }
      thead { display: none; }
      table, tbody, tr, td { display: block; width: 100%; }
      tbody tr {
        border: 1px solid var(--line); border-radius: 10px;
        margin-bottom: 12px; padding: 6px 0; background: #fff !important;
      }
      td { border: 0; padding: 6px 14px; }
      td[data-label="Reg. No"] { white-space: normal; }
      td::before {
        content: attr(data-label); display: block; font-size: .75rem;
        font-weight: 700; text-transform: uppercase; color: var(--muted);
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>Assignment Submission Portal</h1>
    <p>CSC418 &ndash; DevOps &middot; COMSATS University Islamabad, Attock Campus</p>
  </header>

  <main>
    <section class="card">
      <h2>Submit an assignment</h2>
      {% if errors %}
      <div class="errors">
        {% for e in errors %}<div class="error">{{ e }}</div>{% endfor %}
      </div>
      {% endif %}
      <form method="post" action="/" novalidate>
        <div class="grid">
          <div>
            <label for="name">Name</label>
            <input id="name" name="name" placeholder="e.g. Haroon Ijaz"
                   value="{{ form.get('name', '') }}">
          </div>
          <div>
            <label for="reg_no">Registration Number</label>
            <input id="reg_no" name="reg_no" placeholder="e.g. FA23-BSE-002"
                   value="{{ form.get('reg_no', '') }}">
          </div>
          <div class="full">
            <label for="title">Assignment Title</label>
            <input id="title" name="title" placeholder="e.g. Lab Assignment 2"
                   value="{{ form.get('title', '') }}">
          </div>
          <div class="full">
            <label for="url">Submission URL</label>
            <input id="url" name="url" placeholder="https://github.com/username/repository"
                   value="{{ form.get('url', '') }}">
          </div>
        </div>
        <button type="submit">Submit</button>
      </form>
    </section>

    <section class="card">
      <h2>Saved Submissions <span class="badge">{{ submissions|length }}</span></h2>
      <div class="table-wrap">
        <table id="submissions">
          <thead>
            <tr><th>Name</th><th>Reg. No</th><th>Assignment</th><th>URL</th></tr>
          </thead>
          <tbody>
            {% for s in submissions %}
            <tr>
              <td data-label="Name">{{ s.name }}</td>
              <td data-label="Reg. No">{{ s.reg_no }}</td>
              <td data-label="Assignment">{{ s.title }}</td>
              <td data-label="URL"><a href="{{ s.url }}" target="_blank" rel="noopener noreferrer">{{ s.url }}</a></td>
            </tr>
            {% else %}
            <tr><td class="empty" colspan="4">No submissions yet. Be the first to submit.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <footer>Haroon Ijaz &middot; FA23-BSE-002 &middot; CSC418 Lab Midterm</footer>
</body>
</html>
"""


def is_valid_url(value):
    """A URL is valid if it is http(s), has a host and contains no spaces."""
    value = (value or "").strip()
    if not value or " " in value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    # # creating defect 
    # parsed = urlparse(value) 
    # return True    


def validate_submission(form):
    errors = []
    if not form.get("name", "").strip():
        errors.append("Name is required.")
    if not form.get("reg_no", "").strip():
        errors.append("Registration number is required.")
    if not form.get("title", "").strip():
        errors.append("Assignment title is required.")
    url = form.get("url", "").strip()
    if not url:
        errors.append("Submission URL is required.")
    elif not is_valid_url(url):
        errors.append("Submission URL is not a valid http(s) URL.")
    return errors


def load_submissions(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_submission(path, record):
    data = load_submissions(path)
    data.append(record)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_app(data_file="submissions.json"):
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            form = request.form
            errors = validate_submission(form)
            if errors:
                return (
                    render_template_string(
                        PAGE, errors=errors, form=form,
                        submissions=load_submissions(data_file)),
                    400,
                )
            save_submission(data_file, {
                "name": form["name"].strip(),
                "reg_no": form["reg_no"].strip(),
                "title": form["title"].strip(),
                "url": form["url"].strip(),
            })
            return redirect(url_for("index"))
        return render_template_string(
            PAGE, errors=[], form={}, submissions=load_submissions(data_file))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)