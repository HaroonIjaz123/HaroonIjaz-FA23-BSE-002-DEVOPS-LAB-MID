import json
import os
from urllib.parse import urlparse

from flask import Flask, redirect, render_template_string, request, url_for

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Assignment Submission Portal</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 30px auto; }
    label { display: block; margin-top: 12px; font-weight: bold; }
    input { width: 100%; padding: 8px; box-sizing: border-box; }
    button { margin-top: 16px; padding: 10px 20px; }
    .error { background: #fdecea; color: #b71c1c; padding: 8px; margin-top: 8px; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { border: 1px solid #999; padding: 6px; text-align: left; }
  </style>
</head>
<body>
  <h1>Assignment Submission Portal</h1>
  {% for e in errors %}<div class="error">{{ e }}</div>{% endfor %}
  <form method="post" action="/">
    <label>Name</label>
    <input name="name" value="{{ form.get('name', '') }}">
    <label>Registration Number</label>
    <input name="reg_no" value="{{ form.get('reg_no', '') }}">
    <label>Assignment Title</label>
    <input name="title" value="{{ form.get('title', '') }}">
    <label>Submission URL</label>
    <input name="url" value="{{ form.get('url', '') }}">
    <button type="submit">Submit</button>
  </form>
  <h2>Saved Submissions</h2>
  <table id="submissions">
    <tr><th>Name</th><th>Reg. No</th><th>Assignment</th><th>URL</th></tr>
    {% for s in submissions %}
    <tr><td>{{ s.name }}</td><td>{{ s.reg_no }}</td><td>{{ s.title }}</td><td>{{ s.url }}</td></tr>
    {% endfor %}
  </table>
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
