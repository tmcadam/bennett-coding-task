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



## AI Usage




## Setup development environment

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
