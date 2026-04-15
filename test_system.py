import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import load_model, analyze_url

load_model()

print("\n" + "="*80)
print("TESTING E-COMMERCE PHISHING DETECTION SYSTEM")
print("="*80)

test_cases = [
    # Global marketplaces
    ('https://www.amazon.com', 'Legitimate E-commerce Website'),
    ('https://www.ebay.com', 'Legitimate E-commerce Website'),
    ('https://www.walmart.com', 'Legitimate E-commerce Website'),
    ('https://www.alibaba.com', 'Legitimate E-commerce Website'),
    ('https://www.aliexpress.com', 'Legitimate E-commerce Website'),
    ('https://www.etsy.com', 'Legitimate E-commerce Website'),
    ('https://www.target.com', 'Legitimate E-commerce Website'),
    ('https://www.bestbuy.com', 'Legitimate E-commerce Website'),
    ('https://www.newegg.com', 'Legitimate E-commerce Website'),
    ('https://www.overstock.com', 'Legitimate E-commerce Website'),
    
    # Indian e-commerce
    ('https://www.amazon.in', 'Legitimate E-commerce Website'),
    ('https://www.flipkart.com', 'Legitimate E-commerce Website'),
    ('https://www.myntra.com', 'Legitimate E-commerce Website'),
    ('https://www.ajio.com', 'Legitimate E-commerce Website'),
    ('https://www.nykaa.com', 'Legitimate E-commerce Website'),
    ('https://www.tatacliq.com', 'Legitimate E-commerce Website'),
    ('https://www.snapdeal.com', 'Legitimate E-commerce Website'),
    ('https://www.paytmmall.com', 'Legitimate E-commerce Website'),
    ('https://www.firstcry.com', 'Legitimate E-commerce Website'),
    ('https://www.lenskart.com', 'Legitimate E-commerce Website'),
    
    # Fashion brands
    ('https://www.zara.com', 'Legitimate E-commerce Website'),
    ('https://www.hm.com', 'Legitimate E-commerce Website'),
    ('https://www.asos.com', 'Legitimate E-commerce Website'),
    ('https://www.forever21.com', 'Legitimate E-commerce Website'),
    ('https://www.urbanic.com', 'Legitimate E-commerce Website'),
    ('https://www.koovs.com', 'Legitimate E-commerce Website'),
    
    # Electronics brands
    ('https://www.croma.com', 'Legitimate E-commerce Website'),
    ('https://www.reliancedigital.in', 'Legitimate E-commerce Website'),
    ('https://www.apple.com/in/store', 'Legitimate E-commerce Website'),
    ('https://www.samsung.com/in/store', 'Legitimate E-commerce Website'),
    ('https://www.mi.com/in', 'Legitimate E-commerce Website'),
    
    # Grocery & others
    ('https://www.bigbasket.com', 'Legitimate E-commerce Website'),
    ('https://www.grofers.com', 'Legitimate E-commerce Website'),  # now Blinkit
    ('https://www.jiomart.com', 'Legitimate E-commerce Website'),
    ('https://www.spencers.in', 'Legitimate E-commerce Website'),
    
    # Previously tested cases
    ('https://export.ebay.com/in/', 'Legitimate E-commerce Website'),
    ('https://seller.ebay.com', 'Legitimate E-commerce Website'),
    ('https://stores.ebay.com', 'Legitimate E-commerce Website'),
    ('https://pages.aliexpress.com', 'Legitimate E-commerce Website'),
    ('https://seller.flipkart.com', 'Legitimate E-commerce Website'),
    ('https://www2.zara.com', 'Legitimate E-commerce Website'),
    ('http://amazon-login-secure.xyz', 'Phishing E-commerce Website'),
    ('http://flipkart.verify-payment.ru', 'Phishing E-commerce Website'),
    ('http://amazom.com', 'Phishing E-commerce Website'),
    ('http://flipkarrt.com', 'Phishing E-commerce Website'),
    ('https://google.com', 'Not an E-commerce URL'),
    ('https://wikipedia.org', 'Not an E-commerce URL'),
    ('http://amazon.com', 'Phishing E-commerce Website'),
    ('http://google.com', 'Not an E-commerce URL'),
    ('https://www.bbc.com/news', 'Not an E-commerce URL'),
    ('https://www.nytimes.com', 'Not an E-commerce URL'),
]

print(f"\n{'URL':<45} | {'Expected':<35} | {'Result':<35} | Match")
print("-"*120)

passed = 0
failed = 0

for url, expected in test_cases:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = analyze_url(url)
    actual_result = result['result']
    match = actual_result == expected
    
    if match:
        passed += 1
        status = "[PASS]"
    else:
        failed += 1
        status = "[FAIL]"
    
    print(f"{url:<45} | {expected:<35} | {actual_result:<35} | {status}")

print("-"*120)
print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")

print("\n" + "="*80)
print("DETAILED EXPLANATIONS FOR KEY TEST CASES")
print("="*80)

key_tests = [
    'https://export.ebay.com/in/',
    'https://seller.ebay.com',
    'https://stores.ebay.com',
    'https://amazon.com',
    'http://amazon.com',
    'http://amazom.com',
    'http://flipkarrt.com',
    'http://amazon-login-secure.xyz',
]

for url in key_tests:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = analyze_url(url)
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    print(f"Result: {result['result']}")
    print(f"Confidence: {result['confidence']:.1f}%")
    print(f"\nTriggered Rules ({len(result['triggered_rules'])}):")
    for rule in result['triggered_rules']:
        print(f"  - [{rule['severity'].upper()}] {rule['rule']}")
    
    print(f"\nExplanations:")
    for exp in result['explanations']:
        print(f"  [{exp['type'].upper()}] {exp['title']}")
        if len(exp['description']) > 100:
            print(f"    {exp['description'][:100]}...")
        else:
            print(f"    {exp['description']}")
