import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import subprocess
import os

st.set_page_config(page_title="IDOT Dashboard - All Districts", page_icon="🚗", layout="wide")

st.markdown('<div style="font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center;">🚗 IDOT Dashboard - All 17 Districts</div>', unsafe_allow_html=True)
st.markdown("---")

# ALL 17 DISTRICTS - Full Data
DISTRICTS = {
    "IL-01": {"rep": "Jonathan Jackson", "party": "D", "area": "Chicago South Side", "lat": 41.7276, "lon": -87.6243,
              "committees": ["Agriculture", "Foreign Affairs"],
              "closures": [{"route": "I-94", "location": "95th Street", "type": "Construction", "status": "Active", "lat": 41.7220, "lon": -87.6246}],
              "grants": [{"program": "RAISE", "amount": 15000000, "project": "Red Line Extension", "lat": 41.7220, "lon": -87.6246}],
              "bills": [{"number": "H.R.1234", "title": "South Side Transit Improvement Act"}]},
    
    "IL-02": {"rep": "Robin Kelly", "party": "D", "area": "South suburbs", "lat": 41.5992, "lon": -87.6772,
              "committees": ["Energy and Commerce", "Oversight"],
              "closures": [{"route": "I-57", "location": "Matteson", "type": "Resurfacing", "status": "Planned", "lat": 41.5039, "lon": -87.7323}],
              "grants": [{"program": "INFRA", "amount": 12500000, "project": "Lincoln Highway Corridor", "lat": 41.5039, "lon": -87.7323}],
              "bills": [{"number": "H.R.2345", "title": "Suburban Transit Access Act"}]},
    
    "IL-03": {"rep": "Delia Ramirez", "party": "D", "area": "Northwest Chicago", "lat": 41.9208, "lon": -87.8084,
              "committees": ["Homeland Security", "Oversight"],
              "closures": [{"route": "I-90", "location": "Kennedy Expressway", "type": "Bridge repair", "status": "Active", "lat": 41.9742, "lon": -87.9073}],
              "grants": [{"program": "CRISI", "amount": 35000000, "project": "Milwaukee District North Line", "lat": 41.9742, "lon": -87.9073}],
              "bills": [{"number": "H.R.3456", "title": "Urban Multimodal Act"}]},
    
    "IL-04": {"rep": "Jesús García", "party": "D", "area": "Southwest Chicago", "lat": 41.8370, "lon": -87.7446,
              "committees": ["Financial Services", "Transportation"],
              "closures": [{"route": "Cicero Ave", "location": "26th Street", "type": "Complete streets", "status": "Design", "lat": 41.8370, "lon": -87.7446}],
              "grants": [{"program": "RAISE", "amount": 18000000, "project": "Cicero Multimodal Corridor", "lat": 41.8370, "lon": -87.7446}],
              "bills": [{"number": "H.R.4567", "title": "Complete Streets Funding Act"}]},
    
    "IL-05": {"rep": "Mike Quigley", "party": "D", "area": "North Chicago", "lat": 41.9534, "lon": -87.6981,
              "committees": ["Appropriations", "Intelligence"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-06": {"rep": "Sean Casten", "party": "D", "area": "Western suburbs", "lat": 41.8256, "lon": -88.0814,
              "committees": ["Financial Services", "Science"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-07": {"rep": "Danny Davis", "party": "D", "area": "West Chicago", "lat": 41.8781, "lon": -87.6298,
              "committees": ["Ways and Means"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-08": {"rep": "Raja Krishnamoorthi", "party": "D", "area": "Northwest suburbs", "lat": 42.0883, "lon": -88.1357,
              "committees": ["Oversight", "Intelligence"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-09": {"rep": "Jan Schakowsky", "party": "D", "area": "North suburbs", "lat": 42.0450, "lon": -87.6877,
              "committees": ["Energy and Commerce", "Budget"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-10": {"rep": "Brad Schneider", "party": "D", "area": "Lake County", "lat": 42.3369, "lon": -87.8658,
              "committees": ["Ways and Means", "Foreign Affairs"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-11": {"rep": "Bill Foster", "party": "D", "area": "Aurora/Joliet", "lat": 41.5253, "lon": -88.1473,
              "committees": ["Financial Services", "Science"],
              "closures": [{"route": "I-80", "location": "Joliet", "type": "Freight facility", "status": "Construction", "lat": 41.5250, "lon": -88.0817}],
              "grants": [{"program": "INFRA", "amount": 45000000, "project": "I-80 Intermodal Access", "lat": 41.5250, "lon": -88.0817}],
              "bills": []},
    
    "IL-12": {"rep": "Mike Bost", "party": "R", "area": "Southern Illinois", "lat": 38.1406, "lon": -89.2645,
              "committees": ["Transportation", "Veterans Affairs"],
              "closures": [],
              "grants": [{"program": "RAISE", "amount": 22000000, "project": "MetroLink Eastside Center", "lat": 38.6247, "lon": -90.1848}],
              "bills": [{"number": "H.R.8901", "title": "Rural Highway Safety Act"}]},
    
    "IL-13": {"rep": "Nikki Budzinski", "party": "D", "area": "Central Illinois", "lat": 39.8403, "lon": -88.9548,
              "committees": ["Agriculture", "Transportation"],
              "closures": [
                  {"route": "US-36", "location": "Decatur-Springfield", "type": "Bridge replacement", "status": "Active", "lat": 39.8403, "lon": -89.6515},
                  {"route": "IL-29", "location": "Macon County", "type": "Resurfacing", "status": "Active", "lat": 39.9064, "lon": -88.9548}
              ],
              "grants": [
                  {"program": "RAISE", "amount": 15000000, "project": "Decatur Multi-Modal Center", "lat": 39.8403, "lon": -89.6515},
                  {"program": "INFRA", "amount": 25000000, "project": "I-72 Freight Corridor", "lat": 39.9064, "lon": -88.6548}
              ],
              "bills": [
                  {"number": "H.R.3250", "title": "Rural Transportation Safety Act"},
                  {"number": "H.R.4872", "title": "Agricultural Freight Infrastructure Act"}
              ]},
    
    "IL-14": {"rep": "Lauren Underwood", "party": "D", "area": "Far west suburbs", "lat": 41.7606, "lon": -88.5855,
              "committees": ["Appropriations", "Veterans Affairs"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-15": {"rep": "Mary Miller", "party": "R", "area": "Eastern Illinois", "lat": 40.1164, "lon": -88.2434,
              "committees": ["Agriculture", "Education"],
              "closures": [], "grants": [], "bills": []},
    
    "IL-16": {"rep": "Darin LaHood", "party": "R", "area": "Peoria/Rockford", "lat": 40.6936, "lon": -89.5890,
              "committees": ["Ways and Means"],
              "closures": [],
              "grants": [{"program": "RAISE", "amount": 20000000, "project": "Peoria Warehouse District", "lat": 40.6936, "lon": -89.5890}],
              "bills": []},
    
    "IL-17": {"rep": "Eric Sorensen", "party": "D", "area": "Quad Cities", "lat": 41.5067, "lon": -90.5151,
              "committees": ["Agriculture", "Science"],
              "closures": [],
              "grants": [{"program": "Port Infrastructure", "amount": 28000000, "project": "Mississippi River Lock", "lat": 41.5067, "lon": -90.5780}],
              "bills": []},
}

# Session state
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None

# Navigation
view = st.radio("Navigation", ["🗺️ Statewide Map", "📍 District View", "🤖 AV Policy", "📄 Reports"], horizontal=True)

# STATEWIDE MAP
if view == "🗺️ Statewide Map":
    st.header("Illinois - All 17 Congressional Districts")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts", "17")
    col2.metric("Democrats", "14")
    col3.metric("Republicans", "3")
    total_grants = sum(sum(g['amount'] for g in d['grants']) for d in DISTRICTS.values())
    col4.metric("Total Grants", f"${total_grants/1e6:.0f}M")
    
    m = folium.Map(location=[40.0, -89.0], zoom_start=7)
    
    for district_id, info in DISTRICTS.items():
        color = 'blue' if info['party'] == 'D' else 'red'
        n_closures = len(info['closures'])
        n_grants = len(info['grants'])
        grant_total = sum(g['amount'] for g in info['grants'])
        
        popup = f"<b>{district_id}: {info['rep']} ({info['party']})</b><br>{info['area']}<br><br>🚧 Closures: {n_closures}<br>💰 Grants: ${grant_total:,}"
        
        folium.Marker(
            [info['lat'], info['lon']],
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"{district_id}: {info['rep']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
        
        for closure in info['closures']:
            folium.CircleMarker([closure['lat'], closure['lon']], radius=6, color='orange', fill=True, popup=f"🚧 {closure['route']}").add_to(m)
        
        for grant in info['grants']:
            folium.CircleMarker([grant['lat'], grant['lon']], radius=8, color='green', fill=True, popup=f"💰 ${grant['amount']:,}").add_to(m)
    
    folium_static(m, width=1400, height=600)
    
    st.markdown("---")
    st.subheader("Click a District Below")
    
    cols = st.columns(6)
    for idx, district_id in enumerate(sorted(DISTRICTS.keys())):
        info = DISTRICTS[district_id]
        if cols[idx % 6].button(f"{district_id}\n{info['rep']}", key=f"btn_{district_id}"):
            st.session_state.selected_district = district_id
            st.rerun()

# DISTRICT VIEW
elif view == "📍 District View":
    st.sidebar.title("Select District")
    for district_id in sorted(DISTRICTS.keys()):
        info = DISTRICTS[district_id]
        if st.sidebar.button(f"{district_id}: {info['rep']}", key=f"side_{district_id}", use_container_width=True):
            st.session_state.selected_district = district_id
    
    if st.session_state.selected_district:
        district = st.session_state.selected_district
        info = DISTRICTS[district]
        
        st.header(f"{district}: {info['rep']} ({info['party']})")
        st.markdown(f"**Area:** {info['area']}")
        st.markdown(f"**Committees:** {', '.join(info['committees'])}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Closures", len(info['closures']))
        col2.metric("Grants", f"${sum(g['amount'] for g in info['grants'])/1e6:.1f}M")
        col3.metric("Bills", len(info['bills']))
        
        st.markdown("---")
        
        # District map
        dm = folium.Map(location=[info['lat'], info['lon']], zoom_start=10)
        folium.Marker([info['lat'], info['lon']], popup=f"{district}: {info['rep']}").add_to(dm)
        
        for closure in info['closures']:
            folium.Marker([closure['lat'], closure['lon']], icon=folium.Icon(color='orange', icon='road', prefix='fa'), popup=f"🚧 {closure['route']}").add_to(dm)
        
        for grant in info['grants']:
            folium.Marker([grant['lat'], grant['lon']], icon=folium.Icon(color='green', icon='dollar', prefix='fa'), popup=f"💰 ${grant['amount']:,}").add_to(dm)
        
        folium_static(dm, width=1400, height=500)
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🚧 Closures", "💰 Grants", "📜 Legislation"])
        
        with tab1:
            if info['closures']:
                df = pd.DataFrame(info['closures'])
                st.dataframe(df[['route', 'location', 'type', 'status']], use_container_width=True, hide_index=True)
            else:
                st.info("No active closures")
        
        with tab2:
            if info['grants']:
                df = pd.DataFrame(info['grants'])
                df['amount'] = df['amount'].apply(lambda x: f"${x:,}")
                st.dataframe(df[['program', 'amount', 'project']], use_container_width=True, hide_index=True)
            else:
                st.info("No grants")
        
        with tab3:
            if info['bills']:
                df = pd.DataFrame(info['bills'])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No bills tracked")
        
        st.markdown("---")
        if st.button(f"📄 Generate {district} Report", type="primary", use_container_width=True):
            from docx import Document
            doc = Document()
            doc.add_heading(f'District {district} Dashboard', 0)
            doc.add_paragraph(f'Representative: {info["rep"]} ({info["party"]})')
            doc.add_paragraph(f'Area: {info["area"]}')
            doc.add_paragraph(f'Committees: {", ".join(info["committees"])}')
            doc.add_paragraph()
            
            doc.add_heading('Closures', 1)
            for c in info['closures']:
                doc.add_paragraph(f"{c['route']} - {c['location']}: {c['type']}", style='List Bullet')
            
            doc.add_heading('Grants', 1)
            for g in info['grants']:
                doc.add_paragraph(f"{g['program']}: ${g['amount']:,} - {g['project']}", style='List Bullet')
            
            doc.add_heading('Legislation', 1)
            for b in info['bills']:
                doc.add_paragraph(f"{b['number']}: {b['title']}", style='List Bullet')
            
            path = os.path.expanduser(f'~/Downloads/{district}_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
            doc.save(path)
            st.success(f"✅ {path}")
            subprocess.Popen(['libreoffice', '--writer', path])
    else:
        st.info("👈 Select a district from sidebar")

# AV POLICY
elif view == "🤖 AV Policy":
    st.header("AV Policy Goblin")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Comprehensive Laws", "8")
    col2.metric("Pending Bills", "3")
    col3.metric("Permissive States", "2")
    col4.metric("No Activity", "23")
    
    st.markdown("---")
    
    with st.expander("⭐ Option B: Pilot Program (RECOMMENDED)", expanded=True):
        st.write("**Chicago-based pilot with 2-3 year evaluation**")
        st.write("✅ Test-and-learn | ✅ Build trust | ✅ Flexible")
        st.success("Staff recommendation for Illinois")
    
    with st.expander("Option A: Comprehensive Framework"):
        st.write("**Full regulatory system like California**")
        st.write("✅ Safety standards | ⚠️ Resource intensive")
    
    with st.expander("⚠️ Option C: Status Quo (NOT RECOMMENDED)"):
        st.write("**Minimal regulation (Arizona model)**")
        st.error("This is what Waymo is lobbying for")

# REPORTS
elif view == "📄 Reports":
    st.header("Generate Reports")
    
    st.subheader("District Reports")
    selected = st.selectbox("Select District", sorted(DISTRICTS.keys()))
    
    if st.button(f"Generate {selected} Report", use_container_width=True, type="primary"):
        from docx import Document
        info = DISTRICTS[selected]
        doc = Document()
        doc.add_heading(f'{selected} Dashboard', 0)
        doc.add_paragraph(f'{info["rep"]} ({info["party"]}) - {info["area"]}')
        
        path = os.path.expanduser(f'~/Downloads/{selected}_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        doc.save(path)
        st.success(f"✅ Saved: {path}")
        subprocess.Popen(['libreoffice', '--writer', path])
    
    st.markdown("---")
    st.subheader("AV Policy Report")
    
    if st.button("Generate AV Policy Report", use_container_width=True):
        from docx import Document
        doc = Document()
        doc.add_heading('AV Policy Options for Illinois', 0)
        doc.add_paragraph('Option B (Pilot Program) - RECOMMENDED')
        
        path = os.path.expanduser(f'~/Downloads/AV_Policy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        doc.save(path)
        st.success(f"✅ Saved: {path}")
        subprocess.Popen(['libreoffice', '--writer', path])

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666;'>IDOT | {datetime.now().strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)
