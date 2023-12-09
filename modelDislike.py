from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from surprise import Dataset, Reader, SVD

def load_user_car_data1(user_car_data_interaction):
    df_user_car_data = pd.DataFrame(user_car_data_interaction)
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(df_user_car_data[['user_id', 'id', 'interaction']], reader)
    return data.build_full_trainset()

def train_collaborative_filtering_model1(trainset):
    collaborative_filtering_model = SVD()
    collaborative_filtering_model.fit(trainset)
    return collaborative_filtering_model

def preprocess_user_car_profiles1(user_car_profiles, numerical_features, categorical_features):
    if 'dislikes' in user_car_profiles and user_car_profiles['dislikes']:
        user_car_profiles_df = pd.json_normalize(user_car_profiles['dislikes'], sep='_')
    else:
        user_car_profiles_df = pd.DataFrame(columns=['id', 'make', 'gearbox', 'fueltype', 'price', 'engineSizeInLiter'])

    encoder = OneHotEncoder(drop='first', sparse=False)
    encoded_features = encoder.fit_transform(user_car_profiles_df[categorical_features].astype(str))

    user_car_profiles_df['user_id'] = user_car_profiles.get('user_id', '')
    user_car_profiles = pd.concat([
        user_car_profiles_df[['user_id']],
        user_car_profiles_df[numerical_features],
        pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_features)),
    ], axis=1)

    return user_car_profiles

def preprocess_car_profiles1(car_profiles, numerical_features, categorical_features):
    car_profiles_df = pd.DataFrame(car_profiles)
    encoder = OneHotEncoder(drop='first', sparse=False)
    encoded_features = encoder.fit_transform(car_profiles_df[categorical_features].astype(str))

    car_profiles_df['user_id'] = car_profiles_df.get('user_id', '')
    car_profiles = pd.concat([
        car_profiles_df[['user_id', 'id']],
        car_profiles_df[numerical_features],
        pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_features)),
    ], axis=1)

    return car_profiles

def calculate_cosine_similarity1(user_features, car_features):
    return cosine_similarity(user_features, car_features)

def get_top_recommendations1(cosine_sim, car_profiles):
    car_indices = np.argsort(cosine_sim, axis=1)
    car_indices = np.flip(car_indices, axis=1)
    cosine_sim = np.flip(np.sort(cosine_sim, axis=1), axis=1)

    car_ids = car_profiles['id'].iloc[car_indices[0]]
    similarity_scores = cosine_sim[0]

    recommendations_df = pd.DataFrame({'Car_ID': car_ids})
    return recommendations_df
