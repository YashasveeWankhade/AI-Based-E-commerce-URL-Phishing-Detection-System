from difflib import SequenceMatcher
import Levenshtein
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
    'nykaa.com', 'moglix.com', 'university.com', 'greetingcards.com',
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
    # Flipkart regional
    'flipkart.com',
    # eBay regional
    'ebay.com', 'ebay.co.uk', 'ebay.de', 'ebay.fr', 'ebay.it', 'ebay.es',
    'ebay.com.au', 'ebay.ca', 'ebay.co.in',
    # Walmart regional
    'walmart.com', 'walmart.ca', 'walmart.com.mx', 'flipkart.com',
    # Other major e-commerce
    'aliexpress.com', 'alibaba.com', 'tata.com', 'myntra.com',
    'shopify.com', 'etsy.com', 'mercadolibre.com', 'rakuten.com',
    'jd.com', 'pinduoduo.com', 'lazada.com', 'zalando.com',
    # Indian e-commerce
    'nykaa.com', 'nykaafashion.com', 'snapdeal.com', 'paytmmall.com',
    'shopclues.com', 'bigbasket.com', 'grofers.com', 'pepperfry.com',
    'urbanladder.com', 'fabhotels.com', 'licious.in', 'healthifyme.com',
    'tatacliq.com', 'firstcry.com', 'lenskart.com',
    'reliancedigital.in', 'jiomart.com', 'spencers.in',
}

TRUSTED_DOMAIN_ROOTS = {d.split('.')[-2] + '.' + d.split('.')[-1] for d in KNOWN_ECOMMERCE_DOMAINS}

def extract_domain(url):
    """Extract domain from URL"""
    if '://' in url:
        domain = url.split('://')[1].split('/')[0]
    else:
        domain = url.split('/')[0]
    return domain.lower()

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
        
        if f"{parts[-3]}.{potential_root}" in TRUSTED_DOMAIN_ROOTS:
            return f"{parts[-3]}.{potential_root}"
    
    return f"{parts[-2]}.{parts[-1]}"

def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def string_similarity(s1, s2):
    """Calculate similarity ratio between two strings using SequenceMatcher"""
    return SequenceMatcher(None, s1, s2).ratio() * 100

def check_typosquatting(url):
    """
    Check if URL is a typosquatting attack against known e-commerce domains
    Returns: (is_typosquatting: bool, matched_domain: str, similarity: float)
    """
    domain = extract_domain(url)
    
    if domain.startswith('www.'):
        domain = domain[4:]
    
    if domain in KNOWN_ECOMMERCE_DOMAINS:
        return False, None, 0
    
    root_domain = get_root_domain(domain)
    if root_domain in KNOWN_ECOMMERCE_DOMAINS:
        return False, None, 0
    
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        main_domain = domain_parts[-2]
    else:
        main_domain = domain
    
    best_match = None
    best_similarity = 0
    best_distance = float('inf')
    
    for known_domain in KNOWN_ECOMMERCE_DOMAINS:
        # Get the main part of known domain
        known_parts = known_domain.split('.')
        known_main = known_parts[0]
        
        # Skip if main domains don't match
        if main_domain != known_main:
            continue
            
        # Calculate similarity
        similarity = string_similarity(main_domain, known_main)
        distance = levenshtein_distance(main_domain, known_main)
        
        # Only flag as typosquatting if:
        # 1. Main domain names are identical (same brand)
        # 2. TLD is suspicious or very different
        if similarity >= 100 and domain != known_domain:
            suspicious_tlds = ['.xyz', '.top', '.club', '.win', '.online', '.site', 
                             '.work', '.click', '.link', '.ru', '.cn', '.tk', '.ml',
                             '.ga', '.cf', '.gq', '.pw', '.cc', '.ws', '.info',
                             '.click', '.download', '.stream', '.racing']
            
            current_tld = '.' + domain_parts[-1] if len(domain_parts) > 1 else ''
            known_tld = '.' + known_parts[-1] if len(known_parts) > 1 else ''
            
            # Flag as typosquatting if same brand but suspicious/different TLD
            if current_tld in suspicious_tlds:
                return True, known_domain, similarity
            # Flag if TLD is completely different (e.g., .com vs .xyz)
            if current_tld != known_tld and current_tld not in ['.com', '.org', '.net', '.co']:
                return True, known_domain, similarity
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = known_domain
            best_distance = distance
    
    # Check for character-level typosquatting (substitution, missing chars)
    for known_domain in KNOWN_ECOMMERCE_DOMAINS:
        known_parts = known_domain.split('.')
        known_main = known_parts[0]
        
        # Skip if main domains are the same
        if main_domain == known_main:
            continue
            
        distance = levenshtein_distance(main_domain, known_main)
        similarity = string_similarity(main_domain, known_main)
        
        # Flag as typosquatting if very small edit distance (1-2 chars different)
        # and high similarity (>80%)
        if distance <= 2 and distance > 0 and similarity > 80:
            return True, known_domain, similarity
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = known_domain
            best_distance = distance
    
    # Only flag as typosquatting if high similarity AND domain is not in known list
    if best_similarity > 80 and best_distance <= 2:
        return True, best_match, best_similarity
    
    return False, None, 0

def is_known_ecommerce(url):
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
