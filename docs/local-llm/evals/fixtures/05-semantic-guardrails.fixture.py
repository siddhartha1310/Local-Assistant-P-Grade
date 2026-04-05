# Fixture: Hallucination Test Cases
# (Context, Claim, Expected Safe Status)
hallucination_test_cases = [
    (
        "The project codename is 'CYBER-X'. The lead scientist is Dr. Aris.",
        "The project codename is CYBER-X.",
        True
    ),
    (
        "The project codename is 'CYBER-X'. The lead scientist is Dr. Aris.",
        "The project is led by a robot named BOB-9.",
        False
    ),
    (
        "The server is located in the London data center. Port 443 is open.",
        "The London data center has port 443 open.",
        True
    ),
    (
        "The server is located in the London data center. Port 443 is open.",
        "The server is actually in New York and port 80 is open.",
        False
    )
]

# Fixture: Vault Quota Test Data
# (File Name, Size in MB, Expected result)
vault_test_files = [
    ("safe_file.txt", 1, "PASS"),
    ("boundary_file.txt", 10, "PASS"),
    ("oversized_file.txt", 11, "FAIL"),
]

# A 1MB block of text for vault testing
ONE_MB_TEXT = "A" * (1024 * 1024)
