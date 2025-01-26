# Profit and Loss Extractor Python Backend
## Tech stack:
- Python 3.11
- Poetry
- Sanic
- Docker

## How to Deploy
Instead of deploying the backend alone, you should use the given docker-compose.yml file in the root dir where both frontend and backend directories are found. (One level up than this README file) to run both frontend and backend together.

Before deploying, make sure the `.env` file is properly configured in the backend project root directory.
If you cannot find a `.env` in the root dir, please create one with the following variables.

```.env
# server configs
PLEX_ROUTER_HOST=0.0.0.0
PLEX_ROUTER_PORT=8000
PLEX_ROUTER_WORKERS=2
PLEX_ROUTER_ACCESS_LOG=false
PLEX_ROUTER_DEBUG_MODE=true
PLEX_ROUTER_CORS_ORIGIN=*

# mongodb configs
PLEX_MONGO_URI=<your_secure_mongo_connection_string>
PLEX_MONGO_DB=arcadea_test

# llm configs
PLEX_DEEPSEEK_BASE_URL=https://api.deepseek.com
PLEX_DEEPSEEK_API_KEY=<your_deepseek_api_key>
PLEX_DEEPSEEK_LLM_MODEL=deepseek-chat
PLEX_LLM_TEMPERATURE=0.0
PLEX_LLM_MAX_TOKENS=1000
```

- Once the env is created, go one level up and simply run `docker compose up -d` to run the frontend and backend services
- You can find the primary README file in the project root, one level up.
