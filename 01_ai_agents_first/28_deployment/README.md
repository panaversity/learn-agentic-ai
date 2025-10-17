# Stage 28 – Deploy Your First Agent

By now you have built Python agents and run them with Chainlit. This stage shows how to share that agent with the world. The lessons use short steps and repeat the same friendly Chainlit app so you can focus on the new ideas.

## Learning Path

```
28_deployment/
├── 01_prepare_app/         # Clean up the Chainlit app for sharing
├── 02_huggingface_spaces/  # Click-and-deploy on a free host
├── 03_docker_basics/       # Understand containers and run the app anywhere
└── 04_cicd_auto_deploy/    # Let GitHub redeploy for you after each push
```

Take the lessons in order. Each step is short and builds on the last one.

### Stage 1 – Prepare the App

- Set up `.env` and secrets the safe way
- Add a tiny health check and helpful logging
- Lock your Python packages with `uv`

### Stage 2 – Hugging Face Spaces

- Make a new Space with the web UI
- Upload the three files the Space needs
- Store your API key as a secret, not in code

### Stage 3 – Docker Basics

- Learn what images and containers are in plain words
- Build and run the same Chainlit app inside Docker
- Push the image to Render or Railway when you are ready

### Stage 4 – CI/CD Auto Deploy

- Copy a friendly GitHub Actions workflow
- Trigger a rebuild and deploy when you push to `main`
- Spot common errors and how to fix them fast

## How to Use This Module

- Follow each README one at a time
- Copy the sample code into your working project
- Test locally after every change
- Deploy only when the local check passes

## After You Finish

- Try hosting the agent inside an MCP server
- Add tracing, analytics, or a queue in later tracks
- Teach the agent to serve other channels (Slack, voice, etc.)

Have fun! Deployment is just another way of sharing the agent you already built.
