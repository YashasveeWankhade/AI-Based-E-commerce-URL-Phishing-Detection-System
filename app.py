from flask import Flask, render_template, request, jsonify
import pickle
import sys
import os

from utils.feature_extraction import extract_features, get_domain, is_trusted_domain
from utils.domain_checker import is_ecommerce_url, get_detection_info, has_brand_impersonation
from utils.typo_detector import check_typosquatting, is_known_ecommerce

def check_insecure_http(url):
    """Check if URL uses insecure HTTP protocol instead of HTTPS"""
    return url.lower().startswith('http://')

app = Flask(__name__)

model = None
feature_columns = None

def load_model():
    """Load the trained ML model"""
    global model, feature_columns
    
    try:
        with open('model/model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        with open('model/vectorizer.pkl', 'rb') as f:
            feature_columns = pickle.load(f)
        
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")

def get_ml_prediction(url):
    """Get ML model prediction with detailed feature contribution"""
    if model is None:
        return None
    
    from utils.feature_extraction import ECOMMERCE_KEYWORDS, TRUSTED_BRANDS
    
    features = extract_features(url)
    features['is_ecommerce_keyword'] = 1 if any(kw in url.lower() for kw in ECOMMERCE_KEYWORDS) else 0
    features['is_trusted_brand'] = 1 if any(brand in url.lower() for brand in TRUSTED_BRANDS) else 0
    
    feature_vector = [[features[col] for col in feature_columns]]
    
    prediction = model.predict(feature_vector)[0]
    probability = model.predict_proba(feature_vector)[0]
    
    feature_importance = {}
    for i, col in enumerate(feature_columns):
        if feature_vector[0][i] > 0:
            feature_importance[col] = {
                'value': feature_vector[0][i],
                'importance': model.feature_importances_[i]
            }
    
    return {
        'prediction': int(prediction),
        'confidence': float(max(probability)),
        'prob_phishing': float(probability[1]) if len(probability) > 1 else 0,
        'prob_legitimate': float(probability[0]),
        'prob_non_ecommerce': float(probability[2]) if len(probability) > 2 else 0,
        'triggered_features': feature_importance
    }

def ml_prediction_to_result(ml_result):
    """Convert ML prediction to classification result"""
    if ml_result is None:
        return None, None
    
    pred = ml_result['prediction']
    
    if pred == 0:
        return "Legitimate E-commerce Website", "ml_legitimate"
    elif pred == 1:
        return "Phishing E-commerce Website", "ml_phishing"
    else:
        return "Not an E-commerce URL", "ml_non_ecommerce"

def generate_explanation(url, result, is_ecommerce, ecommerce_reason):
    """
    Generate detailed human-readable explanation
    Returns: dict with result, explanations list, confidence
    """
    explanations = []
    confidence_factors = []
    triggered_rules = []
    confidence = 0.0
    
    if result == "Not an E-commerce URL":
        explanations.append({
            'type': 'info',
            'title': 'Not an E-commerce Website',
            'description': f'This URL does not appear to be from an e-commerce website. Detection method: {ecommerce_reason}',
            'icon': 'info'
        })
        confidence = 95.0
        return {
            'result': result,
            'explanations': explanations,
            'confidence': confidence,
            'triggered_rules': [],
            'is_phishing': False
        }
    
    features = extract_features(url)
    domain = get_domain(url)
    domain_is_trusted = is_trusted_domain(domain)
    
    if domain_is_trusted and result == "Legitimate E-commerce Website":
        explanations.append({
            'type': 'success',
            'title': 'Known Trusted E-commerce Domain',
            'description': f'This domain belongs to a trusted e-commerce platform. Subdomains like this are commonly used by official services.',
            'icon': 'success'
        })
        confidence = 98.0
        triggered_rules.append({
            'rule': 'Trusted Domain',
            'severity': 'safe',
            'description': 'Domain root is in whitelist of trusted e-commerce sites'
        })
        return {
            'result': result,
            'explanations': explanations,
            'confidence': confidence,
            'triggered_rules': triggered_rules,
            'is_phishing': False,
            'ml_prediction': get_ml_prediction(url) if 'get_ml_prediction' in dir() else None
        }
    
    is_typosquatting, matched_domain, similarity = check_typosquatting(url)
    
    if is_typosquatting:
        triggered_rules.append({
            'rule': 'Typosquatting Detection',
            'severity': 'critical',
            'description': f'Domain "{domain}" is very similar to legitimate domain "{matched_domain}"'
        })
        explanations.append({
            'type': 'danger',
            'title': 'Typosquatting Detected',
            'description': f'The domain "{domain}" is {similarity:.1f}% similar to the legitimate "{matched_domain}". '
                          f'This is a common phishing technique where attackers register domains that look '
                          f'very similar to legitimate e-commerce sites (e.g., replacing "a" with "o", '
                          f'missing letters, or adding extra characters).',
            'icon': 'warning'
        })
        confidence = max(confidence, 85.0 + similarity * 0.1)
    
    # Check for brand impersonation
    from utils.domain_checker import has_brand_impersonation
    has_brand, brand = has_brand_impersonation(url)
    
    if has_brand and not is_known_ecommerce(url):
        triggered_rules.append({
            'rule': 'Brand Impersonation',
            'severity': 'high',
            'description': f'URL contains brand name "{brand}" but is not the official domain'
        })
        explanations.append({
            'type': 'danger',
            'title': 'Brand Impersonation',
            'description': f'This URL contains the brand name "{brand}" but is NOT the official {brand}.com website. '
                          f'Attackers often use legitimate brand names in subdomains to trick users.',
            'icon': 'warning'
        })
        confidence = max(confidence, 80.0)
    
    # Check suspicious TLDs
    if features['suspicious_tlds'] == 1:
        triggered_rules.append({
            'rule': 'Suspicious TLD',
            'severity': 'high',
            'description': 'URL uses a top-level domain commonly used in phishing'
        })
        explanations.append({
            'type': 'danger',
            'title': 'Suspicious Top-Level Domain',
            'description': 'This URL uses a domain extension (like .xyz, .ru, .cn, .top, .club) that is '
                          'commonly used by phishing websites. Legitimate e-commerce sites typically use '
                          'standard extensions like .com, .org, .net, or country-specific domains.',
            'icon': 'warning'
        })
        confidence = max(confidence, 75.0)
    
    # Check suspicious keywords
    if features['suspicious_keywords'] > 0:
        keyword_list = []
        keywords_map = {
            'login': 'Login/Authentication page',
            'verify': 'Account verification required',
            'secure': 'Security verification',
            'payment': 'Payment processing',
            'update': 'Account update required',
            'bank': 'Banking information',
            'account': 'Account access',
            'confirm': 'Confirmation required'
        }
        
        if features['suspicious_keywords'] >= 1:
            keyword_list.append('login')
        if features['suspicious_keywords'] >= 2:
            keyword_list.append('verify')
        if features['suspicious_keywords'] >= 3:
            keyword_list.append('secure')
        
        triggered_rules.append({
            'rule': 'Suspicious Keywords',
            'severity': 'medium',
            'description': f'URL contains suspicious keywords: {", ".join(keyword_list)}'
        })
        explanations.append({
            'type': 'warning',
            'title': 'Suspicious Keywords Found',
            'description': f'This URL contains words like "{", ".join(keyword_list)}" which are commonly used '
                          f'in phishing attacks. Legitimate e-commerce sites usually don\'t need these words '
                          f'in their main domain name.',
            'icon': 'warning'
        })
        confidence = max(confidence, 60.0 + features['suspicious_keywords'] * 10)
    
    # Check for IP address usage
    if features['has_ip'] == 1:
        triggered_rules.append({
            'rule': 'IP Address Usage',
            'severity': 'critical',
            'description': 'Domain is using an IP address instead of a domain name'
        })
        explanations.append({
            'type': 'danger',
            'title': 'Using IP Address Instead of Domain',
            'description': 'This URL uses a numerical IP address instead of a proper domain name. '
                          'Legitimate websites always use domain names. This is a strong indicator of phishing.',
            'icon': 'warning'
        })
        confidence = max(confidence, 90.0)
    
    # Check for random strings
    if features['random_string'] == 1:
        triggered_rules.append({
            'rule': 'Random String Detection',
            'severity': 'medium',
            'description': 'Domain contains random-looking string'
        })
        explanations.append({
            'type': 'warning',
            'title': 'Random-Looking String in Domain',
            'description': 'The domain contains a random-looking string that doesn\'t form meaningful words. '
                          'This is often used to generate many phishing domains automatically.',
            'icon': 'warning'
        })
        confidence = max(confidence, 65.0)
    
    # Check for long subdomains
    if features['long_subdomain'] == 1:
        triggered_rules.append({
            'rule': 'Long Subdomain',
            'severity': 'medium',
            'description': 'URL has unusually long subdomain'
        })
        explanations.append({
            'type': 'warning',
            'title': 'Unusually Long Subdomain',
            'description': 'This URL has an unusually long subdomain. Phishing sites often use long subdomains '
                          'to include multiple words that try to look legitimate.',
            'icon': 'warning'
        })
        confidence = max(confidence, 55.0)
    
    # Check for multiple subdomains
    if features['num_subdomains'] > 2:
        triggered_rules.append({
            'rule': 'Multiple Subdomains',
            'severity': 'medium',
            'description': f'URL has {features["num_subdomains"]} subdomains'
        })
        explanations.append({
            'type': 'warning',
            'title': 'Multiple Subdomains',
            'description': f'This URL has {features["num_subdomains"]} subdomains. Legitimate e-commerce sites '
                          f'typically have 0-2 subdomains. Multiple subdomains can be used to hide the '
                          f'real destination.',
            'icon': 'warning'
        })
        confidence = max(confidence, 50.0)
    
    # Check for many hyphens
    if features['num_hyphens'] > 2:
        triggered_rules.append({
            'rule': 'Multiple Hyphens',
            'severity': 'low',
            'description': f'URL has {features["num_hyphens"]} hyphens'
        })
        explanations.append({
            'type': 'info',
            'title': 'Many Hyphens in Domain',
            'description': f'This URL contains {features["num_hyphens"]} hyphens. While not always suspicious, '
                          f'phishing sites often use multiple hyphens to include many keywords (like '
                          f'"amazon-secure-login-verify.xyz").',
            'icon': 'info'
        })
        confidence = max(confidence, 40.0)
    
    # ML Model Analysis
    ml_result = get_ml_prediction(url)
    
    if ml_result and ml_result['prediction'] == 1:
        ml_confidence = ml_result['confidence'] * 100
        triggered_rules.append({
            'rule': 'ML Model Detection',
            'severity': 'high',
            'description': f'Machine learning model classified as phishing with {ml_confidence:.0f}% confidence'
        })
        
        top_features = sorted(ml_result['triggered_features'].items(), 
                            key=lambda x: x[1]['importance'], reverse=True)[:3]
        
        feature_descriptions = {
            'url_length': 'unusually long URL',
            'domain_length': 'unusually long domain',
            'num_dots': 'unusual number of dots',
            'num_subdomains': 'too many subdomains',
            'suspicious_tlds': 'suspicious domain extension',
            'suspicious_keywords': 'contains suspicious keywords',
            'num_hyphens': 'many hyphens in domain',
            'path_length': 'unusually long path',
            'random_string': 'random-looking string',
            'num_digits': 'many digits in domain'
        }
        
        feature_list = [feature_descriptions.get(f[0], f[0]) for f in top_features]
        
        explanations.append({
            'type': 'warning',
            'title': 'Machine Learning Detection',
            'description': f'The ML model detected this as phishing ({ml_confidence:.0f}% confidence) based on: '
                          f'{", ".join(feature_list)}. The model was trained on thousands of phishing '
                          f'URLs and learned these patterns.',
            'icon': 'ai'
        })
        confidence = max(confidence, ml_confidence * 0.9)
    
    # Check for HTTPS
    if features['has_https'] == 0:
        if check_insecure_http(url):
            triggered_rules.append({
                'rule': 'Insecure HTTP Protocol',
                'severity': 'critical',
                'description': 'URL uses insecure HTTP instead of HTTPS'
            })
            explanations.append({
                'type': 'danger',
                'title': 'Uses Insecure HTTP Protocol',
                'description': 'This URL uses insecure HTTP instead of HTTPS. E-commerce websites must use '
                              'secure HTTPS protocol to protect user data and payment information. '
                              'No legitimate e-commerce site should use HTTP.',
                'icon': 'warning'
            })
            confidence = max(confidence, 95.0)
        else:
            explanations.append({
                'type': 'info',
                'title': 'No HTTPS Encryption',
                'description': 'This URL does not use HTTPS encryption. Legitimate e-commerce websites always '
                              'use HTTPS to protect user data. However, many phishing sites now also use HTTPS, '
                              'so this alone does not guarantee safety.',
                'icon': 'info'
            })
    
    # Known legitimate domain
    if is_known_ecommerce(url):
        explanations.append({
            'type': 'success',
            'title': 'Known Legitimate E-commerce Domain',
            'description': f'This domain is in our list of known legitimate e-commerce websites. '
                          f'The URL appears to be the official {domain} website.',
            'icon': 'success'
        })
        confidence = 98.0
        triggered_rules.append({
            'rule': 'Known Domain',
            'severity': 'safe',
            'description': 'Domain is in whitelist of known e-commerce sites'
        })
    
    # Add ML confidence if it's high and supports legitimate
    if ml_result and ml_result['prediction'] == 0 and not is_known_ecommerce(url):
        ml_confidence = ml_result['confidence'] * 100
        if ml_confidence > 70:
            explanations.append({
                'type': 'success',
                'title': 'ML Model Confirms Legitimate',
                'description': f'The ML model classified this as legitimate ({ml_confidence:.0f}% confidence). '
                              f'No suspicious patterns were detected.',
                'icon': 'success'
            })
    
    # Cap confidence
    confidence = min(confidence, 99.0)
    if confidence == 0:
        confidence = 50.0
    
    is_phishing = result == "Phishing E-commerce Website"
    
    return {
        'result': result,
        'explanations': explanations,
        'confidence': confidence,
        'triggered_rules': triggered_rules,
        'is_phishing': is_phishing,
        'ml_prediction': ml_result
    }

def analyze_url(url):
    """
    Main analysis function that combines all detection methods
    Returns detailed analysis result
    """
    domain = get_domain(url)
    
    if is_known_ecommerce(url):
        result = "Legitimate E-commerce Website"
        is_ecommerce, reason = True, "whitelist"
        return generate_explanation(url, result, is_ecommerce, reason)
    
    if check_insecure_http(url):
        result = "Phishing E-commerce Website"
        is_ecommerce, reason = True, "insecure_http"
        return generate_explanation(url, result, is_ecommerce, reason)
    
    is_typosquatting, matched_domain, similarity = check_typosquatting(url)
    
    if is_typosquatting:
        result = "Phishing E-commerce Website"
        is_ecommerce, reason = True, "typosquatting"
        return generate_explanation(url, result, is_ecommerce, reason)
    
    has_brand, brand = has_brand_impersonation(url)
    if has_brand:
        result = "Phishing E-commerce Website"
        is_ecommerce, reason = True, "brand_impersonation"
        return generate_explanation(url, result, is_ecommerce, reason)
    
    features = extract_features(url)
    
    if features['suspicious_tlds'] == 1 or features['has_ip'] == 1:
        result = "Phishing E-commerce Website"
        is_ecommerce, reason = True, "suspicious_tld"
        return generate_explanation(url, result, is_ecommerce, reason)
    
    ml_result = get_ml_prediction(url)
    
    ECOMMERCE_PATH_PATTERNS = ['/product', '/shop', '/store', '/cart', '/checkout', '/buy', '/order', '/category', '/item']
    has_ecom_path = any(pattern in url.lower() for pattern in ECOMMERCE_PATH_PATTERNS)
    
    TRUSTED_BRANDS = {
        'amazon', 'ebay', 'flipkart', 'walmart', 'target', 'aliexpress',
        'alibaba', 'myntra', 'ajio', 'nykaa', 'snapdeal', 'shopify',
        'zara', 'hm', 'nike', 'adidas', 'apple', 'samsung', 'costco',
        'bestbuy', 'overstock', 'etsy', 'lazada', 'rakuten', 'tata',
        'paytm', 'meesho', 'urbanic', 'koovs', 'croma', 'lenskart',
        'bigbasket', 'grofers', 'jiomart', 'firstcry', 'forever21',
        'asos', 'uniqlo', 'sony', 'lg', 'xiaomi', 'mi', 'reliancedigital',
        'realme', 'poco', 'nothing', 'asus', 'dell', 'hp', 'lenovo', 'oneplus',
        'vivo', 'oppo', 'honor', 'motorola', 'infinix', 'tecno', 'iqoo'
    }
    is_trusted_brand = any(brand in url.lower() for brand in TRUSTED_BRANDS)
    
    if ml_result:
        pred = ml_result['prediction']
        
        if pred == 0:
            result = "Legitimate E-commerce Website"
        elif pred == 1:
            result = "Phishing E-commerce Website"
        else:
            if has_ecom_path or is_trusted_brand:
                result = "Legitimate E-commerce Website"
            else:
                result = "Not an E-commerce URL"
    else:
        if features['suspicious_keywords'] >= 2:
            result = "Phishing E-commerce Website"
        elif has_ecom_path or is_trusted_brand:
            result = "Legitimate E-commerce Website"
        else:
            result = "Not an E-commerce URL"
    
    is_ecommerce, reason = True, "ml_model"
    return generate_explanation(url, result, is_ecommerce, reason)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze a URL"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({
            'error': 'Please provide a URL'
        }), 400
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = analyze_url(url)
    
    return jsonify(result)

@app.route('/test-urls', methods=['GET'])
def test_urls():
    """Test with sample URLs"""
    test_cases = [
        ('https://amazon.com', 'Legitimate E-commerce Website'),
        ('https://flipkart.com', 'Legitimate E-commerce Website'),
        ('https://myntra.com', 'Legitimate E-commerce Website'),
        ('http://amazon-login-secure.xyz', 'Phishing E-commerce Website'),
        ('http://flipkart.verify-payment.ru', 'Phishing E-commerce Website'),
        ('http://amazom.com', 'Phishing E-commerce Website'),
        ('http://flipkarrt.com', 'Phishing E-commerce Website'),
        ('https://google.com', 'Not an E-commerce URL'),
        ('https://wikipedia.org', 'Not an E-commerce URL'),
        ('http://amazon.com', 'Phishing E-commerce Website'),
        ('http://google.com', 'Not an E-commerce URL'),
    ]
    
    results = []
    for url, expected in test_cases:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        result = analyze_url(url)
        results.append({
            'url': url,
            'expected': expected,
            'result': result['result'],
            'match': result['result'] == expected,
            'confidence': result['confidence'],
            'triggered_rules_count': len(result['triggered_rules'])
        })
    
    return jsonify(results)

if __name__ == '__main__':
    load_model()
    print("\n" + "="*60)
    print("E-COMMERCE PHISHING DETECTION SYSTEM")
    print("="*60)
    print("Server running at: http://localhost:5000")
    app.run(debug=True, port=5000)
