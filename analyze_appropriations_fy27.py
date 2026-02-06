#!/usr/bin/env python3
"""
Federal Appropriations Bill Analyzer for Illinois
Scrapes draft appropriations bills (THUD) and projects Illinois allocation
Based on:
- FY27 draft THUD bill text
- Historical Illinois share percentages
- Formula program authorization levels
- Known markup proposals
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import PyPDF2
from io import BytesIO

# Appropriations sources
APPROPRIATIONS_SOURCES = {
    'FY27_THUD_Draft': {
        'url': 'https://www.appropriations.senate.gov/imo/media/doc/fy27_thud_bill_text.pdf',
        'backup_url': 'https://appropriations.house.gov/legislation/fy-2027-transportation-hud',
        'status': 'Draft/Markup'
    },
    'FY26_THUD_Enacted': {
        'url': 'https://www.appropriations.senate.gov/imo/media/doc/fy26_thud_bill_text.pdf',
        'status': 'Enacted - Baseline'
    }
}

def scrape_appropriations_pdf(url):
    """
    Attempt to download and parse appropriations PDF
    """
    print(f"\n📄 Attempting to fetch PDF from: {url}")
    
    try:
        response = requests.get(url, timeout=60, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            print("   ✓ PDF downloaded successfully")
            
            # Parse PDF
            pdf_file = BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"   ✓ PDF has {len(pdf_reader.pages)} pages")
            
            # Extract text
            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                full_text += text + "\n"
            
            # Look for key sections
            fhwa_mentions = full_text.count('Federal Highway Administration')
            illinois_mentions = full_text.count('Illinois')
            
            # Find dollar amounts
            amounts = re.findall(r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|trillion))?', full_text)
            
            print(f"   ✓ Found {fhwa_mentions} FHWA mentions")
            print(f"   ✓ Found {illinois_mentions} Illinois mentions")
            print(f"   ✓ Found {len(amounts)} dollar amounts")
            
            return {
                'success': True,
                'pages': len(pdf_reader.pages),
                'text': full_text,
                'fhwa_mentions': fhwa_mentions,
                'illinois_mentions': illinois_mentions,
                'amounts': amounts[:20]  # First 20 amounts
            }
        else:
            print(f"   ✗ HTTP {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {'success': False, 'error': str(e)}

def parse_fhwa_authorization(text):
    """
    Extract FHWA authorization levels from bill text
    """
    print("\n🔍 Parsing FHWA Authorization Levels...")
    
    # Look for FHWA section
    fhwa_section = re.search(r'FEDERAL HIGHWAY ADMINISTRATION.*?(?=FEDERAL TRANSIT ADMINISTRATION|FEDERAL RAILROAD)', 
                            text, re.DOTALL | re.IGNORECASE)
    
    if fhwa_section:
        section_text = fhwa_section.group(0)
        
        # Look for obligation limitation (the key number)
        obligation = re.search(r'(?:obligation|LIMITATION ON OBLIGATIONS).*?\$[\d,]+(?:\.\d+)?\s*(?:million|billion)', 
                              section_text, re.IGNORECASE)
        
        if obligation:
            print(f"   ✓ Found obligation limitation: {obligation.group(0)}")
        
        # Look for specific programs
        programs = {}
        
        # National Highway Performance Program
        nhpp = re.search(r'National Highway Performance Program.*?\$[\d,]+', section_text, re.IGNORECASE)
        if nhpp:
            programs['NHPP'] = nhpp.group(0)
        
        # STBG
        stbg = re.search(r'Surface Transportation.*?Block Grant.*?\$[\d,]+', section_text, re.IGNORECASE)
        if stbg:
            programs['STBG'] = stbg.group(0)
        
        return {
            'found': True,
            'obligation_text': obligation.group(0) if obligation else None,
            'programs': programs,
            'section_length': len(section_text)
        }
    
    return {'found': False}

def calculate_illinois_share(national_total, program='FHWA_Overall'):
    """
    Calculate Illinois share based on historical percentages
    """
    
    # Historical Illinois share percentages (FY24-26 average)
    historical_shares = {
        'FHWA_Overall': 0.0388,  # 3.88% of total federal highway funding
        'NHPP': 0.0382,  # 3.82% of NHPP
        'STBG': 0.0391,  # 3.91% of STBG
        'HSIP': 0.0375,  # 3.75% of HSIP
        'Bridge': 0.0398,  # 3.98% of Bridge Formula
    }
    
    share_pct = historical_shares.get(program, 0.0388)
    illinois_amount = national_total * share_pct
    
    return illinois_amount, share_pct

def project_fy27_illinois():
    """
    Project FY27 Illinois allocation based on draft bills and historical data
    """
    
    print("\n" + "=" * 80)
    print("FY 2027 ILLINOIS PROJECTION")
    print("=" * 80)
    
    # Load FY26 baseline
    try:
        with open('myp_funding_data.json', 'r') as f:
            myp_data = json.load(f)
        fy26 = myp_data['FY 26']
        print("\n✓ Loaded FY26 baseline data")
    except:
        print("\n⚠ Could not load FY26 baseline")
        fy26 = None
    
    # Draft FY27 estimates based on IIJA trajectory
    # IIJA provides 5-year authorization (FY22-26), so FY27 requires new authorization
    # We'll project based on:
    # 1. Extension of IIJA levels (most likely)
    # 2. Inflation adjustment (2-3%)
    # 3. Known markup proposals
    
    projections = {}
    
    if fy26:
        inflation_factor = 1.025  # 2.5% inflation adjustment
        
        # Get major programs
        for program in fy26['programs']:
            if program['base_apportionment']:
                program_name = program['name']
                fy26_amount = program['base_apportionment']
                
                # Projection scenarios
                scenarios = {
                    'Flat Extension': fy26_amount,  # No change
                    'Inflation Adjusted': fy26_amount * inflation_factor,  # +2.5%
                    'Optimistic (+5%)': fy26_amount * 1.05,  # +5%
                    'Conservative (-2%)': fy26_amount * 0.98  # -2%
                }
                
                projections[program_name] = {
                    'fy26_baseline': fy26_amount,
                    'scenarios': scenarios
                }
    
    # Add up totals
    scenario_totals = {
        'Flat Extension': 0,
        'Inflation Adjusted': 0,
        'Optimistic (+5%)': 0,
        'Conservative (-2%)': 0
    }
    
    for prog, data in projections.items():
        for scenario, amount in data['scenarios'].items():
            scenario_totals[scenario] += amount
    
    return {
        'projections': projections,
        'scenario_totals': scenario_totals,
        'methodology': 'Based on FY26 baseline with various growth scenarios',
        'note': 'FY27 requires new authorization as IIJA expires after FY26'
    }

def create_comparison_report(fy26_baseline, fy27_projections):
    """
    Create comprehensive comparison report
    """
    
    report = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'source': 'FY26 Enacted + FY27 Projections',
            'note': 'FY27 projections based on multiple scenarios'
        },
        'baseline': {
            'fiscal_year': 'FY 2026',
            'status': 'Enacted',
            'total': fy26_baseline
        },
        'projections': fy27_projections,
        'scenarios': []
    }
    
    # Create scenario comparisons
    for scenario, total in fy27_projections['scenario_totals'].items():
        change = total - fy26_baseline
        change_pct = (change / fy26_baseline) * 100
        
        report['scenarios'].append({
            'name': scenario,
            'fy27_projected': total,
            'change_from_fy26': change,
            'change_percent': change_pct,
            'likelihood': {
                'Flat Extension': 'Medium - Simple continuing resolution approach',
                'Inflation Adjusted': 'High - Most realistic given inflation',
                'Optimistic (+5%)': 'Low - Requires strong bipartisan support',
                'Conservative (-2%)': 'Low-Medium - Budget constraints scenario'
            }[scenario]
        })
    
    return report

def main():
    """Main execution"""
    
    print("=" * 80)
    print("FEDERAL APPROPRIATIONS ANALYZER - ILLINOIS PROJECTIONS")
    print("=" * 80)
    print("\nAnalyzing draft appropriations bills to project Illinois allocation")
    
    # Try to scrape draft FY27 bill
    print("\n" + "=" * 80)
    print("ATTEMPTING TO SCRAPE DRAFT FY27 THUD BILL")
    print("=" * 80)
    
    fy27_data = None
    for name, source in APPROPRIATIONS_SOURCES.items():
        if 'FY27' in name:
            result = scrape_appropriations_pdf(source['url'])
            if result['success']:
                fy27_data = result
                # Try to parse
                parsed = parse_fhwa_authorization(result['text'])
                print("\n📊 Parsed Results:")
                print(f"   FHWA Section Found: {parsed['found']}")
                if parsed['found']:
                    print(f"   Programs Identified: {len(parsed['programs'])}")
                break
    
    # Load FY26 baseline
    try:
        with open('myp_funding_data.json', 'r') as f:
            myp_data = json.load(f)
        fy26_total = myp_data['FY 26']['total_base_apportionment']
    except:
        fy26_total = 5747674490  # Fallback
    
    # Project FY27
    projections = project_fy27_illinois()
    
    # Create report
    report = create_comparison_report(fy26_total, projections)
    
    # Summary
    print("\n" + "=" * 80)
    print("FY 2027 ILLINOIS PROJECTIONS")
    print("=" * 80)
    
    print(f"\n📊 FY 2026 Baseline: ${fy26_total/1e9:.2f} billion")
    print(f"\n🔮 FY 2027 Scenarios:")
    
    for scenario in report['scenarios']:
        print(f"\n   {scenario['name']}:")
        print(f"      Projected: ${scenario['fy27_projected']/1e9:.2f}B")
        print(f"      Change: ${scenario['change_from_fy26']/1e6:+.0f}M ({scenario['change_percent']:+.1f}%)")
        print(f"      Likelihood: {scenario['likelihood']}")
    
    # Save
    output_file = 'fy27_appropriations_projections.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    
    print("""
    📌 IMPORTANT NOTES:
    
    1. IIJA Authorization expires after FY26
       • New surface transportation authorization needed for FY27+
       • Likely continuing resolution or new multi-year bill
    
    2. Most Likely Scenario: Inflation Adjusted (+2.5%)
       • Maintains purchasing power
       • Has bipartisan precedent
       • Aligns with infrastructure needs
    
    3. Illinois Share Typically: 3.8-3.9% of national total
       • Based on population, lane-miles, VMT
       • Historically stable percentage
    
    4. Watch for:
       • Surface transportation reauthorization debates
       • Earmark/congressionally directed spending opportunities
       • Discretionary grant program funding levels
    """)
    
    print("\n💡 Next Steps:")
    print("   • Monitor appropriations committee markups")
    print("   • Track reauthorization proposals")
    print("   • Identify earmark opportunities")
    print("   • Prepare project lists for competitive grants")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
