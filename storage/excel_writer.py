"""
Excel spreadsheet storage manager.

This module provides the ExcelWriter class which handles exporting tracked 
recruiter contacts and sent outreach emails into formatted Excel files (.xlsx).
"""

import os
import pandas as pd


class ExcelWriter:
    """
    Handles exporting and reading tracking data using Excel spreadsheets.
    
    Provides formatted writes for recruiter records and sent emails. Includes
    error handling for permission locks (e.g., when the spreadsheet is currently
    open in Microsoft Excel).
    """

    def __init__(self, excel_path):
        """
        Initializes the ExcelWriter.
        
        Args:
            excel_path (str): File system path where the Excel spreadsheet will be saved.
        """
        self.excel_path = excel_path

    def save_recruiters(self, recruiters):
        """
        Converts the list of recruiter dicts into an Excel sheet and saves it.
        
        Renames database keys to user-friendly column headers.
        
        Args:
            recruiters (list): List of recruiter data dictionaries.
        """
        if not recruiters:
            print("No recruiters found to save.")
            return

        try:
            df = pd.DataFrame(recruiters)

            # Define preferred column ordering
            preferred_columns = [
                "recruiter_name",
                "recruiter_email",
                "company",
                "email_count",
                "first_seen",
                "last_seen"
            ]

            available_columns = [
                column
                for column in preferred_columns
                if column in df.columns
            ]

            df = df[available_columns]

            # Rename columns to human-readable headers
            df.rename(
                columns={
                    "recruiter_name": "Recruiter Name",
                    "recruiter_email": "Recruiter Email",
                    "company": "Company",
                    "email_count": "Email Count",
                    "first_seen": "First Seen",
                    "last_seen": "Last Seen"
                },
                inplace=True
            )

            df.to_excel(
                self.excel_path,
                index=False
            )

            print(f"Excel updated: {self.excel_path}")
            print(f"Recruiters saved: {len(df)}")

        except PermissionError:
            # Inform the user to close the document if it's locked by another process
            print(
                f"\n[ERROR] Permission denied when writing to {self.excel_path}.\n"
                f"Please close '{os.path.basename(self.excel_path)}' if it is open in Excel and run again.\n"
            )
        except Exception as e:
            print(f"Excel write error: {e}")

    def file_exists(self):
        """
        Checks if the Excel spreadsheet exists on disk.
        
        Returns:
            bool: True if it exists, False otherwise.
        """
        return os.path.exists(self.excel_path)

    def read_excel(self):
        """
        Reads the content of the Excel sheet into a Pandas DataFrame.
        
        Returns:
            pd.DataFrame: Loaded DataFrame, or an empty DataFrame on error or if missing.
        """
        if not self.file_exists():
            return pd.DataFrame()

        try:
            return pd.read_excel(self.excel_path)
        except Exception as e:
            print(f"Excel read error: {e}")
            return pd.DataFrame()

    def save_sent_emails(self, sent_emails):
        """
        Saves sent email logs into the spreadsheet.
        
        Deduplicates recruiter emails, formats the send date, and sorts them chronologically.
        
        Args:
            sent_emails (list): List of sent email log dictionaries.
        """
        if not sent_emails:
            print("No sent emails found to save.")
            return

        try:
            df = pd.DataFrame(sent_emails)

            preferred_columns = [
                "recruiter_name",
                "recruiter_email",
                "company",
                "date"
            ]

            available_columns = [
                column
                for column in preferred_columns
                if column in df.columns
            ]

            df = df[available_columns]

            # Parse dates and sort them chronologically
            if "date" in df.columns:
                df["parsed_date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
                df.sort_values(by="parsed_date", ascending=True, inplace=True)
                df["date"] = df["parsed_date"].dt.strftime("%Y-%m-%d")
                df.drop(columns=["parsed_date"], inplace=True)

            # Deduplicate by recipient email to only count each recruiter once in logs
            if "recruiter_email" in df.columns:
                df["email_lower"] = df["recruiter_email"].str.lower()
                df.drop_duplicates(subset=["email_lower"], keep="first", inplace=True)
                df.drop(columns=["email_lower"], inplace=True)

            df.rename(
                columns={
                    "recruiter_name": "Recruiter Name",
                    "recruiter_email": "Recruiter Email",
                    "company": "Company",
                    "date": "Date"
                },
                inplace=True
            )

            df.to_excel(
                self.excel_path,
                index=False
            )

            print(f"Excel updated: {self.excel_path}")
            print(f"Sent emails saved: {len(df)}")

        except PermissionError:
            print(
                f"\n[ERROR] Permission denied when writing to {self.excel_path}.\n"
                f"Please close '{os.path.basename(self.excel_path)}' if it is open in Excel and run again.\n"
            )
        except Exception as e:
            print(f"Excel write error: {e}")