"""
Local JSON cache manager for recruiter data and processed emails.

This module provides CacheManager, which handles reading, writing, and updating
JSON files used to cache processed email IDs and recruiter contact details.
"""

import json
import os
from datetime import datetime


class CacheManager:
    """
    Manages a simple local JSON file cache.
    
    Provides key-value helper methods to load, query, update, and write structured
    recruiter records or email message logs.
    """

    def __init__(self, cache_file):
        """
        Initializes the CacheManager.
        
        Args:
            cache_file (str): Absolute file path to the JSON cache file.
        """
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        """
        Loads the cache dictionary from the local file system.
        
        If the file does not exist or has formatting errors, returns an empty dictionary.
        
        Returns:
            dict: The cached data dictionary.
        """
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
            print(f"Error loading cache: {e}")
            return {}

    def save_cache(self):
        """
        Persists the current in-memory cache state back to the JSON file.
        """
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
            print(f"Error saving cache: {e}")

    def recruiter_exists(self, recruiter_email):
        """
        Checks if a recruiter email is already registered in the cache.
        
        Args:
            recruiter_email (str): The email address of the recruiter.
            
        Returns:
            bool: True if they exist, False otherwise.
        """
        return recruiter_email in self.cache

    def get_recruiter(self, recruiter_email):
        """
        Retrieves cached data for a recruiter.
        
        Args:
            recruiter_email (str): The recruiter's email.
            
        Returns:
            dict: The recruiter data dictionary, or None if not found.
        """
        return self.cache.get(recruiter_email)

    def create_recruiter(self, recruiter_data):
        """
        Saves a new recruiter record to the cache and commits changes to disk.
        
        Args:
            recruiter_data (dict): Dictionary with recruiter details.
        """
        email = recruiter_data["recruiter_email"]
        self.cache[email] = recruiter_data
        self.save_cache()

    def update_recruiter(self, recruiter_email, updates):
        """
        Updates fields on an existing recruiter record and saves the cache.
        
        Args:
            recruiter_email (str): Email of the recruiter to update.
            updates (dict): Key-value pairs to update on the record.
        """
        if recruiter_email not in self.cache:
            return

        self.cache[recruiter_email].update(updates)
        self.cache[recruiter_email]["last_seen"] = datetime.now().isoformat()
        self.save_cache()

    def increment_email_count(self, recruiter_email):
        """
        Increments the email interaction count for a recruiter.
        
        Args:
            recruiter_email (str): Email of the recruiter.
        """
        if recruiter_email not in self.cache:
            return

        current_count = self.cache[recruiter_email].get("email_count", 0)
        self.cache[recruiter_email]["email_count"] = current_count + 1
        self.cache[recruiter_email]["last_seen"] = datetime.now().isoformat()
        self.save_cache()

    def get_all_recruiters(self):
        """
        Retrieves a list of all cached recruiter records.
        
        Returns:
            list: List of recruiter detail dictionaries.
        """
        return list(self.cache.values())

    def total_recruiters(self):
        """
        Returns the total count of recruiters in the cache.
        
        Returns:
            int: Number of cached recruiters.
        """
        return len(self.cache)

    def sent_email_exists(self, message_id):
        """
        Checks if a sent message ID has already been recorded in the cache.
        
        Args:
            message_id (str): The sent email ID or cache compound key.
            
        Returns:
            bool: True if it exists, False otherwise.
        """
        return message_id in self.cache

    def save_sent_email(self, message_id, email_data):
        """
        Caches a sent email log and commits the cache to disk.
        
        Args:
            message_id (str): Compound ID (e.g. {msg_id}_{recipient}).
            email_data (dict): Detailed email metadata (recipient, subject, date).
        """
        self.cache[message_id] = email_data
        self.save_cache()

    def get_all_sent_emails(self):
        """
        Retrieves all logged sent email records from the cache.
        
        Returns:
            list: List of sent email data dictionaries.
        """
        return list(self.cache.values())