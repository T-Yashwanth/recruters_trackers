import os
import sys
import re
from datetime import datetime

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from gmail.auth import get_credentials
from googleapiclient.discovery import build
import pandas as pd

def extract_company_from_email(email):
    if "@" not in email:
        return "Unknown"
    domain = email.split("@")[1].lower()
    common_providers = {
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", 
        "icloud.com", "mail.com", "aol.com", "zoho.com", 
        "proton.me", "protonmail.com", "live.com", "msn.com"
    }
    if domain in common_providers:
        return "Independent"
    
    # Extract company name from domain (e.g., 'sub.company.com' -> 'company')
    parts = domain.split(".")
    if len(parts) >= 2:
        # If second to last part is a common second-level domain (like co.uk, com.au)
        if parts[-2] in {"co", "com", "org", "net", "edu", "gov"} and len(parts) >= 3:
            company_name = parts[-3]
        else:
            company_name = parts[-2]
        return company_name.capitalize()
    return domain.capitalize()

def parse_sender(sender_value):
    # Match "Name <email>" or just "email"
    name_match = re.match(r'^(.*?)\s*<(.*)>$', sender_value)
    if name_match:
        name = name_match.group(1).strip().strip('"').strip("'")
        email = name_match.group(2).strip()
    else:
        name = ""
        email = sender_value.strip()
    return name, email

def run_extractor():
    print("Starting Recruiter Extractor...")
    
    # 1. Get credentials and build service
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    
    # 2. Fetch recent messages
    # We search for emails with "recruiter", "job", "career", "interview", "application", "hiring"
    # to filter relevant ones.
    query = "recruiter OR job OR career OR interview OR application OR hiring"
    print(f"Searching for messages with query: '{query}'...")
    
    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=50
    ).execute()
    
    messages_summary = results.get("messages", [])
    if not messages_summary:
        print("No matching emails found.")
        return
        
    print(f"Found {len(messages_summary)} emails to process.")
    
    # Ensure data directory exists
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    excel_path = os.path.join(data_dir, "recruiters.xlsx")
    
    # Load existing data to check for duplicates
    existing_ids = set()
    if os.path.exists(excel_path):
        try:
            df_existing = pd.read_excel(excel_path)
            if "Message ID" in df_existing.columns:
                existing_ids = set(df_existing["Message ID"].dropna().astype(str))
                print(f"Loaded {len(existing_ids)} existing recruiters from Excel.")
        except Exception as e:
            print(f"Warning: Could not read existing Excel file: {e}. A new file will be created.")
            df_existing = pd.DataFrame()
    else:
        df_existing = pd.DataFrame()
        
    new_recruiters = []
    
    # 3. Process each message
    for i, msg in enumerate(messages_summary):
        msg_id = msg["id"]
        if msg_id in existing_ids:
            # Skip duplicates
            continue
            
        try:
            message = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full"
            ).execute()
            
            headers = message.get("payload", {}).get("headers", [])
            
            sender_value = ""
            subject = ""
            date_value = ""
            
            for header in headers:
                name = header.get("name", "").lower()
                if name == "from":
                    sender_value = header.get("value", "")
                elif name == "subject":
                    subject = header.get("value", "")
                elif name == "date":
                    date_value = header.get("value", "")
            
            recruiter_name, recruiter_email = parse_sender(sender_value)
            company = extract_company_from_email(recruiter_email)
            snippet = message.get("snippet", "")
            
            new_recruiters.append({
                "Message ID": msg_id,
                "Date": date_value,
                "Recruiter Name": recruiter_name if recruiter_name else "N/A",
                "Recruiter Email": recruiter_email,
                "Company": company,
                "Subject": subject,
                "Snippet": snippet
            })
            print(f"[{i+1}/{len(messages_summary)}] Extracted: {recruiter_name} ({company})")
            
        except Exception as e:
            print(f"Error processing message {msg_id}: {e}")
            
    # 4. Save to Excel
    if new_recruiters:
        df_new = pd.DataFrame(new_recruiters)
        if not df_existing.empty:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
            
        # Reorder columns to make it look clean
        cols = ["Date", "Recruiter Name", "Recruiter Email", "Company", "Subject", "Snippet", "Message ID"]
        df_combined = df_combined[[c for c in cols if c in df_combined.columns]]
        
        # Sort by date (optional, let's keep order or sort if dates are parseable)
        df_combined.to_excel(excel_path, index=False)
        print(f"Success! Saved {len(new_recruiters)} new records to '{excel_path}'.")
    else:
        print("No new recruiters to add.")

if __name__ == "__main__":
    run_extractor()
