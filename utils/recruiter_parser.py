"""
Recruiter contact and domain parsing utility.

This module provides the RecruiterParser class which uses regex parsing to
split sender headers into name/email pairs, extract domains, and infer company names.
"""

import re


class RecruiterParser:
    """
    Utility parser for dissecting email headers and extracting recruiter metadata.
    """

    @staticmethod
    def parse_sender(sender):
        """
        Extracts the human-readable name and clean email address from a 'From' header.
        
        Example:
            "John Smith <john@teksystems.com>" -> ("John Smith", "john@teksystems.com")
            "john@teksystems.com"             -> ("", "john@teksystems.com")
            
        Args:
            sender (str): Raw sender string from email header.
            
        Returns:
            tuple: (name, email) as strings.
        """
        if not sender:
            return "", ""

        match = re.match(
            r"^(.*?)\s*<(.*?)>$",
            sender
        )

        if match:
            name = match.group(1).strip()
            email = match.group(2).strip()
            return (
                name,
                email
            )

        return (
            "",
            sender.strip()
        )

    @staticmethod
    def get_domain(email):
        """
        Extracts the host domain name from a clean email address.
        
        Example:
            "john@teksystems.com" -> "teksystems.com"
            
        Args:
            email (str): Clean email address.
            
        Returns:
            str: Domain name in lowercase.
        """
        if "@" not in email:
            return ""

        return email.split("@")[-1].lower()

    @staticmethod
    def get_company(email):
        """
        Infers the company name by extracting and formatting the second-level domain.
        
        Examples:
            "john@teksystems.com"     -> "Teksystems"
            "john@insight-global.com" -> "Insight Global"
            "john@mail.apollo.io"     -> "Apollo"
            
        Args:
            email (str): Clean email address.
            
        Returns:
            str: Title-cased company name.
        """
        domain = RecruiterParser.get_domain(
            email
        )

        if not domain:
            return ""

        parts = domain.split(".")

        if len(parts) < 2:
            return domain.title()

        company = parts[-2]

        company = company.replace(
            "-",
            " "
        )

        return company.title()

    @staticmethod
    def parse(sender):
        """
        Performs a full extraction pipeline on a sender header.
        
        Extracts recruiter name, email, domain, and company name.
        
        Args:
            sender (str): Raw sender email address or "Name <email>" string.
            
        Returns:
            dict: Parsed fields ("recruiter_name", "recruiter_email", "domain", "company").
        """
        recruiter_name, recruiter_email = (
            RecruiterParser.parse_sender(
                sender
            )
        )

        domain = RecruiterParser.get_domain(
            recruiter_email
        )

        company = RecruiterParser.get_company(
            recruiter_email
        )

        return {
            "recruiter_name":
                recruiter_name,

            "recruiter_email":
                recruiter_email,

            "domain":
                domain,

            "company":
                company
        }