# FastAPI Backend API

## Development Server

For Windows:
```bash
uv run uvicorn main:app
```

With custom host/port:
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

```
GET /leetcode_stats/{username}
GET /github_stats/{username}
GET /geeksforgeeks_stats/{username}
```