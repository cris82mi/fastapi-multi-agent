from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from swarm import Swarm, Agent, Result
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Swarm client
client = Swarm()

class Query(BaseModel):
    text: str

# Define agent transfer functions
def transfer_to_agent1():
    return agent1

def transfer_to_agent2():
    return agent2

# Define agents
manager_agent = Agent(
    name="Manager",
    model="gpt-4o-mini",
    instructions="""You are the manager agent. Your role is to analyze user queries and:
    1. Direct questions about bills or bill savings to Agent2 (the bill expert)
    2. Direct all other questions to Agent1 (the general expert)
    Use transfer_to_agent1() or transfer_to_agent2() based on the query content.""",
    functions=[transfer_to_agent1, transfer_to_agent2]
)

agent1 = Agent(
    name="GeneralAgent",
    model="gpt-4o-mini",
    instructions="You are the main agent. Respond to any general questions. Always start your response with 'I am the main agent.'."
)

agent2 = Agent(
    name="BillExpert",
    model="gpt-4o-mini",
    instructions="You are the bill expert. Handle all questions related to bills and bill savings. Always start your response with 'I am the bill expert.'."
)

@app.post("/query")
async def process_query(query: Query):
    try:
        # Create message format for Swarm
        messages = [{"role": "user", "content": query.text}]
        
        # Process query through manager agent first
        response = client.run(
            agent=manager_agent,
            messages=messages,
            max_turns=3  # Limit the number of turns to prevent infinite loops
        )
        
        # Extract the final response
        final_response = response.messages[-1]["content"]
        
        return {"response": final_response, "agent": response.agent.name}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)