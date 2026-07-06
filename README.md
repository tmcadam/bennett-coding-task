# Bennett Institute Coding Task

A command line tool which uses the OpenPrescribing API to retrieve information about prescribing of
particular drugs and calculate how this varies around the country.


## Run the tool

### Using **UV**


  - Install **UV** https://docs.astral.sh/uv/getting-started/installation/
  - Clone the repo
  - Install dependencies `uv sync --no-dev`
  - `uv run optool.py 1304000H0AAAAAA --user-agent optional-user-agent`

### Using **Pip**

  - Clone the repo
  - Setup up virtual environment `python3 -m venv venv`
  - Activate the virtual environment `. venv/bin/activate`
  - Install dependencies `pip install -r requirements.txt ]`
  - `python optool.py 1304000H0AAAAAA --user-agent optional-user-agent`


## Project Structure

```text
bennett-coding-task/
├── custom_types.py          # TypedDict definitions for API responses and summary data
├── opclient.py              # Client wrapper for the OpenPrescribing API
├── optool.py                # CLI entry point and command-line argument handling
├── opsummary.py             # Helpers for summarising monthly prescribing results
├── pyproject.toml           # Project metadata and dependency configuration
├── README.md                # Project overview and usage instructions
├── test_opclient.py         # Tests for the API client behaviour
├── test_optool.py           # Tests for the CLI and summary logic
├── test_opsummary.py        # Tests for summarising monthly prescribing results
├── docs/                    # Project documentation and notes
```

## AI Usage

AI was used in the completeion of this task in the following ways:

  - IDE autocomplete
  - IDE chat, for clarifying syntax or broader queries
  - IDE chat for analysing terminal errors, test failures
  - Generating some individual tests and sample data for tests
  - Generating docstrings

I didn't give it the task outline document, I architected the solution myself.

## Design Decisions

The main design choices were driven by simplicity, maintainability, and keeping the implementation lightweight.

- I used `requests` for API access and `click` for the command-line interface because they provide a small, practical dependency footprint for this kind of tool.
- I did not use `pandas` for the summarising logic, since the data transformations were straightforward and could be implemented clearly with plain Python data structures.
- I used synchronous requests rather than an asynchronous approach, as the scope of the project is small and the performance was acceptable for manual testing.
- I started with a single-file implementation and then split the functionality into separate modules as the code became longer and harder to follow.
- I used modern Python tooling UV, pytest, ruff and mypy.
- I didn't want to have the user-agent string stored in the codebase. I initially had this as an environmental variable and then modified it to be an CLI option. This change was for simplicity of running the tool.


## Development setup

  - Clone the project from Github
  - Install dependencies (including dev) with `uv sync`

### Run the tests

Test use **pytest**

`uv run pytest -v`


### Run type checking

Type checking uses **mypy**

`uv run mypy .`


### Run linting and formatting

Linting and formatting with **ruff**

  - `uv run ruff check`
  - `uv run ruff format`


### Update requirements.txt

`uv export --no-dev --format requirements-txt -o requirements.txt`
