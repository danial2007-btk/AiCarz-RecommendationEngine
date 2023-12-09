from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel

from main import AiScoreMain,FeedManagerMain

app = FastAPI()

# The single valid API key
API_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

# Dependency to check API key
def check_api_key(api_key: str = Query(..., description="API Key")):
    if api_key != API_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

class CarIdInput(BaseModel):
    carid: str  # Car ID as input

# Ai Score API Endpoint
@app.post("/aiscore")
async def calculate_ai_score(
    car_data: CarIdInput,
    api_key: str = Depends(check_api_key, use_cache=True),
):
    try:
        # Function named AiScoreMain that takes a car_id as input
        ai_score = AiScoreMain(car_data.carid)
        return {"CarId": car_data.carid, "AIScore": ai_score}

    except Exception as e:
        # Handle exceptions, log them, and return an appropriate response
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    
    

# FeedManager API Endpoint
class FeedManagerInput(BaseModel):
    user_id: str # User ID as input
    longitude: float # User latitude as input
    latitude: float # User longitude as input
    
@app.post("/feedmanager")
async def feed_manager(
    feed_data: FeedManagerInput,
    api_key: str = Depends(check_api_key, use_cache=True),
):
    try:
        
        coordinates = []
        coordinates.append(feed_data.longitude)
        coordinates.append(feed_data.latitude)
        
        # print("User ID: ", feed_data.user_id)
        # print("User Coordinates: ", coordinates)
                        
        # Function named AiScoreMain that takes a car_id as input
        carIds_ouput = FeedManagerMain(feed_data.user_id, coordinates)
        print("output in APP:::",carIds_ouput)
        
        return carIds_ouput

    except Exception as e:
        # Handle exceptions, log them, and return an appropriate response
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    