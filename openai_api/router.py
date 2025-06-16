from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from openai_api.service import ask_openai

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)


router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo"  

class PromptResponse(BaseModel):
    response: str

@router.post("/ask", response_model=PromptResponse)
@limiter.limit("3/minute")
def ask(prompt_request: PromptRequest, request: Request):
    try:
        result = ask_openai(prompt_request.prompt, prompt_request.model)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))