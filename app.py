# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import uvicorn

# from main import AiScoreMain

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
    
# if __name__ == "__main__":
#     # Use the uvicorn.run method to start the FastAPI application
#     uvicorn.run(app, port=9090)


from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel

from main import AiScoreMain

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