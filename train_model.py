import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import pickle
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.feature_extraction import extract_features

ECOMMERCE_KEYWORDS = [
    'shop', 'store', 'cart', 'buy', 'product', 'checkout', 
    'order', 'payment', 'billing', 'shipping', 'track', 'deal',
    'sale', 'discount', 'offer', 'price', 'marketplace', 'mall',
    'retail', 'purchase', 'item', 'collection', 'category', 'brand'
]

TRUSTED_BRANDS = {
    'amazon', 'ebay', 'flipkart', 'walmart', 'target', 'aliexpress',
    'alibaba', 'myntra', 'ajio', 'nykaa', 'snapdeal', 'shopify',
    'zara', 'hm', 'nike', 'adidas', 'apple', 'samsung', 'costco',
    'bestbuy', 'overstock', 'etsy', 'lazada', 'rakuten', 'tata',
    'paytm', 'meesho', 'urbanic', 'koovs', 'croma', 'lenskart',
    'bigbasket', 'grofers', 'jiomart', 'firstcry'
}

def extract_all_features(urls):
    """Extract features for all URLs"""
    print("Extracting features...")
    features_list = []
    
    for i, url in enumerate(urls):
        features = extract_features(url)
        features['is_ecommerce_keyword'] = 1 if any(kw in url.lower() for kw in ECOMMERCE_KEYWORDS) else 0
        features['is_trusted_brand'] = 1 if any(brand in url.lower() for brand in TRUSTED_BRANDS) else 0
        features_list.append(features)
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(urls)} URLs")
    
    return pd.DataFrame(features_list)

def load_dataset():
    """Load the dataset"""
    print("Loading dataset...")
    df = pd.read_csv('dataset/urls.csv')
    print(f"Total samples: {len(df)}")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    print(f"Label meaning: 0=legitimate, 1=phishing, 2=non_ecommerce")
    return df

def prepare_data():
    """Prepare data for training"""
    df = load_dataset()
    
    X = extract_all_features(df['url'].tolist())
    y = df['label'].values
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Features: {list(X.columns)}")
    
    return X, np.array(y), df['url'].tolist()

def train_model():
    """Train the ML model with 3-class classification"""
    print("\n" + "="*60)
    print("TRAINING E-COMMERCE PHISHING DETECTION MODEL")
    print("="*60)
    
    X, y, urls = prepare_data()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        min_samples_split=3,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    print("\n" + "="*60)
    print("MODEL EVALUATION (3-CLASS)")
    print("="*60)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['legitimate', 'phishing', 'non_ecommerce']))
    
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"              Predicted")
    print(f"              Legit  Phish  NonEcom")
    print(f"Actual Legit   {cm[0][0]:4d}   {cm[0][1]:4d}    {cm[0][2]:4d}")
    print(f"       Phish   {cm[1][0]:4d}   {cm[1][1]:4d}    {cm[1][2]:4d}")
    print(f"       NonEcom {cm[2][0]:4d}   {cm[2][1]:4d}    {cm[2][2]:4d}")
    
    print("\nFeature Importance (Top 10):")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    print("\n" + "="*60)
    print("SAVING MODEL")
    print("="*60)
    
    with open('model/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('model/vectorizer.pkl', 'wb') as f:
        pickle.dump(list(X.columns), f)
    
    print("Model saved to model/model.pkl")
    print("Vectorizer saved to model/vectorizer.pkl")
    
    return model, accuracy

if __name__ == '__main__':
    train_model()
