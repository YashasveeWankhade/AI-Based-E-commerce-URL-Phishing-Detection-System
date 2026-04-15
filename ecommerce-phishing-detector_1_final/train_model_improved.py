import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report)
from sklearn.utils.class_weight import compute_class_weight
import pickle
import sys
import os
import re
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.feature_extraction import extract_features
from utils.domain_checker import KNOWN_ECOMMERCE_DOMAINS as KNOWN_DOMAINS


ECOMMERCE_KEYWORDS = [
    'shop', 'store', 'cart', 'buy', 'product', 'checkout', 
    'order', 'payment', 'billing', 'shipping', 'track', 'deal',
    'sale', 'discount', 'offer', 'price', 'marketplace', 'mall',
    'retail', 'purchase', 'item', 'collection'
]

ECOMMERCE_PATH_PATTERNS = [
    '/product/', '/products/', '/cart/', '/checkout/', '/order/',
    '/buy/', '/shop/', '/store/', '/category/', '/item/', '/p/',
]

KNOWN_ECOMMERCE_DOMAINS_EXENDED = KNOWN_DOMAINS.copy()


def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ""


def extract_path(url):
    """Extract path from URL"""
    try:
        parsed = urlparse(url)
        return parsed.path.lower()
    except:
        return ""


def is_known_ecommerce_domain(url):
    """Check if URL is from a known e-commerce domain"""
    domain = extract_domain(url)
    if domain in KNOWN_ECOMMERCE_DOMAINS_EXENDED:
        return True
    for known in KNOWN_ECOMMERCE_DOMAINS_EXENDED:
        if domain == known or domain.endswith('.' + known):
            return True
    return False


def has_ecommerce_keywords(url):
    """Check for e-commerce keywords in URL"""
    url_lower = url.lower()
    keyword_count = sum(1 for k in ECOMMERCE_KEYWORDS if k in url_lower)
    return keyword_count >= 2


def has_ecommerce_path(url):
    """Check for e-commerce path patterns"""
    path = extract_path(url)
    for pattern in ECOMMERCE_PATH_PATTERNS:
        if pattern in path:
            return True
    return False


def is_ecommerce_url(url):
    """
    Determine if URL is an e-commerce URL
    Returns: (is_ecommerce: bool, reason: str)
    """
    if is_known_ecommerce_domain(url):
        return True, "known_domain"
    
    if has_ecommerce_keywords(url):
        return True, "keywords"
    
    if has_ecommerce_path(url):
        return True, "path_pattern"
    
    return False, "not_ecommerce"


def clean_url(url):
    """Normalize URL"""
    url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    while url.endswith('/'):
        url = url[:-1]
    return url


def load_and_clean_dataset():
    """Load and clean the dataset"""
    print("Loading dataset...")
    
    df = pd.read_csv('dataset/urls.csv')
    print(f"Total samples: {len(df)}")
    
    df = df.drop_duplicates(subset=['url'])
    print(f"After removing duplicates: {len(df)}")
    
    df = df.dropna(subset=['url', 'label'])
    print(f"After removing nulls: {len(df)}")
    
    df['url'] = df['url'].apply(clean_url)
    
    return df


def label_urls(df):
    """
    Relabel URLs based on e-commerce detection
    0 = Legitimate (e-commerce + legitimate)
    1 = Phishing (e-commerce + phishing)
    2 = Not E-commerce (non e-commerce URLs)
    """
    print("\nLabeling URLs...")
    
    labels = []
    ecommerce_flags = []
    
    for idx, row in df.iterrows():
        url = row['url']
        original_label = row['label']
        url_type = row.get('type', 'unknown')
        
        is_ecom, reason = is_ecommerce_url(url)
        
        if is_ecom:
            ecommerce_flags.append(True)
            if original_label == 0 or url_type == 'legitimate':
                labels.append(0)  # Legitimate
            else:
                labels.append(1)  # Phishing
        else:
            ecommerce_flags.append(False)
            labels.append(2)  # Not E-commerce
    
    df['final_label'] = labels
    df['is_ecommerce'] = ecommerce_flags
    
    print(f"E-commerce URLs: {sum(ecommerce_flags)}")
    print(f"Non-e-commerce URLs: {len(df) - sum(ecommerce_flags)}")
    print(f"Label distribution:\n{df['final_label'].value_counts().sort_index()}")
    
    return df


def extract_all_features(urls):
    """Extract features for all URLs"""
    print("Extracting features...")
    features_list = []
    
    for i, url in enumerate(urls):
        features = extract_features(url)
        features_list.append(features)
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(urls)} URLs")
    
    return pd.DataFrame(features_list)


def train_model():
    """Train the improved ML model"""
    print("\n" + "="*60)
    print("TRAINING IMPROVED PHISHING DETECTION MODEL")
    print("="*60)
    
    df = load_and_clean_dataset()
    df = label_urls(df)
    
    X = extract_all_features(df['url'].tolist())
    y = df['final_label'].values
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Feature names: {list(X.columns)}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    print(f"\nTraining label distribution:")
    unique, counts = np.unique(y_train, return_counts=True)
    for u, c in zip(unique, counts):
        label_name = ['Legitimate', 'Phishing', 'Not-Ecommerce'][u]
        print(f"  {label_name}: {c}")
    
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(zip(np.unique(y_train), class_weights))
    print(f"\nClass weights: {class_weight_dict}")
    
    print("\n" + "-"*40)
    print("Training Random Forest with class balancing...")
    
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    print("\n" + "-"*40)
    print("Cross-validation (5-fold)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted')
    print(f"CV F1-scores: {cv_scores}")
    print(f"Mean CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')
    f1_macro = f1_score(y_test, y_pred, average='macro')
    
    print(f"\nOverall Metrics (macro-averaged):")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision_macro:.4f}")
    print(f"Recall: {recall_macro:.4f}")
    print(f"F1-Score: {f1_macro:.4f}")
    
    print(f"\nPer-class Metrics:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing', 'Not-Ecommerce']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"                Predicted")
    print(f"             Legit  Phish  NotEcom")
    print(f"Actual Legit  {cm[0][0]:4d}   {cm[0][1]:4d}    {cm[0][2]:4d}")
    print(f"       Phish  {cm[1][0]:4d}   {cm[1][1]:4d}    {cm[1][2]:4d}")
    print(f"       NotEco {cm[2][0]:4d}   {cm[2][1]:4d}    {cm[2][2]:4d}")
    
    print(f"\nFalse Positives for Legitimate: {cm[0][1]} (legitimate URLs wrongly flagged as phishing)")
    print(f"False Negatives for Phishing: {cm[1][0]} (phishing URLs wrongly classified as legitimate)")
    
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
    
    os.makedirs('model', exist_ok=True)
    with open('model/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('model/vectorizer.pkl', 'wb') as f:
        pickle.dump(list(X.columns), f)
    
    print("Model saved to model/model.pkl")
    print("Vectorizer saved to model/vectorizer.pkl")
    
    return model, accuracy, precision_macro, recall_macro, f1_macro, cm


def test_specific_urls():
    """Test specific URLs including amazon.in"""
    print("\n" + "="*60)
    print("TESTING SPECIFIC URLs")
    print("="*60)
    
    import pickle
    
    try:
        with open('model/model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('model/vectorizer.pkl', 'rb') as f:
            feature_columns = pickle.load(f)
    except:
        print("Model not found. Train first.")
        return
    
    test_urls = [
        ('https://amazon.in', 'Legitimate'),
        ('https://amazon.com', 'Legitimate'),
        ('https://flipkart.com', 'Legitimate'),
        ('https://amazon.co.in', 'Legitimate'),
        ('http://amazon-login-secure.xyz', 'Phishing'),
        ('http://flipkart.verify-payment.ru', 'Phishing'),
        ('http://amazom.com', 'Phishing'),
        ('https://google.com', 'Not-Ecommerce'),
        ('https://wikipedia.org', 'Not-Ecommerce'),
    ]
    
    print(f"\n{'URL':<45} | {'Expected':<15} | {'Prediction'}")
    print("-"*80)
    
    for url, expected in test_urls:
        url = clean_url(url)
        features = extract_features(url)
        feature_vector = [[features[col] for col in feature_columns]]
        pred = model.predict(feature_vector)[0]
        label_names = ['Legitimate', 'Phishing', 'Not-Ecommerce']
        result = label_names[pred]
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{url:<45} | {expected:<15} | {result} {status}")


if __name__ == '__main__':
    train_model()
    test_specific_urls()
