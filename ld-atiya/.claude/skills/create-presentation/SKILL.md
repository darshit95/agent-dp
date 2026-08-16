---
name: create-presentation
description: Transform learning materials into enhanced presentations with smart diagrams and speaker notes
---

# Create Presentation

Transform your learning materials into enhanced presentations with visual diagrams and rich speaker notes.

## Usage

```bash
# With folder path (direct execution)
/create-presentation /path/to/folder

# Without folder path (prompts for input)
/create-presentation
→ "Which folder contains your learning materials?"
→ User provides path
→ Skill executes
```

**IMPORTANT:** When invoked without a folder path argument, the skill MUST:
1. Ask user: "Which folder contains your learning materials for the presentation?"
2. Wait for user response
3. Validate the provided path exists
4. Then proceed with the workflow

Do NOT assume or guess the folder path.

## What It Does

**Input:** Folder with `*-slides.md` + `complete-learning.md` or `<topic>.md`  
**Output:** `<concept>-presentation.html` (standalone HTML presentation)

## Intelligence Features

### Content Enhancement
- Identifies gaps in explanations → fills from full content
- Improves unclear sections → restructures for clarity
- Adds missing context → enriches with examples
- Ensures consistency → uniform depth and tone

### Smart Diagrams
Generates Mermaid diagrams automatically for:
- Architecture (component relationships)
- Flows (request/response, sequences)
- State Machines (circuit breakers, lifecycles)
- Comparisons (trade-offs, tables)
- Timelines (deployment, debugging)

### Speaker Notes
- Deep-dive content from `<topic>.md`
- Real-world examples and edge cases
- Implementation details and gotchas
- Keeps slides concise while enriching presentation

## Workflow

**Step 0: Get Folder Path (if not provided)**
- If invoked without folder path: Ask user "Which folder contains your learning materials?"
- Wait for user to provide path
- Validate folder exists and contains required files

**Step 1: Analyze**
- Read `*-slides.md` (quick reference structure)
- Read `complete-learning.md` or `<topic>.md` (full content)
- Identify content gaps and enhancement opportunities

**Step 2: Enhance**
- Add Mermaid diagrams for visual concepts
- Enrich explanations with context from full content
- Generate speaker notes with implementation details

**Step 3: Generate**
- Create `enhanced-slides.md` (Markdown with Mermaid) as reference
- Generate `<concept>-presentation.html` (standalone HTML presentation)
- Output both files to the source folder
- Extract concept name from directory name (e.g., `model-provider-abstraction` → `model-provider-abstraction-presentation.html`)

## Example

**Input:**
```markdown
## Circuit Breaker
CLOSED → OPEN → HALF-OPEN
```

**Output:**
- Clear explanation with problem/solution
- State diagram with transitions
- Speaker notes with timeline example

## Requirements

**Python 3** - Already available in your environment

No additional tools needed! The skill generates a standalone HTML presentation.

## Output Files

After skill completes:

1. **`<concept>-presentation.html`** - Interactive HTML presentation
   - Open in any browser (Firefox, Chrome, Edge)
   - Full-featured with Mermaid diagrams
   - Speaker notes included
   - Keyboard navigation
   
2. **`enhanced-slides.md`** - Markdown source with Mermaid diagrams
   - Backup/reference format
   - Can be edited and regenerated

## How to Use the Presentation

**Present directly:**
```bash
# Open in browser
firefox <concept>-presentation.html
```

**Controls:**
- Arrow keys / Space: Navigate slides
- `N`: Toggle speaker notes on/off
- `F`: Fullscreen mode
- Home/End: Jump to first/last slide

**Convert to Google Slides (if needed):**
1. Open HTML in browser → Print (`Ctrl+P`)
2. Save as PDF (Landscape, No margins)
3. Upload PDF to Google Drive
4. Open with Google Slides

## Implementation Notes

**For Claude executing this skill:**

After creating `enhanced-slides.md`, use the provided generator script to create the HTML presentation:

```bash
/home/test/reg/bin/python /home/test/reg/agent-dp/ld-atiya/.claude/skills/create-presentation/generate-html-presentation.py <folder_path>
```

The script will:
1. Read `enhanced-slides.md` from the provided folder
2. Extract the concept name from the directory name
3. Generate `<concept>-presentation.html` in the same folder
4. Include all speaker notes, Mermaid diagrams, and interactive features

Example:
- Folder: `/path/to/model-provider-abstraction/`
- Output: `/path/to/model-provider-abstraction/model-provider-abstraction-presentation.html`

## Ready?

```bash
/create-presentation /path/to/folder
```

The skill will create a complete HTML presentation ready to present!
