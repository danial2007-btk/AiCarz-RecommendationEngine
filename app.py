from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel

from main import AiScoreMain,FeedManagerMain
from mongodb import mongodbConn, carzcollection, carzdb
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("======> loading statup event")
    # ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    print("xxxxxxxx   shurting down event")
    mongodbConn.close()
    print("mongodb disconnected")    
    
app = FastAPI(lifespan=lifespan)


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
        return {"Response": ai_score}

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
        print(coordinates)
        
        # Function named FeedManagerMain that takes a car_id and coordinates as input
        carIds_ouput = FeedManagerMain(feed_data.user_id, coordinates)        
        return carIds_ouput

    except Exception as e:
        # Handle exceptions, log them, and return an appropriate response
        raise HTTPException(status_code=500, detail="Internal Server Error::") from e
    