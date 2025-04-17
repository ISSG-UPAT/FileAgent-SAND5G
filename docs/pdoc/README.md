## Documentation

The project documentation is generated using pdoc3. To generate and view the documentation:

In the project root directory, run:

```bash
make docs-pdoc
```

or in the `docs` directory:

```bash
pdoc3 <package name> --html -o ./docs/pdoc/<package name>
```

or

```bash
make create
```

Open the generated HTML files in the `docs` directory.

Open the generated HTML files in the browser

in the root directory:

```bash
make docs-pdoc-host
```

or in the `docs` directory:

```bash
make host
```

### API Documentation

Additionally the FastAPI framework provides an interactive API documentation at `http://localhost:8000/docs` when the application is running. This allows you to test the API endpoints directly from your browser.
