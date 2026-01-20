
import re
import os
import sys

def convert_header(line):
    match = re.match(r'^(#+)\s+(.+)$', line)
    if not match:
        return line
    level = len(match.group(1))
    title = match.group(2)
    return f'<h{level}>{title}</h{level}>'

def convert_formatting(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text

def convert_images(text):
    # Markdown image: ![Alt](path)
    match = re.search(r'!\[(.*?)\]\((.*?)\)', text)
    if match:
        alt = match.group(1)
        path = match.group(2)
        # Ensure path is relative and correct. 
        # The MD has "outputs/aadhaar_plots_final..." but if HTML is IN outputs/, 
        # we need "aadhaar_plots_final..." (strip outputs/ prefix if present)
        if path.startswith('outputs/'):
            path = path.replace('outputs/', '')
            
        html_img = (
            f'<div class="figure">'
            f'<img src="{path}" alt="{alt}">'
            f'<p class="caption">{alt}</p>'
            f'</div>'
        )
        return html_img
    return text

def parse_table(lines):
    html = '<div class="table-container"><table>'
    # Header
    header_cols = [c.strip() for c in lines[0].split('|') if c.strip()]
    html += '<thead><tr>'
    for col in header_cols:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    # Body (skip separator line 1)
    for row in lines[2:]:
        cols = [c.strip() for c in row.split('|') if c.strip() or c=='']
        # Clean edges
        cols = [c.strip() for c in row.strip().split('|')]
        if row.strip().startswith('|'): cols = cols[1:]
        if row.strip().endswith('|'): cols = cols[:-1]
        
        html += '<tr>'
        for col in cols:
            html += f'<td>{convert_formatting(col)}</td>'
        html += '</tr>'
        
    html += '</tbody></table></div>'
    return html

def main():
    input_file = "outputs/final_report.md"
    output_file = "outputs/final_report.html"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    html_lines = []
    html_lines.append('<!DOCTYPE html><html><head>')
    html_lines.append('<meta charset="utf-8">')
    html_lines.append('<title>Forensic Analytical Audit</title>')
    html_lines.append('<style>')
    html_lines.append("""
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }
        h1, h2, h3 { color: #2c3e50; margin-top: 1.5em; }
        h1 { font-size: 2.5em; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; }
        h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        h3 { font-size: 1.4em; }
        img { max-width: 100%; height: auto; border: 1px solid #ddd; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin: 20px 0; }
        .figure { text-align: center; margin: 30px 0; }
        .caption { font-style: italic; color: #666; font-size: 0.9em; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        blockquote { border-left: 4px solid #3498db; margin: 0; padding-left: 20px; color: #555; }
        li { margin-bottom: 8px; }
        hr { border: 0; border-top: 1px solid #eee; margin: 40px 0; }
        
        /* Title Page Style */
        .title-page { text-align: center; padding: 60px 0; page-break-after: always; }
        .title-page h1 { border: none; }
        
        @media print {
            body { max-width: 100%; padding: 0; }
            h1, h2 { page-break-after: avoid; }
            img { max-width: 100% !important; page-break-inside: avoid; }
            .no-print { display: none; }
            a { text-decoration: none; color: #333; }
        }
    """)
    html_lines.append('</style></head><body>')
    
    # Add Print Button
    html_lines.append('<div class="no-print" style="position:fixed; top:20px; right:20px;">')
    html_lines.append('<button onclick="window.print()" style="background:#3498db; color:white; border:none; padding:10px 20px; font-size:16px; border-radius:5px; cursor:pointer;">Print to PDF</button>')
    html_lines.append('</div>')
    
    in_yaml = False
    in_list = False
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Strip simple yaml
        if line.strip() == '---':
            if i == 0: in_yaml = True
            elif in_yaml: in_yaml = False
            else: html_lines.append('<hr>')
            i += 1
            continue
        if in_yaml:
            i += 1
            continue
            
        # Headers
        if line.startswith('#'):
            html_lines.append(convert_header(line))
            i += 1
            continue
            
        # Custom Title Page Center block
        if line.startswith(r'\begin{center}'):
            html_lines.append('<div class="title-page">')
            i += 1
            continue
        if line.startswith(r'\end{center}'):
            html_lines.append('</div>')
            i += 1
            continue
        # Skip raw latex commands
        if line.strip().startswith('\\'):
            i += 1
            continue
            
        # Tables
        if '|' in line and i+1 < len(lines) and re.match(r'^\s*\|?[-:| ]+\|?\s*$', lines[i+1]):
            table_lines = [line]
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].rstrip())
                i += 1
            html_lines.append(parse_table(table_lines))
            continue
            
        # Images
        if '![' in line:
            html_lines.append(convert_images(line))
            i += 1
            continue
            
        # Lists
        if re.match(r'^\s*[-*]\s+', line):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = re.sub(r"^\s*[-*]\s+", "", line)
            html_lines.append(f'<li>{convert_formatting(content)}</li>')
            i += 1
            continue
        elif in_list:
            html_lines.append('</ul>')
            in_list = False
            
        # Paragraphs
        if line.strip():
            html_lines.append(f'<p>{convert_formatting(line)}</p>')
            
        i += 1
        
    html_lines.append('</body></html>')
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(html_lines))
    print(f"Generated {output_file}")

if __name__ == "__main__":
    main()
