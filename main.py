from dataLoader import dataGather, collection
from AiScore import AIScoreInput, AIScoreCalculator

def AiScoreMain(car_id):
        
    car_id = car_id

    # Assuming gathered_data is the result of dataGather function
    aiscore_input = dataGather(collection, car_id)

    # Create an instance of AIScoreCalculator
    aiscore_calculator = AIScoreCalculator()

    # Calculate AI Score
    ai_score = aiscore_calculator.calculate_ai_score(aiscore_input)

    # Print the AI Score
    ai_score_rounded = round(ai_score, 4)

    return ai_score_rounded


# The below work is a structure of Main function where the feed manager will be called and the recommendations will be generated
from dataLoader import load_car_profiles_from_mongodb,mainReturn, load_user_likes, load_likes_interaction, load_user_dislikes, load_dislikes_interaction  
from modelLike import get_top_recommendations, calculate_cosine_similarity, preprocess_car_profiles, preprocess_user_car_profiles, train_collaborative_filtering_model, load_user_car_data
from feedManager import suggest_cars_for_user
from modelDislike import get_top_recommendations1, calculate_cosine_similarity1, preprocess_car_profiles1, preprocess_user_car_profiles1, train_collaborative_filtering_model1, load_user_car_data1

def FeedManagerMain(user_id, coordinates):
    # User ID
    user_id = user_id

    # User coordinates
    coordinates = coordinates
    
    recommended_car_pairs = suggest_cars_for_user(user_id, coordinates)

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

    unique_recommendation_dislikes_car_ids = unique_recommendation_dislikes_car_ids[:7]

    final_recommation = recommended_car_pairs + unique_recommendation_likes_car_ids + unique_recommendation_dislikes_car_ids

    final_recommation_25_carID = list(set(final_recommation))
    
    carGets = []
    
    for ids in final_recommation_25_carID:
        carGets.append(mainReturn(ids))

    return carGets