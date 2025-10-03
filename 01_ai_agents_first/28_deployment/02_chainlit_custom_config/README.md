# Chainlit Custom Configuration

This guide demonstrates how to enhance your Chainlit chat application with custom configurations and advanced features.

## What You'll Learn

- Chainlit configuration file setup
- Custom theming and UI elements
- Chat history persistence
- Error handling
- Session management
- Custom welcome messages

## Project Structure
```
.
├── main.py           # Enhanced application code
├── chainlit.yaml     # Chainlit configuration
├── chainlit.md      # Custom welcome message
├── requirements.txt  # Project dependencies
└── README.md        # This file
```

## Local Development Setup

1. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/Mac
# OR
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`

5. Run the application:
```bash
chainlit run main.py -w
```

## Configuration Details

### Theme Customization
The `chainlit.yaml` file contains theme settings for both light and dark modes:
```yaml
theme:
  light:
    primary: "#2E7D32"
    background: "#FFFFFF"
  dark:
    primary: "#388E3C"
    background: "#1A1A1A"
```

### Chat History
Chat history is persisted using SQLite:
```yaml
database:
  enabled: true
  type: "sqlite"
  url: "chat_history.db"
```

### Custom Welcome Message
The `chainlit.md` file contains a markdown-formatted welcome message shown to users when they start the chat.

## Features

1. **Enhanced UI**
   - Custom theme colors
   - Chainlit logo display
   - Markdown support

2. **Session Management**
   - Conversation history tracking
   - Session-based settings
   - Cleanup on chat end

3. **Error Handling**
   - Graceful error messages
   - Exception catching
   - User feedback

4. **Settings Management**
   - Model selection
   - Runtime configuration updates
   - User preferences

## Deploying to Hugging Face

1. Create a new Space on Hugging Face
2. Upload all files including:
   - main.py
   - chainlit.yaml
   - chainlit.md
   - requirements.txt
3. Add OPENAI_API_KEY to Space secrets
4. The Space will automatically build and deploy

## Notes

- The chat history is stored per session
- Custom settings can be updated during runtime
- Error messages are displayed in the chat interface
- The theme adapts to the user's system preferences 