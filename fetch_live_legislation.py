#!/usr/bin/env python3
"""
Fetch LIVE legislation data from Congress.gov for all Illinois members
Uses the same URL structure as the Garcia link
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# Illinois Delegation - 119th Congress (2025-2027)
ILLINOIS_DELEGATION = {
    "IL-01": {"bioguide": "J000308", "name": "Jonathan Jackson", "chamber": "house"},
    "IL-02": {"bioguide": "K000385", "name": "Robin Kelly", "chamber": "house"},
    "IL-03": {"bioguide": "R000617", "name": "Delia Ramirez", "chamber": "house"},
    "IL-04": {"bioguide": "G000586", "name": "Jesús García", "chamber": "house"},
    "IL-05": {"bioguide": "Q000023", "name": "Mike Quigley", "chamber": "house"},
    "IL-06": {"bioguide": "C001117", "name": "Sean Casten", "chamber": "house"},
    "IL-07": {"bioguide": "D000096", "name": "Danny Davis", "chamber": "house"},
    "IL-08": {"bioguide": "K000391", "name": "Raja Krishnamoorthi", "chamber": "house"},
    "IL-09": {"bioguide": "S001145", "name": "Jan Schakowsky", "chamber": "house"},
    "IL-10": {"bioguide": "S001190", "name": "Brad Schneider", "chamber": "house"},
    "IL-11": {"bioguide": "F000454", "name": "Bill Foster", "chamber": "house"},
    "IL-12": {"bioguide": "B001295", "name": "Mike Bost", "chamber": "house"},
    "IL-13": {"bioguide": "B001316", "name": "Nikki Budzinski", "chamber": "house"},
    "IL-14": {"bioguide": "U000040", "name": "Lauren Underwood", "chamber": "house"},
    "IL-15": {"bioguide": "M001211", "name": "Mary Miller", "chamber": "house"},
    "IL-16": {"bioguide": "L000585", "name": "Darin LaHood", "chamber": "house"},
    "IL-17": {"bioguide": "S001224", "name": "Eric Sorensen", "chamber": "house"},
    
    # Senators
    "IL-SEN1": {"bioguide": "D000563", "name": "Dick Durbin", "chamber": "senate"},
    "IL-SEN2": {"bioguide": "D000622", "name": "Tammy Duckworth", "chamber": "senate"},
}

def fetch_member_bills(bioguide, name, congress="119"):
    """
    Fetch transportation bills for a member using Congress.gov structure
    URL pattern: https://www.congress.gov/member/{name}/{bioguide}?q={"subject":"Transportation+and+Public+Works","congress":"119"}
    """
    
    # Format name for URL (lowercase, replace spaces with dashes)
    url_name = name.lower().replace(" ", "-").replace("á", "a").replace("é", "e")
    
    # Build URL with transportation filter
    base_url = f"https://www.congress.gov/member/{url_name}/{bioguide}"
    params = {
        "q": json.dumps({
            "subject": "Transportation and Public Works",
            "congress": congress
        })
    }
    
    print(f"Fetching: {name} ({bioguide})...")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse bills from the results
        bills = []
        
        # Find all bill items (this will need to be adjusted based on actual HTML structure)
        bill_items = soup.find_all('li', class_='expanded')
        
        for item in bill_items[:10]:  # Limit to 10 most recent
            try:
                # Extract bill number
                bill_link = item.find('span', class_='result-heading').find('a')
                bill_number = bill_link.text.strip() if bill_link else "Unknown"
                bill_url = "https://www.congress.gov" + bill_link['href'] if bill_link else ""
                
                # Extract title
                title_elem = item.find('span', class_='result-title')
                title = title_elem.text.strip() if title_elem else "No title"
                
                # Extract latest action
                action_elem = item.find('span', class_='result-item')
                latest_action = action_elem.text.strip() if action_elem else "No action info"
                
                bills.append({
                    "bill_number": bill_number,
                    "title": title,
                    "latest_action": latest_action,
                    "url": bill_url,
                    "sponsor": name,
                    "retrieved_at": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"  Error parsing bill item: {e}")
                continue
        
        print(f"  Found {len(bills)} transportation bills")
        return bills
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def fetch_all_illinois_members():
    """Fetch transportation bills for all Illinois delegation members"""
    
    print("=" * 80)
    print("FETCHING LIVE CONGRESS.GOV DATA - ALL ILLINOIS MEMBERS")
    print("=" * 80)
    print()
    
    all_data = {}
    
    for district, info in ILLINOIS_DELEGATION.items():
        bills = fetch_member_bills(info['bioguide'], info['name'])
        
        all_data[district] = {
            "member": info['name'],
            "bioguide": info['bioguide'],
            "chamber": info['chamber'],
            "bills": bills,
            "count": len(bills)
        }
        
        # Be nice to Congress.gov servers
        time.sleep(2)
    
    # Save results
    output_file = f"live_legislation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print()
    print("=" * 80)
    print("FETCH COMPLETE")
    print("=" * 80)
    print(f"Saved to: {output_file}")
    print()
    
    # Summary
    total_bills = sum(d['count'] for d in all_data.values())
    print(f"Total members: {len(all_data)}")
    print(f"Total transportation bills: {total_bills}")
    print()
    
    return all_data

if __name__ == "__main__":
    data = fetch_all_illinois_members()
