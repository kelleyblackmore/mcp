
from fastapi import FastAPI, Query
import httpx
import os
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()

@app.get("/")
def root():
    return {"message": "MCP Server is running."}

@app.get("/llm")
async def call_llm_api(prompt: str, api_url: str = Query(...), api_key: str = Query(None)):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json={"prompt": prompt}, headers=headers)
        return response.json()


@app.get("/logs/github")
async def get_github_logs(owner: str, repo: str, run_id: int, token: str = Query(None)):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    # Use token from .env if not provided
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return {"log_url": str(response.url), "status": response.status_code, "token_used": bool(token)}

@app.get("/logs/gitlab")
async def get_gitlab_logs(project_id: int, job_id: int, token: str = Query(...)):
    url = f"https://gitlab.com/api/v4/projects/{project_id}/jobs/{job_id}/trace"
    headers = {"PRIVATE-TOKEN": token}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return {"logs": response.text, "status": response.status_code}
