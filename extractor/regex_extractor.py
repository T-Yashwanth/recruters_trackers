import re


class RegexExtractor:

    @staticmethod
    def extract_phone_numbers(text):

        if not text:
            return []

        patterns = [

            # (802) 793-9450
            r"\(\d{3}\)\s*\d{3}[-\s]?\d{4}",

            # 802-793-9450
            r"\d{3}[-\s]\d{3}[-\s]\d{4}",

            # +1 281-985-5921
            r"\+1\s*\d{3}[-\s]\d{3}[-\s]\d{4}",

            # +1 (281) 985-5921
            r"\+1\s*\(\d{3}\)\s*\d{3}[-\s]?\d{4}",

            # ☎ +1 281-985-5921
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

        if not text:
            return ""

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

        if not text:
            return ""

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

        phones = RegexExtractor.extract_phone_numbers(
            text
        )

        if not phones:
            return ""

        return phones[0]

    @staticmethod
    def extract_all(text):

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