from dataLoader import dataGather, collection
from AiScore import AIScoreInput, AIScoreCalculator
from pymongo import MongoClient
from bson import ObjectId

updateClient = MongoClient("mongodb+srv://aicarz:kxnJuY2Vc1UtHYVF@cluster0.uarux4m.mongodb.net/?retryWrites=true&w=majority")
carzdb = updateClient["aicarsdb"]
carzcollection = carzdb["cars"]

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
            return ("Update successful")
        else:
            return ("No matching document found")

    else:
        return ("CarId not found / AiScore not found")



# The below work is a structure of Main function where the feed manager will be called and the recommendations will be generated
from dataLoader import load_car_profiles_from_mongodb,mainReturn, load_user_likes, load_likes_interaction, load_user_dislikes, load_dislikes_interaction  
from modelLike import get_top_recommendations, calculate_cosine_similarity, preprocess_car_profiles, preprocess_user_car_profiles, train_collaborative_filtering_model, load_user_car_data
from feedManager import feedCarId
from modelDislike import get_top_recommendations1, calculate_cosine_similarity1, preprocess_car_profiles1, preprocess_user_car_profiles1, train_collaborative_filtering_model1, load_user_car_data1

def FeedManagerMain(user_id, coordinates):
    # User ID
    user_id = user_id

    # User coordinates
    coordinates = coordinates
    
    recommended_car_pairs = feedCarId(coordinates)

   # Example usage likes recommadation
    user_car_data_interaction = load_likes_interaction(user_id)
    user_car_profiles = load_user_likes(user_id)
    car_profiles = load_car_profiles_from_mongodb(coordinates)

    numerical_features = ['price', 'engineSizeInLiter']
    categorical_features = ['make', 'gearbox', 'fueltype']

    trainset = load_user_car_data(user_car_data_interaction)

    user_car_profiles = preprocess_user_car_profiles(user_car_profiles, numerical_features, categorical_features)
    car_profiles = preprocess_car_profiles(car_profiles, numerical_features, categorical_features)

    user_numerical_features = user_car_profiles[numerical_features].values
    car_numerical_features = car_profiles[numerical_features].values

    cosine_sim = calculate_cosine_similarity(user_numerical_features, car_numerical_features)
    recommendations = get_top_recommendations(cosine_sim, car_profiles)

    recommendation_likes_car_ids = recommendations['Car_ID'].tolist()

    unique_recommendation_likes_car_ids = [car_id for car_id in recommendation_likes_car_ids if car_id not in recommended_car_pairs]

    unique_recommendation_likes_car_ids = unique_recommendation_likes_car_ids[:7]

    user_car_data_interaction = load_dislikes_interaction(user_id)
    user_car_profiles = load_user_dislikes(user_id)
    car_profiles = load_car_profiles_from_mongodb(coordinates)
    
    numerical_features = ['price', 'engineSizeInLiter']
    categorical_features = ['make', 'gearbox', 'fueltype']

    trainset = load_user_car_data1(user_car_data_interaction)

    user_car_profiles = preprocess_user_car_profiles1(user_car_profiles, numerical_features, categorical_features)
    car_profiles = preprocess_car_profiles1(car_profiles, numerical_features, categorical_features)

    user_numerical_features = user_car_profiles[numerical_features].values
    car_numerical_features = car_profiles[numerical_features].values

    cosine_sim = calculate_cosine_similarity1(user_numerical_features, car_numerical_features)
    recommendations = get_top_recommendations1(cosine_sim, car_profiles)

    recommendation_dislikes_car_ids = recommendations['Car_ID'].tolist()

    unique_recommendation_dislikes_car_ids = [car_id for car_id in recommendation_dislikes_car_ids if car_id not in recommended_car_pairs]

    unique_recommendation_dislikes_car_ids = unique_recommendation_dislikes_car_ids[:11]

    final_recommation = recommended_car_pairs + unique_recommendation_likes_car_ids + unique_recommendation_dislikes_car_ids

    final_recommation_25_carID = list(set(final_recommation))
    
    carGets = []
    
    for ids in final_recommation_25_carID:
        carGets.append(mainReturn(ids))
        
    print("Length of CarGets",len(carGets))

    return carGets