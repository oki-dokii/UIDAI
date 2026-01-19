#!/usr/bin/env python3
"""
Generate a 1-Page Judges Cheat Sheet - A visual summary for busy juries.
"""

import os
import sys
import datetime

try:
    from fpdf import FPDF
except ImportError:
    print("pip install fpdf2")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SUBMISSION_DIR = os.path.join(BASE_DIR, "submission")
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# Colors
UIDAI_ORANGE = (237, 125, 49)
UIDAI_BLUE = (47, 84, 150)


class CheatSheetPDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'UIDAI Data Hackathon 2026 | Team: Ayush Patel', align='C')


def create_cheat_sheet():
    pdf = CheatSheetPDF(orientation='L', format='A4')  # Landscape for more space
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    # =========================================================================
    # HEADER
    # =========================================================================
    pdf.set_font('helvetica', 'B', 28)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.cell(0, 15, "UIDAI Hackathon 2026 - One-Page Summary", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Orange line
    pdf.set_draw_color(*UIDAI_ORANGE)
    pdf.set_line_width(1.5)
    pdf.line(20, 22, 277, 22)
    pdf.ln(8)
    
    # =========================================================================
    # LEFT COLUMN - Key Numbers
    # =========================================================================
    col1_x = 15
    col2_x = 115  
    col3_x = 200
    
    pdf.set_xy(col1_x, 30)
    
    # KEY INSIGHT BOX
    pdf.set_fill_color(*UIDAI_BLUE)
    pdf.set_text_color(255)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(80, 10, "  KEY INSIGHT", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col1_x, 42)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(80, 7, 
        '"For every 1 new Aadhaar,\nthere are 22 updates.\n\nBut children are being\nleft behind."', 
        fill=True, align='C')
    
    # CHILD GAP NUMBER
    pdf.set_xy(col1_x, 80)
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.cell(80, 8, "CHILD ATTENTION GAP", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col1_x, 90)
    pdf.set_font('helvetica', 'B', 36)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(80, 15, "-0.228", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col1_x, 107)
    pdf.set_font('helvetica', 'I', 9)
    pdf.set_text_color(100)
    pdf.cell(80, 6, "(Negative = Children Under-Served)", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Key Metrics Table
    pdf.set_xy(col1_x, 120)
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.cell(80, 8, "KEY METRICS", align='C', new_x="LMARGIN", new_y="NEXT")
    
    metrics = [
        ("Total Records", "124M+"),
        ("Enrolments", "5.4M"),
        ("Updates", "119M"),
        ("Update:Enrol Ratio", "21.9x"),
        ("Child Share (Enrol)", "97.5%"),
        ("Child Share (Updates)", "~30%"),
        ("Critical Districts", "20"),
    ]
    
    pdf.set_font('helvetica', '', 9)
    y = 130
    for label, value in metrics:
        pdf.set_xy(col1_x, y)
        pdf.set_text_color(50)
        pdf.cell(50, 6, label, border=0)
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_text_color(*UIDAI_ORANGE)
        pdf.cell(30, 6, value, border=0, align='R')
        pdf.set_font('helvetica', '', 9)
        y += 7
    
    # =========================================================================
    # MIDDLE COLUMN - ML & Methodology
    # =========================================================================
    pdf.set_xy(col2_x, 30)
    pdf.set_fill_color(*UIDAI_ORANGE)
    pdf.set_text_color(255)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(75, 10, "  METHODOLOGY", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col2_x, 42)
    pdf.set_text_color(50)
    pdf.set_font('helvetica', '', 9)
    
    methods = [
        "1. Data Cleaning: 30+ state name",
        "   normalizations, deduplication",
        "",
        "2. Feature Engineering:",
        "   - child_attention_gap metric",
        "   - update_intensity ratio",
        "",
        "3. ML Models:",
        "   - K-Means (5 clusters)",
        "   - Prophet (6-month forecast)",
        "   - Isolation Forest (anomalies)",
    ]
    
    for line in methods:
        pdf.set_xy(col2_x, pdf.get_y())
        pdf.cell(75, 5, line, new_x="LMARGIN", new_y="NEXT")
    
    # TOP 5 DISTRICTS
    pdf.set_xy(col2_x, 105)
    pdf.set_fill_color(*UIDAI_BLUE)
    pdf.set_text_color(255)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(75, 8, "  TOP 5 PRIORITY DISTRICTS", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    districts = [
        ("North East", "Delhi", "-1.000"),
        ("Jhajjar", "Haryana", "-1.000"),
        ("Kendrapara", "Odisha", "-1.000"),
        ("Namakkal", "Tamil Nadu", "-1.000"),
        ("Kushi Nagar", "UP", "-0.991"),
    ]
    
    pdf.set_font('helvetica', 'B', 8)
    pdf.set_xy(col2_x, 115)
    pdf.set_text_color(255)
    pdf.set_fill_color(*UIDAI_BLUE)
    pdf.cell(35, 6, "District", border=1, fill=True, align='C')
    pdf.cell(25, 6, "State", border=1, fill=True, align='C')
    pdf.cell(15, 6, "Gap", border=1, fill=True, align='C')
    pdf.ln()
    
    pdf.set_font('helvetica', '', 8)
    pdf.set_text_color(0)
    for dist, state, gap in districts:
        pdf.set_x(col2_x)
        pdf.cell(35, 5, dist, border=1, align='C')
        pdf.cell(25, 5, state, border=1, align='C')
        pdf.set_text_color(200, 0, 0)
        pdf.cell(15, 5, gap, border=1, align='C')
        pdf.set_text_color(0)
        pdf.ln()
    
    # =========================================================================
    # RIGHT COLUMN - Recommendations
    # =========================================================================
    pdf.set_xy(col3_x, 30)
    pdf.set_fill_color(0, 128, 0)
    pdf.set_text_color(255)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(80, 10, "  RECOMMENDATIONS", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col3_x, 42)
    pdf.set_text_color(50)
    pdf.set_font('helvetica', '', 9)
    
    recs = [
        "IMMEDIATE (0-3 months):",
        "  [!] Child update campaigns in 20",
        "      critical-gap districts",
        "  [!] Extend weekend biometric hours",
        "",
        "MEDIUM-TERM (3-6 months):",
        "  [*] Mobile update camps for rural",
        "      under-served cluster (280 dist)",
        "  [*] Awareness programs for emerging",
        "      growth hub districts",
        "",
        "MONITORING KPIs:",
        "  - Update:Enrol Ratio (target: 15-25)",
        "  - Child Gap (target: > -0.1)",
        "  - Weekend Ratio (target: > 0.7)",
    ]
    
    for line in recs:
        pdf.set_xy(col3_x, pdf.get_y())
        if line.startswith("IMMEDIATE") or line.startswith("MEDIUM") or line.startswith("MONITORING"):
            pdf.set_font('helvetica', 'B', 9)
            pdf.set_text_color(*UIDAI_BLUE)
        else:
            pdf.set_font('helvetica', '', 9)
            pdf.set_text_color(50)
        pdf.cell(80, 5, line, new_x="LMARGIN", new_y="NEXT")
    
    # TECH STACK BOX
    pdf.set_xy(col3_x, 130)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.cell(80, 6, "TECH STACK", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_xy(col3_x, 138)
    pdf.set_font('helvetica', '', 8)
    pdf.set_text_color(100)
    pdf.multi_cell(80, 4, "Python | Pandas | Scikit-learn | Prophet\nRich CLI | Folium Maps | FPDF", align='C')
    
    # =========================================================================
    # BOTTOM TAGLINE
    # =========================================================================
    pdf.set_xy(15, 175)
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(*UIDAI_BLUE)
    pdf.cell(0, 8, '"Data-Driven Policy for 1.4 Billion Citizens"', align='C')
    
    # Save
    output = os.path.join(SUBMISSION_DIR, "JUDGES_CHEAT_SHEET.pdf")
    pdf.output(output)
    print(f"Cheat sheet created: {output}")


if __name__ == "__main__":
    create_cheat_sheet()
