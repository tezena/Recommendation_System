import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from recommendation.qdrant_helper import upsert_post_vector, upsert_user_profile
import numpy as np

def build_tfidf_model(posts_df):
    vectorizer = TfidfVectorizer(analyzer='word', min_df=0.003, max_df=0.5, max_features=5000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(posts_df['title'] + " " + posts_df['content'])
    return vectorizer, tfidf_matrix



def get_item_profiles(post_ids, tfidf_matrix, all_post_ids):
    if isinstance(post_ids, (np.int64, int)):
        post_ids = [post_ids]
    indices = [all_post_ids.index(post_id) for post_id in post_ids]
    return tfidf_matrix[indices]

def create_user_profiles(interactions_df, tfidf_matrix, post_ids):
    interactions_indexed_df = interactions_df.set_index('user__user_id')
    user_profiles = {}
    
    for user_id in interactions_indexed_df.index.unique():
        user_interactions = interactions_indexed_df.loc[user_id]
        
        if isinstance(user_interactions, pd.Series):
            user_interactions = user_interactions.to_frame().T
        
        user_item_profiles = get_item_profiles(user_interactions['post__content_id'], tfidf_matrix, post_ids)
        user_item_profiles = user_item_profiles.toarray()  # Ensure it's a dense array
        user_item_strengths = user_interactions['event_strength'].values.reshape(-1, 1)
        
        user_profiles[user_id] = np.sum(user_item_profiles * user_item_strengths, axis=0) / np.sum(user_item_strengths, axis=0)
    
    return user_profiles

