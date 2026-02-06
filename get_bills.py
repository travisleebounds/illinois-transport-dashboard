import requests
import json
from datetime import datetime
import time

API_KEY = "IE9bLJbEq56e0AUfy5K5CSg4VuGx7M4csHwgcIfm"

MEMBERS = {
    "IL-01": {"bioguide": "J000308", "name": "Jonathan Jackson"},
    "IL-02": {"bioguide": "K000385", "name": "Robin Kelly"},
    "IL-03": {"bioguide": "R000617", "name": "Delia Ramirez"},
    "IL-04": {"bioguide": "G000586", "name": "Jesús García"},
    "IL-05": {"bioguide": "Q000023", "name": "Mike Quigley"},
    "IL-06": {"bioguide": "C001117", "name": "Sean Casten"},
    "IL-07": {"bioguide": "D000096", "name": "Danny Davis"},
    "IL-08": {"bioguide": "K000391", "name": "Raja Krishnamoorthi"},
    "IL-09": {"bioguide": "S001145", "name": "Jan Schakowsky"},
    "IL-10": {"bioguide": "S001190", "name": "Brad Schneider"},
    "IL-11": {"bioguide": "F000454", "name": "Bill Foster"},
    "IL-12": {"bioguide": "B001295", "name": "Mike Bost"},
    "IL-13": {"bioguide": "B001316", "name": "Nikki Budzinski"},
    "IL-14": {"bioguide": "U000040", "name": "Lauren Underwood"},
    "IL-15": {"bioguide": "M001211", "name": "Mary Miller"},
    "IL-16": {"bioguide": "L000585", "name": "Darin LaHood"},
    "IL-17": {"bioguide": "S001224", "name": "Eric Sorensen"},
}

print("=" * 70)
print("FETCHING REAL BILLS FROM CONGRESS.GOV API")
print("=" * 70)

all_bills = {}

for dist, info in MEMBERS.items():
    print(f"\n{dist}: {info['name']}...", end=" ")
    
    bills = []
    
    # Sponsored bills
    url = f"https://api.congress.gov/v3/member/{info['bioguide']}/sponsored-legislation"
    params = {"api_key": API_KEY, "format": "json", "limit": 250}
    
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        for bill in data.get('sponsoredLegislation', []):
            if bill.get('congress') == 119:
                bills.append({
                    "number": f"{bill.get('type', '')}.{bill.get('number', '')}",
                    "title": bill.get('title', 'No title'),
                    "relationship": "Sponsor",
                    "url": bill.get('url', '')
                })
        
        print(f"Sponsored: {len(bills)}", end=" ")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Cosponsored bills
    cosp_url = f"https://api.congress.gov/v3/member/{info['bioguide']}/cosponsored-legislation"
    
    try:
        r = requests.get(cosp_url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        cosp_count = 0
        for bill in data.get('cosponsoredLegislation', []):
            if bill.get('congress') == 119:
                bills.append({
                    "number": f"{bill.get('type', '')}.{bill.get('number', '')}",
                    "title": bill.get('title', 'No title'),
                    "relationship": "Cosponsor",
                    "url": bill.get('url', '')
                })
                cosp_count += 1
        
        print(f"| Cosponsored: {cosp_count}")
    except Exception as e:
        print(f"ERROR cosponsor: {e}")
    
    all_bills[dist] = {
        "member": info['name'],
        "bills": bills,
        "total": len(bills)
    }
    
    time.sleep(1)  # Be nice to API

output_file = f"bills_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(all_bills, f, indent=2)

total = sum(d['total'] for d in all_bills.values())

print("\n" + "=" * 70)
print("✅ COMPLETE")
print("=" * 70)
print(f"Saved: {output_file}")
print(f"Total bills: {total}")
print()

