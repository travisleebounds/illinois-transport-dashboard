import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="IDOT Dashboard", page_icon="🚗", layout="wide")

st.markdown('<div style="font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; padding: 1rem 0;">🚗 IDOT Transportation Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
<div style="background-color: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; margin: 1rem 0; font-size: 0.9rem;">
    <strong>DRAFT — INTERNAL REVIEW</strong><br>
    Illinois Department of Transportation | Office of Federal Policy Analysis<br>
    118th Congress (2023-2025)
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Overview", "🤖 AV Policy", "📖 Guide"])

with tab1:
    st.header("Illinois Congressional Districts Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Districts", "17")
    with col2:
        st.metric("Delegation", "14 D / 3 R")
    with col3:
        st.metric("Congress", "118th")
    
    st.markdown("---")
    st.subheader("District Roster")
    
    districts = {
        "IL-01": {"rep": "Jonathan Jackson (D)", "area": "Chicago South Side"},
        "IL-02": {"rep": "Robin Kelly (D)", "area": "South suburbs"},
        "IL-03": {"rep": "Delia Ramirez (D)", "area": "Northwest Chicago"},
        "IL-04": {"rep": "Jesús García (D)", "area": "Southwest Chicago"},
        "IL-05": {"rep": "Mike Quigley (D)", "area": "North Chicago"},
        "IL-06": {"rep": "Sean Casten (D)", "area": "Western suburbs"},
        "IL-07": {"rep": "Danny Davis (D)", "area": "West Chicago"},
        "IL-08": {"rep": "Raja Krishnamoorthi (D)", "area": "Northwest suburbs"},
        "IL-09": {"rep": "Jan Schakowsky (D)", "area": "North suburbs"},
        "IL-10": {"rep": "Brad Schneider (D)", "area": "Lake County"},
        "IL-11": {"rep": "Bill Foster (D)", "area": "Aurora/Joliet"},
        "IL-12": {"rep": "Mike Bost (R)", "area": "Southern Illinois"},
        "IL-13": {"rep": "Nikki Budzinski (D)", "area": "Central Illinois"},
        "IL-14": {"rep": "Lauren Underwood (D)", "area": "Far west suburbs"},
        "IL-15": {"rep": "Mary Miller (R)", "area": "Eastern Illinois"},
        "IL-16": {"rep": "Darin LaHood (R)", "area": "Peoria/Rockford"},
        "IL-17": {"rep": "Eric Sorensen (D)", "area": "Quad Cities"}
    }
    
    for district, info in districts.items():
        st.write(f"**{district}**: {info['rep']} — {info['area']}")

with tab2:
    st.header("🤖 AV Policy Goblin")
    st.markdown("Autonomous Vehicle policy tracker (50 states + 20 cities)")
    
    st.subheader("Illinois Policy Options")
    
    with st.expander("Option A: Comprehensive Framework (CA/MI Model)"):
        st.write("**Advantages:**")
        st.write("- Clear regulatory framework")
        st.write("- Safety standards protect public")
        st.write("- Incident reporting")
        st.write("\n**Model:** California SB 500 (2024)")
    
    with st.expander("Option B: Pilot Program (MA/WA Model) — RECOMMENDED"):
        st.write("**Advantages:**")
        st.write("- Test-and-learn approach")
        st.write("- Build public trust")
        st.write("- Flexibility to adjust")
        st.write("\n**Recommendation:** Chicago pilot (2-3 years)")
    
    with st.expander("Option C: Status Quo (AZ Model)"):
        st.warning("⚠️ NOT RECOMMENDED: Limited safety protections")
        st.write("This is what Waymo is lobbying for")

with tab3:
    st.header("📖 System Guide")
    st.markdown("""
    ### 🎯 What This System Does
    
    This dashboard tracks federal transportation activity across Illinois:
    - **17 Congressional Districts**
    - **Discretionary Grants** (RAISE, INFRA, CRISI)
    - **Transportation Legislation** (118th Congress)
    - **AV Policy** (50 states + 20 cities)
    
    ### 🚀 Full System Features
    
    The complete system includes:
    - Python scripts for data collection
    - Word document generators
    - Batch processing (all 17 districts)
    - FOIA-compliant reporting
    
    ### 📁 Files You Downloaded
    
    - `scripts/` — Data collection scripts
    - `dashboard/` — Full dashboard apps
    - `outputs/` — Generated reports (Word docs)
    - `data/` — Raw data files
    
    ### 🔧 To Run Full System
```bash
    cd ~/Downloads/idot-dashboard
    pip install --break-system-packages -r requirements.txt
    streamlit run dashboard/dashboard_master.py
```
    
    ### 📞 Next Steps
    
    1. Explore this simplified dashboard
    2. Read FINAL_DELIVERABLES.md
    3. Run full system when ready
    4. Configure Congress.gov API for real data
    """)

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666;'>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>", unsafe_allow_html=True)
