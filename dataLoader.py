from bson import ObjectId
import time

from AiScore import AIScoreInput
from mongodb import mongodbConn, carzcollection, carzdb

collection = carzcollection

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# the dataGather function is for the AI Score


def dataGather(collection, car_id):
    try:
        car_object_id = ObjectId(car_id)
        car_data = collection.find_one({"_id": car_object_id})

        if car_data:
            time_spent_values = [
                time["durationInMilliseconds"] for time in car_data.get("timeSpent", [])
            ]
            mean_time_spent = (
                sum(time_spent_values) / len(time_spent_values)
                if time_spent_values
                else 0
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

    except Exception as e:
        return "Error in dataGather function: ", e


# the data loader function for the recommadation model and the feed manager


def load_car_profiles_from_mongodb(user_id, user_coordinates):
    # Load car profiles from MongoDB based on the specified city and user ID

    startTime = time.time()

    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": user_coordinates,
                },
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": 500 * 1000,  # in-meters
                "query": {
                    "isActive": True,
                    "likes": {"$nin": [ObjectId(user_id)]},
                    "dislikes": {"$nin": [ObjectId(user_id)]},
                },
            },
        },
        {
            "$limit": 500,
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
        {
            "$addFields": {
                "lastAiScore": {"$arrayElemAt": ["$AiScore", -1]},
            },
        },
        # {
        #     "$match": {
        #         "carImages": {"$exists": True},
        #         "$expr": {"$gt": [{"$size": {"$ifNull": ["$carImages", []]}}, 1]},
        #     }
        # },
        {
            "$sort": {
                "lastAiScore": -1,
            },
        },
    ]

    try:
        # Execute explain on the aggregation pipeline
        # explain_result = carzdb.command('aggregate', collection.name, pipeline=pipeline, explain=True)

        # # Print execution statistics
        # print(explain_result['serverParameters'])

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
                "carid": car_id,
                "make": make,
                "gearbox": gearbox,
                "price": price,
                "fueltype": fuel_type,
                "engineSizeInLiter": engine_size_in_liter,
                "ai_score": ai_score,
            }

            car_profiles.append(car_profile)

        return car_profiles

    except Exception as e:
        print("Error in load_car_profiles_from_mongodb function: ", e)


def get_car_profiles_by_user_like(userId):
    pipeline = [
        {"$match": {"likes": {"$elemMatch": {"$eq": ObjectId(userId)}}}},
        {
            "$match": {
                "timeSpent.userId": ObjectId(userId),
                "timeSpent.isLiked": True,
            }
        },
        {"$sort": {"timeSpent.createdOn": -1}},
        {"$limit": 100},
        {
            "$project": {
                "make": 1,
                "fuelType": 1,
                "bodyType": 1,
                "engineSizeInLiter": 1,
                "gearbox": 1,
                "price": 1,
                "AiScore": 1,
            }
        },
    ]

    try:
        startTime = time.time()

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
                "carid": car_id,
                "make": make,
                "gearbox": gearbox,
                "price": price,
                "fueltype": fuel_type,
                "engineSizeInLiter": engine_size_in_liter,
                "ai_score": ai_score,
            }

            car_profiles.append(car_profile)

        return car_profiles

    except Exception as e:
        print("Error in load_car_profiles_from_mongodb function: ", e)


def get_car_profiles_by_user_dislike(userId):
    pipeline = [
        {"$match": {"dislikes": {"$elemMatch": {"$eq": ObjectId(userId)}}}},
        {
            "$match": {
                "timeSpent.userId": ObjectId(userId),
                "timeSpent.isLiked": False,
            }
        },
        {"$sort": {"timeSpent.createdOn": -1}},
        {"$limit": 100},
        {
            "$project": {
                "make": 1,
                "fuelType": 1,
                "bodyType": 1,
                "engineSizeInLiter": 1,
                "gearbox": 1,
                "price": 1,
                "AiScore": 1,
            }
        },
    ]

    try:
        startTime = time.time()

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
                "carid": car_id,
                "make": make,
                "gearbox": gearbox,
                "price": price,
                "fueltype": fuel_type,
                "engineSizeInLiter": engine_size_in_liter,
                "ai_score": ai_score,
            }

            car_profiles.append(car_profile)

        return car_profiles

    except Exception as e:
        print("Error in load_car_profiles_from_mongodb function: ", e)


def load_likes_interaction(userId, userLike):
    # Load user likes interaction data for further processing
    try:
        user_like_interaction = []

        like_id = userLike
        for car in like_id:
            L_id = car["carid"]
            user_like_interaction.append(
                {"user_id": userId, "carid": L_id, "interaction": 1}
            )

        return user_like_interaction

    except Exception as e:
        print("Error in load_likes_interaction function: ", e)


def load_dislikes_interaction(userId, userDisLike):
    try:
        user_like_interaction = []

        like_id = userDisLike
        for car in like_id:
            L_id = car["carid"]
            user_like_interaction.append(
                {"user_id": userId, "carid": L_id, "interaction": 0}
            )

        return user_like_interaction

    except Exception as e:
        print("Error in load_likes_interaction function: ", e)


def mainReturn(carIds):
    try:
        car_profiles = []

        object_ids = [ObjectId(carIds) for carIds in carIds]

        # Query to retrieve car data based on IDs
        query = {"_id": {"$in": object_ids}}

        # Fetch the data
        result = list(collection.find(query))
        # print(result)

        for item in result:
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
            isActive = item.get("isActive", None)

            # Check for the existence of the 'location' field
            location_data = item.get("location")
            coordinates = (
                location_data.get("coordinates", None) if location_data else None
            )
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
                "isActive": isActive,
                "location": (
                    None
                    if coordinates is None
                    else {"type": "Point", "coordinates": coordinates}
                ),
                "fuelConsumptionInMPG": fuelConsumptionInMPG,
            }

            car_profiles.append(car_profile)

        return car_profiles

    except Exception as e:
        print("Error in mainReturn function: ", e)


# the data Gather function below is for the Ad Status API
def getData(carID):
    carId = ObjectId(carID)

    query = {"_id": carId}

    data = []

    # Fetch the data
    result = list(carzcollection.find(query))

    for item in result:
        car_id = str(item.get("_id", ""))
        description = str(item.get("description", ""))
        carImages = item.get("carImages", [])
        adStatus = str(item.get("adStatus", ""))

        car_data = {
            "Id": car_id,
            "description": description,
            "images": carImages,
            "adStatus": adStatus,
        }

        data.append(car_data)

    return data
