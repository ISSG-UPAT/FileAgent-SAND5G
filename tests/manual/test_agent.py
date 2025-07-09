import requests
from pathlib import Path


class AgentTester:
    def __init__(self):
        self.path = Path(__file__).parent
        self.port = 8000

    def send(self, url, file_path, content_type):
        # Ensure the file exists before attempting to send
        if not file_path.exists():
            print(f"Error: File not found - {file_path}")
            return

        with open(file_path, "rb") as file:
            files = {
                "file": (
                    file_path.name,
                    file,
                    content_type,
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
        file_json = self.path / "sample.json"
        # file_txt = self.path / "sample.txt"

        # Send requests for both files
        self.send(url, file_json, "application/json")
        # self.send(url, file_txt, "text/plain")


if __name__ == "__main__":
    tester = AgentTester()
    tester.main()
