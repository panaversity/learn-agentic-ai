    uv init helloworld

    cd helloworld

    uv venv

On Mac:

    source .venv/bin/activate

Let’s create a .gitignore file at the root of our project, and add this simple line:

    .venv

Let’s install chainlit with our preferred tool, UV:

    uv add chainlit

Test if it works by running this simple command line to start the chainlit server:

    uv run chainlit hello

It launches the Chainlit interface on http://localhost:8000 and prompts you to enter your name, initiating the interactive experience.

When we initiated our project with UV, it created a default file named main.py. Delete it and create an file:

    chatbot.py

We import chainlit (obviously).

We listen for incoming messages with the @cl.on_message decorator, meaning whenever a user sends a message, the main function gets triggered.

The main function will be called every time a user inputs a message in the chatbot UI. You can put your custom logic within the function to process the user’s input, such as analyzing the text, calling an API, or computing a result.

Inside, we can write our custom logic to process the message. In this simple example, we’re sending a fake response back to the user that echoes what they sent, using. cl.Message.

The content is formatted as “Received: {message.content}” and then sent back to the user asynchronously with .send().

Let’s test it with the run command of chainlit:

    uv run chainlit run chatbot.py -w

Note: the -w parameter enables hot reloading when we change our code