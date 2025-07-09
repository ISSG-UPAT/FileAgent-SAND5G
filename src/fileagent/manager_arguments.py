from pathlib import Path
import json
import re
import argparse
import datetime


class ManagerArguments:
    def __init__(self, *args, **kwargs):

        # Setup default values
        self.default_values(**kwargs)

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
            help="Port to run the fastapi server on",
        )

        self.parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Host of the fastapi server",
        )

        self.parser.add_argument(
            "-f",
            "--file",
            type=str,
            default=None,
            help="Path to the file",
        )

        self.parser.add_argument(
            "-d",
            "--directory",
            type=str,
            default=None,
            help="Path to the data directory",
        )

    def assign_attributes(self, attributes):
        """
        Assign attributes dynamically based on provided arguments or defaults.

        Args:
            attributes (dict): A dictionary where keys are attribute names and values are tuples
                            of (provided_value, default_value).
        """
        for attr, (provided_value, default_value) in attributes.items():
            setattr(
                self,
                attr,
                provided_value if provided_value is not None else default_value,
            )

    def default_values(self, **kwargs):
        """
        Description:
            This function is meant to be run by the init function of the class
            Set the default values for the agent
            This function sets the default values for the agent. It checks if the arguments passed to the Class are None, and calls the arguments from argparse.
            If the arguments are not None, it assigns the values to the attribute of the class.
            If the directory is None, it sets the directory to the parent of the file.
            It also checks if the file is None, and raises a ValueError if it is.

        Args:
            port (int): Port to run the fastapi server on
            host (str): Host of the fastapi server
            directory (str): Path to the data directory
            file (str): Path to the file

        Raises:
            ValueError: File name is required
        """

        if any(value is None for value in kwargs.values()) or len(kwargs) == 0:
            self.set_arguments()
            self.args = self.parser.parse_args()

        attributes = {
            "port": (kwargs.get("port"), self.args.port),
            "host": (kwargs.get("host"), self.args.host),
            "directory": (kwargs.get("directory"), self.args.directory),
            "file": (kwargs.get("file"), self.args.file),
        }

        self.assign_attributes(attributes)

        if self.file is None:
            raise ValueError("File name is required")

        if self.directory is None:
            self.directory = Path(__file__).parent


if __name__ == "__main__":

    agent = ManagerArguments()
    agent.run_uvicorn()
