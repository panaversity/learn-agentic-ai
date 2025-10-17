# Stage 2 – Deploy on Hugging Face Spaces

Now we share the same Chainlit agent with the world. Hugging Face Spaces is free, friendly, and runs in your browser. Keep this folder open while you click through the steps.

## Before You Start

- Finish Stage 1 and make sure the app works on your laptop.
- Create a free Hugging Face account at https://huggingface.co/join.
- Install `git` if you want to push from the terminal later (optional).

---

## Step 1 – Make a New Space

1. Visit https://huggingface.co/spaces.
2. Click **Create New Space**.
3. Choose a name, set **Space SDK** to **Docker** (best for Chainlit), and pick **Public** or **Private**.
4. Click **Create Space**.

The Space page will load and wait for files.

---

## Step 2 – Upload the Project Files

You only need the three files from this folder:

- `main.py`
- `requirements.txt`
- `chainlit.md`

Drag them into the file area or use the **Upload files** button. When the files finish uploading the Space will start to build.

---

## Step 3 – Add Your Secret Key

1. On the Space page click the **Settings** tab.
2. Choose **Secrets**.
3. Add a new secret with:
   - Name: `OPENAI_API_KEY`
   - Value: your real key (starts with `sk-`).
4. Click **Add secret**.

The Space will reboot with the secret in place.

---

## Step 4 – Test the Live App

- Wait for the build log to say `App running on port 7860`.
- Click the **App** tab.
- Chat with the agent. You should see the same answers as on your laptop.

If you get an error, open the **Logs** tab. Most issues come from a missing key or a typo in `requirements.txt`.

---

## Optional – Update with `git`

Spaces are regular git repos. You can clone the repo the Space page gives you, copy your files inside, then push any future updates with:

```bash
git add .
git commit -m "Deploy Chainlit app"
git push
```

Hugging Face will rebuild the Space each time you push.

---

## When You Are Done

Congrats! You now have a live URL you can share. Take a note of the link and keep your API key secret. Head to Stage 3 to learn how to run the same app inside Docker.
