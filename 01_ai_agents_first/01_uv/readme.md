# Python UV

[How to install UV - Notion Guide?](https://www.notion.so/UV-Installation-236e9749823180b7ab82d96a3b5997fd?source=copy_link)

[Python UV: The Ultimate Guide to the Fastest Python Package Manager](https://www.datacamp.com/tutorial/python-uv)

[Official Docs](https://docs.astral.sh/uv/)

[Running scripts](https://docs.astral.sh/uv/guides/scripts/)

[Working on projects](https://docs.astral.sh/uv/guides/projects/)

[CLI Reference](https://docs.astral.sh/uv/reference/cli/)

[Watch: Python Setup, Simplified: A Complete "uv" Tutorial!](https://www.youtube.com/watch?v=-J5SnWR4UXw)

## UV Project Create and Setup Project

    uv version

    uv help

    uv init explore-uv

This command sets up a project structured for packaging, placing your code inside a src directory, aligning with best practices for Python project structures.

    cd explore-uv

    code .

Use code . on terminal or open the directory explore-uv in VSCode

Now Create Virtual environment:

    uv venv

Activate virtual environment:

    source .venv/bin/activate

    In Windows 
    \explore-uv\.venv\Scripts\activate

Select Recommended Python Interpreter (./.venv/bin/python) created by virtual envirnoment in VSCode

    uv run explore-uv

## Cursor System Rules:

When working in Python always use UV as package manager.

Instead of writing code you can use cli to run commands where it's efficient like when prompted to create new project using uv use: 

Packaged applications
Many use-cases require a package. For example, if you are creating a command-line interface that will be published to PyPI or if you want to define tests in a dedicated directory.

The --package flag can be used to create a packaged application:

    uv init --package example-pkg

And to install packages in project

To add a dependency:

    uv add openai-agents




    


