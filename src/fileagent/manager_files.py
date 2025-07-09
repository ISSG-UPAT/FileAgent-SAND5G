from pathlib import Path
import datetime
import inspect


class ManagerFiles:
    def __init__(self, *args, **kwargs):

        # Initialize some paths that are deemed important

        self.data_backup_path = Path(self.directory, "backup")
        if not self.data_backup_path.exists():
            self.data_backup_path.mkdir(parents=True, exist_ok=True)

        self.rules_file = Path(self.directory, self.args.file)

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

    def get_parent(self):
        """
        Description:
            Retrieves the absolute path of the parent directory of the file
            that is at the bottom of the current call stack.
            This method uses the `inspect` module to access the call stack
            and determines the file path of the last frame in the stack.
            It then resolves and returns the parent directory of that file.

        Returns:
            pathlib.Path: The absolute path of the parent directory of the file
            at the bottom of the call stack.
        """

        file_called_frame = inspect.stack()
        file_called_path = Path(file_called_frame[-1].filename)
        return Path(file_called_path).parent.resolve()
