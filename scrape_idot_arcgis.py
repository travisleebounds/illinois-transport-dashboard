#!/usr/bin/env python3
"""
Illinois IDOT ArcGIS Construction/Closure Data Scraper
Fetches real construction projects and road closures from IDOT's ArcGIS
Then maps them to congressional districts
"""

import requests
import json
from datetime import datetime
import time

# IDOT ArcGIS REST API endpoints
ARCGIS_ENDPOINTS = {
    'construction': 'https://gis.dot.illinois.gov/arcgis/rest/services/Transportation/Construction/MapServer/0/query',
    'closures': 'https://gis.dot.illinois.gov/arcgis/rest/services/Transportation/RoadClosures/MapServer/0/query',
    'incidents': 'https://gis.dot.illinois.gov/arcgis/rest/services/Transportation/Incidents/MapServer/0/query'
}

# Congressional District boundaries (simplified - we have the full geojson)
# Format: district_id -> (min_lat, max_lat, min_lon, max_lon) bounding box
DISTRICT_BOUNDS = {
    'IL-01': (41.64, 41.81, -87.71, -87.52),  # Chicago South
    'IL-02': (41.45, 41.64, -87.80, -87.55),  # South suburbs
    'IL-03': (41.85, 41.99, -87.95, -87.65),  # Northwest Chicago
    'IL-04': (41.70, 41.90, -87.85, -87.60),  # Southwest Chicago
    'IL-05': (41.90, 42.05, -87.80, -87.60),  # North Chicago
    'IL-06': (41.70, 41.95, -88.30, -87.90),  # Western suburbs
    'IL-07': (41.80, 41.95, -87.75, -87.55),  # West Chicago
    'IL-08': (42.00, 42.25, -88.40, -87.90),  # Northwest suburbs
    'IL-09': (42.00, 42.20, -87.85, -87.55),  # North suburbs
    'IL-10': (42.15, 42.50, -88.20, -87.65),  # Lake County
    'IL-11': (41.35, 41.70, -88.50, -87.85),  # Aurora/Joliet
    'IL-12': (37.50, 38.80, -90.25, -88.50),  # Southern Illinois
    'IL-13': (38.80, 40.50, -89.50, -87.50),  # Central Illinois
    'IL-14': (41.70, 42.30, -88.90, -88.20),  # Far west/north suburbs
    'IL-15': (38.90, 40.50, -88.50, -87.50),  # Eastern Illinois
    'IL-16': (40.50, 42.50, -90.50, -88.50),  # Peoria/Rockford
    'IL-17': (40.30, 42.50, -91.50, -89.50),  # Quad Cities/Western
}

def query_arcgis(endpoint_url, where_clause="1=1", max_records=1000):
    """
    Query IDOT ArcGIS REST API
    """
    params = {
        'where': where_clause,
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'json',
        'resultRecordCount': max_records,
        'outSR': '4326'  # WGS84 coordinate system
    }
    
    try:
        response = requests.get(endpoint_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'features' in data:
            return data['features']
        else:
            print(f"   ⚠️  No features returned. Response keys: {data.keys()}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON decode error: {e}")
        return []

def point_in_bounds(lat, lon, bounds):
    """Check if a point is within bounding box"""
    min_lat, max_lat, min_lon, max_lon = bounds
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

def assign_to_district(lat, lon):
    """Assign a lat/lon to a congressional district"""
    for district, bounds in DISTRICT_BOUNDS.items():
        if point_in_bounds(lat, lon, bounds):
            return district
    return None

def extract_feature_data(feature, data_type):
    """Extract relevant fields from ArcGIS feature"""
    attrs = feature.get('attributes', {})
    geom = feature.get('geometry', {})
    
    # Get coordinates
    lat, lon = None, None
    if 'x' in geom and 'y' in geom:
        lon, lat = geom['x'], geom['y']
    elif 'paths' in geom and geom['paths']:
        # Line geometry - use midpoint
        coords = geom['paths'][0]
        if coords:
            mid = len(coords) // 2
            lon, lat = coords[mid]
    
    if not lat or not lon:
        return None
    
    # Common fields
    common = {
        'lat': lat,
        'lon': lon,
        'district': assign_to_district(lat, lon)
    }
    
    if data_type == 'construction':
        return {
            **common,
            'route': attrs.get('ROUTE', attrs.get('RoadName', 'Unknown')),
            'location': attrs.get('LOCATION', attrs.get('Description', 'Unknown')),
            'type': attrs.get('WORKTYPE', attrs.get('ProjectType', 'Construction')),
            'status': attrs.get('STATUS', attrs.get('ProjectStatus', 'Active')),
            'description': attrs.get('DESCRIPTION', attrs.get('ProjectName', '')),
            'budget': attrs.get('BUDGET', attrs.get('EstimatedCost', '')),
            'timeline': attrs.get('TIMELINE', ''),
            'start_date': attrs.get('START_DATE', ''),
            'end_date': attrs.get('END_DATE', ''),
            'contractor': attrs.get('CONTRACTOR', ''),
            'url': 'https://www.gettingaroundillinois.com/'
        }
    
    elif data_type == 'closure':
        return {
            **common,
            'route': attrs.get('ROUTE', attrs.get('RoadName', 'Unknown')),
            'location': attrs.get('LOCATION', attrs.get('Description', 'Unknown')),
            'type': attrs.get('CLOSURETYPE', attrs.get('Type', 'Road Closure')),
            'status': attrs.get('STATUS', 'Active'),
            'description': attrs.get('DESCRIPTION', attrs.get('Reason', '')),
            'start_date': attrs.get('START_DATE', ''),
            'end_date': attrs.get('END_DATE', ''),
            'url': 'https://www.gettingaroundillinois.com/'
        }
    
    return common

def scrape_idot_data():
    """
    Main scraper function
    """
    print("=" * 80)
    print("IDOT ArcGIS DATA SCRAPER")
    print("=" * 80)
    print("\nFetching data from IDOT ArcGIS servers...")
    
    results = {
        'metadata': {
            'scraped_date': datetime.now().isoformat(),
            'source': 'IDOT ArcGIS REST Services',
            'note': 'Real-time construction and closure data'
        },
        'by_district': {}
    }
    
    # Initialize districts
    for district in DISTRICT_BOUNDS.keys():
        results['by_district'][district] = {
            'construction': [],
            'closures': []
        }
    
    # Scrape Construction Projects
    print("\n📊 Fetching construction projects...")
    construction_features = query_arcgis(ARCGIS_ENDPOINTS['construction'])
    print(f"   Found {len(construction_features)} construction records")
    
    for feature in construction_features:
        data = extract_feature_data(feature, 'construction')
        if data and data['district']:
            results['by_district'][data['district']]['construction'].append(data)
    
    time.sleep(1)  # Be nice to the API
    
    # Scrape Road Closures
    print("\n🚧 Fetching road closures...")
    closure_features = query_arcgis(ARCGIS_ENDPOINTS['closures'])
    print(f"   Found {len(closure_features)} closure records")
    
    for feature in closure_features:
        data = extract_feature_data(feature, 'closure')
        if data and data['district']:
            results['by_district'][data['district']]['closures'].append(data)
    
    # Summary
    print("\n" + "=" * 80)
    print("RESULTS BY DISTRICT")
    print("=" * 80)
    
    total_construction = 0
    total_closures = 0
    
    for district in sorted(results['by_district'].keys()):
        data = results['by_district'][district]
        const_count = len(data['construction'])
        closure_count = len(data['closures'])
        
        total_construction += const_count
        total_closures += closure_count
        
        if const_count > 0 or closure_count > 0:
            print(f"\n{district}:")
            print(f"  🏗️  Construction: {const_count}")
            print(f"  🚧 Closures: {closure_count}")
            
            # Show samples
            if const_count > 0:
                sample = data['construction'][0]
                print(f"     Sample: {sample['route']} - {sample['location']}")
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL: {total_construction} construction, {total_closures} closures")
    print(f"{'=' * 80}")
    
    # Save to JSON
    output_file = f'idot_arcgis_data_{datetime.now():%Y%m%d_%H%M%S}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Saved to: {output_file}")
    
    return results

def main():
    """Main execution"""
    print("\n🚀 Starting IDOT ArcGIS scraper...")
    print("\nThis will fetch real construction and closure data from IDOT")
    print("and assign them to congressional districts.\n")
    
    try:
        results = scrape_idot_data()
        
        print("\n" + "=" * 80)
        print("✅ SCRAPING COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review the JSON file")
        print("  2. Copy to dashboard directory")
        print("  3. Update dashboard to use this data")
        print("\nThe dashboard will automatically load the most recent idot_arcgis_data_*.json file")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
