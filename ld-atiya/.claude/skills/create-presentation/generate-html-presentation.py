#!/usr/bin/env python3
"""
HTML Presentation Generator for Create-Presentation Skill

Converts enhanced-slides.md with speaker notes to a standalone HTML presentation.
"""

import re
import sys
import os


def convert_markdown_to_html(text):
    """Convert markdown to HTML with proper formatting."""
    # Headers
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)

    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # Mermaid diagrams
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', text, flags=re.DOTALL)
    for mermaid in mermaid_blocks:
        text = text.replace(f'```mermaid\n{mermaid}\n```',
                          f'<div class="mermaid">\n{mermaid}\n</div>')

    # Code blocks (non-mermaid)
    code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', text, flags=re.DOTALL)
    for lang, code in code_blocks:
        if lang != 'mermaid':
            text = text.replace(f'```{lang}\n{code}\n```',
                              f'<pre><code class="language-{lang}">{code}</code></pre>')

    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Tables
    table_pattern = r'\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)'
    tables = re.findall(table_pattern, text)
    for header, rows in tables:
        table_html = '<table>\n<thead><tr>'
        for cell in header.split('|'):
            if cell.strip():
                table_html += f'<th>{cell.strip()}</th>'
        table_html += '</tr></thead>\n<tbody>'

        for row in rows.strip().split('\n'):
            table_html += '<tr>'
            for cell in row.split('|'):
                if cell.strip():
                    table_html += f'<td>{cell.strip()}</td>'
            table_html += '</tr>\n'
        table_html += '</tbody>\n</table>'

        # Replace original table
        original = header + '\n|' + re.search(r'\|([-:\s|]+)\|', text).group(1) + '|\n' + rows
        text = text.replace('|' + original, table_html)

    # Lists
    lines = text.split('\n')
    processed = []
    in_list = False

    for line in lines:
        if re.match(r'^[\-\*\+] ', line):
            if not in_list:
                processed.append('<ul>')
                in_list = True
            item = re.sub(r'^[\-\*\+] (.+)$', r'<li>\1</li>', line)
            processed.append(item)
        else:
            if in_list:
                processed.append('</ul>')
                in_list = False
            processed.append(line)

    if in_list:
        processed.append('</ul>')

    text = '\n'.join(processed)

    # Paragraphs
    lines = text.split('\n')
    final = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
            final.append(f'<p>{line}</p>')
        else:
            final.append(line)

    return '\n'.join(final)


def generate_html_presentation(slides_file, output_file, concept_name):
    """Generate HTML presentation from enhanced-slides.md."""

    # Read the enhanced slides
    with open(slides_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into slides
    slides_raw = content.split('\n---\n')

    # Remove YAML frontmatter from first slide
    if slides_raw[0].startswith('---'):
        slides_raw[0] = re.split(r'^---\n.*?\n---\n', slides_raw[0], 1, flags=re.MULTILINE | re.DOTALL)[-1].strip()

    html_slides = []

    for i, slide_raw in enumerate(slides_raw):
        if not slide_raw.strip():
            continue

        # Extract speaker notes (HTML comments)
        speaker_notes_match = re.search(r'<!--\n(.*?)\n-->', slide_raw, flags=re.DOTALL)
        speaker_notes = speaker_notes_match.group(1).strip() if speaker_notes_match else ""

        # Remove speaker notes from slide content
        slide_content = re.sub(r'<!--.*?-->', '', slide_raw, flags=re.DOTALL).strip()

        # Convert markdown to HTML
        slide_html = convert_markdown_to_html(slide_content)

        # Format speaker notes
        if speaker_notes:
            notes_html = f'''<div class="speaker-notes">
                <h4>Speaker Notes</h4>
                <div class="notes-content">{convert_markdown_to_html(speaker_notes)}</div>
            </div>'''
        else:
            notes_html = ""

        html_slides.append(f'''<section class="slide" id="slide-{i+1}">
            <div class="slide-content">
                {slide_html}
            </div>
            {notes_html}
        </section>''')

    # Create complete HTML
    html_output = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{concept_name.replace('-', ' ').title()} - Presentation</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Arial', sans-serif;
            background: #1a1a1a;
            color: #333;
            overflow: hidden;
        }}

        .slide {{
            display: none;
            width: 100vw;
            height: 100vh;
            background: white;
            position: relative;
        }}

        .slide.active {{
            display: flex;
            flex-direction: column;
        }}

        .slide-content {{
            flex: 1;
            padding: 40px 60px;
            overflow-y: auto;
        }}

        .speaker-notes {{
            background: #f8f9fa;
            border-top: 3px solid #3498db;
            padding: 20px 60px;
            max-height: 30vh;
            overflow-y: auto;
        }}

        .speaker-notes h4 {{
            color: #3498db;
            font-size: 1.2em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}

        .speaker-notes h4:before {{
            content: "📝 ";
            margin-right: 8px;
        }}

        .notes-content {{
            font-size: 0.9em;
            color: #555;
            line-height: 1.6;
        }}

        .notes-content p {{
            margin: 0.5em 0;
            font-size: 1em;
        }}

        .notes-content code {{
            font-size: 0.85em;
        }}

        .notes-content pre {{
            font-size: 0.8em;
            padding: 10px;
            margin: 0.5em 0;
        }}

        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 0.4em;
            border-bottom: 4px solid #3498db;
            padding-bottom: 0.2em;
        }}

        h2 {{
            color: #3498db;
            font-size: 1.8em;
            margin: 0.8em 0 0.4em 0;
        }}

        h3 {{
            color: #555;
            font-size: 1.4em;
            margin: 0.6em 0 0.3em 0;
        }}

        p {{
            font-size: 1.2em;
            line-height: 1.6;
            margin: 0.4em 0;
        }}

        code {{
            background: #ecf0f1;
            padding: 2px 8px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }}

        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 0.8em 0;
            font-size: 1em;
        }}

        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}

        ul {{
            margin: 0.8em 0 0.8em 2em;
            font-size: 1.2em;
        }}

        li {{
            margin: 0.4em 0;
            line-height: 1.5;
        }}

        strong {{
            color: #e74c3c;
            font-weight: bold;
        }}

        .mermaid {{
            background: white;
            padding: 15px;
            margin: 0.8em 0;
            border-radius: 5px;
            display: flex;
            justify-content: center;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0.8em 0;
            font-size: 1.1em;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}

        th {{
            background: #3498db;
            color: white;
        }}

        tr:nth-child(even) {{
            background: #f9f9f9;
        }}

        .controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            display: flex;
            gap: 10px;
        }}

        .btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1em;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .btn:hover {{
            background: #2980b9;
        }}

        .btn-toggle {{
            background: #27ae60;
        }}

        .btn-toggle:hover {{
            background: #229954;
        }}

        .slide-number {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            color: #666;
            font-size: 1.1em;
            z-index: 1000;
            background: rgba(255,255,255,0.9);
            padding: 8px 15px;
            border-radius: 5px;
        }}

        .notes-hidden .speaker-notes {{
            display: none;
        }}

        .columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 0.8em 0;
        }}
    </style>
</head>
<body>
    <div class="presentation">
{chr(10).join(html_slides)}
    </div>

    <div class="slide-number">
        <span id="current-slide">1</span> / <span id="total-slides"></span>
    </div>

    <div class="controls">
        <button class="btn btn-toggle" onclick="toggleNotes()" title="Toggle speaker notes (N)">
            📝 Notes
        </button>
        <button class="btn" onclick="previousSlide()" title="Previous (← or Left Arrow)">
            ← Previous
        </button>
        <button class="btn" onclick="nextSlide()" title="Next (→ or Right Arrow or Space)">
            Next →
        </button>
    </div>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});

        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        let notesVisible = true;

        document.getElementById('total-slides').textContent = totalSlides;

        function showSlide(n) {{
            slides.forEach(slide => slide.classList.remove('active'));
            currentSlide = (n + totalSlides) % totalSlides;
            slides[currentSlide].classList.add('active');
            document.getElementById('current-slide').textContent = currentSlide + 1;
        }}

        function nextSlide() {{
            showSlide(currentSlide + 1);
        }}

        function previousSlide() {{
            showSlide(currentSlide - 1);
        }}

        function toggleNotes() {{
            notesVisible = !notesVisible;
            document.body.classList.toggle('notes-hidden');
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') {{
                e.preventDefault();
                nextSlide();
            }} else if (e.key === 'ArrowLeft') {{
                e.preventDefault();
                previousSlide();
            }} else if (e.key === 'Home') {{
                showSlide(0);
            }} else if (e.key === 'End') {{
                showSlide(totalSlides - 1);
            }} else if (e.key === 'n' || e.key === 'N') {{
                toggleNotes();
            }} else if (e.key === 'f' || e.key === 'F') {{
                document.documentElement.requestFullscreen();
            }}
        }});

        // Show first slide
        showSlide(0);
    </script>
</body>
</html>
'''

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    return len(html_slides)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate-html-presentation.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)

    # Find enhanced-slides.md
    slides_file = os.path.join(folder_path, 'enhanced-slides.md')
    if not os.path.exists(slides_file):
        print(f"Error: enhanced-slides.md not found in {folder_path}")
        sys.exit(1)

    # Extract concept name from directory
    concept_name = os.path.basename(folder_path.rstrip('/'))
    output_file = os.path.join(folder_path, f'{concept_name}-presentation.html')

    # Generate presentation
    try:
        num_slides = generate_html_presentation(slides_file, output_file, concept_name)
        print(f"✅ HTML presentation created: {output_file}")
        print(f"📊 Total slides: {num_slides}")
        print("\nFeatures:")
        print("  ✓ All slide content from enhanced-slides.md")
        print("  ✓ Complete speaker notes")
        print("  ✓ All Mermaid diagrams")
        print("  ✓ Interactive navigation")
        print("\nControls:")
        print("  - Arrow keys / Space: Navigate slides")
        print("  - N: Toggle speaker notes")
        print("  - F: Fullscreen")
        print("  - Home/End: First/Last slide")
        print(f"\nTo view: firefox {output_file}")
    except Exception as e:
        print(f"Error generating presentation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
