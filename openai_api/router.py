from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai_api.service import ask_openai

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo"  

class PromptResponse(BaseModel):
    response: str

@router.post("/ask", response_model=PromptResponse)
def ask(prompt_request: PromptRequest):
    try:
        result = ask_openai(prompt_request.prompt, prompt_request.model)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))