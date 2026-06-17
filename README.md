# MailSift

Bulk email verification made simple.

MailSift is a lightweight web application for validating email lists using multiple verification layers including syntax validation, MX record checks, SMTP verification, catch-all detection, and email reputation analysis.

Upload a CSV file containing email addresses and receive categorized results as **Valid**, **Risky**, or **Invalid**, along with downloadable filtered outputs.

---

## Features

### Email Validation Pipeline

MailSift validates emails using multiple checks:

* Syntax validation
* Disposable email detection
* Role-based email detection
* MX record verification
* SMTP mailbox verification
* Catch-all domain detection
* Email reputation analysis (Abstract API fallback)

### Bulk Processing

* Upload CSV files containing email lists
* Real-time progress tracking
* Live verification logs
* Cancel running jobs
* Download filtered results

### Result Categories

| Status  | Description                                              |
| ------- | -------------------------------------------------------- |
| Valid   | Email appears deliverable and passes verification checks |
| Risky   | Verification could not be completed with high confidence |
| Invalid | Email failed validation checks                           |

---

## Tech Stack

### Frontend

* HTML
* CSS
* Vanilla JavaScript

### Backend

* Python
* Flask
* Flask-CORS

### Verification Services

* DNS MX Record Lookup
* SMTP Verification
* Abstract Email Reputation API

### Deployment

* Frontend: Vercel
* Backend: Render

---

## How It Works

### 1. CSV Upload

Upload a CSV file containing an `email` column.

Example:

```csv
email
john@example.com
test@gmail.com
invalid@domain.xyz
```

### 2. Validation Flow

For each email:

1. Validate syntax
2. Check for disposable domains
3. Check for role-based addresses
4. Verify MX records
5. Perform SMTP verification
6. Detect catch-all domains
7. Fall back to Abstract Email Reputation API when necessary

### 3. Results

Emails are categorized as:

* Valid
* Risky
* Invalid

and can be downloaded as filtered CSV files.

---

## Downloads

After processing completes, MailSift generates:

* All Results
* Valid Emails
* Risky Emails
* Risky + Invalid Emails

---

## Running Locally

### Clone Repository

```bash
git clone https://github.com/Krish-Anand-dev/mailsift.git
cd mailsift
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
ABSTRACT_API_KEY=your_api_key_here
```

Start the backend:

```bash
python app.py
```

Backend runs on:

```text
http://localhost:5050
```

### Frontend

Open:

```text
public/index.html
```

or serve it using any static web server.

---

## API Endpoints

### Start Verification

```http
POST /verify
```

Upload CSV file and create a verification job.

### Progress

```http
GET /progress?job_id=<id>
```

Retrieve current progress.

### Logs

```http
GET /log?job_id=<id>
```

Retrieve latest verification log.

### Statistics

```http
GET /stats?job_id=<id>
```

Get counts for valid, risky, and invalid emails.

### Download Results

```http
GET /download?job_id=<id>&type=<filter>
```

Available filters:

* all
* valid
* risky
* risky_invalid

### Cancel Job

```http
POST /cancel?job_id=<id>
```

Stop a running verification job.

---

## Example Use Cases

* Cleaning outreach lists
* Validating lead databases
* Removing invalid emails before campaigns
* Verifying contact exports
* Filtering disposable or risky addresses

---

## Limitations

* Some mail providers intentionally obscure mailbox existence.
* Catch-all domains reduce verification certainty.
* SMTP verification behavior varies between providers.
* Verification accuracy depends on external mail server responses.

---

## Author

**Krish Anand**

GitHub: https://github.com/Krish-Anand-dev
LinkedIN: https://www.linkedin.com/in/krish-anand-/
---

## License

MIT License
