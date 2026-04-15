import random
import csv

# Known legitimate e-commerce domains
legitimate_domains = [
    'amazon.com', 'flipkart.com', 'ebay.com', 'myntra.com', 'ajio.com',
    'meesho.com', 'shopify.com', 'snapdeal.com', 'aliexpress.com',
    'walmart.com', 'target.com', 'bestbuy.com', 'homedepot.com',
    'lowes.com', 'costco.com', 'wayfair.com', 'overstock.com',
    'newegg.com', 'rakuten.com', 'tata.com', 'paytmmall.com',
    'nykaa.com', 'bigbasket.com', 'pepperfry.com', 'alibaba.com'
]

# Typosquatting variations of legitimate domains
typosquatting_domains = [
    'amazom.com', 'flipkart.com', 'amazonn.com', 'flipkarrt.com',
    'amazon-login.com', 'flipkart-verify.com', 'ebay-secure.com',
    'myntra-shop.com', 'ajio-offer.com', 'meesho-sale.com',
    'amaz0n.com', 'fl1pkart.com', 'eb4y.com', 'myntr4.com',
    'amazon-secure.xyz', 'flipkart-payment.ru', 'ebay-login.info',
    'amazom.net', 'flipkart-verify.ru', 'myntra-deals.com'
]

# Suspicious TLDs often used for phishing
suspicious_tlds = ['.xyz', '.top', '.club', '.win', '.online', '.site', '.work', '.click', '.link', '.ru', '.cn', '.tk']

# Suspicious keywords
suspicious_keywords = ['login', 'verify', 'secure', 'payment', 'update', 'bank', 'account', 'confirm']

# Generate legitimate URLs
def generate_legitimate_urls(count):
    urls = []
    paths = ['', '/product/1234', '/shop', '/cart', '/checkout', '/order/12345', 
             '/store', '/products', '/category/electronics', '/buy-now']
    
    for _ in range(count):
        domain = random.choice(legitimate_domains)
        path = random.choice(paths)
        
        # Vary between http/https
        protocol = random.choice(['http://', 'https://'])
        
        # Sometimes add www
        prefix = random.choice(['', 'www.'])
        
        url = f"{protocol}{prefix}{domain}{path}"
        urls.append(url)
    
    return urls

# Generate phishing URLs
def generate_phishing_urls(count):
    urls = []
    patterns = [
        '{domain}/login', '{domain}/verify', '{domain}/secure',
        '{domain}/payment', '{domain}/update', '{domain}/account',
        'login-{domain}.xyz', 'secure-{domain}.ru', '{domain}-verify.com',
        '{domain}.secure-login.xyz', '{domain}-payment.ru'
    ]
    
    for _ in range(count):
        domain = random.choice(legitimate_domains)
        pattern = random.choice(patterns)
        
        # Create phishing variations
        phishing_domain = random.choice([
            f"login-{domain}.xyz",
            f"secure-{domain}.ru",
            f"{domain}-verify.com",
            f"{domain}.xyz",
            f"www-{domain}.top"
        ])
        
        protocol = random.choice(['http://', 'https://'])
        url = f"{protocol}{phishing_domain}"
        urls.append(url)
    
    return urls

# Generate typosquatting URLs
def generate_typosquatting_urls(count):
    urls = []
    
    for _ in range(count):
        domain = random.choice(typosquatting_domains)
        protocol = random.choice(['http://', 'https://'])
        url = f"{protocol}{domain}"
        urls.append(url)
    
    return urls

# Generate non-ecommerce URLs
def generate_non_ecommerce_urls(count):
    urls = []
    non_ecommerce = [
        'google.com', 'facebook.com', 'wikipedia.org', 'youtube.com',
        'twitter.com', 'instagram.com', 'linkedin.com', 'github.com',
        'stackoverflow.com', 'reddit.com', 'netflix.com', 'microsoft.com',
        'apple.com', 'yahoo.com', 'bing.com', 'amazon.in', 'cnn.com'
    ]
    paths = ['', '/about', '/contact', '/blog', '/news', '/support']
    
    for _ in range(count):
        domain = random.choice(non_ecommerce)
        path = random.choice(paths)
        protocol = random.choice(['http://', 'https://'])
        url = f"{protocol}{domain}{path}"
        urls.append(url)
    
    return urls

# Generate and save dataset
def generate_dataset():
    print("Generating dataset...")
    
    data = []
    
    # Generate 1500 legitimate e-commerce URLs
    legitimate = generate_legitimate_urls(1500)
    for url in legitimate:
        data.append([url, 0, 'legitimate'])
    
    # Generate 1000 phishing URLs
    phishing = generate_phishing_urls(1000)
    for url in phishing:
        data.append([url, 1, 'phishing'])
    
    # Generate 500 typosquatting URLs
    typosquatting = generate_typosquatting_urls(500)
    for url in typosquatting:
        data.append([url, 1, 'phishing'])
    
    # Generate 500 non-ecommerce URLs
    non_ecommerce = generate_non_ecommerce_urls(500)
    for url in non_ecommerce:
        data.append([url, 2, 'non_ecommerce'])
    
    # Shuffle the data
    random.shuffle(data)
    
    # Write to CSV
    with open('dataset/urls.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'label', 'type'])
        writer.writerows(data)
    
    print(f"Dataset generated with {len(data)} URLs")
    print(f"  - Legitimate: {len(legitimate)}")
    print(f"  - Phishing: {len(phishing) + len(typosquatting)}")
    print(f"  - Non-ecommerce: {len(non_ecommerce)}")

if __name__ == '__main__':
    generate_dataset()
