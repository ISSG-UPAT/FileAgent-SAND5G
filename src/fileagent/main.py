from pathlib import Path
import json
import re
import argparse
import datetime
from apiclass import APIClass
from manager_arguments import ManagerArguments
from manager_files import ManagerFiles
from manager_snort import ManagerSnort


class FileAgent(APIClass, ManagerArguments, ManagerFiles, ManagerSnort):
    def __init__(self, *args, **kwargs):
        ManagerArguments.__init__(self, *args, **kwargs)
        ManagerFiles.__init__(self, *args, **kwargs)
        # Handle the api
        APIClass.__init__(self, *args, **kwargs)


if __name__ == "__main__":

    agent = FileAgent()
    agent.run_uvicorn()
