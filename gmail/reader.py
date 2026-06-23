import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from googleapiclient.discovery import build

from gmail.auth import get_credentials
from config import MAX_EMAILS


class GmailReader:

    def __init__(self):

        self.creds = get_credentials()
        self._thread_local = threading.local()

    @property
    def service(self):
        if not hasattr(self._thread_local, "service"):
            self._thread_local.service = build(
                "gmail",
                "v1",
                credentials=self.creds
            )
        return self._thread_local.service

    def get_profile(self):

        return self.service.users().getProfile(
            userId="me"
        ).execute(num_retries=5)

    def get_latest_messages(self):

        messages = []
        page_token = None

        while True:
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

    def get_message_details(
        self,
        message_id
    ):

        return self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute(num_retries=5)

    def get_header(
        self,
        headers,
        header_name
    ):

        for header in headers:

            if (
                header.get(
                    "name",
                    ""
                ).lower()
                ==
                header_name.lower()
            ):

                return header.get(
                    "value",
                    ""
                )

        return ""

    def extract_body(
        self,
        payload
    ):

        import base64

        body_parts = []

        def extract_recursive(part):

            body = part.get(
                "body",
                {}
            )

            data = body.get(
                "data"
            )

            if data:

                try:

                    decoded = (
                        base64.urlsafe_b64decode(
                            data
                        )
                        .decode(
                            "utf-8",
                            errors="ignore"
                        )
                    )

                    if decoded.strip():

                        body_parts.append(
                            decoded
                        )

                except Exception:
                    pass

            for child in part.get(
                "parts",
                []
            ):

                extract_recursive(
                    child
                )

        extract_recursive(
            payload
        )

        return "\n".join(
            body_parts
        )

    def get_latest_emails(self, processed_ids=None):

        messages = self.get_latest_messages()
        if processed_ids:
            messages = [msg for msg in messages if msg["id"] not in processed_ids]

        emails = []

        def fetch_one(msg):
            try:
                message = self.get_message_details(
                    msg["id"]
                )

                headers = (
                    message.get(
                        "payload",
                        {}
                    )
                    .get(
                        "headers",
                        []
                    )
                )

                body = self.extract_body(
                    message.get(
                        "payload",
                        {}
                    )
                )

                return {

                    "message_id":
                        msg["id"],

                    "from":
                        self.get_header(
                            headers,
                            "From"
                        ),

                    "subject":
                        self.get_header(
                            headers,
                            "Subject"
                        ),

                    "date":
                        self.get_header(
                            headers,
                            "Date"
                        ),

                    "snippet":
                        message.get(
                            "snippet",
                            ""
                        ),

                    "body":
                        body
                }

            except Exception as e:
                print(
                    f"Email read error: {e}"
                )
                return None

        total_msgs = len(messages)
        if total_msgs > 0:
            print(f"Fetching details for {total_msgs} messages in parallel...")

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

        messages = []
        page_token = None

        while True:
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

        messages = self.get_sent_messages()
        if processed_ids:
            messages = [msg for msg in messages if msg["id"] not in processed_ids]

        emails = []

        def fetch_one(msg):
            try:
                message = self.get_message_details(
                    msg["id"]
                )

                headers = (
                    message.get(
                        "payload",
                        {}
                    )
                    .get(
                        "headers",
                        []
                    )
                )

                return {

                    "message_id":
                        msg["id"],

                    "from":
                        self.get_header(
                            headers,
                            "From"
                        ),

                    "to":
                        self.get_header(
                            headers,
                            "To"
                        ),

                    "subject":
                        self.get_header(
                            headers,
                            "Subject"
                        ),

                    "date":
                        self.get_header(
                            headers,
                            "Date"
                        ),

                    "snippet":
                        message.get(
                            "snippet",
                            ""
                        )
                }

            except Exception as e:
                print(
                    f"Email read error: {e}"
                )
                return None

        total_msgs = len(messages)
        if total_msgs > 0:
            print(f"Fetching details for {total_msgs} sent messages in parallel...")

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

    print(
        f"Connected Gmail: "
        f"{profile['emailAddress']}"
    )

    emails = reader.get_latest_emails()

    print(
        f"\nEmails Found: {len(emails)}"
    )