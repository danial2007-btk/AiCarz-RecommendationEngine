from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from dataLoader import dataGather, collection
from AiScore import AIScoreInput, AIScoreCalculator

def AiScoreMain(car_id):
        
    car_id = car_id

    # Assuming gathered_data is the result of dataGather function
    aiscore_input = dataGather(collection, car_id)

    # Create an instance of AIScoreCalculator
    aiscore_calculator = AIScoreCalculator()

    # Calculate AI Score
    ai_score = aiscore_calculator.calculate_ai_score(aiscore_input)

    # Print the AI Score
    # print("AI Score: %.4f" % ai_score)
    ai_score_rounded = round(ai_score, 4)

    return ai_score_rounded


# app = FastAPI()

# class CarIdInput(BaseModel):
#     carid: str

# @app.post("/calculate_ai_score")
# async def calculate_ai_score(car_data: CarIdInput):
#     try:

#         # Assuming you have a function named AiScoreMain that takes a car_id as input
#         ai_score = AiScoreMain(car_data.carid)
#         return {"car_id": car_data.carid, "ai_score": ai_score}

#     except Exception as e:

#         # Handle exceptions, log them, and return an appropriate response
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    
# if __name__ == "__app__":
#     # Use the uvicorn.run method to start the FastAPI application
#     uvicorn.run(app, host="0.0.0.0", port=100)