import csv
import io
import os
import re
import time
import uuid
import threading
import dns.resolver
import smtplib
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")
print("ABSTRACT KEY PRESENT:", bool(ABSTRACT_API_KEY), flush=True)
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
DISPOSABLE_DOMAINS = {"mailinator.com", "10minutemail.com", "guerrillamail.com"}
ROLE_BASED_PREFIXES = {"info", "support", "admin", "sales", "contact"}

jobs = {}


def smtp_check(email, mx_record):
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo("example.com")
        server.mail("verifier@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code
    except Exception:
        return None


def abstract_verify(email):
    try:
        r = requests.get(
            "https://emailreputation.abstractapi.com/v1/",
            params={
                "api_key": ABSTRACT_API_KEY,
                "email": email,
            },
            timeout=15,
        )

        data = r.json()

        print("=" * 60, flush=True)
        print("ABSTRACT API RESPONSE:", data, flush=True)
        print("=" * 60, flush=True)

        deliverability = (
            data.get("email_deliverability", {})
            .get("status", "")
            .lower()
        )

        if deliverability == "deliverable":
            return "valid", "abstract_deliverable"

        elif deliverability in [
            "undeliverable",
            "invalid",
            "invalid_email"
        ]:
            return "invalid", "abstract_undeliverable"

        elif deliverability:
            return "risky", f"abstract_{deliverability}"

        return "risky", "abstract_no_deliverability"

    except Exception as e:
        print("ABSTRACT ERROR:", str(e), flush=True)
        return "risky", "abstract_error"


def check_email(email):
    if not EMAIL_REGEX.match(email):
        return "invalid", "bad_syntax"

    domain = email.split("@")[1]
    local = email.split("@")[0]

    if domain.lower() in DISPOSABLE_DOMAINS:
        return "invalid", "disposable_domain"
    if local.lower() in ROLE_BASED_PREFIXES:
        return "invalid", "role_based"

    try:
        records = dns.resolver.resolve(domain, "MX")
        mx_record = str(records[0].exchange)
    except Exception:
        return "invalid", "no_mx"

    # Catch-all probe
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo("example.com")
        server.mail("probe@example.com")
        code, _ = server.rcpt(f"doesnotexist123xyzabc@{domain}")
        server.quit()
        if code == 250:
            # Domain accepts all — go straight to Abstract
            return abstract_verify(email)
    except Exception:
        pass

    code = smtp_check(email, mx_record)
    if code in [421, 450, 451, 452, 503]:
        time.sleep(5)
        code = smtp_check(email, mx_record)

    if code == 250:
        return "valid", "smtp_ok"
    elif code == 550:
        return "invalid", "smtp_reject"
    elif code is None:
        # SMTP unreachable — fall back to Abstract
        return abstract_verify(email)
    elif code in [421, 450, 451, 452, 503]:
        # Soft fail — fall back to Abstract
        return abstract_verify(email)
    else:
        return "invalid", f"smtp_{code}"


@app.route("/verify", methods=["POST"])
def verify():
    job_id = str(uuid.uuid4())
    file = request.files["file"]
    content = file.read().decode("utf-8")
    reader = list(csv.DictReader(io.StringIO(content)))
    total = len(reader)
    email_field = next(
        (f for f in reader[0].keys() if f.lower().strip() == "email"), None
    )

    output = io.StringIO()
    fieldnames = list(reader[0].keys()) + ["status", "reason"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    jobs[job_id] = {
        "progress": 0,
        "row": 0,
        "total": total,
        "log": "",
        "cancel": False,
        "output": output,
        "writer": writer,
        "records": reader,
        "email_field": email_field,
        "filename": file.filename,
        "done": False,
    }

    def run():
        for i, row in enumerate(reader, start=1):
            if jobs[job_id]["cancel"]:
                jobs[job_id]["log"] = f"❌ Canceled job {job_id}"
                break
            email = (row.get(email_field) or "").strip()
            if not email:
                status, reason = "invalid", "empty_email"
            else:
                status, reason = check_email(email)
            row["status"], row["reason"] = status, reason
            writer.writerow(row)
            percent = int((i / total) * 100)
            jobs[job_id].update(
                {
                    "progress": percent,
                    "row": i,
                    "log": f"✅ {email} → {status} ({reason})",
                }
            )
        jobs[job_id]["done"] = True

    threading.Thread(target=run).start()
    return jsonify({"job_id": job_id})


@app.route("/progress")
def progress():
    job_id = request.args.get("job_id")
    d = jobs.get(job_id, {})
    return jsonify(
        {
            "percent": d.get("progress", 0),
            "row": d.get("row", 0),
            "total": d.get("total", 0),
            "done": d.get("done", False),
        }
    )


@app.route("/log")
def log():
    job_id = request.args.get("job_id")
    return Response(jobs.get(job_id, {}).get("log", ""), mimetype="text/plain")


@app.route("/cancel", methods=["POST"])
def cancel():
    job_id = request.args.get("job_id")
    if job_id in jobs:
        jobs[job_id]["cancel"] = True
    return "", 204


@app.route("/download")
def download():
    job_id = request.args.get("job_id")
    filter_type = request.args.get("type", "all")
    job = jobs.get(job_id)
    if not job:
        return "Invalid job ID", 404

    job["output"].seek(0)
    reader = list(csv.DictReader(job["output"]))

    if filter_type == "valid":
        filtered = [r for r in reader if r["status"] == "valid"]
    elif filter_type == "risky":
        filtered = [r for r in reader if r["status"] == "risky"]
    elif filter_type == "risky_invalid":
        filtered = [r for r in reader if r["status"] in ("risky", "invalid")]
    else:
        filtered = reader

    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=reader[0].keys())
    w.writeheader()
    for row in filtered:
        w.writerow(row)
    out.seek(0)

    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filter_type}-{job['filename']}"
        },
    )


@app.route("/stats")
def stats():
    job_id = request.args.get("job_id")
    job = jobs.get(job_id)
    if not job:
        return jsonify({})
    job["output"].seek(0)
    reader = list(csv.DictReader(job["output"]))
    counts = {"valid": 0, "risky": 0, "invalid": 0}
    for row in reader:
        s = row.get("status", "invalid")
        counts[s] = counts.get(s, 0) + 1
    return jsonify(counts)


if __name__ == "__main__":
    app.run(debug=True, port=5050)