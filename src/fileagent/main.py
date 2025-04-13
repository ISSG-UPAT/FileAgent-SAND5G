from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
import os
import json
import re
import uvicorn
import argparse
import datetime


class FileAgent:
    def __init__(self):
        self.set_arguments()
        self.app = FastAPI()
        self.internal_path = Path(__file__).parent.parent
        # For non docker usage
        self.internal_path = Path(self.internal_path.parent, "snort", "volumes")
        self.data_path = Path(self.internal_path, "custom")
        self.data_backup_path = Path(self.data_path, "backup")
        self.rules_file = Path(self.data_path, self.args.file)

        self.setup_routes()

    def set_arguments(self):
        """
        Description:
            Set the arguments for the agent, and save the important information as attributes of the class
        """

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=8000,
            help="Path to the data directory",
        )

        self.parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Path to the data directory",
        )

        self.parser.add_argument(
            "-f",
            "--file",
            type=str,
            default="mock.local.rules",
            help="Path to the data directory",
        )

        self.args = self.parser.parse_args()
        self.port = self.args.port
        self.host = self.args.host

    def setup_routes(self):
        """
        Description:
            Setup the routes for the agent

        Raises:
            HTTPException:
            HTTPException: _description_
            HTTPException: _description_

        Returns:
            _type_: _description_
        """

        @self.app.post("/upload")
        async def upload_file(file: UploadFile = File(...)):
            if not file:
                raise HTTPException(
                    status_code=400, detail="No file part in the request"
                )

            if file.filename == "":
                raise HTTPException(status_code=400, detail="No file selected")

            content = await file.read()
            content_str = content.decode("utf-8")

            if file.content_type == "application/json":
                self.append_rule(
                    {"content_type": "application/json", "content": content_str}
                )
                return {"message": "JSON file received", "content": content_str}
            elif file.content_type == "text/plain":
                self.append_rule({"content_type": "text/plain", "content": content_str})
                return {"message": "Text file received", "content": content_str}
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")

    def ip_matches(self, data: str) -> str:
        """
        Description:
            Check if the data contains an ip address. Checks for ipv4, ipv6 and url

        Args:
            data (str): Data to be checked for ip address

        Returns:
            str: the ip/url regex matching case
        """
        ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ipv6_pattern = r"\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b"
        url_pattern = r"\bhttps?://[^\s/$.?#].[^\s]*\b"

        for pattern in [ipv4_pattern, ipv6_pattern, url_pattern]:
            match = re.search(pattern, data)
            if match:
                return match.group(0)
        return None

    def rule_translator(self, data: dict) -> str:
        """
        Description:
            Translate the data into a rule
            Right now this is a simple implementation
            Checks if it is a json or text file and extracts the ip address

        Args:
            data (dict): Data from the post request to be translated into a rule,

        Returns:
            str: Rule to be appended to the rules file
        """

        if data.get("content_type") == "application/json":
            data = json.loads(data.get("content"))
            rule = f"block {data.get('ip')}"
        elif data.get("content_type") == "text/plain":
            ip = self.ip_matches(data.get("content"))
            if ip is None:
                return None
            # rule = f"block {ip}"
            rule = f"""alert ip {ip} any -> $HOME_NET any (msg: "IP Alert Incoming From IP: {ip}";   classtype:tcp-connection; sid:28154103; rev:1; reference:url,https://misp.gsma.com/events/view/19270;)"""

        return rule

    def append_rule(self, data):
        """
        Description:
        Append rule to the local.rules

        Args:
            data (str): Data to be appended to the local.rules file
        """

        # Right now this is just a simple implementation

        rule = self.rule_translator(data)
        if rule is None:
            return

        if self.rule_exists(rule):
            return

        print(f"Appending rule: {rule}")
        # Backup the rules file
        self.file_backup()

        # Append the rule to the rules file
        with open(self.rules_file, "a") as file:
            file.write(f"\n{rule}\n")

    def rule_exists(self, rule):
        """
        Description:
            Check if the rule already exists in the rules file
            This function reads the rules file line by line and determines if the
            provided rule is present in any of the lines. It is useful for avoiding
            duplicate entries in the rules file.

        Args:
            rule (str): Rule to be checked

        Returns:
            bool: True if the rule exists, False otherwise
        """

        with open(self.rules_file, "r") as file:
            rules = file.readlines()
            if any(rule in rule_line for rule_line in rules):
                return True
            return False

    def file_backup(self):
        """
        Description:
            -----------

            Creates a backup of the rules file in the specified backup directory.
            This method ensures that the backup directory exists, then creates a backup
            of the `self.rules_file` by copying its contents to a new file in the backup
            directory. The backup file is named using the original file's stem and the
            current timestamp in the format 'YYYY-MM-DD_HH-MM-SS.bak'.
            Steps:
            1. Ensures the backup directory (`self.data_backup_path`) exists.
            2. Constructs the backup file path using the original file's stem and a timestamp.
            3. Reads the contents of the `self.rules_file`.
            4. Writes the contents to the newly created backup file.
            Raises:
                FileNotFoundError: If `self.rules_file` does not exist.
                IOError: If there is an issue reading from or writing to the files.
            Note:
                - The method assumes `self.rules_file` and `self.data_backup_path` are
                valid `Path` objects.
                - The timestamp ensures that each backup file has a unique name.

        Raises:
            FileNotFoundError: If `self.rules_file` does not exist.
            IOError: If there is an issue reading from or writing to the files.

        """

        # Copy the self.rules_file to the backup directory with the name filename-time.bak
        # Ensure the backup directory exists
        self.data_backup_path.mkdir(parents=True, exist_ok=True)
        print(f"Creating backup in {self.data_backup_path}")
        # Create the backup file path
        backup_file = Path(
            self.data_backup_path,
            f"{self.rules_file.stem}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.bak",
        )
        with open(self.rules_file, "r") as file:
            rules = file.readlines()

            with open(backup_file, "w") as file:
                file.writelines(rules)

    def main(self):
        """
        Description
        -----------
        Main function to run the agent

        Parameters
        ----------
        None
        """
        uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":

    agent = FileAgent()
    agent.main()
