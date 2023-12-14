from bson import ObjectId
import pymongo
import logging
import random
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


def load_car_profiles_from_mongodb(user_id, coordinates):
    # Load car profiles from MongoDB based on the specified city and user ID
    result = collection.find(
        {
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": coordinates},
                    "$maxDistance": 482803,
                }
            },
            "isActive": True,  # Add this filter to check for isActive field
            "$and": [
                {"likes": {"$nin": [ObjectId(user_id)]}},
                {"dislikes": {"$nin": [ObjectId(user_id)]}},
            ],
        },
        {
            "make": 1,
            "fuelType": 1,
            "gearbox": 1,
            "engineSizeInLiter": 1,
            "price": 1,
            "_id": 1,
            "AiScore": 1,
        },
    )

    data = list(result)
    car_profiles = []

    # Extract relevant information from MongoDB query results
    for item in data:
        car_id = str(item.get("_id", ""))
        make = item.get("make", "")
        fuelType = item.get("fuelType", "")
        gearbox = item.get("gearbox", "")
        engineSizeInLiter = item.get("engineSizeInLiter", 0.0)
        price = item.get("price", 0.0)
        aiScore = item.get("AiScore", 0.0)[-1]

        car_profile = {
            "id": car_id,
            "make": make,
            "gearbox": gearbox,
            "price": price,
            "fueltype": fuelType,
            "engineSizeInLiter": engineSizeInLiter,
            "AiScore": aiScore,
        }

        car_profiles.append(car_profile)

    return car_profiles


def load_user_likes(user_id):
    # Load user likes from MongoDB based on user ID
    user_data = collection.find({"likes": ObjectId(user_id)})
    user_likes = {"user_id": user_id, "likes": extract_car_data(user_data)}

    # If user_likes["likes"] is empty, get random likes from the collection (up to 25)
    if not user_likes["likes"]:
        user_likes["likes"].extend(get_random_cars(user_id, "likes", limit=25))

    return user_likes


def load_user_dislikes(user_id):
    # Load user dislikes from MongoDB based on user ID
    user_data = collection.find({"dislikes": ObjectId(user_id)})
    user_dislikes = {"user_id": user_id, "dislikes": extract_car_data(user_data)}

    # If user_dislikes["dislikes"] is empty, get random dislikes from the collection (up to 25)
    if not user_dislikes["dislikes"]:
        user_dislikes["dislikes"].extend(get_random_cars(user_id, "dislikes", limit=25))

    return user_dislikes


def extract_car_data(user_data):
    # Extract car information from user data
    return [
        {
            "id": str(doc["_id"]),
            "make": doc["make"],
            "gearbox": doc["gearbox"],
            "fueltype": doc["fuelType"],
            "price": doc["price"],
            "engineSizeInLiter": doc["engineSizeInLiter"],
        }
        for doc in user_data
    ]


def get_random_cars(user_id, category, limit=25):
    # Implement a function to retrieve random cars from the MongoDB collection
    query = {
        "$and": [
            {f"{category}": {"$ne": ObjectId(user_id)}},
            {"_id": {"$nin": get_user_ids(user_id, category)}},
        ]
    }
    random_cars = collection.find(query).limit(limit)

    return extract_car_data(random_cars)


def get_user_ids(user_id, category):
    # Get a list of IDs from the specified category (likes or dislikes) for the given user
    user_data = collection.find({category: ObjectId(user_id)})
    return [doc["_id"] for doc in user_data]


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
