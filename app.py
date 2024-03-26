from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Query,
    status,
    File,
    UploadFile,
    Request,
)
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from io import BytesIO


from contextlib import asynccontextmanager
from pydantic import BaseModel, validator
from bson import ObjectId

from main import AiScoreMain, FeedManagerMain, modelStatsMain, LikeandDislikecount

from mongodb import mongodbConn, carzcollection, usercollection

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

    class CatchLargeUploadMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if "content-length" in request.headers:
                content_length = int(request.headers["content-length"])
                max_size = 5 * 1024 * 1024  # 5 MB
                if content_length > max_size:
                    return JSONResponse(
                        status_code=413,
                        content={"message": "Please upload a file of maximum 5 MB."},
                    )
            response = await call_next(request)
            return response

    app.add_middleware(CatchLargeUploadMiddleware)

    # Base URL for the API
    app.baseURL = "https://aiengine.aicarz.com"

    # The single valid API key
    API_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

    # Dependency to check API key
    def check_api_key(api_key: str = Query(..., description="API Key")):
        if api_key != API_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key

    # **************************       BODY INPUT FOR API ENDPOINT         **************************
    class FileUploadInput(BaseModel):
        file: UploadFile

        @validator("file")
        def check_file_format(cls, v):
            allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
            if v.content_type not in allowed_formats:
                raise ValueError(
                    "Invalid file type: Only PNG, JPG, and JPEG are allowed."
                )
            return v

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
                detail="User Id not found in database .",
            )

        # ===================== Validating the Longitude and Latitude is empty or not =====================

        # Validate input data
        if not feed_data.longitude or not feed_data.latitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Longitude and latitude are required fields.",
            )

        # ===================== Validating the Longitude and Latitude is empty or not =====================

        # Validate longitude and latitude input data
        try:
            longitude = float(feed_data.longitude)
            latitude = float(feed_data.latitude)

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

            coordinates = [feed_data.longitude, feed_data.latitude]

            # Function named FeedManagerMain that takes a car_id and coordinates as input
            carIds_ouput = FeedManagerMain(feed_data.user_id, coordinates)

            return carIds_ouput

        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail=e)

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

    # **************************       Car AD Checker API ENDPOINT         **************************

    # class AdCarIdInput(BaseModel):
    #     carid: str  # Car ID as input

    # # car AdChecking API Endpoint
    # # @profile
    # @app.post("/adChecker")
    # async def car_ad_checker(
    #     car_data: AdCarIdInput,
    #     api_key: str = Depends(check_api_key, use_cache=True),
    # ):

    #     # ================== Checking Valid ObjectId for Car ID ==================

    #     # Check if car_id is a valid MongoDB ObjectId
    #     if not ObjectId.is_valid(car_data.carid):
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid car_id. Must be a valid MongoDB ObjectId.",
    #         )

    #     # ======================= Checking if UserID is in Database or not =======================

    #     # Check if user_id exists in the database
    #     if not carzcollection.find_one({"_id": ObjectId(car_data.carid)}):
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="User Id not found in database.",
    #         )

    #     # ======================= Ad Checking =======================

    #     try:
    #         # car_ad_score = carAdMain(car_data.carid)
    #         car_ad_score = dummy(car_data.carid)
    #         return car_ad_score

    #     except Exception as e:
    #         # Handle exceptions, log them, and return an appropriate response
    #         raise HTTPException(status_code=500, detail="Internal Server Error") from e

    # **************************       Car Tier Tread API ENDPOINT         **************************
    # class CarTireInput(FileUploadInput):
    #     file: UploadFile

    # @app.post("/tirechecker")
    # async def tire_checker(
    #     file_input: CarTireInput = Depends(),
    #     api_key: str = Depends(check_api_key, use_cache=True),
    # ):
    #     try:
    #         contents = await file_input.file.read()
    #         result = carTire(contents)
    #         return {"result": result}
    #     except ValueError as e:
    #         raise HTTPException(status_code=400, detail=str(e))
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    # **************************       Car Body Pannel Gap API ENDPOINT         **************************

    # class CarPanelInput(FileUploadInput):
    #     file: UploadFile

    # @app.post("/panelgap")
    # async def panel_gap(
    #     panel_input: CarPanelInput = Depends(), api_key: str = Depends(check_api_key)
    # ):
    #     try:
    #         contents = await panel_input.file.read()
    #         # Process car panel gap analysis using panel_input.car_id
    #         # Replace the following line with your actual implementation
    #         # result = process_car_panel_gap(contents, panel_input.car_id)
    #         return StreamingResponse(
    #             BytesIO(contents), media_type=panel_input.file.content_type
    #         )
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

except Exception as e:
    print(e)
