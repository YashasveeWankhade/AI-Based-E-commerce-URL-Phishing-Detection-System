import re
from urllib.parse import urlparse
import math

TRUSTED_ECOMMERCE_DOMAINS = {
    'amazon.com', 'flipkart.com', 'ebay.com', 'myntra.com', 'ajio.com',
    'meesho.com', 'shopify.com', 'snapdeal.com', 'aliexpress.com',
    'walmart.com', 'target.com', 'bestbuy.com', 'homedepot.com',
    'lowes.com', 'costco.com', 'wayfair.com', 'overstock.com',
    'newegg.com', 'bhphotovideo.com', 'adorama.com', 'rakuten.com',
    'tata.com', 'paytmmall.com', 'shopclues.com', 'indiamart.com',
    'nykaa.com', 'moglix.com', 'bigbasket.com', 'pepperfry.com',
    'alibaba.com', 'wish.com', 'groupon.com', 'livingsocial.com',
    'zappos.com', 'nordstrom.com', 'macys.com', 'kohls.com',
    'jcpenney.com', 'sears.com', 'dillards.com', 'neimanmarcus.com',
    'saks.com', 'bloomingdales.com', 'marshalls.com', 'tjmaxx.com',
    'rossstores.com', 'burlington.com', 'gap.com', 'oldnavy.com',
    'bananarepublic.com', 'jcrew.com', 'landsend.com', 'l.lbean.com',
    'etsy.com', 'mercadolibre.com', 'lazada.com', 'zalando.com',
    'jd.com', 'pinduoduo.com',
    'amazon.in', 'amazon.co.in', 'amazon.co.uk', 'amazon.de', 'amazon.fr',
    'amazon.it', 'amazon.es', 'amazon.ca', 'amazon.com.au', 'amazon.com.mx',
    'amazon.com.br', 'amazon.co.jp', 'amazon.sg', 'amazon.nl', 'amazon.se',
    'amazon.ae', 'amazon.sa', 'amazon.com.tr', 'amazon.pl', 'amazon.be',
    'ebay.co.uk', 'ebay.de', 'ebay.fr', 'ebay.it', 'ebay.es',
    'ebay.com.au', 'ebay.ca', 'ebay.co.in',
    'flipkart.com',
    'walmart.ca', 'walmart.com.mx',
    'nykaafashion.com', 'grofers.com', 'urbanladder.com', 'fabhotels.com',
    'licious.in', 'healthifyme.com', 'dmart.in',
    'tatacliq.com', 'firstcry.com', 'lenskart.com',
    'reliancedigital.in', 'jiomart.com', 'spencers.in',
    'zara.com', 'hm.com', 'nike.com', 'adidas.com', 'uniqlo.com',
    'asos.com', 'forever21.com', 'koovs.com', 'urbanic.com',
    'apple.com', 'samsung.com', 'sony.com', 'lg.com', 'xiaomi.com',
    'croma.com', 'mi.com',
}

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
    'bigbasket', 'grofers', 'jiomart', 'firstcry', 'forever21',
    'asos', 'uniqlo', 'sony', 'lg', 'xiaomi', 'mi', 'reliancedigital'
}

PUBLIC_SUFFIX_LIST = {
    'com', 'co', 'org', 'net', 'edu', 'gov', 'ac', 'or', 'mil',
    'in', 'co.in', 'com.au', 'co.uk', 'de', 'fr', 'it', 'es', 'ca', 'jp',
    'com.br', 'co.jp', 'com.mx', 'com.tr', 'com.sg', 'nl', 'se', 'ae',
    'sa', 'pl', 'be', 'co.in', 'com.hk', 'co.nz', 'com.ph', 'com.tw',
    'co.za', 'co.kr', 'co.id', 'co.th', 'co.my', 'com.ar', 'com.mx',
    'com.co', 'com.pe', 'com.cl', 'com.vn', 'com.eg'
}

def get_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""

def get_path(url):
    """Extract path from URL"""
    try:
        parsed = urlparse(url)
        return parsed.path.lower()
    except:
        return ""

def get_root_domain(domain):
    """Extract root domain from any domain (handles subdomains)"""
    domain = domain.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    
    parts = domain.split('.')
    
    if len(parts) < 2:
        return domain
    
    if len(parts) >= 3:
        second_last = parts[-2]
        last = parts[-1]
        potential_root = f"{second_last}.{last}"
        
        if last in PUBLIC_SUFFIX_LIST:
            return potential_root
        
        if f"{parts[-3]}.{potential_root}" in TRUSTED_ECOMMERCE_DOMAINS:
            return f"{parts[-3]}.{potential_root}"
    
    return f"{parts[-2]}.{parts[-1]}"

def is_trusted_domain(domain):
    """Check if domain belongs to a trusted e-commerce site"""
    if domain.startswith('www.'):
        domain = domain[4:]
    
    if domain in TRUSTED_ECOMMERCE_DOMAINS:
        return True
    
    root_domain = get_root_domain(domain)
    return root_domain in TRUSTED_ECOMMERCE_DOMAINS

def get_url_length(url):
    """Get total URL length"""
    return len(url)

def get_domain_length(domain):
    """Get domain length"""
    return len(domain)

def count_dots(domain):
    """Count number of dots in domain"""
    return domain.count('.')

def count_subdomains(domain):
    """Count number of subdomains, excluding trusted domains"""
    if is_trusted_domain(domain):
        return 0
    parts = domain.split('.')
    if len(parts) > 2:
        return len(parts) - 2
    return 0

def has_ip_address(domain):
    """Check if domain contains IP address"""
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, domain):
        return 1
    return 0

def has_https(url):
    """Check if URL uses HTTPS"""
    if url.startswith('https://'):
        return 1
    return 0

def count_special_chars(url):
    """Count special characters in URL"""
    special_chars = ['@', '-', '_', '=', '?', '&', '%', '#']
    count = 0
    for char in url:
        if char in special_chars:
            count += 1
    return count

def check_suspicious_keywords(url):
    """Check for suspicious keywords in URL"""
    suspicious_keywords = ['login', 'verify', 'secure', 'payment', 'update', 
                          'bank', 'account', 'confirm', 'password', 'credential']
    url_lower = url.lower()
    count = 0
    for keyword in suspicious_keywords:
        if keyword in url_lower:
            count += 1
    return count

def check_suspicious_tlds(domain):
    """Check for suspicious TLDs commonly used in phishing"""
    suspicious_tlds = ['.xyz', '.top', '.club', '.win', '.online', '.site', 
                      '.work', '.click', '.link', '.ru', '.cn', '.tk', '.ml',
                      '.ga', '.cf', '.gq', '.pw', '.cc', '.ws', '.info']
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            return 1
    return 0

def check_long_subdomain(domain):
    """Check if subdomain is unusually long (exclude trusted domains)"""
    if is_trusted_domain(domain):
        return 0
    parts = domain.split('.')
    for part in parts[:-2]:
        if len(part) > 20:
            return 1
    return 0

def check_random_string(domain):
    """Check for random-looking strings in domain (high entropy)"""
    parts = domain.split('.')
    for part in parts[:-2]:
        if len(part) > 10:
            unique_ratio = len(set(part)) / len(part)
            if unique_ratio > 0.8 and len(part) > 15:
                return 1
    return 0

def count_digits(domain):
    """Count digits in domain"""
    return sum(c.isdigit() for c in domain)

def count_hyphens(domain):
    """Count hyphens in domain"""
    return domain.count('-')

def extract_features(url):
    """
    Extract all features from URL for ML model
    Returns a dictionary of features
    """
    domain = get_domain(url)
    path = get_path(url)
    
    features = {
        'url_length': get_url_length(url),
        'domain_length': get_domain_length(domain),
        'num_dots': count_dots(domain),
        'num_subdomains': count_subdomains(domain),
        'has_ip': has_ip_address(domain),
        'has_https': has_https(url),
        'special_chars': count_special_chars(url),
        'suspicious_keywords': check_suspicious_keywords(url),
        'suspicious_tlds': check_suspicious_tlds(domain),
        'long_subdomain': check_long_subdomain(domain),
        'random_string': check_random_string(domain),
        'num_digits': count_digits(domain),
        'num_hyphens': count_hyphens(domain),
        'path_length': len(path),
        'has_at_symbol': 1 if '@' in url else 0,
        'has_double_slash': 1 if '//' in url[8:] else 0,
    }
    
    return features

def get_feature_vector(url):
    """
    Get feature vector as a list for ML model prediction
    """
    features = extract_features(url)
    feature_names = [
        'url_length', 'domain_length', 'num_dots', 'num_subdomains',
        'has_ip', 'has_https', 'special_chars', 'suspicious_keywords',
        'suspicious_tlds', 'long_subdomain', 'random_string',
        'num_digits', 'num_hyphens', 'path_length', 
        'has_at_symbol', 'has_double_slash'
    ]
    
    return [features[name] for name in feature_names]
