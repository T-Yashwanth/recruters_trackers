import json
import os
from datetime import datetime


class CacheManager:

    def __init__(self, cache_file):

        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):

        if not os.path.exists(self.cache_file):
            return {}

        try:
            with open(
                self.cache_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception as e:

            print(
                f"Error loading cache: {e}"
            )

            return {}

    def save_cache(self):

        try:

            with open(
                self.cache_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.cache,
                    file,
                    indent=4
                )

        except Exception as e:

            print(
                f"Error saving cache: {e}"
            )

    def recruiter_exists(
        self,
        recruiter_email
    ):

        return recruiter_email in self.cache

    def get_recruiter(
        self,
        recruiter_email
    ):

        return self.cache.get(
            recruiter_email
        )

    def create_recruiter(
        self,
        recruiter_data
    ):

        email = recruiter_data[
            "recruiter_email"
        ]

        self.cache[email] = recruiter_data

        self.save_cache()

    def update_recruiter(
        self,
        recruiter_email,
        updates
    ):

        if recruiter_email not in self.cache:
            return

        self.cache[
            recruiter_email
        ].update(updates)

        self.cache[
            recruiter_email
        ]["last_seen"] = datetime.now(
        ).isoformat()

        self.save_cache()

    def increment_email_count(
        self,
        recruiter_email
    ):

        if recruiter_email not in self.cache:
            return

        current_count = self.cache[
            recruiter_email
        ].get(
            "email_count",
            0
        )

        self.cache[
            recruiter_email
        ]["email_count"] = current_count + 1

        self.cache[
            recruiter_email
        ]["last_seen"] = datetime.now(
        ).isoformat()

        self.save_cache()

    def get_all_recruiters(self):

        return list(
            self.cache.values()
        )

    def total_recruiters(self):

        return len(
            self.cache
        )

    def sent_email_exists(self, message_id):

        return message_id in self.cache

    def save_sent_email(self, message_id, email_data):

        self.cache[message_id] = email_data
        self.save_cache()

    def get_all_sent_emails(self):

        return list(self.cache.values())