from pathlib import Path
import json
import re
import argparse
import datetime


class ManagerFiles:
    def __init__(self, *args, **kwargs):

        # This should change to correlate with the arguments passed
        # TODO: This should change to accept from the user
        self.internal_path = Path(__file__).parent.parent
        # For non docker usage
        self.internal_path = Path(self.internal_path.parent, "snort", "volumes")

        self.data_path = Path(self.internal_path, "custom")
        self.data_backup_path = Path(self.data_path, "backup")
        self.rules_file = Path(self.data_path, self.args.file)

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


if __name__ == "__main__":

    agent = ManagerFiles()
    agent.run_uvicorn()
