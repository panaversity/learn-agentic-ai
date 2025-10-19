# Deployment using Render

[Render Docs](https://render.com/docs/your-first-deploy)

## **Render Deployment Guide (Baby Steps)**

### 🧩 Prerequisites

Before starting, make sure you have:

* A **GitHub account**
* Your project code pushed to **a public GitHub repo**
* A file like `main.py` (entry point)
* A `pyproject.toml` listing dependencies
* A working local start command like:

  ```bash
  uv run chainlit run main.py
  ```

---

## Step 1: Sign Up or Log In

1. Go to [Render.com](https://render.com)
2. Click **Sign Up** (or **Log In**)
3. Sign in with **GitHub** (recommended)

---

## Step 2: Create a New Web Service

1. On your dashboard, click **“+ New” → “Web Service”**
2. Choose **Git Provider** tab
3. If you don’t see your repos, click **Reconnect GitHub → Grant full repo access**
4. Pick the repo you want to deploy
   *(Example: `panaversity/learn-agentic-ai`)*

---

## Step 3: Fill in Basic Info

Render will now ask for setup info 👇

| Field              | What to put                                                                          |
| ------------------ | ------------------------------------------------------------------------------------ |
| **Branch**         | `main`                                                                               |
| **Root Directory** | Leave empty *(unless your app lives inside a subfolder like `/app`)*                 |
| **Build Command**  | `pip install uv && uv sync` |
| **Start Command**  | `uv run chainlit run main.py --host 0.0.0.0 --port $PORT`                            |
| **Instance Type**  | Choose **Free (512 MB RAM)**                                                         |

---

## Step 4: Set Environment Variables (if needed)

If your app uses API keys or secrets:

1. Scroll to the **Environment Variables** section
2. Add variables like:

   ```
   OPENAI_API_KEY = your_api_key_here
   OPENAI_VECTOR_STORE_ID = your_api_key_here
   ```
3. You can edit or add more later anytime.

---

## Step 5: Click “Deploy Web Service”

Render will:

* Clone your GitHub repo
* Install dependencies (`uv sync` or `pip install`)
* Start your app with your start command

You’ll see live logs during deployment.

---

## Step 6: Watch Logs

* Wait for logs like:

  ```
  ==> Running 'uv run chainlit run main.py --host 0.0.0.0 --port $PORT'
  ==> Your service is live 🎉
  ```
* If something fails, Render shows the full error log for debugging.

---

## Step 7: Visit Your App

Once you see **✅ Live**, click the generated Render URL, e.g.

```
https://your-app-name.onrender.com
```

🎉 Your Chainlit or Python app is now running online!

---

## Step 8: Redeploy When You Update

Any time you push new code to the same GitHub branch (`main`),
Render automatically detects it and redeploys your app.

---

## Optional Step 9: Troubleshooting Tips

| Problem                   | Fix                                                                  |
| ------------------------- | -------------------------------------------------------------------- |
| “No pyproject.toml found” | Make sure your repo root has it, or set **Root Directory** correctly |
| Repo not visible          | Reconnect GitHub and grant full access                               |
| App won’t start           | Ensure start command uses `$PORT` and `--host 0.0.0.0`               |
| Slow spin-up              | Free tier apps sleep after 15 minutes idle; they wake automatically  |
