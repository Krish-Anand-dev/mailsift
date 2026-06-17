# MailSift

> Bulk email verification — syntax checks, MX records, SMTP probing, catch-all detection, and reputation analysis, all in one place.

**Live demo:** [mailsift.vercel.app](https://mailsift-one.vercel.app) &nbsp;·&nbsp; **Backend:** [Render](https://render.com)

---
<img width="1728" height="887" alt="image" src="https://github.com/user-attachments/assets/bc6d5f14-2d30-41e6-849a-d030ade109fe" />

## What It Does

MailSift takes a list of email addresses — either uploaded as a CSV or pasted directly into the page — runs them through a multi-layer verification pipeline, and gives you downloadable results split by outcome: **Valid**, **Risky**, or **Invalid**.

Every email goes through up to seven checks before it's categorized:

1. **Syntax validation** — confirms the address is structurally valid.
2. **Disposable domain detection** — flags addresses from throwaway providers like Mailinator and Guerrilla Mail.
3. **Role-based address detection** — flags generic inboxes (`info@`, `admin@`, `support@`, etc.) that are unlikely to belong to a real person.
4. **MX record lookup** — verifies the domain has a valid, working mail server.
5. **Catch-all probe** — before trusting SMTP results, MailSift sends a probe to a random address on the domain. If the server accepts anything, it's flagged as a catch-all and handed off to the reputation API instead.
6. **SMTP mailbox verification** — connects directly to the mail server and probes whether the specific mailbox exists, without sending an actual email.
7. **Abstract Email Reputation API fallback** — used when SMTP is unavailable, rate-limited, or when the domain is a catch-all. Provides a deliverability verdict based on reputation signals.

---

## Input Methods

### Upload a CSV

Prepare a `.csv` file with a column named exactly `email` (lowercase):

```csv
email
john@example.com
test@gmail.com
invalid@domain.xyz
```

Click the upload area (or drag and drop your file onto it) and verification starts immediately.

### Paste Emails Directly

No CSV needed. Paste a list of addresses into the text area below the upload box. Supported separators are newlines, commas, and semicolons:

```
john@gmail.com
test@yahoo.com
hello@example.com
```

or

```
john@gmail.com, test@yahoo.com; hello@example.com
```

Click **Verify Emails** and the job starts just like a CSV upload.

---

## Tracking Progress

Each verification job appears as a card on the page showing:

- A live progress bar and percentage.
- A row counter (`row X of Y`).
- A live log of the most recent result, updating every second.

Jobs run in the background — you can submit multiple at once and track them all simultaneously. Each card has a **Cancel** button to stop a running job early.

---

## Downloading Results

Once a job finishes, the job card displays a summary of results and four download buttons:

| Button | What you get |
|---|---|
| **⬇ All Results** | The full processed list with `status` and `reason` columns appended |
| **✓ Valid** | Only emails that passed all checks |
| **⚠ Risky** | Emails where verification was inconclusive |
| **✕ Bad** | Risky and Invalid emails combined — useful for suppression lists |

Each download is a `.csv` file containing the original columns from your input plus `status` and `reason`, ready to re-import into any CRM, ESP, or spreadsheet.

---

## Result Categories

| Status | Meaning |
|---|---|
| **Valid** | Passed syntax, MX, and SMTP checks — mailbox appears deliverable |
| **Risky** | Domain is a catch-all, SMTP was unreachable, or reputation is uncertain |
| **Invalid** | Bad syntax, no MX record, disposable domain, role-based address, or SMTP rejection |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask, Flask-CORS |
| DNS verification | dnspython |
| SMTP verification | Python `smtplib` |
| Reputation fallback | Abstract Email Reputation API |
| Frontend hosting | Vercel |
| Backend hosting | Render |

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Krish-Anand-dev/mailsift.git
cd mailsift
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:

```env
ABSTRACT_API_KEY=your_api_key_here
```

Get a free key at [abstractapi.com](https://www.abstractapi.com/api/email-verification-validation-api).

Start the server:

```bash
python app.py
```

Backend runs at `http://localhost:5050`.

### 3. Open the frontend

Open `public/index.html` in your browser, or serve it with any static file server:

```bash
npx serve public
```

---

## API Reference

### `POST /verify`

Start a verification job. Accepts either a CSV file upload or a JSON body.

**CSV upload:**
```
Content-Type: multipart/form-data
file: <your .csv file>
```

**Pasted emails:**
```json
Content-Type: application/json

{ "emails": "a@example.com\nb@example.com" }
```

Returns:
```json
{ "job_id": "uuid" }
```

---

### `GET /progress?job_id=<id>`

```json
{ "percent": 42, "row": 21, "total": 50, "done": false }
```

### `GET /log?job_id=<id>`

Returns the latest log line as plain text.

### `GET /stats?job_id=<id>`

```json
{ "valid": 30, "risky": 10, "invalid": 10 }
```

### `GET /download?job_id=<id>&type=<filter>`

`type` options: `all` · `valid` · `risky` · `risky_invalid`

Returns a filtered `.csv` file.

### `POST /cancel?job_id=<id>`

Stops a running job. Returns `204 No Content`.

---

## Limitations

- Some providers (notably Google, Microsoft) block SMTP probing and will always fall back to the reputation API.
- Catch-all domains cannot be verified at the mailbox level — results are always `Risky`.
- Verification speed depends on mail server response times. Large lists may take a while.
- The free tier of Abstract API has a monthly request limit.

---

## Use Cases

- Cleaning cold outreach lists before a campaign
- Validating lead database imports
- Removing invalid addresses before an ESP upload
- Filtering contact exports from CRMs
- Building suppression lists from Risky + Invalid results

---

## Author

**Krish Anand**
GitHub: [github.com/Krish-Anand-dev](https://github.com/Krish-Anand-dev)
LinkedIn: [linkedin.com/in/krish-anand-](https://www.linkedin.com/in/krish-anand-/)

---

## License

MIT
