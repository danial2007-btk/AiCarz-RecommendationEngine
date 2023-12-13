import random
from dataLoader import load_car_profiles_from_mongodb

def extract_car_ids_by_ai_score_range(car_profiles):
    ai_score_ranges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    unique_car_ids = set()

    for score_range in ai_score_ranges:
        range_car_ids = set()
        for profile in car_profiles:
            ai_scores = profile.get('AiScore', [2.5])

            if isinstance(ai_scores, list):
                ai_score = ai_scores[-1]  # Get the last AiScore if it is a list
            else:
                ai_score = ai_scores  # Use the single AiScore value if it is not a list

            if score_range[0] <= ai_score < score_range[1]:
                range_car_ids.add(profile['id'])
        
        # If there are fewer than 2 car IDs in the range, add from the default range
        while len(range_car_ids) < 2:
            for profile in car_profiles:
                ai_scores = profile.get('AiScore', [2.5])

                if isinstance(ai_scores, list):
                    ai_score = ai_scores[-1]
                else:
                    ai_score = ai_scores

                if 2.5 <= ai_score < 2.6 and profile['id'] not in range_car_ids:
                    range_car_ids.add(profile['id'])
                    break
        
        unique_car_ids.update(range_car_ids)  # Add the car IDs from the range to the set

    return unique_car_ids

def get_random_car_ids(car_profiles, num_cars=10):
    all_car_ids = [profile['id'] for profile in car_profiles]
    random_car_ids = set(random.sample(all_car_ids, min(num_cars, len(all_car_ids))))
    return random_car_ids

def feedCarId(user_id,coordinates):

    # Assuming car_profiles is the result from load_car_profiles_from_mongodb
    car_profiles = load_car_profiles_from_mongodb(user_id, coordinates)

    # Extract unique car IDs by AI score range
    unique_car_ids_by_ai_score_range = extract_car_ids_by_ai_score_range(car_profiles)

    # Get unique 10 random car IDs
    unique_random_car_ids = get_random_car_ids(car_profiles, num_cars=6)

    # Combine unique car IDs from both sources
    final_unique_car_ids = list(unique_car_ids_by_ai_score_range.union(unique_random_car_ids))

    # Ensure the final list has exactly 20 unique car IDs
    final_unique_car_ids = final_unique_car_ids[:20]

    print("Final Unique Car IDs:",final_unique_car_ids)
    print("Len",len(final_unique_car_ids))
    
    return final_unique_car_ids
