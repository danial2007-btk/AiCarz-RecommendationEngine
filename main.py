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
