import os
from datetime import datetime

from config import (
    BLOCKED_DOMAINS,
    PERSONAL_DOMAINS,
    BLOCKED_EMAIL_PREFIXES
)

from gmail.reader import GmailReader
from utils.recruiter_parser import RecruiterParser
from storage.cache_manager import CacheManager
from storage.excel_writer import ExcelWriter

def build_paths():
    project_root = os.path.dirname(
        os.path.abspath(__file__)
    )

    data_dir = os.path.join(
        project_root,
        "data"
    )

    os.makedirs(
        data_dir,
        exist_ok=True
    )

    cache_file = os.path.join(
        data_dir,
        "recruiter_cache.json"
    )

    excel_file = os.path.join(
        data_dir,
        "recruiters.xlsx"
    )

    sent_cache_file = os.path.join(
        data_dir,
        "sent_emails_cache.json"
    )

    sent_excel_file = os.path.join(
        data_dir,
        "sent_emails.xlsx"
    )

    processed_incoming_file = os.path.join(
        data_dir,
        "processed_incoming_cache.json"
    )

    return (
        cache_file,
        excel_file,
        sent_cache_file,
        sent_excel_file,
        processed_incoming_file
    )

def is_blocked_domain(domain):
    if not domain:
        return False

    domain = domain.lower()

    for blocked in BLOCKED_DOMAINS:

        if blocked in domain:
            return True

    return False

def is_personal_domain(domain):
    if not domain:
        return False

    domain = domain.lower()

    return domain in PERSONAL_DOMAINS

def is_blocked_email(recruiter_email):
    if not recruiter_email:
        return False

    username = recruiter_email.split("@")[0]

    username = username.lower()

    for blocked in BLOCKED_EMAIL_PREFIXES:

        if username.startswith(blocked):
            return True

    return False

def create_recruiter_record(
    recruiter_name,
    recruiter_email,
    company
):

    now = datetime.now().isoformat()

    return {

        "recruiter_name":
            recruiter_name,

        "recruiter_email":
            recruiter_email,

        "company":
            company,

        "email_count":
            1,

        "first_seen":
            now,

        "last_seen":
            now
    }

def process_email(
    email,
    cache_manager
):
    parsed = RecruiterParser.parse(
        email["from"]
    )

    recruiter_name = parsed[
        "recruiter_name"
    ]

    recruiter_email = parsed[
        "recruiter_email"
    ]

    domain = parsed[
        "domain"
    ]

    company = parsed[
        "company"
    ]

    if not recruiter_email:
        return

    if is_blocked_email(
        recruiter_email
    ):

        print(
            f"SKIPPED SYSTEM EMAIL: {recruiter_email}"
        )

        return

    if is_blocked_domain(
        domain
    ):

        print(
            f"SKIPPED BLOCKED DOMAIN: {domain}"
        )

        return

    if is_personal_domain(
        domain
    ):

        print(
            f"SKIPPED PERSONAL DOMAIN: {domain}"
        )

        return

    if cache_manager.recruiter_exists(
        recruiter_email
    ):
        cache_manager.increment_email_count(
            recruiter_email
        )
        return

    recruiter = create_recruiter_record(
        recruiter_name,
        recruiter_email,
        company
    )

    cache_manager.create_recruiter(
        recruiter
    )

    print()
    print("=" * 90)

    safe_name = recruiter_name.encode('ascii', 'ignore').decode('ascii')
    safe_company = company.encode('ascii', 'ignore').decode('ascii')

    print(
        f"Recruiter Name : {safe_name}"
    )

    print(
        f"Recruiter Email: {recruiter_email}"
    )

    print(
        f"Company        : {safe_company}"
    )

    print(
        f"Email Count    : 1"
    )

    print("=" * 90)

def process_sent_emails(
    reader,
    sent_cache_manager,
    sent_excel_writer
):
    print("\nFetching sent emails...")
    processed_sent_msg_ids = {key.split("_")[0] for key in sent_cache_manager.cache.keys()}
    sent_emails = reader.get_sent_emails(processed_sent_msg_ids)

    print(
        f"\nProcessing {len(sent_emails)} sent emails...\n"
    )

    for email in sent_emails:
        msg_id = email["message_id"]
        to_header = email.get("to", "")
        if not to_header:
            continue

        recipients = [r.strip() for r in to_header.split(",") if r.strip()]

        for recipient in recipients:
            parsed = RecruiterParser.parse(recipient)
            recruiter_name = parsed["recruiter_name"]
            recruiter_email = parsed["recruiter_email"]
            domain = parsed["domain"]
            company = parsed["company"]

            if not recruiter_email:
                continue

            if is_blocked_email(recruiter_email):
                continue
            if is_blocked_domain(domain):
                continue
            if is_personal_domain(domain):
                continue

            cache_key = f"{msg_id}_{recruiter_email}"
            if sent_cache_manager.sent_email_exists(cache_key):
                continue

            if not recruiter_name:
                recruiter_name = recruiter_email.split("@")[0].title()

            sent_record = {
                "recruiter_name": recruiter_name,
                "recruiter_email": recruiter_email,
                "company": company,
                "subject": email.get("subject", ""),
                "date": email.get("date", ""),
                "snippet": email.get("snippet", ""),
                "message_id": msg_id
            }

            sent_cache_manager.save_sent_email(cache_key, sent_record)

            safe_name = recruiter_name.encode('ascii', 'ignore').decode('ascii')
            safe_subj = email.get('subject', '').encode('ascii', 'ignore').decode('ascii')
            print(
                f"TRACKED SENT EMAIL to: {safe_name} "
                f"({recruiter_email}) - Subject: {safe_subj}"
            )

    all_sent_records = sent_cache_manager.get_all_sent_emails()
    sent_excel_writer.save_sent_emails(all_sent_records)

def main():
    cache_file, excel_file, sent_cache_file, sent_excel_file, processed_incoming_file = (
        build_paths()
    )

    cache_manager = CacheManager(
        cache_file
    )

    excel_writer = ExcelWriter(
        excel_file
    )

    sent_cache_manager = CacheManager(
        sent_cache_file
    )

    sent_excel_writer = ExcelWriter(
        sent_excel_file
    )

    processed_incoming_cache = CacheManager(
        processed_incoming_file
    )

    reader = GmailReader()

    profile = reader.get_profile()

    print()
    print("=" * 90)

    print(
        f"Connected Gmail: "
        f"{profile['emailAddress']}"
    )

    print("=" * 90)

    processed_incoming_ids = set(processed_incoming_cache.cache.keys())
    emails = reader.get_latest_emails(processed_incoming_ids)

    print(
        f"\nProcessing {len(emails)} received emails...\n"
    )

    for email in emails:

        try:

            process_email(
                email,
                cache_manager
            )
            processed_incoming_cache.cache[email["message_id"]] = True

        except Exception as e:

            print(
                f"ERROR PROCESSING RECEIVED EMAIL: {e}"
            )

    if len(emails) > 0:
        processed_incoming_cache.save_cache()

    recruiters = (
        cache_manager.get_all_recruiters()
    )

    excel_writer.save_recruiters(
        recruiters
    )

    print()

    print(
        f"Total Recruiters: "
        f"{cache_manager.total_recruiters()}"
    )

    print(
        f"Excel Saved: "
        f"{excel_file}"
    )

    try:
        process_sent_emails(
            reader,
            sent_cache_manager,
            sent_excel_writer
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(
            f"ERROR PROCESSING SENT EMAILS: {e}"
        )

if __name__ == "__main__":
    main()
