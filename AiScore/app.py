from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from main import AiScoreMain

app = FastAPI()

class CarIdInput(BaseModel):
    carid: str

@app.post("/calculate_ai_score")
async def calculate_ai_score(car_data: CarIdInput):
    try:

        # Assuming you have a function named AiScoreMain that takes a car_id as input
        ai_score = AiScoreMain(car_data.carid)
        return {"car_id": car_data.carid, "ai_score": ai_score}

    except Exception as e:

        # Handle exceptions, log them, and return an appropriate response
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# if __name__ == "__main__":
#     # Use the uvicorn.run method to start the FastAPI application
#     uvicorn.run(app, port=9090)