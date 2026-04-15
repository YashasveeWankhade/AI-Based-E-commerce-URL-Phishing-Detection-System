from urllib.parse import urlparse
import re

PUBLIC_SUFFIX_LIST = {
    'com', 'co', 'org', 'net', 'edu', 'gov', 'ac', 'or', 'mil', 'mil',
    'in', 'co.in', 'com.au', 'co.uk', 'de', 'fr', 'it', 'es', 'ca', 'jp',
    'com.br', 'co.jp', 'com.mx', 'com.tr', 'com.sg', 'nl', 'se', 'ae',
    'sa', 'pl', 'be', 'co.in', 'com.hk', 'co.nz', 'com.ph', 'com.tw',
    'co.za', 'co.kr', 'co.id', 'co.th', 'co.my', 'co.nz', 'com.ar',
    'com.mx', 'com.co', 'com.pe', 'com.cl', 'com.vn', 'com.eg'
}

KNOWN_ECOMMERCE_DOMAINS = {
    # Global
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
    # Fashion brands
    'zara.com', 'hm.com', 'nike.com', 'adidas.com', 'uniqlo.com',
    'asos.com', 'forever21.com', 'koovs.com',
    # Electronics brands
    'apple.com', 'samsung.com', 'sony.com', 'lg.com', 'xiaomi.com',
    'croma.com', 'mi.com',
    # Amazon regional
    'amazon.in', 'amazon.co.in', 'amazon.co.uk', 'amazon.de', 'amazon.fr',
    'amazon.it', 'amazon.es', 'amazon.ca', 'amazon.com.au', 'amazon.com.mx',
    'amazon.com.br', 'amazon.co.jp', 'amazon.sg', 'amazon.nl', 'amazon.se',
    'amazon.ae', 'amazon.sa', 'amazon.com.tr', 'amazon.pl', 'amazon.be',
    # eBay regional
    'ebay.co.uk', 'ebay.de', 'ebay.fr', 'ebay.it', 'ebay.es',
    'ebay.com.au', 'ebay.ca', 'ebay.co.in',
    # Flipkart
    'flipkart.com',
    # Walmart regional
    'walmart.ca', 'walmart.com.mx',
    # Indian e-commerce
    'nykaafashion.com', 'grofers.com', 'urbanladder.com', 'fabhotels.com',
    'licious.in', 'healthifyme.com', 'dmart.in',
    'tatacliq.com', 'firstcry.com', 'lenskart.com',
    'reliancedigital.in', 'jiomart.com', 'spencers.in',
}

# Keywords that indicate e-commerce
ECOMMERCE_KEYWORDS = [
    'shop', 'store', 'cart', 'buy', 'product', 'checkout', 
    'order', 'payment', 'billing', 'shipping', 'track', 'deal',
    'sale', 'discount', 'offer', 'price', 'marketplace', 'mall',
    'retail', 'purchase', 'item', 'collection'
]

# URL path patterns indicating e-commerce
ECOMMERCE_PATH_PATTERNS = [
    '/product/', '/products/', '/cart/', '/checkout/', '/order/',
    '/buy/', '/shop/', '/store/', '/category/', '/item/', '/p/',
    '/producto/', '/produit/', '/warenkorb/', '/kaufen/'
]

# Brand names to detect brand impersonation
BRAND_KEYWORDS = [
    'amazon', 'flipkart', 'ebay', 'myntra', 'ajio', 'meesho', 'shopify',
    'snapdeal', 'aliexpress', 'walmart', 'target', 'bestbuy', 'homedepot',
    'lowes', 'costco', 'wayfair', 'overstock', 'newegg', 'rakuten'
]

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

def extract_main_domain(domain):
    """Extract main domain (without TLD)"""
    parts = domain.split('.')
    if len(parts) >= 2:
        return parts[-2]
    return domain

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
        
        if f"{parts[-3]}.{potential_root}" in KNOWN_ECOMMERCE_DOMAINS:
            return f"{parts[-3]}.{potential_root}"
    
    return f"{parts[-2]}.{parts[-1]}"

def is_known_ecommerce_domain(url):
    """Check if URL is from a known e-commerce domain (checks root domain for subdomains)"""
    domain = extract_domain(url)
    if domain.startswith('www.'):
        domain = domain[4:]
    
    if domain in KNOWN_ECOMMERCE_DOMAINS:
        return True
    
    root_domain = get_root_domain(domain)
    if root_domain in KNOWN_ECOMMERCE_DOMAINS:
        return True
    
    return False

def has_ecommerce_keywords(url):
    """Check for e-commerce keywords in URL"""
    url_lower = url.lower()
    keyword_count = 0
    
    for keyword in ECOMMERCE_KEYWORDS:
        if keyword in url_lower:
            keyword_count += 1
    
    # Consider it e-commerce if 2+ keywords found
    return keyword_count >= 2

def has_ecommerce_path(url):
    """Check for e-commerce path patterns"""
    path = extract_path(url)
    
    for pattern in ECOMMERCE_PATH_PATTERNS:
        if pattern in path:
            return True
    
    return False

def is_similar_to_known_ecommerce(url):
    """Check if domain is similar to known e-commerce (potential typosquatting)"""
    domain = extract_domain(url)
    main_domain = extract_main_domain(domain)
    
    from difflib import SequenceMatcher
    
    for known_domain in KNOWN_ECOMMERCE_DOMAINS:
        known_main = extract_main_domain(known_domain)
        similarity = SequenceMatcher(None, main_domain, known_main).ratio() * 100
        
        # If similarity > 70%, consider it as potential e-commerce (for phishing detection)
        if similarity > 70:
            return True, known_domain, similarity
    
    return False, None, 0

def has_brand_impersonation(url):
    """Check if URL contains brand names (potential brand impersonation/phishing)"""
    domain = extract_domain(url)
    domain_lower = domain.lower()
    
    for brand in BRAND_KEYWORDS:
        if brand in domain_lower:
            return True, brand
    
    return False, None

def is_ecommerce_url(url):
    """
    Determine if URL is an e-commerce URL using hybrid approach
    Returns: (is_ecommerce: bool, reason: str)
    """
    # Method A: Check against known e-commerce domains
    if is_known_ecommerce_domain(url):
        return True, "known_domain"
    
    # Method B: Check for e-commerce keywords
    if has_ecommerce_keywords(url):
        return True, "keyword_detection"
    
    # Method C: Check for e-commerce path patterns
    if has_ecommerce_path(url):
        return True, "path_pattern"
    
    # Method D: Check if similar to known e-commerce (for typosquatting detection)
    is_similar, matched_domain, similarity = is_similar_to_known_ecommerce(url)
    if is_similar:
        return True, f"similar_to_{matched_domain}_({similarity:.0f}%)"
    
    # Method E: Check for brand impersonation (e.g., amazon-login-secure.xyz)
    has_brand, brand = has_brand_impersonation(url)
    if has_brand:
        return True, f"brand_impersonation_{brand}"
    
    return False, "not_ecommerce"

def get_detection_info(url):
    """Get detailed detection information"""
    domain = extract_domain(url)
    path = extract_path(url)
    
    info = {
        'domain': domain,
        'path': path,
        'is_known_domain': is_known_ecommerce_domain(url),
        'keyword_count': sum(1 for k in ECOMMERCE_KEYWORDS if k in url.lower()),
        'has_ecommerce_path': has_ecommerce_path(url)
    }
    
    return info
