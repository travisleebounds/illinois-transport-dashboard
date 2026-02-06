"""
Federal Funding Overview Tab for IDOT Dashboard
Integrates MYP spreadsheet data with visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json

def load_myp_data():
    """Load the parsed MYP funding data"""
    try:
        with open('myp_funding_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ MYP funding data not found. Please run data extraction first.")
        return None

def create_funding_tab():
    st.header("💰 Federal Funding Overview - Illinois IIJA Highway Apportionments")
    
    # Load data
    myp_data = load_myp_data()
    if not myp_data:
        return
    
    # Display summary metrics
    st.markdown("### Multi-Year Funding Summary (FY 2024-2026)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fy24_total = myp_data['FY 24']['total_base_apportionment']
        st.metric("FY 2024 (Actual)", f"${fy24_total/1e9:.2f}B", 
                 help="Total base apportionment for Illinois")
    
    with col2:
        fy25_total = myp_data['FY 25']['total_base_apportionment']
        fy25_change = ((fy25_total - fy24_total) / fy24_total) * 100
        st.metric("FY 2025 (Est.)", f"${fy25_total/1e9:.2f}B", 
                 f"+{fy25_change:.1f}%")
    
    with col3:
        fy26_total = myp_data['FY 26']['total_base_apportionment']
        fy26_change = ((fy26_total - fy25_total) / fy25_total) * 100
        st.metric("FY 2026 (Est.)", f"${fy26_total/1e9:.2f}B", 
                 f"+{fy26_change:.1f}%")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Funding Trends", 
        "🥧 Program Breakdown", 
        "📍 Geographic Distribution",
        "📋 Detailed Tables"
    ])
    
    with tab1:
        st.subheader("Year-over-Year Funding Trends")
        
        # Prepare data for major programs
        major_programs = [
            'National Highway Performance Program',
            'Surface Transportation Grant Block Program',
            'Highway Safety Improvement Program',
            'Bridge Formula',
            'Carbon Reduction Program'
        ]
        
        # Create trend data
        trend_data = []
        for fy in ['FY 24', 'FY 25', 'FY 26']:
            for prog in myp_data[fy]['programs']:
                if prog['name'] in major_programs and prog['base_apportionment']:
                    trend_data.append({
                        'Fiscal Year': fy,
                        'Program': prog['name'],
                        'Amount': prog['base_apportionment']
                    })
        
        df_trends = pd.DataFrame(trend_data)
        
        # Create line chart
        fig = px.line(df_trends, x='Fiscal Year', y='Amount', color='Program',
                     markers=True, 
                     labels={'Amount': 'Funding ($)'},
                     title='Major Program Funding Trends (FY 2024-2026)')
        
        fig.update_layout(
            yaxis_tickformat='$,.0f',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth rates table
        st.markdown("### Program Growth Rates")
        
        growth_data = []
        for prog_name in major_programs:
            fy24_amt = next((p['base_apportionment'] for p in myp_data['FY 24']['programs'] 
                           if p['name'] == prog_name and p['base_apportionment']), None)
            fy26_amt = next((p['base_apportionment'] for p in myp_data['FY 26']['programs'] 
                           if p['name'] == prog_name and p['base_apportionment']), None)
            
            if fy24_amt and fy26_amt:
                growth = ((fy26_amt - fy24_amt) / fy24_amt) * 100
                growth_data.append({
                    'Program': prog_name,
                    'FY 2024': f'${fy24_amt:,.0f}',
                    'FY 2026': f'${fy26_amt:,.0f}',
                    'Growth': f'+{growth:.1f}%'
                })
        
        st.dataframe(pd.DataFrame(growth_data), use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Program Breakdown by Fiscal Year")
        
        # Select fiscal year
        fy_select = st.selectbox("Select Fiscal Year:", ['FY 24', 'FY 25', 'FY 26'])
        
        # Get programs for selected year
        programs = myp_data[fy_select]['programs']
        
        # Filter to programs with base apportionment
        program_data = [(p['name'], p['base_apportionment']) 
                       for p in programs if p['base_apportionment']]
        
        # Sort by amount
        program_data.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 10
        top_programs = program_data[:10]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=[p[0] for p in top_programs],
            values=[p[1] for p in top_programs],
            hole=0.3,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=f'{fy_select} - Top 10 Programs by Funding',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show all programs in table
        st.markdown("### All Programs")
        prog_df = pd.DataFrame([
            {'Program': p[0], 'Funding': f'${p[1]:,.0f}'}
            for p in program_data
        ])
        st.dataframe(prog_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Surface Transportation Block Grant (STBG) Distribution by Area Size")
        
        st.markdown("""
        STBG funding is distributed based on population and area characteristics:
        - **IDOT Flexible**: Available for any area
        - **Areas > 200K**: Urbanized areas over 200,000 population
        - **Areas 50K-200K**: Small urbanized areas
        - **Areas 5K-50K**: Rural areas
        - **Areas < 5K**: Small rural areas
        """)
        
        # Get STBG sub-allocations for each year
        fy_select_geo = st.selectbox("Select Fiscal Year:", ['FY 24', 'FY 25', 'FY 26'], key='geo_fy')
        
        # Find STBG program
        stbg = next((p for p in myp_data[fy_select_geo]['programs'] 
                    if 'Surface Transportation Grant Block Program' in p['name']), None)
        
        if stbg and stbg['sub_allocations']:
            sub_alloc_data = [(s['name'], s['amount']) for s in stbg['sub_allocations']]
            
            # Create bar chart
            fig = go.Figure(data=[go.Bar(
                x=[s[0] for s in sub_alloc_data],
                y=[s[1] for s in sub_alloc_data],
                text=[f'${s[1]:,.0f}' for s in sub_alloc_data],
                textposition='auto',
            )])
            
            fig.update_layout(
                title=f'{fy_select_geo} STBG Geographic Distribution',
                xaxis_title='Area Category',
                yaxis_title='Funding ($)',
                yaxis_tickformat='$,.0f',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show percentage breakdown
            total_stbg = sum(s[1] for s in sub_alloc_data)
            pct_df = pd.DataFrame([
                {
                    'Area Category': s[0],
                    'Amount': f'${s[1]:,.0f}',
                    'Percentage': f'{(s[1]/total_stbg)*100:.1f}%'
                }
                for s in sub_alloc_data
            ])
            st.dataframe(pct_df, use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("Detailed Program Tables")
        
        fy_select_detail = st.selectbox("Select Fiscal Year:", ['FY 24', 'FY 25', 'FY 26'], key='detail_fy')
        
        programs = myp_data[fy_select_detail]['programs']
        
        # Create detailed table
        detail_data = []
        for prog in programs:
            detail_data.append({
                'Program Name': prog['name'],
                'Base Apportionment': f"${prog['base_apportionment']:,.0f}" if prog['base_apportionment'] else '-',
                'Set-Asides': f"${prog['set_asides']:,.0f}" if prog['set_asides'] else '-',
                '2% Planning/Research': f"${prog['planning_research']:,.0f}" if prog['planning_research'] else '-',
                'After Set-Asides': f"${prog['after_set_asides']:,.0f}" if prog['after_set_asides'] else '-',
                'Source': '🔗 Link' if prog['source_url'] else '-'
            })
        
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True, hide_index=True, height=600)
        
        # Export option
        csv = detail_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f'illinois_highway_funding_{fy_select_detail.replace(" ", "")}.csv',
            mime='text/csv'
        )

# Note: This would be integrated into dashboard_ultimate.py as a new view option
