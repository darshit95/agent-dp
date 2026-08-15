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

**Input:** Folder with `*-slides.md` + `<topic>.md`  
**Output:** `enhanced-slides.md` + `presentation.pptx`

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
- Create `enhanced-slides.md` (Markdown with Mermaid)
- Generate `presentation.pptx` using Marp CLI
- Output both files to the source folder

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

```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli
```

## Ready?

```bash
/create-presentation /path/to/folder
```

Upload the generated `presentation.pptx` to Google Drive and open with Google Slides to edit!
