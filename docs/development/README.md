# Development of FileAgent

## Requirements

- Python 3.11 or higher
- Dependencies listed in `pyproject.toml`:
  - `fastapi`
  - `uvicorn`
  - `requests`
  - `python-multipart`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ISSG-Projects/FileAgentSAND5G.git
   cd FileAgentSAND5G
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   ```

   or

   ```bash
   make create-venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   or

   ```bash
   make setup-toml
   ```

5. Run the FastAPI application:

   ```bash
   fileagent --host <host> --port <port> directory file
   ```
