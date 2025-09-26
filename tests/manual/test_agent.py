import requests
import json
import argparse
from pathlib import Path


class AgentTester:
    def __init__(self):
        self.path = Path(__file__).parent
        self.port = 8000

    def send_json(self, url, file_path):
        # Ensure the file exists before attempting to send
        if not file_path.exists():
            print(f"Error: File not found - {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as e:
            print(f"Failed to read/parse {file_path}: {e}")
            return

        try:
            response = requests.post(url, json=payload)
            print("File:", file_path.name)
            print("Status Code:", response.status_code)
            try:
                print("Response JSON:", response.json())
            except ValueError:
                print("Response Text:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")

    def main(self):
        url = f"http://127.0.0.1:{self.port}/upload"

        # Define file paths
        files = [
            "alert_ip.json",
            "block_ip.json",
            "block_domain.json",
        ]

        for file_name in files:
            # Send JSON payloads from the sample files
            self.send_json(url, Path(self.path, file_name))
        # self.send(url, file_txt, "text/plain")


if __name__ == "__main__":
    tester = AgentTester()
    tester.main()
