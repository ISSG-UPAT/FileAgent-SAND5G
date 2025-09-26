from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any
import uvicorn
import json
import time


class ManagerAPI:
    def __init__(self, *args, **kwargs):
        """
        Initializes the API class with the given parameters.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. Expected keys include:
                - "port" (int): The port number on which the API will run.
                - "host" (str): The host address for the API.
        Attributes:
            port (int): The port number on which the API will run.
            host (str): The host address for the API.
            app (FastAPI): The FastAPI application instance.
        Calls:
            setup_routes: Method to set up the API routes.
        """

        self.port = kwargs.get("port", self.port)
        self.host = kwargs.get("host", self.host)
        self.app = FastAPI()
        self.setup_routes()
        super().__init__(*args, **kwargs)

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
        async def upload_json(payload: Dict[str, Any] = Body(...)):
            """
            Accept a JSON body (application/json) in `payload`.
            """

            if not payload:
                raise HTTPException(status_code=400, detail="Empty JSON payload")

            content_dict = payload
            # from managersnort
            self.append_rule(content_dict)
            # from managerfile
            self.save_history(content_dict)
            return {"message": "JSON payload received", "content": content_dict}

        @self.app.get("/notifications")
        async def notifications():
            """
            Description:
                Endpoint to retrieve the notifications data.
                This is a placeholder function that can be expanded to return
                actual notifications data in the future.

            Returns:
                dict: A simple message indicating the notifications is ready.
            """
            # function from manager_files.py

            notifications = self.get_file_content(self.history_file, "json")
            if notifications is None:
                raise HTTPException(status_code=404, detail="No notifications found")

            history = notifications.get("history")

            return {
                "message": "notifications is ready",
                "latest": history[-1] if history else None,
                "timestamp": time.time(),
                "notifications": history[1:] if len(history) > 1 else [],
            }

    # Note: file upload handling removed; /upload accepts JSON payloads only.

    def run_uvicorn(self):
        """
        Description
        -----------
        Main function to run the agent

        Parameters
        ----------
        None
        """
        uvicorn.run(self.app, host=self.host, port=self.port)
