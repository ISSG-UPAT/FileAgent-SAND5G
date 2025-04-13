from fileagent import FileAgent
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from fastapi.testclient import TestClient
import json
import argparse


class TestFileAgent(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.agent = FileAgent()
        self.client = TestClient(self.agent.app)

    @patch("argparse.ArgumentParser.parse_args")
    def test_set_arguments(self, mock_args):
        """Test the set_arguments method."""
        mock_args.return_value = argparse.Namespace(
            port=8080, host="127.0.0.1", file="test.rules"
        )
        self.agent.set_arguments()
        self.assertEqual(self.agent.port, 8080)
        self.assertEqual(self.agent.host, "127.0.0.1")
        self.assertEqual(self.agent.args.file, "test.rules")

    def test_ip_matches(self):
        """Test the ip_matches method."""
        ipv4 = "192.168.1.1"
        ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        url = "https://example.com"
        self.assertEqual(self.agent.ip_matches(ipv4), ipv4)
        self.assertEqual(self.agent.ip_matches(ipv6), ipv6)
        self.assertEqual(self.agent.ip_matches(url), url)
        self.assertIsNone(self.agent.ip_matches("invalid data"))

    def test_rule_translator_json(self):
        """Test the rule_translator method with JSON input."""
        data = {
            "content_type": "application/json",
            "content": json.dumps({"ip": "192.168.1.1"}),
        }
        rule = self.agent.rule_translator(data)

        self.assertEqual(
            rule,
            f"""alert ip 192.168.1.1 any -> $HOME_NET any (msg: "IP Alert Incoming From IP: 192.168.1.1";   classtype:tcp-connection; sid:28154103; rev:1; reference:url,https://misp.gsma.com/events/view/19270;)""",
        )

    def test_rule_translator_text(self):
        """Test the rule_translator method with plain text input."""
        data = {"content_type": "text/plain", "content": "192.168.1.1"}
        rule = self.agent.rule_translator(data)
        self.assertIn("alert ip 192.168.1.1", rule)

    @patch("builtins.open", new_callable=mock_open, read_data="existing rule\n")
    def test_rule_exists(self, mock_file):
        """Test the rule_exists method."""
        rule = "existing rule"
        self.assertTrue(self.agent.rule_exists(rule))
        self.assertFalse(self.agent.rule_exists("new rule"))

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_file_backup(self, mock_mkdir, mock_file):
        """Test the file_backup method."""
        mock_file.return_value.readlines.return_value = ["rule1", "rule2"]
        self.agent.file_backup()
        mock_mkdir.assert_called_once()
        mock_file.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("src.fileagent.main.FileAgent.rule_exists", return_value=False)
    @patch("src.fileagent.main.FileAgent.file_backup")
    def test_append_rule(self, mock_backup, mock_rule_exists, mock_file):
        """Test the append_rule method."""
        data = {"content_type": "text/plain", "content": "192.168.1.1"}
        self.agent.append_rule(data)
        mock_backup.assert_called_once()
        mock_file().write.assert_called()

    def test_upload_file(self):
        """Test the /upload endpoint."""
        response = self.client.post(
            "/upload",
            files={"file": ("test.txt", "192.168.1.1", "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Text file received", response.json()["message"])


if __name__ == "__main__":
    unittest.main()
