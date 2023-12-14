from bson import ObjectId
import pymongo
import time
import logging
import random
from concurrent.futures import ThreadPoolExecutor

from mongodb import mongodbConn, carzcollection, carzdb

collection = carzcollection


# Correct import for AIScoreInput in app.py
from AiScore import AIScoreInput

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dataGather(collection, car_id):
    # try:
    car_object_id = ObjectId(car_id)
    car_data = collection.find_one({"_id": car_object_id})

    if car_data:
        time_spent_values = [
            time["durationInMilliseconds"] for time in car_data.get("timeSpent", [])
        ]
        mean_time_spent = (
            sum(time_spent_values) / len(time_spent_values) if time_spent_values else 0
        )
        ai_score_last_value = (
            car_data.get("AiScore", [])[-1] if car_data.get("AiScore") else 0
        )

        total_likes = len(car_data.get("likes", []))
        total_dislikes = len(car_data.get("dislikes", []))
        total_favorites = len(car_data.get("favorites", []))

        # Calculate total_ad_displayed
        total_ad_displayed = total_likes + total_dislikes

        # Set values to 0 if they are null
        total_likes = total_likes or 0
        total_dislikes = total_dislikes or 0
        total_favorites = total_favorites or 0

        return AIScoreInput(
            last_ai_score=ai_score_last_value,
            total_likes=total_likes,
            total_dislikes=total_dislikes,
            total_favorites=total_favorites,
            total_time_displayed=mean_time_spent,
            total_ad_displays=total_ad_displayed,
        )

    else:
        print("Car not found.")
        # Return default values
        return AIScoreInput(0, 0, 0, 0, 0, 0)


# the data loader function for the recommadation model and the feed manager


def load_car_profiles_from_mongodb(user_id, user_coordinates):
    # Load car profiles from MongoDB based on the specified city and user ID

    startTime = time.time()

    print("Inside DataLoader load_car_profiles_from_mongodb: ")
    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": user_coordinates,
                },
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": 500 * 1000,  # in meters
            },
        },
        {
            "$match": {
                "isActive": True,
            },
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "likes",
                "as": "likedByUser",
            },
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "dislikes",
                "as": "dislikedByUser",
            },
        },
        {
            "$match": {
                "likedByUser": {"$not": {"$elemMatch": {"$eq": user_id}}},
                "dislikedByUser": {"$not": {"$elemMatch": {"$eq": user_id}}},
            },
        },
        {
            "$addFields": {
                "lastAiScore": {"$arrayElemAt": ["$AiScore", -1]},
            },
        },
        {
            "$project": {
                "carBuyLink": 1,
                "carImages": 1,
                "make": 1,
                "model": 1,
                "variant": 1,
                "mileageInMiles": 1,
                "year": 1,
                "ageIdentifier": 1,
                "fuelType": 1,
                "bodyType": 1,
                "engineSizeInLiter": 1,
                "gearbox": 1,
                "price": 1,
                "currency": 1,
                "cityName": 1,
                "location": 1,
                "distance": 1,
                "lastAiScore": 1,
            },
        },
        {
            "$limit": 1000,
        },
        {
            "$sort": {
                "lastAiScore": -1,
            },
        },
    ]

    # Execute the pipeline
    result = collection.aggregate(pipeline)

    endTime = time.time()
    print("Time taken to load car profiles from MongoDB: ", endTime - startTime)

    # Extract relevant information from MongoDB query results
    car_profiles = []

    for item in result:
        car_id = str(item.get("_id", ""))
        make = item.get("make", "")
        fuel_type = item.get("fuelType", "")
        gearbox = item.get("gearbox", "")
        engine_size_in_liter = item.get("engineSizeInLiter", 0.0)
        price = item.get("price", 0.0)
        ai_score = item.get("lastAiScore", 0.0)

        car_profile = {
            "id": car_id,
            "make": make,
            "gearbox": gearbox,
            "price": price,
            "fuel_type": fuel_type,
            "engine_size_in_liter": engine_size_in_liter,
            "ai_score": ai_score,
        }

        car_profiles.append(car_profile)

    return car_profiles


def get_car_profiles_by_user_like(user_id):
    print("Inside DataLoader get_car_profiles_by_user_like: ")

    pipeline = [
        {
            "$match": {
                "likes": user_id,
            },
        },
        {
            "$project": {
                "make": 1,
                "fuelType": 1,
                "bodyType": 1,
                "engineSizeInLiter": 1,
                "gearbox": 1,
                "price": 1,
                "lastAiScore": 1,
            },
        },
    ]

    # Execute the pipeline
    result = collection.aggregate(pipeline)

    # Extract car profiles from MongoDB query results
    car_profiles = []

    for item in result:
        car_id = str(item.get("_id", ""))
        make = item.get("make", "")
        gearbox = item.get("gearbox", "")
        price = item.get("price", 0.0)
        fuel_type = item.get("fuelType", "")
        engine_size_in_liter = item.get("engineSizeInLiter", 0.0)
        ai_score = item.get("lastAiScore", 0.0)

        car_profile = {
            "id": car_id,
            "make": make,
            "gearbox": gearbox,
            "price": price,
            "fuel_type": fuel_type,
            "engine_size_in_liter": engine_size_in_liter,
            "ai_score": ai_score,
        }

        car_profiles.append(car_profile)

    return car_profiles


def get_car_profiles_by_user_dislike(user_id):
    print("Inside DataLoader get_car_profiles_by_user_dislike: ")

    pipeline = [
        {
            "$match": {
                "dislikes": user_id,
            },
        },
        {
            "$project": {
                "make": 1,
                "fuelType": 1,
                "bodyType": 1,
                "engineSizeInLiter": 1,
                "gearbox": 1,
                "price": 1,
                "lastAiScore": 1,
            },
        },
    ]

    # Execute the pipeline
    result = collection.aggregate(pipeline)

    # Extract car profiles from MongoDB query results
    car_profiles = []

    for item in result:
        car_id = str(item.get("_id", ""))
        make = item.get("make", "")
        gearbox = item.get("gearbox", "")
        price = item.get("price", 0.0)
        fuel_type = item.get("fuelType", "")
        engine_size_in_liter = item.get("engineSizeInLiter", 0.0)
        ai_score = item.get("lastAiScore", 0.0)

        car_profile = {
            "id": car_id,
            "make": make,
            "gearbox": gearbox,
            "price": price,
            "fuel_type": fuel_type,
            "engine_size_in_liter": engine_size_in_liter,
            "ai_score": ai_score,
        }

        car_profiles.append(car_profile)

    return car_profiles


def load_likes_interaction(userId):
    # Load user likes interaction data for further processing
    user_likes_data = load_user_likes(userId)
    user_car_data = []

    like_id = user_likes_data["likes"]
    for car in like_id:
        L_id = car["id"]
        user_car_data.append({"user_id": userId, "id": L_id, "interaction": 1})

    return user_car_data


def load_dislikes_interaction(userId):
    # Load user dislikes interaction data for further processing
    user_dislikes_data = load_user_dislikes(userId)
    user_car_data = []

    dislike_id = user_dislikes_data["dislikes"]
    for car in dislike_id:
        D_id = car["id"]
        user_car_data.append({"user_id": userId, "id": D_id, "interaction": 0})

    return user_car_data


def mainReturn(carIds):
    carid = carIds
    result = collection.find({"_id": ObjectId(carid)})

    data = list(result)
    car_profiles = []

    for item in data:
        car_id = str(item.get("_id", ""))
        make = item.get("make", None)
        fuelType = item.get("fuelType", None)
        gearbox = item.get("gearbox", None)
        engineSizeInLiter = item.get("engineSizeInLiter", None)
        price = item.get("price", None)
        carBuyLink = item.get("carBuyLink", None)
        carImages = item.get("carImages", [])
        model = item.get("model", None)
        variant = item.get("variant", None)
        mileageInMiles = item.get("mileageInMiles", None)
        year = item.get("year", None)
        ageIdentifier = item.get("ageIdentifier", None)
        bodyType = item.get("bodyType", None)
        currency = item.get("currency", None)
        description = item.get("description", None)
        cityName = item.get("cityName", None)
        fuelConsumptionInMPG = item.get("fuelConsumptionInMPG", None)
        # Check for the existence of the 'location' field
        location_data = item.get("location")
        coordinates = location_data.get("coordinates", None) if location_data else None
        if coordinates is None:
            location_data = None

        # Replace None values with null
        car_profile = {
            "_id": car_id,
            "carBuyLink": carBuyLink,
            "carImages": carImages,
            "make": make,
            "model": model,
            "variant": variant,
            "cityName": cityName,
            "mileageInMiles": mileageInMiles,
            "year": year,
            "ageIdentifier": ageIdentifier,
            "fuelType": fuelType,
            "bodyType": bodyType,
            "engineSizeInLiter": engineSizeInLiter,
            "gearbox": gearbox,
            "price": price,
            "currency": currency,
            "description": description,
            "location": None
            if coordinates is None
            else {"type": "Point", "coordinates": coordinates},
            "fuelConsumptionInMPG": fuelConsumptionInMPG,
        }

        car_profiles.append(car_profile)

    # print("Inside DataLoader mainReturn: ", car_profile)

    return car_profile


def getData(user_id, coordinates):
    # User ID
    user_id = user_id
    # User coordinates
    coordinates = coordinates
    print("inside the getData function")

    try:
        startTime = time.time()

        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_load = executor.submit(
                load_car_profiles_from_mongodb, user_id, coordinates
            )
            future_like = executor.submit(get_car_profiles_by_user_like, user_id)
            future_dislike = executor.submit(get_car_profiles_by_user_dislike, user_id)

        # Retrieve results from the futures
        car_profiles_load = future_load.result()
        car_profiles_like = future_like.result()
        car_profiles_dislike = future_dislike.result()
        
        endTime = time.time()
        print("Took: ", endTime - startTime)
        
    except Exception as e:
        print("Error in getData function: ", e)

    return car_profiles_load, car_profiles_like, car_profiles_dislike
