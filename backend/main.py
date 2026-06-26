from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from ai_agent import graph, SYSTEM_PROMPT, parse_response

app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/ask")
async def ask(query: Query):
    try:
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", query.message)]}
        tool_called_name, final_response = parse_response(inputs)

        return {
            "response": final_response,
            "tool_called": tool_called_name
        }
    except Exception as e:
        print(f"Backend error: {e}")
        return {   
            "response": "I'm having trouble. Please try again.",
            "tool_called": "None"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)