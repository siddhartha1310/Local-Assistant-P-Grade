# Fixtures for Slice 02 Privacy Pipeline
EMAIL_PII_TEXT = "My email is test@example.com"
MULTIPLE_PII_TEXT = "Contact me at 555-0199 or visit 192.168.1.1"

TXT_CONTENT = "Hello, this is a secret: secret@private.com"
CSV_CONTENT = "name,email\nJohn Doe,john@doe.com"

# Expected Placeholders
EMAIL_PLACEHOLDER = "<EMAIL_ADDRESS>"
PHONE_PLACEHOLDER = "<PHONE_NUMBER>"
IP_PLACEHOLDER = "<IP_ADDRESS>"

# Integration Test Data
INTEGRATION_TEST_FILE = "integration_test.txt"
INTEGRATION_CONTENT = "User data: admin@company.com, IP: 10.0.0.1"
