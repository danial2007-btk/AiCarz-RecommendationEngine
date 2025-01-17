import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from surprise import Dataset, Reader, SVD
# from collections import defaultdict

def get_top_n_recommendations(user_id, car_data, user_preference_data, user_interaction_data):
    
    try:

        # Convert data to pandas DataFrames
        car_df = pd.DataFrame(car_data)
        user_preference_df = pd.DataFrame(user_preference_data)
        user_interaction_df = pd.DataFrame(user_interaction_data)

        # Merge user preferences and interactions
        user_data = pd.merge(user_preference_df, user_interaction_df, on='carid')

        # Merge user data with car data
        user_car_data = pd.merge(user_data, car_df, left_on='carid', right_on='carid', suffixes=('_user', '_car'))


        # Define the rating scale for collaborative filtering
        reader = Reader(rating_scale=(0, 1))

        # Load the dataset
        data = Dataset.load_from_df(user_car_data[['user_id', 'carid', 'interaction']], reader)

        # Build the collaborative filtering model
        model = SVD()
        trainset = data.build_full_trainset()
        model.fit(trainset)


        # Create a TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer()

        # Combine relevant features into a single text representation
        car_df['description'] = car_df.apply(lambda x: f"Make: {x['make']} Gearbox: {x['gearbox']} Fuel: {x['fueltype']} Engine: {x['engineSizeInLiter']} Price: {x['price']}", axis=1)

        # Fit and transform the TF-IDF vectorizer on the car descriptions
        tfidf_matrix = tfidf_vectorizer.fit_transform(car_df['description'])

        # Calculate cosine similarity between car descriptions
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Function to get top N recommendations for a user
        # Get a list of all car IDs
        all_car_ids = car_df['carid'].tolist()

        # Get the car IDs that the user has interacted with
        interacted_car_ids = user_car_data[user_car_data['user_id'] == user_id]['carid'].tolist()

        # Remove the interacted car IDs from the list of all car IDs
        car_ids_to_recommend = list(set(all_car_ids) - set(interacted_car_ids))

        # Make predictions using collaborative filtering
        predictions = [model.predict(user_id, car_id).est for car_id in car_ids_to_recommend]
        # print("Model Prediction: ",predictions)
    
        # Combine predictions from collaborative and content-based models with adjusted weights
        collaborative_predictions = [model.predict(user_id, car_id).est for car_id in car_ids_to_recommend]
        content_predictions = [cosine_sim[car_df.index[car_df['carid'] == car_id].tolist()[0]].sum() for car_id in car_ids_to_recommend]

        # Adjust the weights for collaborative and content-based predictions
        hybrid_predictions = [0.5 * cf_pred + 0.3 * content_pred for cf_pred, content_pred in zip(collaborative_predictions, content_predictions)]

        # Normalize the hybrid predictions to be between 0 and 1
        max_prediction = max(hybrid_predictions)
        min_prediction = min(hybrid_predictions)
        normalized_predictions = [(pred - min_prediction) / (max_prediction - min_prediction) for pred in hybrid_predictions]
        # print("normalized_predictions:",normalized_predictions)

        # Get indices of top N recommendations
        top_indices = sorted(range(len(normalized_predictions)), key=lambda i: normalized_predictions[i], reverse=True)[:20]

        # Get the corresponding car IDs
        top_car_ids = [car_ids_to_recommend[i] for i in top_indices]

        return top_car_ids

    except Exception as e:
        print("Exception in Recommendation Function:", e)
        
        