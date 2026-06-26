"""
Recruiter Email Tracker - Main Entry Point.

This module coordinates the entire workflow:
1. Connects to Gmail and fetches recent received and sent emails.
2. Parses recruiter name, email address, and company domains.
3. Filters out personal domains, system accounts, and blocked domains.
4. Caches processed email IDs to prevent redundant processing.
5. Saves tracked recruiter details and sent outreach history into Excel files.
"""

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
    """
    Constructs absolute file paths for cache databases and Excel files.
    
    Ensures that the directory structure (the 'data' folder) exists.
    
    Returns:
        tuple: (cache_file, excel_file, sent_cache_file, sent_excel_file, processed_incoming_file)
    """
    project_root = os.path.dirname(
        os.path.abspath(__file__)
    )

    data_dir = os.path.join(
        project_root,
        "data"
    )

    # Automatically initialize the directory for output logs/spreadsheets
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
    """
    Checks if a domain is part of the blocked domains list (e.g. job boards).
    
    Args:
        domain (str): Domain suffix.
        
    Returns:
        bool: True if blocked, False otherwise.
    """
    if not domain:
        return False

    domain = domain.lower()

    for blocked in BLOCKED_DOMAINS:
        if blocked in domain:
            return True

    return False


def is_personal_domain(domain):
    """
    Checks if the email domain belongs to a personal email provider.
    
    Args:
        domain (str): Domain suffix.
        
    Returns:
        bool: True if personal, False otherwise.
    """
    if not domain:
        return False

    domain = domain.lower()

    return domain in PERSONAL_DOMAINS


def is_blocked_email(recruiter_email):
    """
    Filters out system emails (no-reply, support, etc.) based on email prefixes.
    
    Args:
        recruiter_email (str): Clean email address.
        
    Returns:
        bool: True if email starts with a blocked prefix, False otherwise.
    """
    if not recruiter_email:
        return False

    username = recruiter_email.split("@")[0]
    username = username.lower()

    for blocked in BLOCKED_EMAIL_PREFIXES:
        if username.startswith(blocked):
            return True

    return False


def create_recruiter_record(recruiter_name, recruiter_email, company):
    """
    Creates a new recruiter record dictionary with default tracking values.
    
    Args:
        recruiter_name (str): Recruiter's full name.
        recruiter_email (str): Clean email address.
        company (str): Inferred company name.
        
    Returns:
        dict: Populated recruiter record.
    """
    now = datetime.now().isoformat()

    return {
        "recruiter_name": recruiter_name,
        "recruiter_email": recruiter_email,
        "company": company,
        "email_count": 1,
        "first_seen": now,
        "last_seen": now
    }


def process_email(email, cache_manager):
    """
    Processes an incoming email, extracts recruiter info, and registers it.
    
    Checks sender against email filters (blocked domains, system names, personal
    addresses) and updates or inserts recruiter profile in cache.
    
    Args:
        email (dict): The parsed email message metadata.
        cache_manager (CacheManager): Cache manager instance for recruiters.
    """
    parsed = RecruiterParser.parse(
        email["from"]
    )

    recruiter_name = parsed["recruiter_name"]
    recruiter_email = parsed["recruiter_email"]
    domain = parsed["domain"]
    company = parsed["company"]

    if not recruiter_email:
        return

    # Apply filters
    if is_blocked_email(recruiter_email):
        print(f"SKIPPED SYSTEM EMAIL: {recruiter_email}")
        return

    if is_blocked_domain(domain):
        print(f"SKIPPED BLOCKED DOMAIN: {domain}")
        return

    if is_personal_domain(domain):
        print(f"SKIPPED PERSONAL DOMAIN: {domain}")
        return

    # Check if recruiter already exists in database
    if cache_manager.recruiter_exists(recruiter_email):
        cache_manager.increment_email_count(recruiter_email)
        return

    # Record a new recruiter
    recruiter = create_recruiter_record(
        recruiter_name,
        recruiter_email,
        company
    )

    cache_manager.create_recruiter(recruiter)

    print()
    print("=" * 90)
    # Strip non-ASCII characters for clean console logs
    safe_name = recruiter_name.encode('ascii', 'ignore').decode('ascii')
    safe_company = company.encode('ascii', 'ignore').decode('ascii')

    print(f"Recruiter Name : {safe_name}")
    print(f"Recruiter Email: {recruiter_email}")
    print(f"Company        : {safe_company}")
    print(f"Email Count    : 1")
    print("=" * 90)


def process_sent_emails(reader, sent_cache_manager, sent_excel_writer):
    """
    Scans sent emails to log recruiter outreach history.
    
    Filters recipients, processes information, updates the sent cache, and
    saves everything to the output Excel sheet.
    
    Args:
        reader (GmailReader): Authorized Gmail reader instance.
        sent_cache_manager (CacheManager): Cache manager instance for sent emails.
        sent_excel_writer (ExcelWriter): Excel spreadsheet exporter for sent emails.
    """
    print("\nFetching sent emails...")
    # Extract message ID key prefixes to avoid reloading details for cached sent emails
    processed_sent_msg_ids = {key.split("_")[0] for key in sent_cache_manager.cache.keys()}
    sent_emails = reader.get_sent_emails(processed_sent_msg_ids)

    print(f"\nProcessing {len(sent_emails)} sent emails...\n")

    for email in sent_emails:
        msg_id = email["message_id"]
        to_header = email.get("to", "")
        if not to_header:
            continue

        # Split multiple recipients (cc's / multiple addresses)
        recipients = [r.strip() for r in to_header.split(",") if r.strip()]

        for recipient in recipients:
            parsed = RecruiterParser.parse(recipient)
            recruiter_name = parsed["recruiter_name"]
            recruiter_email = parsed["recruiter_email"]
            domain = parsed["domain"]
            company = parsed["company"]

            if not recruiter_email:
                continue

            # Apply same email/domain filters
            if is_blocked_email(recruiter_email):
                continue
            if is_blocked_domain(domain):
                continue
            if is_personal_domain(domain):
                continue

            # Check if this recipient logging combination is already processed
            cache_key = f"{msg_id}_{recruiter_email}"
            if sent_cache_manager.sent_email_exists(cache_key):
                continue

            # Fallback if human-readable name is not parsed
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

    # Re-export entire log back to Excel sheet
    all_sent_records = sent_cache_manager.get_all_sent_emails()
    sent_excel_writer.save_sent_emails(all_sent_records)


def main():
    """
    Main application orchestrator.
    
    Loads configuration settings, creates cache managers, scans for inbox and
    outbound recruiting messages, and outputs consolidated files.
    """
    cache_file, excel_file, sent_cache_file, sent_excel_file, processed_incoming_file = (
        build_paths()
    )

    # Initialize data/cache managers
    cache_manager = CacheManager(cache_file)
    excel_writer = ExcelWriter(excel_file)
    sent_cache_manager = CacheManager(sent_cache_file)
    sent_excel_writer = ExcelWriter(sent_excel_file)
    processed_incoming_cache = CacheManager(processed_incoming_file)

    reader = GmailReader()
    profile = reader.get_profile()

    print()
    print("=" * 90)
    print(f"Connected Gmail: {profile['emailAddress']}")
    print("=" * 90)

    # Fetch and parse received inbox messages
    processed_incoming_ids = set(processed_incoming_cache.cache.keys())
    emails = reader.get_latest_emails(processed_incoming_ids)

    print(f"\nProcessing {len(emails)} received emails...\n")

    for email in emails:
        try:
            process_email(email, cache_manager)
            # Mark incoming email as processed
            processed_incoming_cache.cache[email["message_id"]] = True
        except Exception as e:
            print(f"ERROR PROCESSING RECEIVED EMAIL: {e}")

    # Commit processed incoming logs
    if len(emails) > 0:
        processed_incoming_cache.save_cache()

    # Re-export recruiters list back to Excel sheet
    recruiters = cache_manager.get_all_recruiters()
    excel_writer.save_recruiters(recruiters)

    print()
    print(f"Total Recruiters: {cache_manager.total_recruiters()}")
    print(f"Excel Saved: {excel_file}")

    # Run outbound outreach email parsing
    try:
        process_sent_emails(
            reader,
            sent_cache_manager,
            sent_excel_writer
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR PROCESSING SENT EMAILS: {e}")


if __name__ == "__main__":
    main()

