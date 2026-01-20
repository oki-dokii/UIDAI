
import re
import os
import sys

def escape_tex(text):
    """Escape special LaTeX characters."""
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)
    return text

def convert_header(line):
    """Convert markdown headers to latex sections."""
    match = re.match(r'^(#+)\s+(.+)$', line)
    if not match:
        return line
    
    level = len(match.group(1))
    title = match.group(2)
    
    # We ignore level 1 since we'll use custom title page, 
    # but strictly speaking user might want them. 
    # The file starts with # Monitoring... which is title.
    if level == 1:
        return r'\section{' + title + r'}'
    elif level == 2:
        return r'\section{' + title + r'}'
    elif level == 3:
        return r'\subsection{' + title + r'}'
    elif level == 4:
        return r'\subsubsection{' + title + r'}'
    
    return line

def convert_bold_italic(text):
    """Convert **bold** and *italic*."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)
    return text

def convert_images(text):
    """Convert markdown images to latex figures."""
    # Pattern: ![Caption](path)
    match = re.search(r'!\[(.*?)\]\((.*?)\)', text)
    if match:
        caption = match.group(1)
        path = match.group(2)
        
        # Latex doesn't like spaces in paths usually, but modern engines handle valid relative paths
        # We wrap in figure environment
        latex_img = (
            r'\begin{figure}[H]' + '\n'
            r'    \centering' + '\n'
            r'    \includegraphics[width=0.9\textwidth]{' + path + r'}' + '\n'
            r'    \caption{' + caption + r'}' + '\n'
            r'\end{figure}'
        )
        return latex_img
    return text

def parse_table(lines):
    """Simple markdown table parser to latex tabular."""
    # Identify header, separator, and body
    header = lines[0]
    separator = lines[1]
    body = lines[2:]
    
    cols = [c.strip() for c in header.split('|') if c.strip()]
    num_cols = len(cols)
    
    alignments = []
    sep_cols = [c.strip() for c in separator.split('|') if c.strip()]
    for col in sep_cols:
        if col.startswith(':') and col.endswith(':'):
            alignments.append('c')
        elif col.endswith(':'):
            alignments.append('r')
        else:
            alignments.append('l')
            
    while len(alignments) < num_cols:
        alignments.append('l')
        
    tex = r'\begin{table}[H]' + '\n'
    tex += r'\centering' + '\n'
    tex += r'\begin{tabular}{|' + '|'.join(alignments) + r'|}' + '\n'
    tex += r'\hline' + '\n'
    
    # Header
    header_cells = [r'\textbf{' + c.strip() + r'}' for c in cols]
    tex += ' & '.join(header_cells) + r' \\ \hline' + '\n'
    
    # Body
    for row in body:
        cells = [c.strip() for c in row.split('|') if c.strip() or c == '']
        # Filter out empty strings from split that might be at ends if pipe exists there
        # Row format: | col1 | col2 |
        cells = [c.strip() for c in row.strip().split('|')]
        # Remove empty start/end if they exist due to leading/trailing pipes
        if row.strip().startswith('|'): cells = cells[1:]
        if row.strip().endswith('|'): cells = cells[:-1]
        
        if len(cells) != num_cols:
            # simple fallback or skip
            continue
            
        tex_cells = [convert_bold_italic(c) for c in cells]
        tex += ' & '.join(tex_cells) + r' \\ \hline' + '\n'
        
    tex += r'\end{tabular}' + '\n'
    tex += r'\end{table}'
    return tex

def main():
    input_file = "outputs/final_report.md"
    output_file = "outputs/final_report.tex"
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    tex_lines = []
    
    # Preamble
    tex_lines.append(r'\documentclass{article}')
    tex_lines.append(r'\usepackage{graphicx}')
    tex_lines.append(r'\usepackage{hyperref}')
    tex_lines.append(r'\usepackage{geometry}')
    tex_lines.append(r'\usepackage{booktabs}')
    tex_lines.append(r'\usepackage{float}')
    tex_lines.append(r'\usepackage{enumitem}')
    tex_lines.append(r'\usepackage{caption}')
    tex_lines.append(r'\geometry{margin=1in}')
    tex_lines.append(r'\title{Monitoring Administrative Interaction Patterns in Aadhaar \\ \large A Forensic Analytical Audit of Enrolment and Update Systems}')
    tex_lines.append(r'\author{UIDAI Datathon Submission}')
    tex_lines.append(r'\date{2025}')
    tex_lines.append(r'\begin{document}')
    
    # Custom Title Page from the Markdown content
    # We will skip the YAML frontmatter provided in the MD file
    # and look for the specific title page structure if needed, 
    # OR just rely on standard maketitle. 
    # The MD has a custom title page section with \begin{center}...
    # We can pass those raw latex commands through.
    
    in_yaml = False
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Handle YAML frontmatter
        if line.strip() == '---':
            if i == 0:
                in_yaml = True
                i += 1
                continue
            elif in_yaml:
                in_yaml = False
                i += 1
                continue
            elif not in_code_block:
                # Horizontal rule
                tex_lines.append(r'\hrule')
                i += 1
                continue
        
        if in_yaml:
            i += 1
            continue
            
        # Code blocks - skip or handle simply (formatting)
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            i += 1
            continue
            
        if in_code_block:
            # Simple verbatim for now or ignore code blocks if they are just shell commands
            tex_lines.append(r'\texttt{' + escape_tex(line) + r'} \\')
            i += 1
            continue
            
        # Detect Table
        if '|' in line and (i+1 < len(lines)) and re.match(r'^\s*\|?[-:| ]+\|?\s*$', lines[i+1]):
            # Start of table
            table_lines = []
            table_lines.append(line)
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].rstrip())
                i += 1
            tex_lines.append(parse_table(table_lines))
            continue
            
        # Detect Lists
        if re.match(r'^\s*[-*]\s+', line):
            # Itemize
            content = re.sub(r'^\s*[-*]\s+', '', line)
            tex_lines.append(r'\begin{itemize}')
            tex_lines.append(r'\item ' + convert_bold_italic(content))
            # Check next lines for list items
            i += 1
            while i < len(lines):
                next_line = lines[i].rstrip()
                if re.match(r'^\s*[-*]\s+', next_line):
                    content = re.sub(r'^\s*[-*]\s+', '', next_line)
                    tex_lines.append(r'\item ' + convert_bold_italic(content))
                    i += 1
                elif next_line.strip() == '':
                    break # End of list usually
                else: 
                    # Continuation of item? Or break
                    # For simplicity, break list if not starting with -
                    break
            tex_lines.append(r'\end{itemize}')
            continue
            
        if re.match(r'^\s*\d+\.\s+', line):
            # Enumerate
            content = re.sub(r'^\s*\d+\.\s+', '', line)
            tex_lines.append(r'\begin{enumerate}')
            tex_lines.append(r'\item ' + convert_bold_italic(content))
            i += 1
            while i < len(lines):
                next_line = lines[i].rstrip()
                if re.match(r'^\s*\d+\.\s+', next_line):
                    content = re.sub(r'^\s*\d+\.\s+', '', next_line)
                    tex_lines.append(r'\item ' + convert_bold_italic(content))
                    i += 1
                elif next_line.strip() == '':
                    break
                else:
                    break
            tex_lines.append(r'\end{enumerate}')
            continue
            
        # Raw LaTeX commands in markdown
        if line.strip().startswith('\\'):
            tex_lines.append(line)
            i += 1
            continue
            
        # Headers
        if line.startswith('#'):
            tex_lines.append(convert_header(line))
            i += 1
            continue
            
        # Images
        if '![' in line:
            tex_lines.append(convert_images(line))
            i += 1
            continue
            
        # Regular text
        if line.strip() == '':
            tex_lines.append('')
        else:
            # Bold/Italic
            l = convert_bold_italic(line)
            # We don't escape everything aggressively to allow some raw latex if embedded,
            # but for safety let's assume raw text predominantly.
            # However, since we handled headers/lists/tables, this rest is paragraph text.
            # We should probably escape special chars unless it looks like latex.
            # But the MD file has raw latex title page. 
            
            # Heuristic: if line contains { or } or \ then treat carefully?
            # Or just pass through if it looks like the title page stuff.
            if '{' in l and '}' in l and '\\' in l:
                pass # Assume raw latex
            else:
                # Escape restricted set if not raw latex
                pass 
            
            tex_lines.append(l + r' \\')
            
        i += 1

    tex_lines.append(r'\end{document}')
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(tex_lines))
        
    print(f"Generate {output_file}")

if __name__ == "__main__":
    main()
