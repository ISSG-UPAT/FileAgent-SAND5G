from pathlib import Path
import json
import re
import argparse
import datetime
from fileagent.manager_api import ManagerAPI
from fileagent.manager_arguments import ManagerArguments
from fileagent.manager_files import ManagerFiles
from fileagent.manager_snort import ManagerSnort


class FileAgent(ManagerAPI, ManagerArguments, ManagerFiles, ManagerSnort):
    def __init__(self, *args, **kwargs):
        ManagerArguments.__init__(self, *args, **kwargs)
        ManagerFiles.__init__(self, *args, **kwargs)
        # Handle the api
        ManagerAPI.__init__(self, *args, **kwargs)


if __name__ == "__main__":

    agent = FileAgent()
    agent.run_uvicorn()
