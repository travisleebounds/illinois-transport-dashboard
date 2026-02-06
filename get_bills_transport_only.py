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

def is_transportation_bill(bill_type, bill_number):
    """Check if bill is transportation-related"""
    url = f"https://api.congress.gov/v3/bill/119/{bill_type}/{bill_number}"
    params = {"api_key": API_KEY, "format": "json"}
    
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.ok:
            bill_data = r.json().get('bill', {})
            
            # Check policy area
            policy_area = bill_data.get('policyArea', {}).get('name', '')
            if 'Transportation and Public Works' in policy_area:
                return True
            
            # Check subjects
            subjects = bill_data.get('subjects', {}).get('legislativeSubjects', [])
            for subject in subjects:
                subject_name = subject.get('name', '').lower()
                if 'transportation' in subject_name or 'highway' in subject_name or 'transit' in subject_name:
                    return True
        
        time.sleep(0.3)  # Rate limiting
        return False
    except:
        return False

print("=" * 70)
print("FETCHING TRANSPORTATION BILLS ONLY")
print("=" * 70)

all_bills = {}

for dist, info in MEMBERS.items():
    print(f"\n{dist}: {info['name']}...")
    
    transport_bills = []
    
    # Get all sponsored bills
    url = f"https://api.congress.gov/v3/member/{info['bioguide']}/sponsored-legislation"
    params = {"api_key": API_KEY, "format": "json", "limit": 250}
    
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        for bill in data.get('sponsoredLegislation', []):
            if bill.get('congress') == 119:
                bill_type = bill.get('type', '').lower()
                bill_num = bill.get('number')
                
                # Check if transportation-related
                if is_transportation_bill(bill_type, bill_num):
                    transport_bills.append({
                        "number": f"{bill.get('type', '')}.{bill_num}",
                        "title": bill.get('title', 'No title'),
                        "relationship": "Sponsor",
                        "url": bill.get('url', '')
                    })
        
        print(f"  Sponsored (transport): {len(transport_bills)}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Get cosponsored bills
    cosp_url = f"https://api.congress.gov/v3/member/{info['bioguide']}/cosponsored-legislation"
    
    try:
        r = requests.get(cosp_url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        cosp_count = 0
        for bill in data.get('cosponsoredLegislation', [])[:50]:  # Limit to first 50 to save time
            if bill.get('congress') == 119:
                bill_type = bill.get('type', '').lower()
                bill_num = bill.get('number')
                
                if is_transportation_bill(bill_type, bill_num):
                    transport_bills.append({
                        "number": f"{bill.get('type', '')}.{bill_num}",
                        "title": bill.get('title', 'No title'),
                        "relationship": "Cosponsor",
                        "url": bill.get('url', '')
                    })
                    cosp_count += 1
        
        print(f"  Cosponsored (transport): {cosp_count}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    all_bills[dist] = {
        "member": info['name'],
        "bills": transport_bills,
        "total": len(transport_bills)
    }
    
    time.sleep(1)

output_file = f"bills_transportation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(all_bills, f, indent=2)

total = sum(d['total'] for d in all_bills.values())

print("\n" + "=" * 70)
print("✅ COMPLETE - TRANSPORTATION BILLS ONLY")
print("=" * 70)
print(f"Saved: {output_file}")
print(f"Total transportation bills: {total}")
print()

