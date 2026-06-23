# ==========================================
# Email Processing Configuration
# ==========================================

MAX_EMAILS = 10

# ==========================================
# Domains To Ignore
# ==========================================

BLOCKED_DOMAINS = {

    "linkedin.com",
    "dice.com",
    "indeed.com",
    "glassdoor.com",
    "monster.com",
    "ziprecruiter.com",
    "careerbuilder.com",
    "naukri.com",
    "apollo.io",
    "accounts.google.com",
    "google.com",
    "hello.textnow.com",
    "textnow.com"

}

# ==========================================
# Personal Email Providers
# ==========================================

PERSONAL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "icloud.com",
    "proton.me",
    "protonmail.com",
    "zoho.com",
    "aol.com",
    "mail.com"
}

# ==========================================
# Signature Detection
# ==========================================

SIGNATURE_MARKERS = [
    "regards",
    "best regards",
    "kind regards",
    "warm regards",
    "thanks",
    "thank you",
    "sincerely",
    "respectfully"
]

# ==========================================
# Recruiter Status
# ==========================================

STATUS_COMPLETE = "complete"
STATUS_PARTIAL = "partial"

# ==========================================
# Gemini Configuration
# ==========================================

ENABLE_GEMINI = False

# Future
# GEMINI_API_KEY = ""
# GEMINI_MODEL = "gemini-2.5-flash"

# ==========================================
# Recruiter Fields
# ==========================================

REQUIRED_FIELDS = [
    "recruiter_name",
    "recruiter_email",
    "company"
]

OPTIONAL_FIELDS = [
    "phone",
    "extension",
    "linkedin",
    "title"
]

# ==========================================
# Email Prefixes To Ignore
# ==========================================

BLOCKED_EMAIL_PREFIXES = {
    "noreply",
    "no-reply",
    "mailer-daemon",
    "notification",
    "notifications",
    "account",
    "account-security",
    "admin",
    "support",
    "help",
    "info"
}