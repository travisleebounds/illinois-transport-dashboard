#!/usr/bin/env python3
"""
Fetch REAL bills from Congress.gov using the exact URL structure
Example: https://www.congress.gov/member/janice-schakowsky/S001145?q={"congress":"119","subject":"Transportation+and+Public+Works"}
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re

# Illinois Delegation - 119th Congress (2025-2027)
ILLINOIS_MEMBERS = [
    {"district": "IL-01", "name": "Jonathan Jackson", "bioguide": "J000308", "url_name": "jonathan-jackson"},
    {"district": "IL-02", "name": "Robin Kelly", "bioguide": "K000385", "url_name": "robin-kelly"},
    {"district": "IL-03", "name": "Delia Ramirez", "bioguide": "R000617", "url_name": "delia-ramirez"},
    {"district": "IL-04", "name": "Jesús García", "bioguide": "G000586", "url_name": "jesus-garcia"},
    {"district": "IL-05", "name": "Mike Quigley", "bioguide": "Q000023", "url_name": "mike-quigley"},
    {"district": "IL-06", "name": "Sean Casten", "bioguide": "C001117", "url_name": "sean-casten"},
    {"district": "IL-07", "name": "Danny Davis", "bioguide": "D000096", "url_name": "danny-davis"},
    {"district": "IL-08", "name": "Raja Krishnamoorthi", "bioguide": "K000391", "url_name": "raja-krishnamoorthi"},
    {"district": "IL-09", "name": "Jan Schakowsky", "bioguide": "S001145", "url_name": "janice-schakowsky"},
    {"district": "IL-10", "name": "Brad Schneider", "bioguide": "S001190", "url_name": "brad-schneider"},
    {"district": "IL-11", "name": "Bill Foster", "bioguide": "F000454", "url_name": "bill-foster"},
    {"district": "IL-12", "name": "Mike Bost", "bioguide": "B001295", "url_name": "mike-bost"},
    {"district": "IL-13", "name": "Nikki Budzinski", "bioguide": "B001316", "url_name": "nikki-budzinski"},
    {"district": "IL-14", "name": "Lauren Underwood", "bioguide": "U000040", "url_name": "lauren-underwood"},
    {"district": "IL-15", "name": "Mary Miller", "bioguide": "M001211", "url_name": "mary-miller"},
    {"district": "IL-16", "name": "Darin LaHood", "bioguide": "L000585", "url_name": "darin-lahood"},
    {"district": "IL-17", "name": "Eric Sorensen", "bioguide": "S001224", "url_name": "eric-sorensen"},
    
    # Senators
    {"district": "IL-SEN", "name": "Dick Durbin", "bioguide": "D000563", "url_name": "richard-durbin"},
    {"district": "IL-SEN", "name": "Tammy Duckworth", "bioguide": "D000622", "url_name": "tammy-duckworth"},
]

def fetch_member_bills(member):
    """
    Fetch transportation bills using exact Congress.gov URL structure
    """
    
    url = f"https://www.congress.gov/member/{member['url_name']}/{member['bioguide']}"
    params = {
        "q": json.dumps({
            "congress": "119",
            "subject": "Transportation and Public Works"
        })
    }
    
    print(f"\n{member['district']}: {member['name']}...")
    print(f"  URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        bills = []
        
        # Find all bill listings
        # Congress.gov uses <ol class="results_list"> for bill lists
        results_list = soup.find('ol', class_='results_list')
        
        if results_list:
            bill_items = results_list.find_all('li', class_='expanded')
            
            for item in bill_items:
                try:
                    # Extract bill number and link
                    heading = item.find('span', class_='result-heading')
                    if heading:
                        link = heading.find('a')
                        if link:
                            bill_number = link.text.strip()
                            bill_url = "https://www.congress.gov" + link['href']
                        else:
                            continue
                    else:
                        continue
                    
                    # Extract title
                    title_span = item.find('span', class_='result-title')
                    title = title_span.text.strip() if title_span else "No title available"
                    
                    # Extract sponsor info (to determine if authored or cosponsored)
                    sponsor_info = item.find('span', class_='result-item')
                    sponsor_text = sponsor_info.text.strip() if sponsor_info else ""
                    
                    # Determine relationship
                    if f"Sponsor: {member['name']}" in sponsor_text or f"Sponsor: Rep. {member['name']}" in sponsor_text:
                        relationship = "Sponsor"
                    else:
                        relationship = "Cosponsor"
                    
                    # Extract latest action
                    action_items = item.find_all('span', class_='result-item')
                    latest_action = ""
                    latest_date = ""
                    
                    for action in action_items:
                        text = action.text.strip()
                        if "Latest Action:" in text:
                            latest_action = text.replace("Latest Action:", "").strip()
                            # Try to extract date
                            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', latest_action)
                            if date_match:
                                latest_date = date_match.group(1)
                    
                    bills.append({
                        "bill_number": bill_number,
                        "title": title,
                        "relationship": relationship,
                        "latest_action": latest_action,
                        "latest_date": latest_date,
                        "url": bill_url,
                        "member": member['name'],
                        "district": member['district']
                    })
                    
                except Exception as e:
                    print(f"    Error parsing bill: {e}")
                    continue
        
        print(f"  ✅ Found {len(bills)} bills")
        
        # Show breakdown
        sponsors = [b for b in bills if b['relationship'] == 'Sponsor']
        cosponsors = [b for b in bills if b['relationship'] == 'Cosponsor']
        print(f"    Sponsored: {len(sponsors)}, Cosponsored: {len(cosponsors)}")
        
        return bills
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return []

def main():
    print("=" * 80)
    print("FETCHING REAL TRANSPORTATION BILLS FROM CONGRESS.GOV")
    print("119th Congress (2025-2027)")
    print("=" * 80)
    
    all_bills_by_district = {}
    all_bills_flat = []
    
    for member in ILLINOIS_MEMBERS:
        bills = fetch_member_bills(member)
        
        # Store by district
        if member['district'] not in all_bills_by_district:
            all_bills_by_district[member['district']] = []
        
        all_bills_by_district[member['district']].extend(bills)
        all_bills_flat.extend(bills)
        
        # Be nice to Congress.gov
        time.sleep(2)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save by district
    output_file = f"bills_by_district_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(all_bills_by_district, f, indent=2)
    
    # Save flat list
    flat_file = f"bills_all_{timestamp}.json"
    with open(flat_file, 'w') as f:
        json.dump(all_bills_flat, f, indent=2)
    
    print("\n" + "=" * 80)
    print("FETCH COMPLETE")
    print("=" * 80)
    print(f"\nSaved to:")
    print(f"  By district: {output_file}")
    print(f"  All bills: {flat_file}")
    print(f"\nTotal bills: {len(all_bills_flat)}")
    print(f"Districts covered: {len(all_bills_by_district)}")
    
    # Summary by district
    print("\n" + "-" * 80)
    print("SUMMARY BY DISTRICT:")
    print("-" * 80)
    
    for district in sorted(all_bills_by_district.keys()):
        bills = all_bills_by_district[district]
        if bills:
            member_name = bills[0]['member']
            sponsors = len([b for b in bills if b['relationship'] == 'Sponsor'])
            cosponsors = len([b for b in bills if b['relationship'] == 'Cosponsor'])
            print(f"{district} ({member_name}): {len(bills)} total (S: {sponsors}, C: {cosponsors})")
        else:
            print(f"{district}: No bills found")
    
    print("\n✅ Done! Use this data in the dashboard.\n")

if __name__ == "__main__":
    main()
