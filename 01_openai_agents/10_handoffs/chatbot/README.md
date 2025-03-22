 
 
    uv add openai-agents python-dotenv chainlit

Give these commands to run the project:

    cd chatbot

    uv venv

On Mac:

    source .venv/bin/activate

Using uv to run the project

    
```cmd
uv run chainlit run main.py -w
2025-03-13 08:11:10 - Loaded .env file
2025-03-13 08:11:11 - Your app is available at http://localhost:8000
2025-03-13 08:11:12 - Translated markdown file for en-US not found. Defaulting to chainlit.md.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1741835476.672255 29322037 fork_posix.cc:75] Other threads are currently calling into gRPC, skipping fork() handlers
2025-03-13 08:11:19 - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
History: [{'role': 'user', 'content': 'hi'}, {'role': 'developer', 'content': "Hi, I'm here to help.\n"}]
2025-03-13 08:11:28 - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
--------------------------------
Handing off to Refund Agent...
--------------------------------
```