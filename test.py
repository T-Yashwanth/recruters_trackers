from utils.recruiter_parser import RecruiterParser

sender = (
    "John Smith <john@teksystems.com>"
)

print(
    RecruiterParser.parse(
        sender
    )
)