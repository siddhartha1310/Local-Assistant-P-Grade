from presidio_analyzer import PatternRecognizer, Pattern

# Custom regex for phone numbers (broad enough for common formats)
phone_pattern = Pattern(
    name="phone_number_pattern",
    regex=r"(\d{3}-\d{4})|(\d{3}-\d{3}-\d{4})|(\(\d{3}\)\s?\d{3}-\d{4})",
    score=0.5
)

phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[phone_pattern]
)

# Custom regex for incomplete emails (e.g., user@domain without TLD)
incomplete_email_pattern = Pattern(
    name="incomplete_email_pattern",
    regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\b(?!\.[a-zA-Z]{2,})",
    score=0.4
)

incomplete_email_recognizer = PatternRecognizer(
    supported_entity="EMAIL_ADDRESS",
    patterns=[incomplete_email_pattern]
)
