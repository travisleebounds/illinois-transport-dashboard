import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import subprocess
import os
from pathlib import Path

st.set_page_config(page_title="IDOT Interactive Dashboard", page_icon="🚗", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .district-button {
        background-color: #1f77b4;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
        cursor: pointer;
        display: inline-block;
        width: 100px;
        text-align: center;
    }
    .democrat { background-color: #4285f4; }
    .republican { background-color: #ea4335; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; padding: 1rem 0;">🚗 IDOT Interactive Dashboard</div>', unsafe_allow_html=True)
st.markdown("**Click on any district to view details** | 118th Congress (2023-2025)")
st.markdown("---")

# Full district data with coordinates
DISTRICTS = {
    "IL-01": {"rep": "Jonathan Jackson", "party": "D", "area": "Chicago South Side", "lat": 41.7276, "lon": -87.6243,
              "committees": ["Agriculture", "Foreign Affairs"],
              "closures": [{"route": "I-94", "location": "95th Street", "type": "Construction", "status": "Active"}],
              "grants": [{"program": "RAISE", "amount": 15000000, "project": "Red Line Extension (portion)"}],
              "bills": [{"number": "H.R.1234", "title": "South Side Transit Improvement Act"}]},
    
    "IL-02": {"rep": "Robin Kelly", "party": "D", "area": "South suburbs", "lat": 41.5992, "lon": -87.6772,
              "committees": ["Energy and Commerce", "Oversight"],
              "closures": [{"route": "I-57", "location": "Matteson", "type": "Resurfacing", "status": "Planned"}],
              "grants": [{"program": "INFRA", "amount": 12500000, "project": "Lincoln Highway Corridor"}],
              "bills": [{"number": "H.R.2345", "title": "Suburban Transit Access Act"}]},
    
    "IL-03": {"rep": "Delia Ramirez", "party": "D", "area": "Northwest Chicago", "lat": 41.9208, "lon": -87.8084,
              "committees": ["Homeland Security", "Oversight"],
              "closures": [{"route": "I-90", "location": "Kennedy Expressway", "type": "Bridge repair", "status": "Active"}],
              "grants": [{"program": "CRISI", "amount": 35000000, "project": "Milwaukee District North Line"}],
              "bills": [{"number": "H.R.3456", "title": "Urban Multimodal Act"}]},
    
    "IL-04": {"rep": "Jesús García", "party": "D", "area": "Southwest Chicago", "lat": 41.8370, "lon": -87.7446,
              "committees": ["Financial Services", "Transportation"],
              "closures": [{"route": "Cicero Ave", "location": "26th Street", "type": "Complete streets", "status": "Design"}],
              "grants": [{"program": "RAISE", "amount": 18000000, "project": "Cicero Multimodal Corridor"}],
              "bills": [{"number": "H.R.4567", "title": "Complete Streets Funding Act"}]},
    
    "IL-05": {"rep": "Mike Quigley", "party": "D", "area": "North Chicago", "lat": 41.9534, "lon": -87.6981,
              "committees": ["Appropriations", "Intelligence"],
              "closures": [],
              "grants": [],
              "bills": [{"number": "H.R.5678", "title": "Transit Infrastructure Investment"}]},
    
    "IL-06": {"rep": "Sean Casten", "party": "D", "area": "Western suburbs", "lat": 41.8256, "lon": -88.0814,
              "committees": ["Financial Services", "Science"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-07": {"rep": "Danny Davis", "party": "D", "area": "West Chicago", "lat": 41.8781, "lon": -87.6298,
              "committees": ["Ways and Means"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-08": {"rep": "Raja Krishnamoorthi", "party": "D", "area": "Northwest suburbs", "lat": 42.0883, "lon": -88.1357,
              "committees": ["Oversight", "Intelligence"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-09": {"rep": "Jan Schakowsky", "party": "D", "area": "North suburbs", "lat": 42.0450, "lon": -87.6877,
              "committees": ["Energy and Commerce", "Budget"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-10": {"rep": "Brad Schneider", "party": "D", "area": "Lake County", "lat": 42.3369, "lon": -87.8658,
              "committees": ["Ways and Means", "Foreign Affairs"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-11": {"rep": "Bill Foster", "party": "D", "area": "Aurora/Joliet", "lat": 41.5253, "lon": -88.1473,
              "committees": ["Financial Services", "Science"],
              "closures": [{"route": "I-80", "location": "Joliet", "type": "Freight facility access", "status": "Construction"}],
              "grants": [{"program": "INFRA", "amount": 45000000, "project": "I-80 Intermodal Access"}],
              "bills": []},
    
    "IL-12": {"rep": "Mike Bost", "party": "R", "area": "Southern Illinois", "lat": 38.1406, "lon": -89.2645,
              "committees": ["Transportation", "Veterans Affairs"],
              "closures": [],
              "grants": [{"program": "RAISE", "amount": 22000000, "project": "MetroLink Eastside Transit Center"}],
              "bills": [{"number": "H.R.8901", "title": "Rural Highway Safety Act"}]},
    
    "IL-13": {"rep": "Nikki Budzinski", "party": "D", "area": "Central Illinois (Decatur, Springfield, Champaign)", "lat": 39.8403, "lon": -88.9548,
              "committees": ["Agriculture", "Transportation"],
              "closures": [
                  {"route": "US-36", "location": "Decatur-Springfield", "type": "Bridge replacement", "status": "Active"},
                  {"route": "IL-29", "location": "Macon County", "type": "Resurfacing", "status": "Active"}
              ],
              "grants": [
                  {"program": "RAISE", "amount": 15000000, "project": "Decatur Multi-Modal Center"},
                  {"program": "INFRA", "amount": 25000000, "project": "I-72 Freight Corridor"}
              ],
              "bills": [
                  {"number": "H.R.3250", "title": "Rural Transportation Safety Act"},
                  {"number": "H.R.4872", "title": "Agricultural Freight Infrastructure Act (cosponsor)"}
              ]},
    
    "IL-14": {"rep": "Lauren Underwood", "party": "D", "area": "Far west suburbs", "lat": 41.7606, "lon": -88.5855,
              "committees": ["Appropriations", "Veterans Affairs"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-15": {"rep": "Mary Miller", "party": "R", "area": "Eastern Illinois", "lat": 40.1164, "lon": -88.2434,
              "committees": ["Agriculture", "Education"],
              "closures": [],
              "grants": [],
              "bills": []},
    
    "IL-16": {"rep": "Darin LaHood", "party": "R", "area": "Peoria/Rockford", "lat": 40.6936, "lon": -89.5890,
              "committees": ["Ways and Means"],
              "closures": [],
              "grants": [{"program": "RAISE", "amount": 20000000, "project": "Peoria Warehouse District Access"}],
              "bills": []},
    
    "IL-17": {"rep": "Eric Sorensen", "party": "D", "area": "Quad Cities/Rockford", "lat": 41.5067, "lon": -90.5151,
              "committees": ["Agriculture", "Science"],
              "closures": [],
              "grants": [{"program": "Port Infrastructure", "amount": 28000000, "project": "Mississippi River Lock Facility"}],
              "bills": []},
}

# Initialize session state
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None

# Sidebar with clickable district buttons
st.sidebar.title("Select District")
st.sidebar.markdown("**Click any district:**")

for district_id in sorted(DISTRICTS.keys()):
    info = DISTRICTS[district_id]
    party_class = "democrat" if info['party'] == 'D' else "republican"
    
    if st.sidebar.button(f"{district_id}: {info['rep']}", key=district_id, use_container_width=True):
        st.session_state.selected_district = district_id

# Main map
st.subheader("🗺️ Illinois Congressional Districts Map")

# Create map centered on Illinois
m = folium.Map(location=[40.0, -89.0], zoom_start=7)

# Add markers for each district
for district_id, info in DISTRICTS.items():
    color = 'blue' if info['party'] == 'D' else 'red'
    
    # Count activities
    n_closures = len(info['closures'])
    n_grants = len(info['grants'])
    n_bills = len(info['bills'])
    
    popup_html = f"""
    <b>{district_id}: {info['rep']} ({info['party']})</b><br>
    {info['area']}<br><br>
    Closures: {n_closures}<br>
    Grants: {n_grants} (${sum(g['amount'] for g in info['grants']):,})<br>
    Bills: {n_bills}
    """
    
    folium.Marker(
        location=[info['lat'], info['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{district_id}: {info['rep']}",
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(m)
    
    # Add markers for closures
    for closure in info['closures']:
        folium.CircleMarker(
            location=[info['lat'] + 0.05, info['lon'] + 0.05],
            radius=5,
            popup=f"🚧 {closure['route']}: {closure['type']}",
            color='orange',
            fill=True
        ).add_to(m)

folium_static(m, width=1400, height=500)

st.markdown("---")

# District details
if st.session_state.selected_district:
    district = st.session_state.selected_district
    info = DISTRICTS[district]
    
    st.header(f"📍 {district}: {info['rep']} ({info['party']})")
    st.markdown(f"**Area:** {info['area']}")
    st.markdown(f"**Committees:** {', '.join(info['committees'])}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Closures/Construction", len(info['closures']))
    with col2:
        total_grants = sum(g['amount'] for g in info['grants'])
        st.metric("Grant Awards", f"${total_grants/1e6:.1f}M")
    with col3:
        st.metric("Bills Tracked", len(info['bills']))
    
    st.markdown("---")
    
    # Tabs for details
    tab1, tab2, tab3 = st.tabs(["🚧 Closures & Construction", "💰 Grants", "📜 Legislation"])
    
    with tab1:
        if info['closures']:
            df = pd.DataFrame(info['closures'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active closures or construction projects")
    
    with tab2:
        if info['grants']:
            df = pd.DataFrame(info['grants'])
            df['amount'] = df['amount'].apply(lambda x: f"${x:,}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No discretionary grants in dataset")
    
    with tab3:
        if info['bills']:
            df = pd.DataFrame(info['bills'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No transportation bills tracked")
    
    # Generate Word report button
    st.markdown("---")
    if st.button(f"📄 Generate Word Report for {district}", use_container_width=True):
        with st.spinner("Generating Word report..."):
            # Create simple report
            from docx import Document
            
            doc = Document()
            doc.add_heading(f'District {district} Dashboard Report', 0)
            doc.add_paragraph(f'Representative: {info["rep"]} ({info["party"]})')
            doc.add_paragraph(f'Area: {info["area"]}')
            doc.add_paragraph(f'Committees: {", ".join(info["committees"])}')
            doc.add_paragraph()
            
            doc.add_heading('Closures & Construction', 1)
            if info['closures']:
                for c in info['closures']:
                    doc.add_paragraph(f"{c['route']} - {c['location']}: {c['type']} ({c['status']})", style='List Bullet')
            else:
                doc.add_paragraph('No active projects')
            
            doc.add_heading('Grant Awards', 1)
            if info['grants']:
                for g in info['grants']:
                    doc.add_paragraph(f"{g['program']}: ${g['amount']:,} - {g['project']}", style='List Bullet')
            else:
                doc.add_paragraph('No grants in dataset')
            
            doc.add_heading('Legislation', 1)
            if info['bills']:
                for b in info['bills']:
                    doc.add_paragraph(f"{b['number']}: {b['title']}", style='List Bullet')
            else:
                doc.add_paragraph('No bills tracked')
            
            # Save to Downloads
            report_path = os.path.expanduser(f'~/Downloads/District_{district}_Report_{datetime.now().strftime("%Y%m%d")}.docx')
            doc.save(report_path)
            
            st.success(f"✅ Report generated: {report_path}")
            
            # Auto-open in LibreOffice
            try:
                subprocess.Popen(['libreoffice', report_path])
                st.info("📂 Opening in LibreOffice...")
            except:
                st.warning(f"Report saved to: {report_path}\nOpen manually with LibreOffice")

else:
    st.info("👆 Click a district in the sidebar or on the map to view details")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666;'>IDOT Office of Federal Policy Analysis | {datetime.now().strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)
