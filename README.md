# Recruiter Email Tracker

An automated tool to parse, filter, and track recruiter emails from your Gmail inbox. It automatically extracts recruiter names, email addresses, and company names, tracks email frequency, and outputs everything into clean Excel spreadsheets for easy tracking.

## Features

- **Gmail API Integration:** Securely connects to your Gmail account using OAuth 2.0 to fetch received and sent emails.
- **Smart Recruiter Parsing:** Automatically parses name, email, and company details from headers.
- **Domain & System Email Filtering:** Excludes personal email domains (like `@gmail.com`, `@yahoo.com`), system alerts (like `@dice.com`, `@linkedin.com`), and bounce/no-reply prefixes.
- **Incremental Scanning:** Caches processed email IDs so it only scans new messages on subsequent runs.
- **Excel Reporting:** Automatically generates and updates:
  - `data/recruiters.xlsx` — Tracked recruiters, email counts, and first/last seen timestamps.
  - `data/sent_emails.xlsx` — History of sent emails, subjects, dates, and snippets.

---

## Prerequisites

- **Python 3.8** or higher
- A Google Account

---

## Setup Guide

### 1. Clone the Project
Clone this repository to your local machine and navigate into the project directory:
```bash
git clone <your-repository-url>
cd recruters-trackers
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to manage dependencies locally:

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Enable Google Gmail API & Get Credentials
Because Gmail access is protected, you must set up your own Google API app:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `Recruiter-Tracker`).
3. Search for **Gmail API** in the API library and click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - Select User Type: **External**.
   - Fill in the required developer email fields.
   - **Crucial:** Add your own Gmail address under **Test Users** (since the app is in test mode, only approved test users can authorize it).
5. Create Credentials:
   - Click on the **Credentials** tab on the left.
   - Click **Create Credentials** -> **OAuth Client ID**.
   - Select **Desktop App** as the Application Type.
   - Give it a name and click **Create**.
6. Download the credential file:
   - Next to your new Client ID, click the download button (📥 JSON icon).
   - Rename the downloaded file to exactly **`credentials.json`**.
   - Place this file in the `gmail/` folder of your project:
     ```text
     gmail/credentials.json
     ```

---

## Running the Application

Once `credentials.json` is in the `gmail/` directory, execute:

```bash
python main.py
```

### What to expect on the first run:
1. A browser window will automatically open asking you to log in to your Google Account.
2. You will see a warning stating *"Google hasn't verified this app"* (this is normal for self-created developer apps).
3. Click **Advanced** and then click **Go to [Project Name] (unsafe)**.
4. Grant the requested permissions for Gmail.
5. Once authorized, a file named `gmail/token.json` is generated locally. On all future runs, the script will log in automatically without opening the browser.

---

## Project Structure

```text
├── data/                       # (Auto-generated) Contains spreadsheets & local caches
│   ├── recruiters.xlsx         # Consolidated Excel file of all tracked recruiters
│   ├── sent_emails.xlsx        # Excel tracking of sent outreach emails
│   └── *_cache.json            # Local JSON cache databases to speed up scanning
├── extractor/                  # Parsing and information extraction utilities
├── gmail/                      # Gmail API integration logic
│   ├── credentials.json        # [USER SETUP] Google OAuth credential file
│   ├── token.json              # (Auto-generated) Google OAuth token file
│   └── ...
├── storage/                    # Excel formatting and cache management
├── utils/                      # Helper parsers
├── config.py                   # User domain filters, signature markers, and variables
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git exclude settings
```

## Customization

You can adjust rules by modifying the [config.py](config.py) file:
- **`MAX_EMAILS`**: Number of recent emails to process per run.
- **`BLOCKED_DOMAINS`**: Domains you want to skip entirely (e.g., job boards, system alerts).
- **`PERSONAL_DOMAINS`**: Email providers to ignore (like Gmail/Yahoo) to avoid tracking friends/family.
