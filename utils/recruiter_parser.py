import re


class RecruiterParser:

    @staticmethod
    def parse_sender(sender):

        """
        Example:

        John Smith <john@teksystems.com>

        Returns:

        (
            "John Smith",
            "john@teksystems.com"
        )
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
        Example:

        john@teksystems.com

        Returns:

        teksystems.com
        """

        if "@" not in email:
            return ""

        return email.split("@")[-1].lower()

    @staticmethod
    def get_company(email):

        """
        Examples:

        john@teksystems.com
        -> Teksystems

        john@insight-global.com
        -> Insight Global

        john@mail.apollo.io
        -> Apollo
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