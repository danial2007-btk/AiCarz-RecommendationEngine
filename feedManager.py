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
                range_car_ids.add(profile['carid'])
        
        # If there are fewer than 2 car IDs in the range, add from the default range
        while len(range_car_ids) < 1:
            for profile in car_profiles:
                ai_scores = profile.get('AiScore', [2.5])

                if isinstance(ai_scores, list):
                    ai_score = ai_scores[-1]
                else:
                    ai_score = ai_scores

                if 2.5 <= ai_score < 2.6 and profile['carid'] not in range_car_ids:
                    range_car_ids.add(profile['carid'])
                    break
        
        unique_car_ids.update(range_car_ids)  # Add the car IDs from the range to the set

    return unique_car_ids

def get_random_car_ids(car_profiles, num_cars=15):
    all_car_ids = [profile['carid'] for profile in car_profiles]
    random_car_ids = set(random.sample(all_car_ids, min(num_cars, len(all_car_ids))))
    return random_car_ids

def feedCarId(car_profiles):

    # Extract unique car IDs by AI score range
    unique_car_ids_by_ai_score_range = extract_car_ids_by_ai_score_range(car_profiles)

    # Get unique 10 random car IDs
    unique_random_car_ids = get_random_car_ids(car_profiles, num_cars=15)

    # Combine unique car IDs from both sources
    final_unique_car_ids = list(unique_car_ids_by_ai_score_range.union(unique_random_car_ids))

    # Ensure the final list has exactly 20 unique car IDs
    final_unique_car_ids = final_unique_car_ids[:15]
    
    return final_unique_car_ids

def aiScore_carIDs(car_profiles):
    
    try:
            
        ai_score_ranges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        unique_car_ids = set()
        car_count = 0

        for score_range in ai_score_ranges:
            range_car_ids = set()
            for profile in car_profiles:
                ai_scores = profile.get('AiScore', [2.5])

                if isinstance(ai_scores, list):
                    ai_score = ai_scores[-1]  # Get the last AiScore if it is a list
                else:
                    ai_score = ai_scores  # Use the single AiScore value if it is not a list

                if score_range[0] <= ai_score < score_range[1]:
                    range_car_ids.add(profile['carid'])
            
            # If there are fewer than 2 car IDs in the range, add from the default range
            while len(range_car_ids) < 1:
                for profile in car_profiles:
                    ai_scores = profile.get('AiScore', [2.5])

                    if isinstance(ai_scores, list):
                        ai_score = ai_scores[-1]
                    else:
                        ai_score = ai_scores

                    if 2.5 <= ai_score < 2.6 and profile['carid'] not in range_car_ids:
                        range_car_ids.add(profile['carid'])
                        break

            unique_car_ids.update(range_car_ids)  # Add the car IDs from the range to the set
            car_count += len(range_car_ids)

            # Check if we have collected the top 25 car IDs
            if car_count >= 25:
                break

        return list(unique_car_ids)[:25]
    
    except Exception as e:
        print("Exception in AiScore_carIDs Function:", e)