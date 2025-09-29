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

        @self.app.post(
            "/upload",
            summary="Upload JSON payload and translate to Snort rule",
            description=(
                "Accept a JSON payload which will be translated to a Snort rule by "
                "manager_snort.rule_translator. The endpoint runs the translation/append "
                "pipeline: rule_translator -> duplicate check (rule_exists) -> append_rule -> save_history.\n\n"
                "The rule_translator implementation determines accepted JSON shapes."
                "The json needs two fields: 'command' and 'target' ."
                "Acceptable commands: "
                "alert_ip, block_ip, block_domain, alert_ip, alert_domain"
                "Examples:\n"
            ),
            responses={
                200: {"description": "Rule processed successfully"},
                400: {
                    "description": "Bad request — invalid or empty JSON payload or translation failed"
                },
                409: {"description": "Duplicate rule — rule already exists"},
                500: {"description": "Internal server error while processing rule"},
            },
        )
        async def upload_json(
            payload: Dict[str, Any] = Body(
                ...,
                examples={
                    "alert_ip_sample": {
                        "summary": "Alert on IP (matches tests/manual/alert_ip.json)",
                        "value": {
                            "file": "sample",
                            "command": "alert_ip",
                            "target": "10.1.39.20",
                        },
                    },
                    "block_ip_sample": {
                        "summary": "Block an IP (matches tests/manual/block_ip.json)",
                        "value": {
                            "file": "sample",
                            "command": "block_ip",
                            "target": "10.1.39.20",
                        },
                    },
                    "block_domain_sample": {
                        "summary": "Block a domain (matches tests/manual/block_domain.json)",
                        "value": {
                            "file": "Block Domain",
                            "command": "block_domain",
                            "target": "forbidden.site",
                        },
                    },
                },
            ),
        ):
            """
            Accept a JSON body (application/json) in `payload`.

            Validation and processing notes:
            - The payload must be non-empty JSON.
            - manager_snort.rule_translator(payload) is expected to produce a Snort rule string.
            - If translation fails (translator returns None or empty), a 400 response is appropriate.
            - If a duplicate is detected via manager_snort.rule_exists(rule) a 409 is appropriate.
            - On success the rule is appended (append_rule) and the payload is recorded (save_history).
            """
            if not payload:
                raise HTTPException(status_code=400, detail="Empty JSON payload")

            # Attempt translation if available
            rule = None
            try:
                if hasattr(self, "rule_translator"):
                    rule = self.rule_translator(payload)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Translation error: {exc}")

            if not rule:
                # translation failed or returned nothing; inform the client
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Translation failed or returned no rule. Ensure payload matches "
                        "the manager_snort.rule_translator expected schema (command/target or content)."
                    ),
                )

            # duplicate check
            try:
                if hasattr(self, "rule_exists") and self.rule_exists(rule):
                    raise HTTPException(status_code=409, detail="Duplicate rule")
            except HTTPException:
                raise
            except Exception:
                # If duplicate check fails for any reason, continue cautiously
                pass

            # Append and save
            try:
                if hasattr(self, "append_rule"):
                    # append_rule expects the original payload in current code
                    self.append_rule(payload)
                if hasattr(self, "save_history"):
                    self.save_history(payload)
            except Exception as exc:
                raise HTTPException(
                    status_code=500, detail=f"Failed to persist rule: {exc}"
                )

            return {"message": "JSON payload received and processed", "rule": rule}

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
