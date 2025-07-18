from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import json


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
        async def upload_file(file: UploadFile = File(...)):
            if not file:
                raise HTTPException(
                    status_code=400, detail="No file part in the request"
                )

            if file.filename == "":
                raise HTTPException(status_code=400, detail="No file selected")

            return await self.upload_functionality(file)

        @self.app.get("/dashboard")
        async def dashboard():
            """
            Description:
                Endpoint to retrieve the dashboard data.
                This is a placeholder function that can be expanded to return
                actual dashboard data in the future.

            Returns:
                dict: A simple message indicating the dashboard is ready.
            """
            # function from manager_files.py

            notifications = self.get_file_content(self.history_file, "json")
            if notifications is None:
                raise HTTPException(status_code=404, detail="No notifications found")

            return {
                "message": "Dashboard is ready",
                "notifications": notifications,
            }

    async def upload_functionality(self, file: UploadFile):
        """
        Description:
            Handle the file upload functionality
            This function reads the content of the uploaded file and appends it to the rules file.
            It checks the content type of the file and processes it accordingly.
            If the content type is not supported, it raises an HTTPException.

        Args:
            file (UploadFile): The uploaded file to be processed

        Raises:
            HTTPException: If the file type is unsupported

        Returns:
            dict: A message indicating the file has been received and its content
        """

        content = await file.read()
        content_str = content.decode("utf-8")
        content_dict = {}
        try:
            content_dict = json.loads(content_str)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        if file.content_type == "application/json":
            self.append_rule(content_dict)
            return {"message": "JSON file received", "content": content_str}
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

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
