from config import SIGNATURE_MARKERS


class SignatureExtractor:

    @staticmethod
    def normalize_text(text):

        if not text:
            return ""

        return text.replace(
            "\r\n",
            "\n"
        )

    @staticmethod
    def extract_signature(text):

        text = SignatureExtractor.normalize_text(
            text
        )

        if not text:
            return ""

        lines = text.split("\n")

        marker_index = -1

        for i, line in enumerate(lines):

            line_lower = line.strip().lower()

            for marker in SIGNATURE_MARKERS:

                if marker in line_lower:

                    marker_index = i
                    break

            if marker_index != -1:
                break

        if marker_index == -1:
            return ""

        signature_lines = lines[
            marker_index:
        ]

        return "\n".join(
            signature_lines
        ).strip()

    @staticmethod
    def get_last_lines(
        text,
        count=50
    ):

        text = SignatureExtractor.normalize_text(
            text
        )

        if not text:
            return ""

        lines = text.split("\n")

        return "\n".join(
            lines[-count:]
        )

    @staticmethod
    def extract_for_fallback_1(
        text
    ):

        return SignatureExtractor.extract_signature(
            text
        )

    @staticmethod
    def extract_for_fallback_2(
        text
    ):

        return SignatureExtractor.get_last_lines(
            text,
            50
        )

    @staticmethod
    def extract_for_fallback_3(
        text
    ):

        return text

    @staticmethod
    def build_debug_report(
        text
    ):

        signature = SignatureExtractor.extract_signature(
            text
        )

        last_lines = SignatureExtractor.get_last_lines(
            text,
            50
        )

        return {

            "signature_found":
                bool(signature),

            "signature_length":
                len(signature),

            "last_50_lines_length":
                len(last_lines)
        }