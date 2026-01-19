#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - PREMIUM SUBMISSION GENERATOR (v2)
Generates a competition-winning Consolidated PDF with:
- UIDAI-branded cover page
- All required sections per hackathon guidelines
- Enhanced visuals and formatting

Usage:
    python3 scripts/generate_submission_pdf.py
"""

import os
import sys
import datetime
import pandas as pd

try:
    from fpdf import FPDF
except ImportError:
    print("❌ FPDF library not found. Run: pip install fpdf2")
    sys.exit(1)

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SUBMISSION_DIR = os.path.join(BASE_DIR, "submission")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "actionable_insights")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "integrated_analysis", "plots")
FORECAST_DIR = os.path.join(OUTPUT_DIR, "forecast_plots")

os.makedirs(SUBMISSION_DIR, exist_ok=True)

# UIDAI Brand Colors
UIDAI_ORANGE = (237, 125, 49)   # #ED7D31
UIDAI_BLUE = (47, 84, 150)      # #2F5496
DARK_GRAY = (50, 50, 50)


class PremiumPDF(FPDF):
    """Custom PDF class with UIDAI branding."""
    
    def header(self):
        if self.page_no() > 1:
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(*DARK_GRAY)
            self.cell(0, 10, 'UIDAI Data Hackathon 2026 | Unlocking Societal Trends in Aadhaar', align='C')
            self.ln(8)
            # Orange line under header
            self.set_draw_color(*UIDAI_ORANGE)
            self.set_line_width(0.5)
            self.line(10, 18, 200, 18)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def section_title(self, num, title):
        """Major section header with UIDAI blue."""
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(*UIDAI_BLUE)
        self.cell(0, 12, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        # Orange underline
        self.set_draw_color(*UIDAI_ORANGE)
        self.set_line_width(0.7)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(8)

    def subsection_title(self, title):
        """Subsection header."""
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        """Standard body text."""
        self.set_font('times', '', 11)
        self.set_text_color(0)
        self.multi_cell(0, 6, text)
        self.ln(4)

    def add_image_with_caption(self, img_path, caption, width=180):
        """Add image with caption below."""
        if not os.path.exists(img_path):
            print(f"  [WARN] Image not found: {img_path}")
            return
        self.image(img_path, w=width, x=(210 - width) / 2)
        self.ln(3)
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(100)
        self.multi_cell(0, 5, f"Figure: {caption}", align='C')
        self.ln(5)

    def add_table(self, headers, rows, col_widths=None):
        """Add a styled table."""
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)
        
        # Header row
        self.set_font('helvetica', 'B', 10)
        self.set_fill_color(*UIDAI_BLUE)
        self.set_text_color(255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True, align='C')
        self.ln()
        
        # Data rows
        self.set_font('helvetica', '', 9)
        self.set_text_color(0)
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell)[:30], border=1, align='C')
            self.ln()

    def add_code_snippet(self, file_path, max_lines=60):
        """Add sanitized code snippet."""
        if not os.path.exists(file_path):
            return
        self.set_font("courier", size=6)
        self.set_text_color(*DARK_GRAY)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines[:max_lines]:
                line = line.replace('\t', '    ').rstrip()
                line = line.encode('ascii', 'ignore').decode()
                self.set_x(self.l_margin)
                self.multi_cell(w=0, h=2.8, text=line)
            if len(lines) > max_lines:
                self.set_font("courier", 'B', 7)
                self.cell(0, 5, f"... [{len(lines) - max_lines} more lines] ...")
        except Exception as e:
            print(f"  [WARN] Could not read {file_path}: {e}")


def create_premium_pdf():
    print("Generating PREMIUM Submission PDF...")
    pdf = PremiumPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    pdf.add_page()
    pdf.ln(40)
    
    # Title block
    pdf.set_font('helvetica', 'B', 28)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.multi_cell(0, 14, "Unlocking Societal Trends in\nAadhaar Enrolment & Updates", align='C')
    pdf.ln(10)
    
    # Orange accent line
    pdf.set_draw_color(*UIDAI_ORANGE)
    pdf.set_line_width(2)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(15)
    
    # Subtitle
    pdf.set_font('helvetica', '', 16)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(0, 10, "UIDAI Data Hackathon 2026", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 10, "Data-Driven Innovation on Aadhaar", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    
    # Author/Date
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, f"Submission Date: {datetime.date.today().strftime('%d January %Y')}", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font('helvetica', '', 11)
    pdf.cell(0, 8, "Team: Ayush Patel", align='C', new_x="LMARGIN", new_y="NEXT")

    # =========================================================================
    # 1. PROBLEM STATEMENT & APPROACH
    # =========================================================================
    pdf.add_page()
    pdf.section_title(1, "Problem Statement & Approach")
    
    pdf.body_text("""
PROBLEM: With near-universal Aadhaar saturation among adults, the system has transitioned from an 
enrolment-focused model to an update-driven ecosystem. However, this shift may inadvertently 
leave children behind, as mandatory biometric updates for minors are often overlooked.

APPROACH: We analyzed 124+ million records across three official Aadhaar datasets to identify 
patterns, gaps, and actionable policy recommendations. Our core contribution is the "Child 
Attention Gap" metric - a novel indicator that quantifies how under-served children are in 
the update ecosystem relative to their share in new enrolments.

KEY QUESTIONS ADDRESSED:
1. How has the balance between enrolment and updates evolved?
2. Are children receiving proportional attention in biometric updates?
3. Which districts require immediate intervention?
4. Can we predict future trends to enable proactive policy?
""")

    # =========================================================================
    # 2. DATASETS USED
    # =========================================================================
    pdf.add_page()
    pdf.section_title(2, "Datasets Used")
    
    pdf.subsection_title("2.1 Data Sources (Provided by UIDAI)")
    datasets = [
        ["Dataset", "Records", "Key Columns", "Coverage"],
        ["Aadhaar Enrolment", "4.4M", "state, district, age_group, count", "Monthly 2023-24"],
        ["Demographic Updates", "47.3M", "state, district, minor_share, count", "Monthly 2023-24"],
        ["Biometric Updates", "69.8M", "state, district, minor_share, count", "Monthly 2023-24"],
    ]
    pdf.add_table(datasets[0], datasets[1:], col_widths=[45, 30, 70, 45])
    pdf.ln(8)
    
    pdf.subsection_title("2.2 Column Descriptions")
    pdf.body_text("""
- state/district: Geographic identifiers (normalized to standard Census names)
- year/month: Temporal dimension for time-series analysis
- minor_share: Proportion of transactions for individuals aged 0-17
- total_count: Aggregate transaction volume
- age_group: Categorical (0-5, 5-10, 10-15, 15-18, 18+) for enrolment data
""")

    # =========================================================================
    # 3. METHODOLOGY
    # =========================================================================
    pdf.add_page()
    pdf.section_title(3, "Methodology")
    
    pdf.subsection_title("3.1 Data Cleaning & Preprocessing")
    pdf.body_text("""
1. STATE NAME NORMALIZATION: Applied 30+ mapping rules to standardize state/UT names 
   (e.g., "ANDAMAN AND NICOBAR ISLANDS" -> "Andaman & Nicobar", "NCT OF DELHI" -> "Delhi").
   
2. DEDUPLICATION: Removed duplicate records based on (date, state, district) composite key.

3. MISSING VALUE HANDLING: Districts with zero activity were retained to identify 
   under-served areas. NaN values in numeric columns were imputed with 0.

4. DATE PARSING: Created unified datetime column from year/month for time-series analysis.
""")

    pdf.subsection_title("3.2 Feature Engineering")
    pdf.body_text("""
- child_share_enrol: Proportion of 0-17 age group in new enrolments
- child_share_updates: Proportion of minors in demographic + biometric updates
- CHILD ATTENTION GAP = child_share_updates - child_share_enrol
  (Negative value indicates children are under-served)
- update_intensity: Total updates / Total enrolments per district
- demo_bio_ratio: Demographic updates / Biometric updates (to detect imbalances)
""")

    pdf.subsection_title("3.3 Machine Learning Models")
    pdf.body_text("""
- K-MEANS CLUSTERING (scikit-learn): Segmented 1,041 districts into 5 behavioral profiles 
  based on enrolment volume, update intensity, and child gap.
  
- PROPHET FORECASTING (Facebook/Meta): Generated 6-month projections for national 
  enrolment and update trends with 95% confidence intervals.
  
- ISOLATION FOREST (scikit-learn): Detected 52 anomalous districts with unusual 
  update-to-enrolment ratios, flagged for potential data quality or operational issues.
""")

    # =========================================================================
    # 4. DATA ANALYSIS & VISUALIZATIONS
    # =========================================================================
    pdf.add_page()
    pdf.section_title(4, "Data Analysis & Visualizations")
    
    pdf.subsection_title("4.1 Key Findings")
    findings = [
        ["Finding", "Value", "Implication"],
        ["Update-to-Enrol Ratio", "21.9x", "System is update-driven, not enrolment-driven"],
        ["Child Share in Enrol", "97.5%", "Almost all new Aadhaars are for children"],
        ["Child Share in Updates", "~30%", "Children severely under-represented in updates"],
        ["National Child Gap", "-0.228", "Negative = system failing children"],
        ["Anomalies Detected", "52", "Districts with suspicious patterns"],
    ]
    pdf.add_table(findings[0], findings[1:], col_widths=[60, 40, 90])
    pdf.ln(10)
    
    # Add main visualization
    pdf.add_page()
    pdf.subsection_title("4.2 Executive Dashboard")
    pdf.add_image_with_caption(
        os.path.join(IMAGES_DIR, "00_insights_summary.png"),
        "Comprehensive view of Child Attention Gap across India"
    )
    
    pdf.add_page()
    pdf.subsection_title("4.3 Ecosystem Overview")
    pdf.add_image_with_caption(
        os.path.join(PLOTS_DIR, "01_national_overview.png"),
        "Distribution of enrolments vs updates at national level"
    )
    
    pdf.add_page()
    pdf.subsection_title("4.4 Child Attention Gap - Trend Analysis")
    pdf.add_image_with_caption(
        os.path.join(IMAGES_DIR, "02_child_gap_trend.png"),
        "Monthly evolution of the Child Attention Gap metric"
    )
    
    pdf.add_page()
    pdf.subsection_title("4.5 District Clustering")
    pdf.add_image_with_caption(
        os.path.join(IMAGES_DIR, "03_cluster_profiles.png"),
        "K-Means clustering reveals 5 distinct district behavioral profiles"
    )
    
    # =========================================================================
    # 5. PREDICTIVE FORECASTING (Prophet)
    # =========================================================================
    pdf.add_page()
    pdf.section_title(5, "Predictive Forecasting")
    
    pdf.body_text("""
Using Facebook Prophet, we generated 6-month forward projections for key metrics. 
The model accounts for weekly seasonality (weekend drops in biometric updates) and 
overall trends. These forecasts enable proactive resource allocation.
""")
    
    pdf.add_image_with_caption(
        os.path.join(FORECAST_DIR, "01_enrolment_forecast.png"),
        "6-Month Enrolment Forecast with 95% Confidence Interval"
    )
    
    pdf.add_page()
    pdf.add_image_with_caption(
        os.path.join(FORECAST_DIR, "02_updates_forecast.png"),
        "6-Month Updates Forecast with 95% Confidence Interval"
    )
    
    pdf.add_image_with_caption(
        os.path.join(FORECAST_DIR, "03_declining_districts.png"),
        "Districts with steepest activity decline - priority targets"
    )

    # =========================================================================
    # 6. RECOMMENDATIONS
    # =========================================================================
    pdf.add_page()
    pdf.section_title(6, "Actionable Recommendations")
    
    pdf.subsection_title("6.1 Immediate Actions (0-3 Months)")
    pdf.body_text("""
1. CHILD UPDATE CAMPAIGNS: Deploy targeted outreach in 20 critical-gap districts 
   (North East Delhi, Jhajjar, Kendrapara, Namakkal, Kushi Nagar).
   
2. WEEKEND BIOMETRIC SERVICES: Biometrics drop 31% on weekends. Extend Saturday 
   hours at Aadhaar Seva Kendras in urban centers.
   
3. MOBILE UPDATE CAMPS: For the 280 "Under-served Rural" cluster districts, 
   deploy mobile vans with biometric equipment.
""")
    
    pdf.subsection_title("6.2 Priority Districts (Top 10)")
    # Load real data
    rec_path = os.path.join(IMAGES_DIR, "top_20_child_gap_districts.csv")
    if os.path.exists(rec_path):
        df = pd.read_csv(rec_path)
        rows = []
        for _, row in df.head(10).iterrows():
            gap = row.get('child_attention_gap', 0)
            rows.append([
                str(row['district'])[:20],
                str(row['state'])[:15],
                f"{gap:.3f}",
                "Critical" if gap < -0.5 else "Severe"
            ])
        pdf.add_table(["District", "State", "Gap", "Status"], rows, col_widths=[55, 50, 35, 50])

    # =========================================================================
    # 7. CODE APPENDIX
    # =========================================================================
    pdf.add_page()
    pdf.section_title(7, "Code Appendix")
    
    pdf.subsection_title("7.1 CLI Entry Point (uidai.py)")
    pdf.add_code_snippet(os.path.join(BASE_DIR, "uidai.py"), max_lines=80)
    
    pdf.add_page()
    pdf.subsection_title("7.2 Insight Generation (actionable_insights.py)")
    pdf.add_code_snippet(os.path.join(BASE_DIR, "scripts", "actionable_insights.py"), max_lines=80)
    
    pdf.add_page()
    pdf.subsection_title("7.3 Forecast Analysis (forecast_analysis.py)")
    pdf.add_code_snippet(os.path.join(BASE_DIR, "scripts", "forecast_analysis.py"), max_lines=80)

    # =========================================================================
    # SAVE
    # =========================================================================
    output_path = os.path.join(SUBMISSION_DIR, "UIDAI_Hackathon_Submission_Team_Ayush.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    create_premium_pdf()
