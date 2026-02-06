import re
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import subprocess
import os
import json
import glob
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="IDOT Ultimate Dashboard", page_icon="🚗", layout="wide")

st.markdown("""
<style>
    .preview-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #1f77b4;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 15px;
        line-height: 1.6;
    }
    .preview-box h4 {
        margin-top: 0;
        color: #1f77b4;
        font-size: 18px;
        font-weight: 600;
    }
    .preview-box p {
        margin: 10px 0;
        color: #333;
    }
    .preview-box strong {
        color: #1f77b4;
        font-weight: 600;
    }
    .preview-box a {
        color: #1f77b4;
        font-weight: 600;
        text-decoration: none;
        font-size: 16px;
    }
    .preview-box a:hover {
        text-decoration: underline;
    }
    .clickable-item {
        cursor: pointer;
        padding: 8px;
        margin: 5px 0;
        border-radius: 3px;
        background-color: #ffffff;
        border: 1px solid #ddd;
    }
    .clickable-item:hover {
        background-color: #e8f4f8;
    }
    .district-ref-image {
        border: 2px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center;">🚗 IDOT Ultimate Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Load real bill data if available
def load_real_bills():
    files = glob.glob("bills_*.json")
    if files:
        latest = sorted(files)[-1]
        with open(latest, 'r') as f:
            return json.load(f)
    return {}

real_bills_data = load_real_bills()

# Load district boundaries
if os.path.exists('il_districts_boundaries.py'):
    exec(open('il_districts_boundaries.py').read())
else:
    DISTRICT_BOUNDARIES = {}

# Load dynamic IDOT data if available
def load_idot_data():
    """Load IDOT construction/closure data from JSON if available"""
    try:
        # Look for most recent IDOT data file
        idot_files = glob.glob("idot_dynamic_*.json")
        if idot_files:
            latest = sorted(idot_files)[-1]
            with open(latest, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

idot_live_data = load_idot_data()

# District data with BOUNDARIES
DISTRICTS = {
    "IL-01": {
        "rep": "Jonathan Jackson", "party": "D", "area": "Chicago South Side", 
        "lat": 41.7276, "lon": -87.6243,
        "committees": ["Agriculture", "Foreign Affairs"],
        "boundary": [[41.6447, -87.7105], [41.6447, -87.5241], [41.8085, -87.5241], [41.8085, -87.7105], [41.6447, -87.7105]],
        "closures": [{"route": "I-94", "location": "95th Street", "type": "Lane closure", "status": "Active", "lat": 41.7220, "lon": -87.6246, "description": "Temporary lane closures for bridge work", "url": "https://www.gettingaroundillinois.com/"}],
        "construction": [{"route": "I-94", "location": "95th Street", "type": "Bridge replacement", "status": "Active", "lat": 41.7220, "lon": -87.6246, "description": "Bridge deck replacement and lane reconfiguration project - 18 month timeline", "url": "https://www.gettingaroundillinois.com/", "budget": "$8.5M", "timeline": "2024-2026"}],
        "grants": [{"program": "RAISE", "amount": 15000000, "project": "Red Line Extension", "lat": 41.7220, "lon": -87.6246, "description": "CTA Red Line extension to 130th Street", "url": "https://www.transportation.gov/RAISEgrants"}]
    },
    
    "IL-02": {
        "rep": "Robin Kelly", "party": "D", "area": "South suburbs", 
        "lat": 41.5992, "lon": -87.6772,
        "committees": ["Energy and Commerce", "Oversight"],
        "boundary": [[41.4500, -87.8000], [41.4500, -87.5500], [41.6447, -87.5500], [41.6447, -87.8000], [41.4500, -87.8000]],
        "closures": [{"route": "I-57", "location": "Matteson", "type": "Lane shifts", "status": "Planned", "lat": 41.5039, "lon": -87.7323, "description": "Temporary lane shifts during resurfacing", "url": "https://idot.illinois.gov/"}],
        "construction": [{"route": "I-57", "location": "Matteson", "type": "Resurfacing", "status": "Planned Q2 2026", "lat": 41.5039, "lon": -87.7323, "description": "Interstate resurfacing and shoulder widening project", "url": "https://idot.illinois.gov/", "budget": "$12M", "timeline": "2026-2027"}],
        "grants": [{"program": "INFRA", "amount": 12500000, "project": "Lincoln Highway Corridor", "lat": 41.5039, "lon": -87.7323, "description": "Safety and capacity improvements on US-30", "url": "https://www.transportation.gov/INFRAgrants"}]
    },
    
    "IL-03": {
        "rep": "Delia Ramirez", "party": "D", "area": "Northwest Chicago", 
        "lat": 41.9208, "lon": -87.8084,
        "committees": ["Homeland Security", "Oversight"],
        "boundary": [[41.8500, -87.9500], [41.8500, -87.6500], [41.9900, -87.6500], [41.9900, -87.9500], [41.8500, -87.9500]],
        "closures": [{"route": "I-90", "location": "Kennedy Expressway", "type": "Weekend closures", "status": "Active", "lat": 41.9742, "lon": -87.9073, "description": "Weekend lane closures for bridge repairs", "url": "https://www.gettingaroundillinois.com/"}],
        "construction": [{"route": "I-90", "location": "Kennedy Expressway", "type": "Bridge repair", "status": "Active", "lat": 41.9742, "lon": -87.9073, "description": "Structural repairs to Kennedy Expressway bridges - multi-year project", "url": "https://www.gettingaroundillinois.com/", "budget": "$45M", "timeline": "2024-2027"}],
        "grants": [{"program": "CRISI", "amount": 35000000, "project": "Milwaukee District North Line", "lat": 41.9742, "lon": -87.9073, "description": "Metra line capacity and safety upgrades", "url": "https://railroads.dot.gov/grants-loans/crisi"}]
    },
    
    "IL-04": {
        "rep": "Jesús García", "party": "D", "area": "Southwest Chicago", 
        "lat": 41.8370, "lon": -87.7446,
        "committees": ["Financial Services", "Transportation"],
        "boundary": [[41.7000, -87.8500], [41.7000, -87.6000], [41.9000, -87.6000], [41.9000, -87.8500], [41.7000, -87.8500]],
        "closures": [{"route": "Cicero Ave", "location": "26th Street", "type": "Complete streets", "status": "Design", "lat": 41.8370, "lon": -87.7446, "description": "Complete streets redesign with transit priority lanes", "url": "https://www.chicago.gov/"}], "construction": [],
        "grants": [{"program": "RAISE", "amount": 18000000, "project": "Cicero Multimodal Corridor", "lat": 41.8370, "lon": -87.7446, "description": "Multimodal improvements on Cicero Avenue", "url": "https://www.transportation.gov/RAISEgrants"}]
    },
    
    "IL-05": {
        "rep": "Mike Quigley", "party": "D", "area": "North Chicago", 
        "lat": 41.9534, "lon": -87.6981,
        "committees": ["Appropriations", "Intelligence"],
        "boundary": [[41.9000, -87.8000], [41.9000, -87.6000], [42.0500, -87.6000], [42.0500, -87.8000], [41.9000, -87.8000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-06": {
        "rep": "Sean Casten", "party": "D", "area": "Western suburbs", 
        "lat": 41.8256, "lon": -88.0814,
        "committees": ["Financial Services", "Science"],
        "boundary": [[41.7000, -88.3000], [41.7000, -87.9000], [41.9500, -87.9000], [41.9500, -88.3000], [41.7000, -88.3000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-07": {
        "rep": "Danny Davis", "party": "D", "area": "West Chicago", 
        "lat": 41.8781, "lon": -87.6298,
        "committees": ["Ways and Means"],
        "boundary": [[41.8000, -87.7500], [41.8000, -87.5500], [41.9500, -87.5500], [41.9500, -87.7500], [41.8000, -87.7500]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-08": {
        "rep": "Raja Krishnamoorthi", "party": "D", "area": "Northwest suburbs", 
        "lat": 42.0883, "lon": -88.1357,
        "committees": ["Oversight", "Intelligence"],
        "boundary": [[42.0000, -88.4000], [42.0000, -87.9000], [42.2500, -87.9000], [42.2500, -88.4000], [42.0000, -88.4000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-09": {
        "rep": "Jan Schakowsky", "party": "D", "area": "North suburbs", 
        "lat": 42.0450, "lon": -87.6877,
        "committees": ["Energy and Commerce", "Budget"],
        "boundary": [[42.0000, -87.8500], [42.0000, -87.5500], [42.2000, -87.5500], [42.2000, -87.8500], [42.0000, -87.8500]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-10": {
        "rep": "Brad Schneider", "party": "D", "area": "Lake County", 
        "lat": 42.3369, "lon": -87.8658,
        "committees": ["Ways and Means", "Foreign Affairs"],
        "boundary": [[42.1500, -88.2000], [42.1500, -87.6500], [42.5000, -87.6500], [42.5000, -88.2000], [42.1500, -88.2000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-11": {
        "rep": "Bill Foster", "party": "D", "area": "Aurora/Joliet", 
        "lat": 41.5253, "lon": -88.1473,
        "committees": ["Financial Services", "Science"],
        "boundary": [[41.3500, -88.5000], [41.3500, -87.8500], [41.7000, -87.8500], [41.7000, -88.5000], [41.3500, -88.5000]],
        "closures": [{"route": "I-80", "location": "Joliet", "type": "Freight facility", "status": "Construction", "lat": 41.5250, "lon": -88.0817, "description": "Grade separations and access improvements for intermodal facility", "url": "https://www.transportation.gov/INFRAgrants"}], "construction": [],
        "grants": [{"program": "INFRA", "amount": 45000000, "project": "I-80 Intermodal Access", "lat": 41.5250, "lon": -88.0817, "description": "Freight corridor improvements and intermodal connections", "url": "https://www.transportation.gov/INFRAgrants"}]
    },
    
    "IL-12": {
        "rep": "Mike Bost", "party": "R", "area": "Southern Illinois", 
        "lat": 38.1406, "lon": -89.2645,
        "committees": ["Transportation", "Veterans Affairs"],
        "boundary": [[37.0000, -90.5000], [37.0000, -88.0000], [38.5000, -88.0000], [38.5000, -90.5000], [37.0000, -90.5000]],
        "closures": [], "construction": [],
        "grants": [{"program": "RAISE", "amount": 22000000, "project": "MetroLink Eastside Center", "lat": 38.6247, "lon": -90.1848, "description": "New transit center with parking and bus connections", "url": "https://www.transportation.gov/RAISEgrants"}]
    },
    
    "IL-13": {
        "rep": "Nikki Budzinski", "party": "D", "area": "Central Illinois", 
        "lat": 39.8403, "lon": -88.9548,
        "committees": ["Agriculture", "Transportation"],
        "boundary": [[39.5000, -89.5000], [39.5000, -88.0000], [40.3000, -88.0000], [40.3000, -89.5000], [39.5000, -89.5000]],
        "closures": [
            {"route": "US-36", "location": "Decatur-Springfield", "type": "Bridge replacement", "status": "Active", "lat": 39.8403, "lon": -89.6515, "description": "Full bridge replacement on US-36 corridor", "url": "https://idot.illinois.gov/"},
            {"route": "IL-29", "location": "Macon County", "type": "Resurfacing", "status": "Active", "lat": 39.9064, "lon": -88.9548, "description": "Resurfacing and shoulder improvements", "url": "https://idot.illinois.gov/"}
        ],
        "grants": [
            {"program": "RAISE", "amount": 15000000, "project": "Decatur Multi-Modal Center", "lat": 39.8403, "lon": -89.6515, "description": "Intermodal facility connecting Amtrak, bus, and bike infrastructure", "url": "https://www.transportation.gov/RAISEgrants"},
            {"program": "INFRA", "amount": 25000000, "project": "I-72 Freight Corridor", "lat": 39.9064, "lon": -88.6548, "description": "Highway improvements for agricultural freight movement", "url": "https://www.transportation.gov/INFRAgrants"}
        ]
    },
    
    "IL-14": {
        "rep": "Lauren Underwood", "party": "D", "area": "Far west suburbs", 
        "lat": 41.7606, "lon": -88.5855,
        "committees": ["Appropriations", "Veterans Affairs"],
        "boundary": [[41.5000, -88.9000], [41.5000, -88.3000], [41.9500, -88.3000], [41.9500, -88.9000], [41.5000, -88.9000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-15": {
        "rep": "Mary Miller", "party": "R", "area": "Eastern Illinois", 
        "lat": 40.1164, "lon": -88.2434,
        "committees": ["Agriculture", "Education"],
        "boundary": [[39.0000, -88.5000], [39.0000, -87.5000], [40.5000, -87.5000], [40.5000, -88.5000], [39.0000, -88.5000]],
        "closures": [], "construction": [], "grants": []
    },
    
    "IL-16": {
        "rep": "Darin LaHood", "party": "R", "area": "Peoria/Rockford", 
        "lat": 40.6936, "lon": -89.5890,
        "committees": ["Ways and Means"],
        "boundary": [[40.3000, -90.5000], [40.3000, -89.0000], [42.0000, -89.0000], [42.0000, -90.5000], [40.3000, -90.5000]],
        "closures": [], "construction": [],
        "grants": [{"program": "RAISE", "amount": 20000000, "project": "Peoria Warehouse District", "lat": 40.6936, "lon": -89.5890, "description": "Roadway and river port access improvements", "url": "https://www.transportation.gov/RAISEgrants"}]
    },
    
    "IL-17": {
        "rep": "Eric Sorensen", "party": "D", "area": "Quad Cities", 
        "lat": 41.5067, "lon": -90.5151,
        "committees": ["Agriculture", "Science"],
        "boundary": [[40.5000, -91.5000], [40.5000, -89.5000], [42.5000, -89.5000], [42.5000, -91.5000], [40.5000, -91.5000]],
        "closures": [], "construction": [],
        "grants": [{"program": "Port Infrastructure", "amount": 28000000, "project": "Mississippi River Lock", "lat": 41.5067, "lon": -90.5780, "description": "Port infrastructure and rail access improvements", "url": "https://www.maritime.dot.gov/PIDPgrants"}]
    },
}

# Session state
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None

# Navigation
view = st.radio("Navigation", ["🗺️ Statewide Map", "📍 District View", "🚧 Live IDOT Map", "🤖 AV Policy"], horizontal=True)

# STATEWIDE MAP
if view == "🗺️ Statewide Map":
    st.header("Illinois - All 17 Congressional Districts")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts", "17")
    col2.metric("Democrats", "14")
    col3.metric("Republicans", "3")
    total_grants = sum(sum(g['amount'] for g in d.get('grants', [])) for d in DISTRICTS.values())
    col4.metric("Total Grants", f"${total_grants/1e6:.0f}M")
    
    # Create map with ALL district boundaries
    m = folium.Map(location=[40.0, -89.0], zoom_start=7)
    
    for district_id, info in DISTRICTS.items():
        color = '#4A90E2' if info['party'] == 'D' else '#E24A4A'
        
        # Use REAL GeoJSON boundaries if available
        if district_id in DISTRICT_BOUNDARIES:
            boundary_data = DISTRICT_BOUNDARIES[district_id]
            coords = boundary_data['geometry']['coordinates'][0]
            # Convert from [lon, lat] to [lat, lon] for Folium
            folium_coords = [[lat, lon] for lon, lat in coords]
        else:
            # Fallback to simple boundary if GeoJSON not available
            folium_coords = info.get('boundary', [])
        
        # Add district BOUNDARY polygon
        folium.Polygon(
            locations=folium_coords,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.15,
            weight=2,
            popup=f"<b>{district_id}: {info['rep']} ({info['party']})</b><br>{info['area']}"
        ).add_to(m)
        
        # Add district center marker
        n_closures = len(info.get('closures', []))
        n_grants = len(info.get('grants', []))
        grant_total = sum(g['amount'] for g in info.get('grants', []))
        
        popup = f"<b>{district_id}: {info['rep']} ({info['party']})</b><br>{info['area']}<br><br>🚧 Closures: {n_closures}<br>💰 Grants: ${grant_total:,}"
        
        folium.Marker(
            [info['lat'], info['lon']],
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"{district_id}: {info['rep']}",
            icon=folium.Icon(color='blue' if info['party'] == 'D' else 'red', icon='info-sign')
        ).add_to(m)
        
        # Add project markers
        for closure in info.get('closures', []):
            folium.CircleMarker([closure['lat'], closure['lon']], radius=6, color='orange', fill=True, popup=f"🚧 {closure['route']}").add_to(m)
        
        for grant in info.get('grants', []):
            folium.CircleMarker([grant['lat'], grant['lon']], radius=8, color='green', fill=True, popup=f"💰 ${grant['amount']:,}").add_to(m)
    
    folium_static(m, width=1400, height=600)
    
    st.markdown("---")
    st.subheader("Click a District")
    
    cols = st.columns(6)
    for idx, district_id in enumerate(sorted(DISTRICTS.keys())):
        info = DISTRICTS[district_id]
        if cols[idx % 6].button(f"{district_id}\n{info['rep'][:15]}", key=f"btn_{district_id}"):
            st.session_state.selected_district = district_id
            st.rerun()

# DISTRICT VIEW
elif view == "📍 District View":
    st.sidebar.title("Select District")
    for district_id in sorted(DISTRICTS.keys()):
        info = DISTRICTS[district_id]
        if st.sidebar.button(f"{district_id}: {info['rep']}", key=f"side_{district_id}", use_container_width=True):
            st.session_state.selected_district = district_id
            st.session_state.selected_item = None
    
    if st.session_state.selected_district:
        district = st.session_state.selected_district
        info = DISTRICTS[district].copy()  # Make a copy to avoid modifying original
        
        # Merge in live IDOT data if available
        if district in idot_live_data:
            live_data = idot_live_data[district]
            # Append live closures and construction to existing data
            info['closures'] = info.get('closures', []) + live_data.get('closures', [])
            info['construction'] = info.get('construction', []) + live_data.get('construction', [])
        
        # Two column layout: Info on left, Reference Map on right
        col_info, col_map_ref = st.columns([2, 1])
        
        with col_info:
            st.header(f"{district}: {info['rep']} ({info['party']})")
            st.markdown(f"**Area:** {info['area']}")
            st.markdown(f"**Committees:** {', '.join(info['committees'])}")
        
        with col_map_ref:
            # Display reference map image
            img_path = f'district_images/{district}.png'
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, caption=f"{district} Location", use_container_width=True)
            else:
                st.info("📍 Reference map coming soon")
        
        # Get real bills if available
        district_bills = real_bills_data.get(district, {}).get('bills', [])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Closures", len(info.get('closures', [])))
        col2.metric("Construction", len(info.get('construction', [])))
        col3.metric("Grants", f"${sum(g['amount'] for g in info.get('grants', []))/1e6:.1f}M")
        col4.metric("Bills", len(district_bills))
        
        st.markdown("---")
        
        # District map WITH REAL BOUNDARY
        # Use real GeoJSON boundary if available
        if district in DISTRICT_BOUNDARIES:
            boundary_data = DISTRICT_BOUNDARIES[district]
            coords = boundary_data['geometry']['coordinates'][0]
            # Calculate center from coordinates
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            # Convert to Folium format
            folium_coords = [[lat, lon] for lon, lat in coords]
        else:
            # Fallback to info location and simple boundary
            center_lat = info['lat']
            center_lon = info['lon']
            folium_coords = info.get('boundary', [])
        
        dm = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add boundary polygon with proper colors
        color = '#4A90E2' if info['party'] == 'D' else '#E24A4A'
        folium.Polygon(
            locations=folium_coords,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.2,
            weight=3,
            popup=f"<b>{district} Boundary</b>"
        ).add_to(dm)
        
        # Add markers
        for closure in info.get('closures', []):
            folium.Marker([closure['lat'], closure['lon']], icon=folium.Icon(color='orange', icon='road', prefix='fa'), popup=f"🚧 {closure['route']}").add_to(dm)
        
        for grant in info.get('grants', []):
            folium.Marker([grant['lat'], grant['lon']], icon=folium.Icon(color='green', icon='dollar', prefix='fa'), popup=f"💰 ${grant['amount']:,}").add_to(dm)
        
        folium_static(dm, width=1400, height=500)
        
        st.markdown("---")
        
        # Tabs with CLICKABLE items
        tab1, tab2, tab3, tab4 = st.tabs(["🚧 Closures", "🏗️ Construction", "💰 Grants", "📜 Legislation"])
        
        with tab1:
            if info.get('closures'):
                st.markdown("**Click any item for details:**")
                for idx, closure in enumerate(info['closures']):
                    if st.button(f"🚧 {closure['route']} - {closure['location']} ({closure['status']})", key=f"closure_{idx}", use_container_width=True):
                        st.session_state.selected_item = ('closure', idx)
                
                # Preview box
                if st.session_state.selected_item and st.session_state.selected_item[0] == 'closure':
                    idx = st.session_state.selected_item[1]
                    c = info['closures'][idx]
                    st.markdown(f"""
                    <div class="preview-box">
                        <h4>🚧 {c['route']} - {c['location']}</h4>
                        <p><strong>Type:</strong> {c['type']}</p>
                        <p><strong>Status:</strong> {c['status']}</p>
                        <p><strong>Description:</strong> {c['description']}</p>
                        <p><a href="{c['url']}" target="_blank">🔗 View Source</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active closures")
        
        with tab2:
            if info.get('construction'):
                st.markdown("**Click any item for details:**")
                for idx, construction in enumerate(info['construction']):
                    if st.button(f"🏗️ {construction['route']} - {construction['location']} ({construction['status']})", key=f"construction_{idx}", use_container_width=True):
                        st.session_state.selected_item = ('construction', idx)
                
                # Preview box
                if st.session_state.selected_item and st.session_state.selected_item[0] == 'construction':
                    idx = st.session_state.selected_item[1]
                    c = info['construction'][idx]
                    st.markdown(f"""
                    <div class="preview-box">
                        <h4>🏗️ {c['route']} - {c['location']}</h4>
                        <p><strong>Type:</strong> {c['type']}</p>
                        <p><strong>Status:</strong> {c['status']}</p>
                        <p><strong>Budget:</strong> {c.get('budget', 'N/A')}</p>
                        <p><strong>Timeline:</strong> {c.get('timeline', 'N/A')}</p>
                        <p><strong>Description:</strong> {c['description']}</p>
                        <p><a href="{c['url']}" target="_blank">🔗 View Project Details</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active construction projects")
        
        with tab3:
            if info.get('grants'):
                st.markdown("**Click any item for details:**")
                for idx, grant in enumerate(info['grants']):
                    if st.button(f"💰 {grant['program']}: ${grant['amount']:,} - {grant['project']}", key=f"grant_{idx}", use_container_width=True):
                        st.session_state.selected_item = ('grant', idx)
                
                # Preview box
                if st.session_state.selected_item and st.session_state.selected_item[0] == 'grant':
                    idx = st.session_state.selected_item[1]
                    g = info['grants'][idx]
                    st.markdown(f"""
                    <div class="preview-box">
                        <h4>💰 {g['program']}: ${g['amount']:,}</h4>
                        <p><strong>Project:</strong> {g['project']}</p>
                        <p><strong>Description:</strong> {g['description']}</p>
                        <p><a href="{g['url']}" target="_blank">🔗 View Program Details</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No grants")
        
        with tab4:
            if district_bills:
                st.markdown("**Click any item for details:**")
                for idx, bill in enumerate(district_bills[:20]):  # Show first 20
                    if st.button(f"📜 {bill.get('number', 'N/A')} - {bill.get('title', 'No title')[:80]}...", key=f"bill_{idx}", use_container_width=True):
                        st.session_state.selected_item = ('bill', idx)
                
                # Preview box
                if st.session_state.selected_item and st.session_state.selected_item[0] == 'bill':
                    idx = st.session_state.selected_item[1]
                    b = district_bills[idx]
                    bill_url = b.get('url', f"https://www.congress.gov/search?q={b.get('number', '')}")
                    st.markdown(f"""
                    <div class="preview-box">
                        <h4>📜 {b.get('number', 'N/A')}</h4>
                        <p><strong>Title:</strong> {b.get('title', 'No title')}</p>
                        <p><strong>Relationship:</strong> {b.get('relationship', 'Unknown')}</p>
                        <p><a href="{bill_url}" target="_blank">🔗 View on Congress.gov</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No bills tracked (run get_bills.py to fetch)")
    else:
        st.info("👈 Select a district")

# LIVE IDOT MAP
elif view == "🚧 Live IDOT Map":
    st.header("IDOT Getting Around Illinois - Live Map")
    
    st.markdown("""
    ### 📍 Interactive IDOT Construction Map
    
    This is the live IDOT map showing all current construction and closures across Illinois.
    
    **How to use:**
    - Zoom in/out to see specific areas
    - Click on icons to see project details
    - Use the layer controls to filter by project type
    - Look for projects in your congressional district (use reference maps to match locations)
    """)
    
    st.markdown("---")
    
    # District selector to help focus
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("**Filter by District:**")
        selected_districts = st.multiselect(
            "Show only these districts",
            options=sorted(DISTRICTS.keys()),
            default=[]
        )
        
        if selected_districts:
            st.info(f"Viewing: {', '.join(selected_districts)}")
            for d in selected_districts:
                info = DISTRICTS[d]
                st.write(f"**{d}**: {info['area']}")
    
    with col2:
        st.markdown("**Available Map Sources:**")
        
        map_source = st.radio(
            "Choose data source:",
            [
                "🗺️ IDOT Getting Around Illinois (Main)",
                "🚧 IDOT Construction Projects",
                "📱 IDOT Mobile Map"
            ]
        )
    
    st.markdown("---")
    
    # Embed the actual IDOT map
    if "Main" in map_source:
        iframe_url = "https://www.gettingaroundillinois.com/RoadConstruction/index.html"
        st.markdown("### Live IDOT Map:")
        st.components.v1.iframe(iframe_url, height=800, scrolling=True)
    
    elif "Construction" in map_source:
        # Try alternate IDOT map URLs
        iframe_url = "https://www.gettingaroundillinois.com/"
        st.markdown("### IDOT Home Map:")
        st.components.v1.iframe(iframe_url, height=800, scrolling=True)
    
    else:
        iframe_url = "https://www.gettingaroundillinois.com/RoadConstruction/index.html"
        st.markdown("### IDOT Mobile View:")
        st.components.v1.iframe(iframe_url, height=800, scrolling=True)
    
    st.markdown("---")
    
    # Instructions
    with st.expander("💡 How to Add Projects to Your Dashboard", expanded=True):
        st.markdown("""
        ### When you see a project on the map:
        
        1. **Click on the project** to see details
        2. **Note the information:**
           - Route (I-90, US-30, etc.)
           - Location (city, mile marker)
           - Description
           - Status
        
        3. **Determine the congressional district:**
           - Use the reference maps in "District View"
           - Match the location to a district
           - Or use the route guide below
        
        4. **Add to dashboard:**
           - Option A: Edit `idot_dynamic_XXXXXX.json`
           - Option B: Edit `scrape_idot_simple.py`
           - See SEMI_AUTOMATIC_SOLUTION.md for details
        
        ### Quick District Guide by Route:
        
        **Chicago Metro:**
        - I-94 (south) → IL-01
        - I-57 (south suburbs) → IL-02
        - I-90 Kennedy → IL-03
        - I-55 Stevenson → IL-04
        - I-90/I-94 (north) → IL-05
        - I-88/I-355 → IL-06
        - I-290 → IL-07
        - I-90 Jane Addams → IL-08
        - I-94 Edens → IL-09
        - I-94 (Lake County) → IL-10
        
        **Suburbs/Downstate:**
        - I-80/I-55 (Joliet) → IL-11
        - I-64/I-57 (southern) → IL-12
        - I-72/US-36 (Decatur/Springfield) → IL-13
        - I-88 (far west) → IL-14
        - I-57/I-70 (eastern) → IL-15
        - I-74/I-39 (Peoria/Rockford) → IL-16
        - I-74/I-80 (Quad Cities) → IL-17
        """)

# AV POLICY
elif view == "🤖 AV Policy":
    st.header("🚗 Autonomous Vehicle Policy - 50 State Tracker")
    
    # Load and organize AV policy data by state
    av_states = {'passed': {}, 'active': {}}
    
    # Try to load NCSL AV data
    try:
        with open('ncsl_av_complete.json', 'r') as f:
            ncsl_data = json.load(f)
            
        # Organize states by status
        for state_name, state_info in ncsl_data.get('states', {}).items():
            # States with passed legislation (not "No Legislation" and not pending)
            if state_info.get('type') != 'No Legislation' and state_info.get('year') != 'N/A':
                av_states['passed'][state_name] = state_info
            # States with active/pending legislation could be added here if data exists
            # For now, we'll just track passed vs. no activity
    except FileNotFoundError:
        st.warning("⚠️ NCSL AV data file not found. Showing empty tracker.")
    except Exception as e:
        st.error(f"Error loading AV data: {e}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔵 Laws Passed", len(av_states['passed']))
    col2.metric("🟠 Active Legislation", len(av_states['active']))
    col3.metric("⚪ No Activity", 50 - len(av_states['passed']) - len(av_states['active']))
    col4.metric("📍 Illinois Status", "Pending")
    
    st.markdown("---")
    
    # Create interactive US map with Folium
    import folium
    from folium import plugins
    
    st.subheader("Interactive 50-State Map")
    st.markdown("**🔵 Blue** = Laws Passed | **🟠 Orange** = Active Legislation | **⚪ Gray** = No Activity")
    
    # State coordinates (approximate centers)
    state_coords = {
        'Alabama': [32.8067, -86.7911], 'Alaska': [61.3707, -152.4044], 'Arizona': [33.7298, -111.4312],
        'Arkansas': [34.9697, -92.3731], 'California': [36.1162, -119.6816], 'Colorado': [39.0598, -105.3111],
        'Connecticut': [41.5978, -72.7554], 'Delaware': [39.3185, -75.5071], 'Florida': [27.7663, -81.6868],
        'Georgia': [33.0406, -83.6431], 'Hawaii': [21.0943, -157.4983], 'Idaho': [44.2405, -114.4788],
        'Illinois': [40.3495, -88.9861], 'Indiana': [39.8494, -86.2583], 'Iowa': [42.0115, -93.2105],
        'Kansas': [38.5266, -96.7265], 'Kentucky': [37.6681, -84.6701], 'Louisiana': [31.1695, -91.8678],
        'Maine': [44.6939, -69.3819], 'Maryland': [39.0639, -76.8021], 'Massachusetts': [42.2302, -71.5301],
        'Michigan': [43.3266, -84.5361], 'Minnesota': [45.6945, -93.9002], 'Mississippi': [32.7416, -89.6787],
        'Missouri': [38.4561, -92.2884], 'Montana': [46.9219, -110.4544], 'Nebraska': [41.1254, -98.2681],
        'Nevada': [38.3135, -117.0554], 'New Hampshire': [43.4525, -71.5639], 'New Jersey': [40.2989, -74.5210],
        'New Mexico': [34.8405, -106.2485], 'New York': [42.1657, -74.9481], 'North Carolina': [35.6301, -79.8064],
        'North Dakota': [47.5289, -99.7840], 'Ohio': [40.3888, -82.7649], 'Oklahoma': [35.5653, -96.9289],
        'Oregon': [44.5720, -122.0709], 'Pennsylvania': [40.5908, -77.2098], 'Rhode Island': [41.6809, -71.5118],
        'South Carolina': [33.8569, -80.9450], 'South Dakota': [44.2998, -99.4388], 'Tennessee': [35.7478, -86.6923],
        'Texas': [31.0545, -97.5635], 'Utah': [40.1500, -111.8624], 'Vermont': [44.0459, -72.7107],
        'Virginia': [37.7693, -78.1700], 'Washington': [47.4009, -121.4905], 'West Virginia': [38.4912, -80.9545],
        'Wisconsin': [44.2685, -89.6165], 'Wyoming': [42.7559, -107.3025]
    }
    
    # Create map centered on US
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='CartoDB positron')
    
    # Add state markers
    for state, coords in state_coords.items():
        # Determine color and status
        if state in av_states['passed']:
            color = 'blue'
            icon_color = 'white'
            status_info = av_states['passed'][state]
            status_text = f"<b>✅ PASSED ({status_info['year']})</b><br>{status_info['type']}<br>{status_info['status']}"
        elif state in av_states['active']:
            color = 'orange'
            icon_color = 'white'
            status_info = av_states['active'][state]
            status_text = f"<b>🟠 PENDING ({status_info['year']})</b><br>{status_info['type']}<br>{status_info['status']}"
        else:
            color = 'gray'
            icon_color = 'white'
            status_text = "<b>⚪ NO ACTIVITY</b><br>No AV legislation"
        
        # Add marker
        folium.CircleMarker(
            location=coords,
            radius=8 if state in av_states['passed'] or state in av_states['active'] else 4,
            popup=folium.Popup(f"<b>{state}</b><br>{status_text}", max_width=250),
            tooltip=state,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7 if state in av_states['passed'] or state in av_states['active'] else 0.3,
            weight=2
        ).add_to(m)
    
    # Display map
    folium_static(m, width=1400, height=600)
    
    st.markdown("---")
    
    # State details tabs
    tab1, tab2, tab3 = st.tabs(["🔵 Laws Passed", "🟠 Active Legislation", "📊 Illinois Options"])
    
    with tab1:
        st.markdown("### States with Passed AV Legislation")
        if not av_states['passed']:
            st.info("No states with passed legislation found in database")
        for state, info in sorted(av_states['passed'].items()):
            with st.expander(f"**{state}** - {info.get('type', 'Unknown')} ({info.get('year', 'N/A')})", expanded=False):
                st.markdown(f"**Status:** {info.get('status', 'N/A')}")
                st.markdown(f"**Type:** {info.get('type', 'N/A')}")
                st.markdown(f"**Year Enacted:** {info.get('year', 'N/A')}")
                
                st.markdown("---")
                
                # Primary Law
                st.markdown("#### 📜 Primary Legislation")
                law_name = info.get('law_name', 'N/A')
                st.markdown(f"**{law_name}**")
                
                # Agency
                st.markdown("#### 🏛️ Implementing Agency")
                agency = info.get('agency', 'N/A')
                agency_url = info.get('agency_url', '')
                if agency_url:
                    st.markdown(f"**{agency}** - [Visit Agency Page]({agency_url})")
                else:
                    st.markdown(f"**{agency}**")
                
                # Executive Orders
                if info.get('executive_orders'):
                    st.markdown("#### 📋 Executive Orders")
                    for eo in info['executive_orders']:
                        st.markdown(f"- **{eo.get('title', 'N/A')}** ({eo.get('year', 'N/A')}) - [Read Order]({eo.get('url', '#')})")
                
                # Press Releases
                if info.get('press_releases'):
                    st.markdown("#### 📰 Recent Press Releases")
                    for pr in info['press_releases']:
                        st.markdown(f"- **{pr.get('title', 'N/A')}** ({pr.get('date', 'N/A')}) - [Read More]({pr.get('url', '#')})")
    
    with tab2:
        st.markdown("### States with Active/Pending Legislation")
        if not av_states['active']:
            st.info("📊 Currently tracking passed legislation only. Active bills tracked separately.")
        for state, info in sorted(av_states['active'].items()):
            with st.expander(f"**{state}** - {info.get('status', 'Unknown')}", expanded=False):
                st.markdown(f"**Status:** {info.get('status', 'N/A')}")
                st.markdown(f"**Type:** {info.get('type', 'N/A')}")
                st.markdown(f"**Year:** {info.get('year', 'N/A')}")
                
                st.markdown("---")
                
                # Pending Law
                st.markdown("#### 📜 Pending Legislation")
                law_name = info.get('law_name', 'N/A')
                st.markdown(f"**{law_name}**")
                
                # Agency
                st.markdown("#### 🏛️ Lead Agency")
                agency = info.get('agency', 'N/A')
                agency_url = info.get('agency_url', '')
                if agency_url:
                    st.markdown(f"**{agency}** - [Visit Agency Page]({agency_url})")
                else:
                    st.markdown(f"**{agency}**")
                
                # Bills Pending
                if info.get('bills_pending'):
                    st.markdown("#### 📑 Bills Under Consideration")
                    for bill in info['bills_pending']:
                        st.markdown(f"- **{bill.get('bill', 'N/A')}** - {bill.get('status', 'N/A')} - [View Bill]({bill.get('url', '#')})")
                
                # Executive Orders
                if info.get('executive_orders'):
                    st.markdown("#### 📋 Executive Orders")
                    for eo in info['executive_orders']:
                        st.markdown(f"- **{eo.get('title', 'N/A')}** ({eo.get('year', 'N/A')}) - [Read Order]({eo.get('url', '#')})")
                
                # Press Releases
                if info.get('press_releases'):
                    st.markdown("#### 📰 Recent Announcements")
                    for pr in info['press_releases']:
                        st.markdown(f"- **{pr.get('title', 'N/A')}** ({pr.get('date', 'N/A')}) - [Read More]({pr.get('url', '#')})")
                
                if state == 'Illinois':
                    st.info("👉 See Illinois Options tab for detailed policy recommendations")
    
    with tab3:
        st.markdown("### Illinois AV Policy Options")
        
        # Links to Illinois resources
        st.markdown("#### 🔗 Illinois Resources")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("- [IDOT Homepage](https://idot.illinois.gov/)")
            st.markdown("- [Illinois General Assembly](https://www.ilga.gov/)")
        with col2:
            st.markdown("- [Governor's Office](https://www.illinois.gov/government/governor.html)")
            st.markdown("- [Secretary of State](https://www.cyberdriveillinois.com/)")
        
        st.markdown("---")
        
        with st.expander("⭐ Option B: Pilot Program (RECOMMENDED)", expanded=True):
            st.write("**Chicago-based pilot with 2-3 year evaluation**")
            st.write("✅ Test-and-learn approach")
            st.write("✅ Build public trust gradually")
            st.write("✅ Flexible framework")
            st.write("✅ Data-driven decisions")
            st.success("**Staff recommendation for Illinois**")
            
            st.markdown("**Similar approaches:**")
            st.markdown("- [Massachusetts Pilot Program](https://www.mass.gov/)")
            st.markdown("- [Georgia Testing Framework](http://www.legis.ga.gov/)")
        
        with st.expander("Option A: Comprehensive Framework"):
            st.write("**Full regulatory system like California**")
            st.write("✅ Strong safety standards")
            st.write("✅ Clear liability framework")
            st.write("⚠️ Resource intensive")
            st.write("⚠️ May slow innovation")
            
            st.markdown("**Model legislation:**")
            st.markdown("- [California SB 1298](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201120120SB1298)")
            st.markdown("- [Michigan SB 169](http://www.legislature.mi.gov/)")
        
        with st.expander("⚠️ Option C: Status Quo (NOT RECOMMENDED)"):
            st.write("**Minimal regulation (Arizona model)**")
            st.write("⚠️ Limited safety oversight")
            st.write("⚠️ Unclear liability")
            st.write("⚠️ Public trust concerns")
            st.error("**This is what Waymo is lobbying for**")
            
            st.markdown("**Example approaches:**")
            st.markdown("- [Arizona EO 2015-09](https://azgovernor.gov/)")
            st.markdown("- [Texas Permissive Framework](https://capitol.texas.gov/)")
        
        st.markdown("---")
        st.markdown("**📍 Illinois Status:** Pending - Decision expected Q2 2026")
        st.markdown("**📧 Contact:** [IDOT Policy Office](https://idot.illinois.gov/about-idot/contact-us.html)")
        
        with st.expander("⚠️ Option C: Status Quo (NOT RECOMMENDED)"):
            st.write("**Minimal regulation (Arizona model)**")
            st.write("⚠️ Limited safety oversight")
            st.write("⚠️ Unclear liability")
            st.write("⚠️ Public trust concerns")
            st.error("**This is what Waymo is lobbying for**")
        
        st.markdown("---")
        st.markdown("**📍 Illinois Status:** Pending - Decision expected Q2 2026")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666;'>IDOT | {datetime.now().strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)



# ========================= Policy Goblin =========================
st.sidebar.markdown("---")
st.sidebar.markdown("## 🧠 Policy Goblin")

g_scope = st.sidebar.selectbox("Scope", ["Illinois", "All states"], index=0)
g_query = st.sidebar.text_area("Ask a question", placeholder="e.g., What construction is going on in IL-12?")

def _load_latest_json(pattern: str):
    files = glob.glob(pattern)
    if not files:
        return None, None
    latest = max(files, key=lambda f: Path(f).stat().st_mtime)
    try:
        return latest, json.loads(Path(latest).read_text())
    except Exception:
        return latest, None

def _as_docs():
    docs = []

    # NCSL AV converted payloads (best-effort)
    f_av, d_av = _load_latest_json("dashboard_av_data_*.json")
    if isinstance(d_av, dict):
        for status, items in d_av.items():
            if not isinstance(items, list):
                continue
            for it in items:
                txt = f"[NCSL AV | {status}] " + " ".join(str(v) for v in (it or {}).values())
                docs.append({"source":"NCSL_AV", "status":status, "text":txt, "item":it, "file":f_av})

    # Bills by district
    f_bbd, d_bbd = _load_latest_json("bills_by_district_*.json")
    if isinstance(d_bbd, dict):
        for dist, items in d_bbd.items():
            if not isinstance(items, list):
                continue
            for it in items:
                url = (it or {}).get("url") or (it or {}).get("link") or ""
                title = (it or {}).get("title") or (it or {}).get("bill") or ""
                txt = f"[Congress bills | {dist}] {title} " + " ".join(str(v) for v in (it or {}).values())
                docs.append({"source":"CONGRESS", "district":dist, "url":url, "text":txt, "item":it, "file":f_bbd})

    # IDOT dynamic / closures / construction (explode list-of-dicts into per-record docs)

    # IDOT dynamic / closures / construction (district-aware: IL-## -> {construction, closures})
    f_idot, d_idot = _load_latest_json("idot_dynamic_*.json")

    if isinstance(d_idot, dict):
        for dist, payload in d_idot.items():
            if not isinstance(payload, dict):
                continue

            # Construction items
            cons = payload.get("construction", [])
            if isinstance(cons, list):
                for rec in cons:
                    if not isinstance(rec, dict):
                        continue
                    title = rec.get("title") or rec.get("project") or rec.get("description") or rec.get("location") or "construction"
                    txt = f"[IDOT | {dist} | construction] {title} " + " ".join(str(v) for v in rec.values())
                    docs.append({"source":"IDOT", "district":dist, "category":"construction", "text":txt, "item":rec, "file":f_idot})

            # Closure items
            clos = payload.get("closures", [])
            if isinstance(clos, list):
                for rec in clos:
                    if not isinstance(rec, dict):
                        continue
                    title = rec.get("title") or rec.get("description") or rec.get("location") or "closure"
                    txt = f"[IDOT | {dist} | closures] {title} " + " ".join(str(v) for v in rec.values())
                    docs.append({"source":"IDOT", "district":dist, "category":"closures", "text":txt, "item":rec, "file":f_idot})


    return docs


def _extract_il_cd(q: str):
    m = re.search(r"\bIL[\s\-]?(\d{1,2})\b", (q or "").upper())
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def _score(query, doc_text):
    q = [w for w in re.split(r"[^a-z0-9]+", (query or "").lower()) if w]
    t = (doc_text or "").lower()
    return sum(1 for w in q if w and w in t)

def _retrieve(query, docs, k=12):
    cd = _extract_il_cd(query)
    district_filter = f"IL-{cd:02d}" if cd else None
    if district_filter:
        # Keep IDOT docs only for that district; leave other sources untouched
        docs = [d for d in docs if d.get('source') != 'IDOT' or d.get('district') == district_filter]

    scored = []
    for d in docs:
        sc = _score(query, d.get("text",""))
        if sc > 0:
            scored.append((sc, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:k]]

def _support(items):
    lines = []
    for d in items:
        src = d.get("source","?")
        url = d.get("url") or ""
        if url:
            lines.append(f"- **{src}**: {url}")
        else:
            lines.append(f"- **{src}** (from {d.get('file')})")
    return "\n".join(lines) if lines else "_No supporting items_"

if st.sidebar.button("Ask Goblin"):
    docs = _as_docs()
    if not (g_query or "").strip():
        st.sidebar.warning("Ask a question first.")
    else:
        items = _retrieve(g_query, docs, k=12)
        if not items:
            st.sidebar.warning("No strong matches. Try adding location keywords (city/county/route) or 'closure', 'lane', 'bridge', 'resurfacing'.")
        else:
            # Deterministic brief (no API keys required)
            by_src = {}
            for it in items:
                by_src[it["source"]] = by_src.get(it["source"], 0) + 1

            st.sidebar.markdown(f"**Question:** {g_query}")
            st.sidebar.markdown("**What I found (by source):** " + ", ".join(f"{k}: {v}" for k,v in by_src.items()))
            st.sidebar.markdown("**Supporting items:**\n" + _support(items))
            
            # IDOT-friendly brief when available
            def _parse_date(x):
                # Best-effort: keep as string; parsing can be added later if needed
                return (x or "").strip()

            def _top_counts(vals, n=8):
                from collections import Counter
                c = Counter([v for v in vals if v not in (None, "", "None")])
                return c.most_common(n)

            idot_items = [d for d in items if d.get("source") == "IDOT"]
            if idot_items:
                recs = [d.get("item") for d in idot_items if isinstance(d.get("item"), dict)]
                st.sidebar.markdown("### 🦺 IDOT construction/closures brief")

                st.sidebar.markdown(f"**Total IDOT items returned:** {len(recs)}")

                counties = [r.get("County") for r in recs]
                routes = [r.get("Route") or r.get("Route1") for r in recs]
                ctypes = [r.get("ConstructionType") for r in recs]
                statuses = [r.get("Status") for r in recs]

                st.sidebar.markdown("**Top counties:** " + ", ".join(f"{k} ({v})" for k,v in _top_counts(counties, 6)) )
                st.sidebar.markdown("**Top routes:** " + ", ".join(f"{k} ({v})" for k,v in _top_counts(routes, 6)) )
                st.sidebar.markdown("**Top construction types:** " + ", ".join(f"{k} ({v})" for k,v in _top_counts(ctypes, 6)) )

                # Prefer "active-ish" records
                active = []
                for r in recs:
                    stt = (r.get("Status") or "").lower()
                    if any(w in stt for w in ["active", "in progress", "current", "open"]):
                        active.append(r)
                if not active:
                    active = recs

                st.sidebar.markdown("### Top items (up to 10)")
                for r in active[:10]:
                    route = r.get("Route") or r.get("Route1") or "Route?"
                    town = r.get("NearTown") or ""
                    county = r.get("County") or ""
                    ctype = r.get("ConstructionType") or ""
                    impact = r.get("ImpactOnTravel") or r.get("TrafficAlert") or ""
                    start = _parse_date(r.get("StartDate"))
                    end = _parse_date(r.get("EndDate"))
                    url = r.get("WebAddress") or ""

                    line = f"- **{route}** — {town} ({county}) — *{ctype}* — {start} → {end}"
                    st.sidebar.markdown(line)
                    if impact:
                        st.sidebar.markdown(f"  - Impact: {impact}")
                    if url:
                        st.sidebar.markdown(f"  - Link: {url}")

                st.sidebar.markdown("### Raw sample (first 1)")
                st.sidebar.json(recs[0] if recs else {})
            else:
                # fallback to prior behavior
                st.sidebar.markdown("**Top matches (first 5):**")
                st.sidebar.json([x.get("item") for x in items[:5]])

# ================================================================
