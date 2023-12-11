from bson import ObjectId
import pymongo
import random
import numpy as np

from dataLoader import connect_to_mongodb

# def connect_to_mongodb():
#     # Function to establish a connection to MongoDB
#     connection_string = "mongodb+srv://web_scrapping_read_only:rVXnGzz3jZvnRZx1@cluster0.uarux4m.mongodb.net/?retryWrites=true&w=majority"
#     database_name = "aicarsdb"
#     car_collection_name = "cars"
#     client = pymongo.MongoClient(connection_string)
#     db = client[database_name]
#     car_collection = db[car_collection_name]

#     return car_collection

def get_user_likes_dislikes(collection, user_id, coordinates):
    # Function to retrieve user's likes and dislikes from the MongoDB collection
    collection_data = collection.find({
        'location': {
            '$near': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': coordinates
                },
                '$maxDistance': 321869
            }
        },
        'isActive': True  # Add this filter to check for isActive field
    })

    # user_data = collection.find({"$or": [{"likes": ObjectId(user_id)}, {"dislikes": ObjectId(user_id)}]})
    user_likes_dislikes = {"user_id": user_id, "likes": [], "dislikes": []}

    for car_doc in collection_data:
        if car_doc:
            # Extracting relevant information from the car document
            car_data = {
                "id": car_doc["_id"],
                "make": car_doc["make"],
                "gearbox": car_doc["gearbox"],
                "fuelType": car_doc["fuelType"],
                "price": car_doc["price"],
                "engineSizeInLiter": car_doc["engineSizeInLiter"]
            }

            likes = car_doc.get("likes", [])
            dislikes = car_doc.get("dislikes", [])

            # Organizing the car data based on user's likes and dislikes
            if ObjectId(user_id) in likes:
                user_likes_dislikes["likes"].append(car_data)

            if ObjectId(user_id) in dislikes:
                user_likes_dislikes["dislikes"].append(car_data)

    return user_likes_dislikes

def get_ai_scores_list(car_collection):
    # Function to retrieve the latest AI scores for all cars in the collection
    ai_scores_list = []
    car_data = car_collection.find({}, {"_id": 1, "AiScore": {"$slice": -1}})

    for car_doc in car_data:
        car_id = str(car_doc["_id"])
        ai_scores = car_doc.get("AiScore", [])
        last_ai_score = ai_scores[-1] if ai_scores else "N/A"
        
        ai_scores_list.append({"car_id": car_id, "Aiscore": last_ai_score})

    return ai_scores_list

def filter_cars(user_likes_dislikes, ai_scores_list):
    # Function to filter out cars based on user's likes and dislikes
    liked_ids = [like['id'] for like in user_likes_dislikes['likes']]
    disliked_ids = [dislike['id'] for dislike in user_likes_dislikes['dislikes']]

    filtered_aiscore = []

    for car in ai_scores_list:
        car_id = ObjectId(car['car_id'])
        # Filtering out cars that the user has already liked or disliked
        if car_id not in liked_ids and car_id not in disliked_ids:
            filtered_aiscore.append({'car_id': str(car_id), 'Aiscore': car['Aiscore']})

    return filtered_aiscore 

def generate_recommendations(filtered_aiscore):
    # Function to generate car recommendations based on AI scores
    category_a_1 = [car['car_id'] for car in filtered_aiscore if car['Aiscore'] <= 1.0]
    category_b_2 = [car['car_id'] for car in filtered_aiscore if 1.0 < car['Aiscore'] <= 2.0]
    category_c_3 = [car['car_id'] for car in filtered_aiscore if 2.0 < car['Aiscore'] <= 3.0]
    category_d_4 = [car['car_id'] for car in filtered_aiscore if 3.0 < car['Aiscore'] <= 4.0]
    category_e_5 = [car['car_id'] for car in filtered_aiscore if 4.0 < car['Aiscore'] <= 5.0]
    mid_category = [car['car_id'] for car in filtered_aiscore if car['Aiscore'] == 2.5]

    recommended_aiscore = []

    # Randomly selecting a car from each category
    if category_a_1:
        random_id = random.choice(category_a_1)
        recommended_aiscore.append(random_id)
    if category_b_2:
        random_id = random.choice(category_b_2)
        recommended_aiscore.append(random_id)
    if category_c_3:
        random_id = random.choice(category_c_3)
        recommended_aiscore.append(random_id)
    if category_d_4:
        random_id = random.choice(category_d_4)
        recommended_aiscore.append(random_id)
    if category_e_5:
        random_id = random.choice(category_e_5)
        recommended_aiscore.append(random_id)

    # Randomly selecting from the mid-category until there are 5 recommendations
    while len(recommended_aiscore) < 5 and mid_category:
        random_id = random.choice(mid_category)
        recommended_aiscore.append(random_id)

    return recommended_aiscore

def suggest_cars_for_user(user_id, coordinates):
    # Function to provide final car suggestions for a user
    car_collection = connect_to_mongodb()
    
    user_object_id = ObjectId(user_id)
    
    user_likes_dislikes = get_user_likes_dislikes(car_collection, user_object_id, coordinates)
    ai_scores_list = get_ai_scores_list(car_collection)
    
    filtered_list = filter_cars(user_likes_dislikes, ai_scores_list)
    recommended_aiscore = generate_recommendations(filtered_list)

    # Selecting additional random cars for variety
    all_car_ids = [car['car_id'] for car in filtered_list if car['Aiscore']]
    random_car_ids = random.sample(all_car_ids, 15)
    
    randomly_select_id = [val for val in random_car_ids if val not in recommended_aiscore][:6]

    # Constructing the desired output format
    user_car_pairs = list(recommended_aiscore + randomly_select_id)

    return user_car_pairs
