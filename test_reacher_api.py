import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# API Endpoint
API_URL = "http://localhost:8080/v1/check_email"

# Generate 500 test emails: 250 personal and 250 company emails.
# We use common first names for personal domains and role addresses for company domains.

personal_names = [
    "john", "mary", "david", "sarah", "michael", "jessica", "james", "emily",
    "robert", "jennifer", "william", "elizabeth", "joseph", "linda", "charles",
    "susan", "thomas", "margaret", "christopher", "lisa", "daniel", "karen",
    "paul", "nancy", "mark", "betty", "donald", "sanders", "george", "ashley",
    "kenneth", "kimberly", "steven", "donna", "edward", "carol", "brian", "ruth",
    "ronald", "sharon", "anthony", "michelle", "kevin", "laura", "jason", "sarah",
    "matthew", "kim", "gary", "deborah"
]
personal_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

company_roles = [
    "info", "support", "sales", "contact", "privacy", "security", "press", 
    "careers", "admin", "marketing"
]
company_domains = [
    "google.com", "microsoft.com", "apple.com", "amazon.com", "meta.com",
    "netflix.com", "github.com", "ibm.com", "oracle.com", "intel.com",
    "cisco.com", "hp.com", "dell.com", "salesforce.com", "adobe.com",
    "stripe.com", "paypal.com", "airbnb.com", "uber.com", "tesla.com",
    "spotify.com", "visa.com", "mastercard.com", "disney.com", "nike.com"
]

emails_to_test = []

# Add 250 personal emails (50 names * 5 domains)
for name in personal_names[:50]:
    for domain in personal_domains[:5]:
        emails_to_test.append(f"{name}@{domain}")

# Add 250 company emails (10 roles * 25 domains)
for role in company_roles[:10]:
    for domain in company_domains[:25]:
        emails_to_test.append(f"{role}@{domain}")

def check_email(email):
    """
    Sends a payload to the reacher service.
    """
    payload = {"to_email": email}
    try:
        # Reacher can take a few seconds per email, adding a timeout
        response = requests.post(API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            # Check the debug section to see if a proxy was used
            proxy_used = None
            try:
                verif = data.get("debug", {}).get("smtp", {}).get("verif_method", {}).get("verif_method", {})
                proxy_used = verif.get("proxy")
            except Exception:
                pass

            return {
                "email": email,
                "status": "success",
                "is_reachable": data.get("is_reachable"),
                "is_deliverable": data.get("smtp", {}).get("is_deliverable"),
                "proxy_used": proxy_used,
                "duration_secs": data.get("debug", {}).get("duration", {}).get("secs")
            }
        else:
            return {
                "email": email,
                "status": f"failed_http_{response.status_code}",
                "error": response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            "email": email,
            "status": "exception",
            "error": str(e)
        }

def run_load_test():
    print(f"🚀 Starting load test for {len(emails_to_test)} emails against Reacher API...")
    start_time = time.time()
    
    results = []
    # Using ThreadPoolExecutor to run requests concurrently. 
    # max_workers=10 will send 10 requests at a time. Adjust this based on your system capacity.
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map returns results in the order the calls were started
        for i, result in enumerate(executor.map(check_email, emails_to_test)):
            results.append(result)
            if (i + 1) % 50 == 0:
                print(f"✅ Processed {i + 1}/{len(emails_to_test)} emails...")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"🎉 Testing completed! Took {total_time:.2f} seconds.")

    # Save to JSON
    output_file = "reacher_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"📄 Results saved to {output_file}")

    # Print summary
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n📊 Summary: {success_count} successful API calls out of {len(results)}")

if __name__ == "__main__":
    run_load_test()
