from bson import ObjectId
import pymongo
import random

def connect_to_mongodb():
    connection_string = "mongodb+srv://web_scrapping_read_only:rVXnGzz3jZvnRZx1@cluster0.uarux4m.mongodb.net/?retryWrites=true&w=majority"
    database_name = "aicarsdb"
    car_collection_name = "cars"

    client = pymongo.MongoClient(connection_string)
    db = client[database_name]
    car_collection = db[car_collection_name]
    
    return car_collection

def get_user_likes_dislikes(collection, user_id):
    user_data = collection.find({"$or": [{"likes": ObjectId(user_id)}, {"dislikes": ObjectId(user_id)}]})
    
    user_likes_dislikes = {"user_id": user_id, "likes": [], "dislikes": []}

    for doc in user_data:
        if doc:
            car_data = {
                "id": doc["_id"],
                "make": doc["make"],
                "gearbox": doc["gearbox"],
                "fuelType": doc["fuelType"],
                "price": doc["price"],
                "engineSizeInLiter": doc["engineSizeInLiter"]
            }

            likes = doc.get("likes", [])
            dislikes = doc.get("dislikes", [])

            if ObjectId(user_id) in likes:
                user_likes_dislikes["likes"].append(car_data)

            if ObjectId(user_id) in dislikes:
                user_likes_dislikes["dislikes"].append(car_data)

    return user_likes_dislikes

def get_ai_scores_list(car_collection):
    ai_scores_list = []
    car_data = car_collection.find({}, {"_id": 1, "AiScore": {"$slice": -1}})

    for car in car_data:
        car_id = str(car["_id"])
        ai_scores = car.get("AiScore", [])
        last_ai_score = ai_scores[-1] if ai_scores else "N/A"
        
        ai_scores_list.append({"car_id": car_id, "Aiscore": last_ai_score})

    return ai_scores_list

def filter_cars(user_likes_dislikes, ai_scores_list):
    liked_ids = [like['id'] for like in user_likes_dislikes['likes']]
    disliked_ids = [dislike['id'] for dislike in user_likes_dislikes['dislikes']]

    new_list = []

    for car in ai_scores_list:
        car_id = ObjectId(car['car_id'])
        if car_id not in liked_ids and car_id not in disliked_ids:
            new_list.append({'car_id': str(car_id), 'Aiscore': car['Aiscore']})

    return new_list

def generate_recommendations(new_list):
    
    a_1 = [car['car_id'] for car in new_list if car['Aiscore'] <= 1.0]
    b_2 = [car['car_id'] for car in new_list if 1.0 < car['Aiscore'] <= 2.0]
    c_3 = [car['car_id'] for car in new_list if 2.0 < car['Aiscore'] <= 3.0]
    d_4 = [car['car_id'] for car in new_list if 3.0 < car['Aiscore'] <= 4.0]
    e_5 = [car['car_id'] for car in new_list if 4.0 < car['Aiscore'] <= 5.0]
    randon_val = [car['car_id'] for car in new_list if car['Aiscore'] == 2.5]

    new_list_1 = []

    if a_1:
        random_id = random.choice(a_1)
        new_list_1.append(random_id)
    if b_2:
        random_id = random.choice(b_2)
        new_list_1.append(random_id)
    if c_3:
        random_id = random.choice(c_3)
        new_list_1.append(random_id)
    if d_4:
        random_id = random.choice(d_4)
        new_list_1.append(random_id)
    if e_5:
        random_id = random.choice(e_5)
        new_list_1.append(random_id)

    while len(new_list_1) < 5 and randon_val:
        random_id = random.choice(randon_val)
        new_list_1.append(random_id)

    return new_list_1

def feed_result(userId):
    car_collection = connect_to_mongodb()
    
    # Replace 'user_id' with the actual user ID or pass variable
    user_id = ObjectId(userId)
    
    user_likes_dislikes = get_user_likes_dislikes(car_collection, user_id)
    ai_scores_list = get_ai_scores_list(car_collection)
    
    new_list = filter_cars(user_likes_dislikes, ai_scores_list)
    new_list_1 = generate_recommendations(new_list)

    # Print the results
    # print("User_interest_base_carIds:", new_list_1)

    all_carId = [car['car_id'] for car in new_list if car['Aiscore']]
    random_car_id = random.sample(all_carId, 15)
    
    final_val = [val for val in random_car_id if val not in new_list_1][:6]

    # print("Randomly_suggest_carIDs:", final_val)

    return final_val , new_list_1

userId = '6569c7ba48312fbf0f14326c'
a,b = feed_result(userId)

print("Random IDs::::",a)
print("AIScore IDs::::",b)