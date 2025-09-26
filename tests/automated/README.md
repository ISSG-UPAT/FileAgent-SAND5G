Explanation of the Tests
setUp Method: Initializes the FileAgent instance and a TestClient for testing FastAPI routes.
test_set_arguments: Tests the argument parsing functionality.
test_ip_matches: Verifies the IP matching logic for IPv4, IPv6, and URLs.
test_rule_translator_json and test_rule_translator_text: Test the rule translation logic for JSON and plain text inputs.
test_rule_exists: Checks if the rule existence logic works correctly.
test_file_backup: Tests the backup functionality.
test_append_rule: Verifies that rules are appended correctly.
test_upload_json: Tests the /upload endpoint using FastAPI's TestClient.
