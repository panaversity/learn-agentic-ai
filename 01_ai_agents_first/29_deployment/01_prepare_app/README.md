# Stage 1 – Get the App Ready

This is where we make our Chainlit agent safe to share. We keep the code simple so you can finish this step in one study session.

## What You Will Do

1. Make a fresh virtual environment with `uv`.
2. Store secrets in a `.env` file.
3. Add quick logging and a health check.
4. Test the Chainlit chat one more time.

You already know Python and Chainlit. We are just cleaning things up for other people to use.

---

## Step 1 – Create the Environment

```bash
cd your-agent-folder
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

The `requirements.txt` file in this folder locks the versions we trust.

---

## Step 2 – Add Your Secrets

Copy the example file and place your own keys inside.

```bash
cp .env.example .env
```

Open `.env` and add:

```
OPENAI_API_KEY=sk-...
```

Never push `.env` to GitHub. It stays on your machine only.

---

## Step 3 – Meet the Code

Read `main.py`. The file now has:

- a helper that logs the start and end of each answer
- a health check route at `/health`
- clear error messages when something goes wrong

Feel free to reuse this file in your own app.

---

## Step 4 – Test Locally

```bash
chainlit run main.py -w
```

Open the link in your browser. Ask a question. Check your terminal to see the log lines. Visit [http://localhost:8000/health](http://localhost:8000/health) to see the health text.

If everything works, you are ready to deploy in Stage 2.

---

## Helpful Notes

- You can change the model name in one place near the top of `main.py`.
- Errors will print both in the chat window and in the terminal log.
- If you get an auth error, double-check the API key in `.env`.

Nice work! Move to Stage 2 when you feel confident with this setup.
