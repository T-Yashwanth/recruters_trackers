"""
Regex parser for email body signatures.

This module provides the RegexExtractor class, which extracts recruiter details
such as phone numbers, extensions, LinkedIn profile URLs, and job titles
from email body signatures.
"""

import re


class RegexExtractor:
    """
    Utility to parse and extract contact metadata using regular expressions.
    """

    @staticmethod
    def extract_phone_numbers(text):
        """
        Parses text to find phone numbers matching common US and international formats.
        
        Args:
            text (str): The text block to search (e.g. email signature).
            
        Returns:
            list: List of unique cleaned phone number strings found.
        """
        if not text:
            return []

        # List of regex patterns to capture different formatting variations
        patterns = [
            # (802) 793-9450
            r"\(\d{3}\)\s*\d{3}[-\s]?\d{4}",
            # 802-793-9450
            r"\d{3}[-\s]\d{3}[-\s]\d{4}",
            # +1 281-985-5921
            r"\+1\s*\d{3}[-\s]\d{3}[-\s]\d{4}",
            # +1 (281) 985-5921
            r"\+1\s*\(\d{3}\)\s*\d{3}[-\s]?\d{4}",
            # ☎ +1 281-985-5921 (often found in email footers)
            r"☎\s*\+1\s*\d{3}[-\s]\d{3}[-\s]\d{4}"
        ]

        phones = []

        for pattern in patterns:
            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )
            for match in matches:
                cleaned = match.strip()
                if cleaned not in phones:
                    phones.append(cleaned)

        return phones

    @staticmethod
    def extract_extension(text):
        """
        Extracts office extension numbers from the text block.
        
        Args:
            text (str): The text block to search.
            
        Returns:
            str: Extracted numeric extension, or empty string if not found.
        """
        if not text:
            return ""

        # Capture groups for numeric digits following 'ext', 'extension', etc.
        patterns = [
            r"ext[\s\-:]*([0-9]{1,6})",
            r"extension[\s\-:]*([0-9]{1,6})",
            r"ext\.[\s\-:]*([0-9]{1,6})",
            r"EXT[\s\-:]*([0-9]{1,6})"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )
            if match:
                return match.group(1)

        return ""

    @staticmethod
    def extract_linkedin(text):
        """
        Finds a LinkedIn profile URL in the text.
        
        Args:
            text (str): The text block to search.
            
        Returns:
            str: The full matching LinkedIn URL, or empty string if not found.
        """
        if not text:
            return ""

        match = re.search(
            r"https?://(?:www\.)?linkedin\.com/[^\s]+",
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

        return ""

    @staticmethod
    def extract_title(text):
        """
        Identifies if a common recruiter job title is mentioned in the text.
        
        Args:
            text (str): The text block (typically near the signature) to check.
            
        Returns:
            str: The matched job title in its standard case, or empty string.
        """
        if not text:
            return ""

        # Predefined list of standard recruiting job titles to scan for
        titles = [
            "Senior Technical Recruiter",
            "Technical Recruiter",
            "Senior Recruiter",
            "Recruiter",
            "Talent Partner",
            "Talent Acquisition",
            "Talent Acquisition Specialist",
            "Talent Acquisition Partner",
            "Staffing Specialist",
            "Recruitment Consultant",
            "Senior Recruitment Consultant",
            "Account Manager"
        ]

        text_lower = text.lower()

        for title in titles:
            if title.lower() in text_lower:
                return title

        return ""

    @staticmethod
    def get_best_phone(text):
        """
        Helper method to retrieve the primary phone number from a text block.
        
        Args:
            text (str): The text block to search.
            
        Returns:
            str: The first found phone number, or empty string.
        """
        phones = RegexExtractor.extract_phone_numbers(
            text
        )

        if not phones:
            return ""

        return phones[0]

    @staticmethod
    def extract_all(text):
        """
        Performs a full extraction of all signature metadata from a text block.
        
        Args:
            text (str): Text block containing signature data.
            
        Returns:
            dict: Dictionary with keys: phone, extension, linkedin, title.
        """
        return {
            "phone":
                RegexExtractor.get_best_phone(
                    text
                ),

            "extension":
                RegexExtractor.extract_extension(
                    text
                ),

            "linkedin":
                RegexExtractor.extract_linkedin(
                    text
                ),

            "title":
                RegexExtractor.extract_title(
                    text
                )
        }