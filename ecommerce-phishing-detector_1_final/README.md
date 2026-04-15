# E-Commerce Phishing Detection System

A hybrid machine learning + rule-based phishing detection system specifically designed for E-commerce URLs. This system detects typosquatting attacks like "amazom.com" and classifies URLs as legitimate, phishing, or not e-commerce.

## Project Overview

This project implements a complete phishing detection system with:

- **E-commerce URL Detection**: Identifies if a URL belongs to an e-commerce website
- **Typosquatting Detection**: Uses Levenshtein distance and string similarity to detect fake domains
- **ML Classification**: Random Forest model for phishing detection
- **Rule-Based Checks**: Additional heuristics for suspicious patterns

## System Architecture

### Step 1: Input
User enters a URL via the web interface.

### Step 2: E-commerce Detection (STRICT FILTER)
The system first classifies whether the URL belongs to an e-commerce domain:

- **Known E-commerce Domains**: List of 50+ known legitimate e-commerce domains
- **Keyword Detection**: Checks for keywords like shop, store, cart, buy, product
- **Path Pattern Detection**: Checks for patterns like /product/, /cart/, /checkout/
- **Brand Detection**: Checks for brand impersonation (e.g., amazon-login.xyz)
- **Similarity Detection**: Checks for domains similar to known e-commerce

If NOT e-commerce → Returns: **"Not an E-commerce URL"**

### Step 3: Phishing Detection (ONLY IF E-COMMERCE)

#### Typosquatting Detection (CRITICAL)
- **Levenshtein Distance**: Compares input domain with known e-commerce domains
- **String Similarity**: If similarity > 80% AND not exact match → Phishing

#### ML Model (Random Forest)
- 16 URL-based features extracted
- Trained on 3500 URLs (1500 legitimate, 1500 phishing, 500 non-ecommerce)
- Model accuracy: 92%

#### Rule-Based Checks
- Suspicious TLDs (.xyz, .ru, .cn, etc.)
- Suspicious keywords (login, verify, secure, payment)
- IP address usage
- Long/random subdomains

### Decision Logic

```
IF not e-commerce → "Not an E-commerce URL"
ELSE:
    IF typosquatting detected → "Phishing E-commerce Website"
    ELSE IF ML predicts phishing → "Phishing E-commerce Website"
    ELSE IF rule-based flags → "Phishing E-commerce Website"
    ELSE → "Legitimate E-commerce Website"
```

## Features Used

### URL-Based Features
- URL length
- Domain length
- Number of dots
- Number of subdomains
- Presence of IP address
- Presence of HTTPS
- Special characters count
- Suspicious keywords count
- Suspicious TLDs
- Long subdomain
- Random string detection
- Number of digits
- Number of hyphens
- Path length

### Typosquatting Detection
- **Levenshtein Distance**: Edit distance between strings
- **SequenceMatcher Similarity**: Character-level similarity ratio

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **ML**: scikit-learn (Random Forest)
- **Dependencies**: pandas, numpy, Levenshtein

## Project Structure

```
ecommerce-phishing-detector/
├── app.py                  # Flask backend
├── train_model.py          # Model training script
├── test_system.py          # Test script
├── model/
│   ├── model.pkl          # Trained Random Forest model
│   └── vectorizer.pkl      # Feature column names
├── utils/
│   ├── feature_extraction.py   # Feature extraction
│   ├── domain_checker.py       # E-commerce detection
│   └── typo_detector.py        # Typosquatting detection
├── dataset/
│   ├── urls.csv            # Dataset
│   └── generate_dataset.py # Dataset generator
├── templates/
│   └── index.html          # Frontend
├── static/
│   ├── style.css           # Styles
│   └── script.js           # JavaScript
└── README.md               # This file
```

## Installation

1. Install dependencies:
```bash
pip install flask scikit-learn pandas numpy Levenshtein
```

2. Generate dataset:
```bash
python dataset/generate_dataset.py
```

3. Train model:
```bash
python train_model.py
```

4. Run the application:
```bash
python app.py
```

5. Open browser at: http://localhost:5000

## Testing

Run the test script to verify system functionality:
```bash
python test_system.py
```

### Sample Test Cases

| URL | Expected Result |
|-----|-----------------|
| https://amazon.com | Legitimate E-commerce Website |
| https://flipkart.com | Legitimate E-commerce Website |
| http://amazom.com | Phishing E-commerce Website |
| http://flipkarrt.com | Phishing E-commerce Website |
| http://amazon-login-secure.xyz | Phishing E-commerce Website |
| https://google.com | Not an E-commerce URL |

## Model Evaluation

The model achieves the following metrics on the test set:

- **Accuracy**: 92%
- **Precision**: 91.75%
- **Recall**: 94.50%
- **F1-Score**: 93.10%

### Feature Importance (Top 5)
1. path_length: 34.12%
2. num_hyphens: 12.30%
3. suspicious_tlds: 11.93%
4. url_length: 10.91%
5. domain_length: 8.93%

## How Typosquatting Detection Works

1. **Extract domain**: Get the main domain name (e.g., "amazom" from "amazom.com")
2. **Compare with known domains**: Compare against 50+ known e-commerce domains
3. **Calculate similarity**:
   - Levenshtein distance: Number of edits to transform one string to another
   - SequenceMatcher: Character-level similarity ratio
4. **Apply rules**:
   - If similarity > 80% → Phishing
   - If edit distance ≤ 2 → Phishing

Example: "amazom.com" vs "amazon.com"
- Similarity: 83.3% (above 80% threshold)
- Levenshtein distance: 1 (very close)
- Result: **Phishing detected**

## Hardware Requirements

- CPU-based system (optimized for CPU)
- 8GB RAM
- No GPU required
- Works on integrated graphics (Intel UHD)

## Output Format

The system returns exactly one of:

1. **"Legitimate E-commerce Website"** - Green
2. **"Phishing E-commerce Website"** - Red  
3. **"Not an E-commerce URL"** - Gray

Each result includes an explanation of why that classification was made.

## License

This project is for educational purposes.
