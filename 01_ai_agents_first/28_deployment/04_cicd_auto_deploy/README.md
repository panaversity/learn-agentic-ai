# Stage 4 – Auto Deploy with GitHub Actions

Let GitHub do the busy work for you. In this stage you set up a simple pipeline that builds your Docker image, pushes it to Docker Hub, and pings Render (or any other host) to pull the fresh version.

## Big Idea in Plain Words

- You push code to the `main` branch.
- GitHub builds the container for you.
- GitHub sends the finished image to Docker Hub.
- GitHub pokes your host so it redeploys.

You do not click any buttons after the first setup.

---

## What You Need First

1. A GitHub repository that already holds this project.
2. A Docker Hub account (free) with a blank repository waiting for the image.
3. A Render (or Railway) service created from that image. Copy the deploy hook URL from their dashboard.

---

## Step 1 – Copy the Workflow

Move the `deploy.yml` file in this folder to `.github/workflows/deploy.yml` inside your own project repo. GitHub looks in that exact folder name.

```bash
mkdir -p .github/workflows
cp 04_cicd_auto_deploy/deploy.yml .github/workflows/deploy.yml
```

If your app lives in a different folder, open the workflow and change the `context` line so it points to the right place.

Commit the new file when you are ready.

---

## Step 2 – Add GitHub Secrets

Open your repo on GitHub and go to **Settings → Secrets and variables → Actions**. Add these secrets:

| Secret Name          | Value                                                                             |
| -------------------- | --------------------------------------------------------------------------------- |
| `DOCKERHUB_USERNAME` | your Docker Hub username                                                          |
| `DOCKERHUB_TOKEN`    | a personal access token from Docker Hub                                           |
| `RENDER_DEPLOY_HOOK` | the full deploy hook URL from Render (or leave blank if you only need Docker Hub) |

Your OpenAI key stays with the host (Render secret, Hugging Face secret, etc.), not in GitHub.

---

## Step 3 – Push to `main`

After the secrets are set, push a commit to the `main` branch. GitHub will start the workflow. You can watch the run under the **Actions** tab.

Each run will:

1. Build the Docker image using the files in `03_docker_basics`.
2. Push the image to Docker Hub with the `latest` tag.
3. Trigger the deploy hook.

Render will pull the new image, rebuild, and restart your service automatically.

---

## Step 4 – Check the Result

- Open the Render dashboard to see the new deploy.
- Visit the live URL to chat with the agent.
- If something fails, read the GitHub Actions logs. They spell out the step that broke.

---

## Bonus Ideas

- Add another job that runs tests before the build.
- Use a second environment (staging) by changing the branch filter.
- Swap Render for any host that accepts a web hook.

You made it! From now on a single `git push` keeps your hosted agent fresh.
