from bson import ObjectId
import concurrent.futures
import time
from mongodb import mongodbConn, carzcollection, carzdb

# Calling Function form the Files
from AiScore import AIScoreInput, AIScoreCalculator
from dataLoader import dataGather

collection = carzcollection


def AiScoreMain(car_id):
    carId = car_id

    # Assuming gathered_data is the result of dataGather function
    aiscore_input = dataGather(collection, carId)

    # Create an instance of AIScoreCalculator
    aiscore_calculator = AIScoreCalculator()

    # Calculate AI Score
    ai_score = aiscore_calculator.calculate_ai_score(aiscore_input)

    # Print the AI Score
    getAiScore = round(ai_score, 4)

    # Specify the filter criteria (in this case, finding a document by _id)
    filter_criteria = {"_id": ObjectId(carId)}

    if getAiScore is not None:
        # Specify the update operation (in this case, using $push to update the AiScore field)
        update_operation = {"$push": {"AiScore": getAiScore}}

        # Perform the update
        result = carzcollection.update_one(filter_criteria, update_operation)

        # Check if the update was successful
        if result.modified_count > 0:
            return "Update successful"
        else:
            return "No matching document found"

    else:
        return "CarId not found / AiScore not found"


# The below work is a structure of Main function where the feed manager will be called and the recommendations will be generated

from model import get_top_n_recommendations

from feedManager import feedCarId

from dataLoader import (
    get_car_profiles_by_user_like,
    get_car_profiles_by_user_dislike,
    load_car_profiles_from_mongodb,
    load_likes_interaction,
    load_dislikes_interaction,
    mainReturn
)

def FeedManagerMain(user_id, coordinates):
    # User ID
    user_id = user_id

    # User coordinates
    coordinates = coordinates

    try:
        # load Car Objects from the MongoDB
        carData = load_car_profiles_from_mongodb(user_id, coordinates)
        
        # Get the AI Score and Random Cars
        feedCar = feedCarId(carData)
        print("len of FeedCar",len(feedCar))

        # Load User Like History
        userLike = get_car_profiles_by_user_like(user_id)        
        userInteraction_like = load_likes_interaction(user_id, userLike)

        # Get Like Recommendation
        likeRecommended = get_top_n_recommendations(user_id, carData, userLike, userInteraction_like)
        print("len of LikeRecommended",len(likeRecommended))
        
        #Load User Dislike History
        userDislike = get_car_profiles_by_user_like(user_id)        
        userInteraction_dislike = load_dislikes_interaction(user_id,userDislike)

        # Get DisLike Recommendation
        dislikeRecommended = get_top_n_recommendations(user_id, carData, userDislike, userInteraction_dislike)
        print("len of DislikeRecommended",len(dislikeRecommended))
        #Checking that all the car IDs are Unique
        
        carIDs = set(likeRecommended + dislikeRecommended + feedCar)
        carIDs = list(carIDs)
        carIDs = carIDs[:25]            
        print("Length of CarIDs",len(carIDs))
                 
        # if len(carIDs) < 25:
        #     carIDs = feedCar
            
        carGets = []
        startTime = time.time()
        
        for ids in carIDs:
            carGets.append(mainReturn(ids))

        endTime = time.time()
        print("Time Taken:", endTime - startTime)
        
        return carGets

    except Exception as e:
        print("Exception in Main Function:", e)