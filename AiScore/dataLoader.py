from bson import ObjectId
import pymongo
import logging
# Correct import for AIScoreInput in app.py
from AiScore import AIScoreInput

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Connection URL and Database
connection_string = "mongodb+srv://web_scrapping_read_only:rVXnGzz3jZvnRZx1@cluster0.uarux4m.mongodb.net/?retryWrites=true&w=majority"
database_name = "aicarsdb"
car_db = "cars"

# Establish MongoDB connection
client = pymongo.MongoClient(connection_string)
db = client[database_name]
collection = db[car_db]

def dataGather(collection, car_id):
    # try:
    car_object_id = ObjectId(car_id)
    car_data = collection.find_one({"_id": car_object_id})

    if car_data:
        time_spent_values = [time["durationInMilliseconds"] for time in car_data.get("timeSpent", [])]
        mean_time_spent = sum(time_spent_values) / len(time_spent_values) if time_spent_values else 0

        ai_score_last_value = car_data.get("AiScore", [])[0] if car_data.get("AiScore") else 0
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
            total_ad_displays=total_ad_displayed
        )
    
    else:
        print("Car not found.")
        # Return default values
        return AIScoreInput(0, 0, 0, 0, 0, 0)