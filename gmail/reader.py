import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from googleapiclient.discovery import build

from gmail.auth import get_credentials
from config import MAX_EMAILS


"""
Gmail API message reader and parser.

This module provides the GmailReader class to interact with Gmail, fetch messages
(inbox and sent), extract headers/body payloads, and fetch details in parallel.
"""

import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from googleapiclient.discovery import build

from gmail.auth import get_credentials
from config import MAX_EMAILS


class GmailReader:
    """
    Reader client for fetching and parsing emails via the Gmail API.
    
    Supports parallel message fetching using ThreadPoolExecutor. Uses threading.local
    to maintain thread-safe API service connections, preventing concurrent write/read
    exceptions from the googleapiclient discovery build.
    """

    def __init__(self):
        """
        Initializes the GmailReader client.
        
        Authenticates the user and sets up thread-local storage for API service builders.
        """
        self.creds = get_credentials()
        self._thread_local = threading.local()

    @property
    def service(self):
        """
        Returns a thread-safe Gmail API service instance.
        
        Uses thread-local storage to ensure each execution thread has its own
        service client, preventing threading conflicts during parallel requests.
        
        Returns:
            googleapiclient.discovery.Resource: Gmail API service client.
        """
        if not hasattr(self._thread_local, "service"):
            self._thread_local.service = build(
                "gmail",
                "v1",
                credentials=self.creds
            )
        return self._thread_local.service

    def get_profile(self):
        """
        Retrieves the profile information of the authenticated user.
        
        Returns:
            dict: Gmail user profile metadata (e.g. emailAddress, messagesTotal).
        """
        return self.service.users().getProfile(
            userId="me"
        ).execute(num_retries=5)

    def get_latest_messages(self):
        """
        Retrieves all incoming message summaries from the last 180 days.
        
        Paginates through results up to 500 messages per request.
        
        Returns:
            list: List of message summaries containing message IDs and thread IDs.
        """
        messages = []
        page_token = None

        while True:
            # Query filters messages newer than 180 days
            results = self.service.users().messages().list(
                userId="me",
                maxResults=500,
                pageToken=page_token,
                q="newer_than:180d"
            ).execute(num_retries=5)

            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return messages

    def get_message_details(self, message_id):
        """
        Fetches full details of a specific message by its ID.
        
        Args:
            message_id (str): The unique ID of the message.
            
        Returns:
            dict: The complete message payload (headers, snippets, body parts).
        """
        return self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute(num_retries=5)

    def get_header(self, headers, header_name):
        """
        Extracts the value of a specific header from a list of headers.
        
        Args:
            headers (list): List of header dictionaries (name-value pairs).
            header_name (str): The name of the header to find (e.g. 'From', 'Subject').
            
        Returns:
            str: The value of the header if found, otherwise an empty string.
        """
        for header in headers:
            if (
                header.get("name", "").lower()
                ==
                header_name.lower()
            ):
                return header.get("value", "")
        return ""

    def extract_body(self, payload):
        """
        Recursively extracts and decodes the plaintext email body from raw payloads.
        
        Iterates over MIME parts (plain, html, multi-part) and decodes base64 urlsafe
        data strings into readable UTF-8 strings.
        
        Args:
            payload (dict): The Gmail API message payload dictionary.
            
        Returns:
            str: Combined plain text content of the email body.
        """
        body_parts = []

        def extract_recursive(part):
            body = part.get("body", {})
            data = body.get("data")

            # Decode the base64url-encoded string
            if data:
                try:
                    decoded = (
                        base64.urlsafe_b64decode(data)
                        .decode("utf-8", errors="ignore")
                    )
                    if decoded.strip():
                        body_parts.append(decoded)
                except Exception:
                    pass

            # Recursively search child parts if present (MIME parts)
            for child in part.get("parts", []):
                extract_recursive(child)

        extract_recursive(payload)
        return "\n".join(body_parts)

    def get_latest_emails(self, processed_ids=None):
        """
        Fetches and decodes recent incoming emails that have not been processed.
        
        Executes parallel HTTP requests using a thread pool to optimize fetch times
        for large batches of messages.
        
        Args:
            processed_ids (set, optional): Set of message IDs already in cache.
            
        Returns:
            list: List of dictionaries, each containing parsed details of an email
                  (message_id, from, subject, date, snippet, body).
        """
        messages = self.get_latest_messages()
        # Filter out already processed messages
        if processed_ids:
            messages = [msg for msg in messages if msg["id"] not in processed_ids]

        emails = []

        # Single fetch task executed per thread
        def fetch_one(msg):
            try:
                message = self.get_message_details(msg["id"])
                payload = message.get("payload", {})
                headers = payload.get("headers", [])
                body = self.extract_body(payload)

                return {
                    "message_id": msg["id"],
                    "from": self.get_header(headers, "From"),
                    "subject": self.get_header(headers, "Subject"),
                    "date": self.get_header(headers, "Date"),
                    "snippet": message.get("snippet", ""),
                    "body": body
                }
            except Exception as e:
                print(f"Email read error: {e}")
                return None

        total_msgs = len(messages)
        if total_msgs > 0:
            print(f"Fetching details for {total_msgs} messages in parallel...")

        # Run parallel network tasks via ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_one, msg) for msg in messages]
            for count, future in enumerate(as_completed(futures), 1):
                res = future.result()
                if res:
                    emails.append(res)
                if count % 100 == 0:
                    print(f"Fetched details for {count}/{total_msgs} messages...")

        return emails

    def get_sent_messages(self):
        """
        Retrieves all sent messages (from the authenticated user) from the last 180 days.
        
        Paginates through results up to 500 messages per request.
        
        Returns:
            list: List of sent message summaries containing message IDs and thread IDs.
        """
        messages = []
        page_token = None

        while True:
            # Query filters for messages sent by the user in the last 180 days
            results = self.service.users().messages().list(
                userId="me",
                maxResults=500,
                pageToken=page_token,
                q="from:me newer_than:180d"
            ).execute(num_retries=5)

            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return messages

    def get_sent_emails(self, processed_ids=None):
        """
        Fetches and decodes recent sent emails that have not been processed.
        
        Executes parallel HTTP requests using a thread pool to fetch headers/snippets.
        
        Args:
            processed_ids (set, optional): Set of message IDs already in cache.
            
        Returns:
            list: List of dictionaries, each containing parsed details of a sent email
                  (message_id, from, to, subject, date, snippet).
        """
        messages = self.get_sent_messages()
        # Filter out already processed sent messages
        if processed_ids:
            messages = [msg for msg in messages if msg["id"] not in processed_ids]

        emails = []

        def fetch_one(msg):
            try:
                message = self.get_message_details(msg["id"])
                payload = message.get("payload", {})
                headers = payload.get("headers", [])

                return {
                    "message_id": msg["id"],
                    "from": self.get_header(headers, "From"),
                    "to": self.get_header(headers, "To"),
                    "subject": self.get_header(headers, "Subject"),
                    "date": self.get_header(headers, "Date"),
                    "snippet": message.get("snippet", "")
                }
            except Exception as e:
                print(f"Email read error: {e}")
                return None

        total_msgs = len(messages)
        if total_msgs > 0:
            print(f"Fetching details for {total_msgs} sent messages in parallel...")

        # Run parallel network tasks via ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_one, msg) for msg in messages]
            for count, future in enumerate(as_completed(futures), 1):
                res = future.result()
                if res:
                    emails.append(res)
                if count % 100 == 0:
                    print(f"Fetched details for {count}/{total_msgs} sent messages...")

        return emails


if __name__ == "__main__":
    reader = GmailReader()
    profile = reader.get_profile()
    print(f"Connected Gmail: {profile['emailAddress']}")
    emails = reader.get_latest_emails()
    print(f"\nEmails Found: {len(emails)}")