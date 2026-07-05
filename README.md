# Bennett Institute Coding Task

A command line tool which uses the OpenPrescribing API to retrieve information about prescribing of
particular drugs and calculate how this varies around the country.


## Run the tool

`uv run optool.py`

## Setup development environment

  - Clone the project from Github
  - Install dependencies with `uv sync`


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
