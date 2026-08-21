"""Simple documentation viewer with authentication.

Copyright 2026 Palo Alto Networks.
All Rights reserved. Confidential
"""

import os
from pathlib import Path
from functools import wraps
import markdown
from flask import Flask, render_template, send_file, request, redirect, url_for, session, make_response

app = Flask(__name__)
app.secret_key = 'dpandit-doc-viewer-secret-key-2026'

# Configuration
USERNAME = 'dpandit'
PASSWORD = 'dpandit'
DOCS_DIR = Path('/home/test/reg/agent-dp/ld-atiya/learn-and-build/learning-docs/all-topics')


def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logout user."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main documentation index page."""
    total_docs = 0

    def build_tree(directory, level=0):
        """Build hierarchical tree structure of folders and files."""
        if not directory.exists() or not directory.is_dir():
            return []

        nodes = []
        for item in sorted(directory.iterdir()):
            if not item.is_dir():
                continue

            # Collect files in this directory
            files = []
            for html_file in sorted(item.glob('*.html')):
                rel_path = html_file.relative_to(DOCS_DIR)
                files.append({
                    'name': html_file.name,
                    'path': str(rel_path),
                    'type': 'html'
                })

            for md_file in sorted(item.glob('*.md')):
                rel_path = md_file.relative_to(DOCS_DIR)
                files.append({
                    'name': md_file.name,
                    'path': str(rel_path),
                    'type': 'markdown'
                })

            # Recursively get children
            children = build_tree(item, level + 1)

            # Only include this node if it has files or children with files
            if files or children:
                node = {
                    'name': item.name,
                    'display_name': item.name.replace('-', ' ').title(),
                    'files': files,
                    'children': children,
                    'level': level,
                    'has_children': len(children) > 0
                }
                nodes.append(node)

        return nodes

    def count_docs(nodes):
        """Count total documents in tree."""
        count = 0
        for node in nodes:
            count += len(node['files'])
            if node['children']:
                count += count_docs(node['children'])
        return count

    def count_topics(nodes):
        """Count total topics (folders) in tree."""
        count = len(nodes)
        for node in nodes:
            if node['children']:
                count += count_topics(node['children'])
        return count

    # Build the tree structure
    tree = []
    total_docs = 0
    total_topics = 0
    if DOCS_DIR.exists():
        tree = build_tree(DOCS_DIR)
        total_docs = count_docs(tree)
        total_topics = count_topics(tree)

    return render_template('index.html', tree=tree, total_docs=total_docs, count_topics=total_topics)


@app.route('/view/<path:file_path>')
@login_required
def view_file(file_path):
    """View an HTML or Markdown file."""
    full_path = DOCS_DIR / file_path

    # Security check: ensure the file is within DOCS_DIR
    try:
        full_path = full_path.resolve()
        DOCS_DIR.resolve()
        if not str(full_path).startswith(str(DOCS_DIR.resolve())):
            return "Access denied", 403
    except Exception:
        return "File not found", 404

    if full_path.exists() and full_path.is_file():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if it's a markdown file
        if full_path.suffix.lower() in ['.md', '.markdown']:
            # Convert markdown to HTML with proper code block handling
            md = markdown.Markdown(
                extensions=['extra', 'fenced_code', 'tables'],
                extension_configs={
                    'fenced_code': {
                        'lang_prefix': 'language-'
                    }
                }
            )
            html_content = md.convert(content)

            # Wrap in HTML template with dark styling and diagram support
            html_page = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{full_path.name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #0a0a0a;
            color: #e0e0e0;
        }}
        .markdown-content {{
            background: rgba(23, 23, 23, 0.9);
            padding: 50px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 32px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.3;
            color: #ffffff;
            letter-spacing: -0.3px;
        }}
        h1 {{
            font-size: 2.5em;
            border-bottom: 2px solid rgba(99, 102, 241, 0.3);
            padding-bottom: 12px;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        h2 {{
            font-size: 2em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 10px;
            color: #d0d0d0;
        }}
        h3 {{ font-size: 1.5em; color: #c0c0c0; }}
        h4 {{ font-size: 1.25em; color: #b0b0b0; }}
        h5, h6 {{ font-size: 1.1em; color: #a0a0a0; }}
        p {{
            margin: 16px 0;
            color: #d0d0d0;
        }}
        code {{
            background: rgba(99, 102, 241, 0.1);
            color: #c792ea;
            padding: 3px 8px;
            border-radius: 5px;
            font-family: 'JetBrains Mono', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}
        pre {{
            background: rgba(15, 15, 15, 0.9);
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 20px 0;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
        }}
        pre code {{
            background: none;
            padding: 0;
            border: none;
            color: #89ddff;
            font-size: 0.95em;
            line-height: 1.6;
        }}
        blockquote {{
            border-left: 4px solid #6366f1;
            padding: 12px 20px;
            background: rgba(99, 102, 241, 0.05);
            color: #b0b0b0;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        table th, table td {{
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 16px;
            text-align: left;
        }}
        table th {{
            background: rgba(99, 102, 241, 0.15);
            font-weight: 600;
            color: #ffffff;
        }}
        table tr:nth-child(even) {{
            background: rgba(255, 255, 255, 0.02);
        }}
        table tr:hover {{
            background: rgba(99, 102, 241, 0.08);
        }}
        a {{
            color: #6366f1;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.3s;
        }}
        a:hover {{
            border-bottom-color: #6366f1;
        }}
        ul, ol {{
            padding-left: 28px;
            margin: 16px 0;
        }}
        li {{
            margin: 8px 0;
            color: #d0d0d0;
        }}
        hr {{
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin: 32px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
        strong {{
            color: #ffffff;
            font-weight: 600;
        }}
        em {{
            color: #c0c0c0;
        }}
        /* Mermaid diagram styling */
        .mermaid {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 20px;
            margin: 24px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        /* Force all Mermaid nodes to use dark backgrounds */
        .mermaid .node rect,
        .mermaid .node circle,
        .mermaid .node ellipse,
        .mermaid .node polygon,
        .mermaid .node path {{
            fill: #2d2d3d !important;
            stroke: #6366f1 !important;
            stroke-width: 2px !important;
        }}
        /* Force all Mermaid text to be light colored */
        .mermaid .nodeLabel,
        .mermaid .label,
        .mermaid text,
        .mermaid .node text,
        .mermaid tspan {{
            fill: #e0e0e0 !important;
            color: #e0e0e0 !important;
        }}
        /* Style edge labels */
        .mermaid .edgeLabel {{
            background-color: #1e1e2e !important;
            color: #e0e0e0 !important;
        }}
        .mermaid .edgeLabel rect {{
            fill: #1e1e2e !important;
        }}
        /* Style markers/arrows */
        .mermaid marker {{
            fill: #6366f1 !important;
            stroke: #6366f1 !important;
        }}
        /* Style cluster/subgraph backgrounds */
        .mermaid .cluster rect {{
            fill: #1a1a2e !important;
            stroke: #6366f1 !important;
        }}
        /* Syntax highlighting for code */
        .codehilite {{
            background: rgba(15, 15, 15, 0.9);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body>
    <div class="markdown-content">
        {html_content}
    </div>
    <script>
        // Convert markdown code blocks to Mermaid divs
        document.addEventListener('DOMContentLoaded', function() {{
            // Find all code blocks that might contain mermaid diagrams
            const codeBlocks = document.querySelectorAll('pre code');

            codeBlocks.forEach(function(codeBlock) {{
                const text = codeBlock.textContent.trim();
                const className = codeBlock.className || '';

                // Check if it's marked as mermaid or looks like a mermaid diagram
                const isMermaid = className.includes('mermaid') ||
                                 className.includes('language-mermaid') ||
                                 text.match(/^(graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|flowchart)/);

                if (isMermaid) {{
                    // Create a new div with class mermaid
                    const mermaidDiv = document.createElement('div');
                    mermaidDiv.className = 'mermaid';
                    mermaidDiv.textContent = text;

                    // Replace the pre element with the mermaid div
                    const preElement = codeBlock.parentElement;
                    preElement.parentElement.replaceChild(mermaidDiv, preElement);
                }}
            }});

            // Initialize Mermaid after conversion
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                themeVariables: {{
                    // Dark theme base colors
                    darkMode: true,
                    background: '#0a0a0a',

                    // Primary node colors (rectangles, default shapes)
                    primaryColor: '#2d2d3d',
                    primaryTextColor: '#e0e0e0',
                    primaryBorderColor: '#6366f1',

                    // Secondary node colors
                    secondaryColor: '#1e1e2e',
                    secondaryTextColor: '#e0e0e0',
                    secondaryBorderColor: '#a855f7',

                    // Tertiary colors
                    tertiaryColor: '#252535',
                    tertiaryTextColor: '#e0e0e0',
                    tertiaryBorderColor: '#6366f1',

                    // Note/special box colors
                    noteBkgColor: '#2d2d3d',
                    noteTextColor: '#e0e0e0',
                    noteBorderColor: '#6366f1',

                    // Lines and arrows
                    lineColor: '#6366f1',
                    arrowheadColor: '#6366f1',

                    // Text colors
                    textColor: '#e0e0e0',
                    mainBkg: '#2d2d3d',
                    secondBkg: '#1e1e2e',

                    // Node-specific backgrounds to ensure all are dark
                    nodeBkg: '#2d2d3d',
                    nodeBorder: '#6366f1',
                    clusterBkg: '#1a1a2e',
                    clusterBorder: '#6366f1',
                    defaultLinkColor: '#6366f1',
                    titleColor: '#e0e0e0',
                    edgeLabelBackground: '#1e1e2e',

                    // Actor colors (for sequence diagrams)
                    actorBkg: '#2d2d3d',
                    actorBorder: '#6366f1',
                    actorTextColor: '#e0e0e0',
                    actorLineColor: '#6366f1',
                    signalColor: '#e0e0e0',
                    signalTextColor: '#e0e0e0',
                    labelBoxBkgColor: '#2d2d3d',
                    labelBoxBorderColor: '#6366f1',
                    labelTextColor: '#e0e0e0',
                    loopTextColor: '#e0e0e0',
                    activationBorderColor: '#6366f1',
                    activationBkgColor: '#1e1e2e',
                    sequenceNumberColor: '#0a0a0a',

                    // Font settings
                    fontSize: '16px',
                    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                }}
            }});

            // Manually trigger mermaid rendering
            mermaid.run();
        }});
    </script>
</body>
</html>
"""
            content = html_page

        response = make_response(content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return "File not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
