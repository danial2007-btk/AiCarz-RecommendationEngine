from bson import ObjectId
import concurrent.futures
import time

import warnings
warnings.filterwarnings("ignore") 

# from memory_profiler import profile

from mongodb import mongodbConn, carzcollection, carzdb

# Calling Function form the Files
from AiScore import AIScoreInput, AIScoreCalculator
from dataLoader import dataGather

# The below work is a structure of Main function where the feed manager will be called and the recommendations will be generated

from model import get_top_n_recommendations
from feedManager import feedCarId, aiScore_carIDs
from dataLoader import get_car_profiles_by_user_like,get_car_profiles_by_user_dislike,load_car_profiles_from_mongodb,load_likes_interaction,load_dislikes_interaction,mainReturn


collection = carzcollection

# @profile
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
        try:
            # Specify the update operation (in this case, using $push to update the AiScore field)
            update_operation = {"$push": {"AiScore": getAiScore}}

            # Perform the update
            result = carzcollection.update_one(filter_criteria, update_operation)

            # Check if the update was successful
            if result.modified_count > 0:
                return "Update successful"
            else:
                return "No matching document found"
            
        except Exception as e:
            print("Exception in AiScoreMain Function:", e)

    else:
        return "CarId not found / AiScore not found"


# @profile
def FeedManagerMain(user_id, coordinates):
    
    # User ID
    user_id = user_id

    # User coordinates
    coordinates = coordinates

    carIDs = []
    
    try:
        # load Car Objects from the MongoDB
        carData = load_car_profiles_from_mongodb(user_id, coordinates)

        # Load User Like History
        userLike = get_car_profiles_by_user_like(user_id)   
        # print("UserLike",userLike)
             
            
        #Load User Dislike History
        userDislike = get_car_profiles_by_user_dislike(user_id)   
        # print("UserDislike",userDislike)     
        
        if userLike and userDislike:
            
            #Load User Interaction History
            userInteraction_like = load_likes_interaction(user_id, userLike)
            userInteraction_dislike = load_dislikes_interaction(user_id,userDislike)
            
            # Get the AI Score and Random Cars
            feedCar = feedCarId(carData)
            
            # Get Like Recommendation
            likeRecommended = get_top_n_recommendations(user_id, carData, userLike, userInteraction_like)
            # print("len of LikeRecommended",len(likeRecommended))

            # Get DisLike Recommendation
            dislikeRecommended = get_top_n_recommendations(user_id, carData, userDislike, userInteraction_dislike)
            dislikeRecommended = dislikeRecommended[:10]
            # print("len of DislikeRecommended",len(dislikeRecommended))
                    
            # Combine like and dislike recommendations
            combinedRecommendations = likeRecommended + dislikeRecommended

            # Create a set to track unique carIDs
            uniqueCarIDs = set()

            # Initialize the final carIDs list
            carIDs = []

            # Iterate through combinedRecommendations and feedCar in a single loop
            for carID in combinedRecommendations + feedCar:
                if carID not in uniqueCarIDs:
                    carIDs.append(carID)
                    uniqueCarIDs.add(carID)

                    # Break the loop if we have enough elements
                    if len(carIDs) == 25:
                        break

            # Ensure the final list has at most 25 elements
            carIDs = carIDs[:25]
            # print("Length of CarIDs",len(carIDs))
    
            
        else:
            startTime = time.time()
            carIDs = aiScore_carIDs(carData)
            # print("len of CarIDs in else condition:::",len(carIDs))
            endTime = time.time()
            print("Time for getting carsID:", endTime - startTime)
            
            
              
        startTime = time.time()
        # Populating the CAR Objects
        carGets = mainReturn(carIDs)

        endTime = time.time()
        print("Time Taken:", endTime - startTime)
        
        return carGets

    except Exception as e:
        print("Exception in Main Function:", e)
        
        