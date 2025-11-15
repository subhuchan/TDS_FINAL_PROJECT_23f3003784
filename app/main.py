from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from app.task_processor import process_task_background

load_dotenv()
USER_SECRET = os.getenv("USER_SECRET")

app = FastAPI(title="TDS Project 1 - LLM Code Deployment")

@app.get("/")
async def root():
    return {"status": "running", "message": "TDS Project 1 API Server"}

@app.post("/api-endpoint")
async def api_endpoint(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        
        # Validate secret
        if data.get("secret") != USER_SECRET:
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid secret"}
            )
        
        # Add background task
        background_tasks.add_task(process_task_background, data)
        
        # Immediate 200 response
        return {
            "status": "accepted",
            "note": f"processing round {data.get('round', 1)} started"
        }
        
    except Exception as e:
        print(f"Error in api_endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
