from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import psutil
from contextlib import asynccontextmanager
from pydantic import BaseModel
from bson import ObjectId

from uk_boundary import is_within_uk_boundary
from main import AiScoreMain, FeedManagerMain, modelStatsMain, LikeandDislikecount

from mongodb import mongodbConn, usercollection

# from memory_profiler import profile

try:

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

    @app.middleware("http")
    async def monitor_usage(request, call_next):
        cpu_percent = psutil.cpu_percent()
        cpu_consumption = psutil.cpu_percent(interval=None, percpu=True)

        ram_usage = psutil.virtual_memory().percent
        ram_consumption = psutil.virtual_memory().used / (1024 * 1024)  # in MB

        # Log or store the CPU and RAM usage metrics
        print(f"CPU Usage: {cpu_percent}%")
        print("CPU Consumption:")
        for i, core in enumerate(cpu_consumption):
            print(f"    Core {i+1}: {core}%")
        print(f"RAM Usage: {ram_usage}%")
        print(f"RAM Consumption: {ram_consumption:.2f} MB")

        response = await call_next(request)
        return response

    # Base URL for the API
    app.baseURL = "https://aiengine.aicarz.com"

    # The single valid API key
    API_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

    # Dependency to check API key
    def check_api_key(api_key: str = Query(..., description="API Key")):
        if api_key != API_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key

    # **************************       APP CHECKING         **************************

    # Root Endpoint
    @app.get("/")
    def read_root():
        return {"message": "App is running successfully"}

    # **************************       AI SCORE API ENDPOINT         **************************

    class CarIdInput(BaseModel):
        carid: str  # Car ID as input

    # Ai Score API Endpoint
    # @profile
    @app.post("/aiscore")
    async def calculate_ai_score(
        car_data: CarIdInput,
        api_key: str = Depends(check_api_key, use_cache=True),
    ):

        # ================== Checking Valid ObjectId for Car ID ==================

        # Check if car_id is a valid MongoDB ObjectId
        if not ObjectId.is_valid(car_data.carid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid car_id. Must be a valid MongoDB ObjectId.",
            )

        # ======================= Ai Score Calculation =======================

        try:
            # Function named AiScoreMain that takes a car_id as input
            ai_score = AiScoreMain(car_data.carid)
            return {"Response": ai_score}

        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail="Internal Server Error") from e

    # **************************       FEED MANAGER API ENDPOINT         **************************

    # FeedManager API Endpoint
    class FeedManagerInput(BaseModel):
        user_id: str  # User ID as input
        longitude: float  # User longitude: float
        latitude: float  # User latitude: float

    # @profile
    @app.post("/feedmanager")
    async def feed_manager(
        feed_data: FeedManagerInput,
        api_key: str = Depends(check_api_key, use_cache=True),
    ):

        # ======================= Checking if UserID is correct Object Id =======================

        # Check if user_id is a valid MongoDB ObjectId
        if not ObjectId.is_valid(feed_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id. Must be a valid MongoDB ObjectId.",
            )

        # ======================= Checking if UserID is in Database or not =======================

        # Check if user_id exists in the database
        if not usercollection.find_one({"_id": ObjectId(feed_data.user_id)}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Id not found in database.",
            )

        # ===================== Validating the Longitude and Latitude is empty or not =====================

        # Validate input data
        if not feed_data.longitude or not feed_data.latitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Longitude and latitude are required fields.",
            )

        # ===================== Validating the Longitude and Latitude is correct =====================

        # try:
        # Validate longitude and latitude input data
        longitude = float(feed_data.longitude)
        latitude = float(feed_data.latitude)

        # Check if longitude is in the valid range [-180, 180]
        if not (-180 <= longitude <= 180):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Longitude format is invalid.",
            )

        # Check if latitude is in the valid range [-90, 90]
        if not (-90 <= latitude <= 90):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude format is invalid.",
            )
        
        location = is_within_uk_boundary(latitude,longitude)
        
        print("LOCATION:", location)
        
        if location is not True:
            return [{"message": "LOCATION_OUT_OF_UK_BOUNDARY",
                    "errorCode": "LOCATION_OUT_OF_UK_BOUNDARY"}]

        try:
            coordinates = [feed_data.longitude, feed_data.latitude]

            # Function named FeedManagerMain that takes a user_id and coordinates as input
            carIds_output = FeedManagerMain(feed_data.user_id, coordinates)

            return carIds_output

        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail=str(e))

    # **************************       Model Stats API ENDPOINT         **************************

    # Model Stats Endpoint
    class modelStatsInput(BaseModel):
        user_id: str  # User ID as input

    @app.post("/modelStats")
    async def modelStats(
        modelstats: modelStatsInput,
        api_key: str = Depends(check_api_key, use_cache=True),
    ):
        longitude = 2.9916
        latitude = 53.4048

        try:
            coordinates = [longitude, latitude]
            stats_output = modelStatsMain(modelstats.user_id, coordinates)
            return stats_output
        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail=e)

    # **************************       Like and Dislike Count API ENDPOINT         **************************

    class LikeandDislikecountInput(BaseModel):
        user_id: str  # User ID as input
        longitude: float  # User longitude: float
        latitude: float  # User latitude: float

    @app.post("/likeanddislikecount")
    async def likeanddislikecount(
        likeanddislikecount_data: LikeandDislikecountInput,
        api_key: str = Depends(check_api_key, use_cache=True),
    ):
        # ======================= Checking if UserID is correct Object Id =======================

        # Check if user_id is a valid MongoDB ObjectId
        if not ObjectId.is_valid(likeanddislikecount_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id. Must be a valid MongoDB ObjectId.",
            )

        # ======================= Checking if UserID is in Database or not =======================

        # Check if user_id exists in the database
        if not usercollection.find_one(
            {"_id": ObjectId(likeanddislikecount_data.user_id)}
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Id not found in database.",
            )

        # ===================== Validating the Longitude and Latitude is empty or not =====================

        # Validate input data
        if (
            not likeanddislikecount_data.longitude
            or not likeanddislikecount_data.latitude
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Longitude and latitude are required fields.",
            )

        # ===================== Validating the Longitude and Latitude is empty or not =====================

        # Validate longitude and latitude input data
        try:
            longitude = float(likeanddislikecount_data.longitude)
            latitude = float(likeanddislikecount_data.latitude)

            # Check if longitude is in the valid range [-180, 180]
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude format is invalid.")

            # Check if latitude is in the valid range [-90, 90]
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude format is invalid.")

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid longitude or latitude format.",
            )

        try:
            coordinates = [
                likeanddislikecount_data.longitude,
                likeanddislikecount_data.latitude,
            ]
            likeanddislikecount_output = LikeandDislikecount(
                likeanddislikecount_data.user_id, coordinates
            )
            return likeanddislikecount_output

        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail=e)

except Exception as e:
    print(e)
