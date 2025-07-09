import requests
from pathlib import Path


class AgentTester:
    def __init__(self):
        self.path = Path(__file__).parent
        self.port = 8000

    def send(self, url, file_path):
        # Ensure the file exists before attempting to send
        if not file_path.exists():
            print(f"Error: File not found - {file_path}")
            return

        with open(file_path, "rb") as file:
            files = {
                "file": (
                    file_path.name,
                    file,
                    "application/json",
                )  # Use file_path.name as a string
            }
            try:
                response = requests.post(url, files=files)
                print("Status Code:", response.status_code)
                print("Response JSON:", response.json())
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
            # Send requests for both files
            self.send(url, Path(self.path, file_name))
        # self.send(url, file_txt, "text/plain")


if __name__ == "__main__":
    tester = AgentTester()
    tester.main()
