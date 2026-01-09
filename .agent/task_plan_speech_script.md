# Task Plan: Speech Script Generation Feature

## Goal
Implement a feature that generates a spoken speech script based on the generated presentation and original document, accessible via a button in the presentation UI.

## Phases
- [ ] Phase 1: Exploration & Design
    - [ ] Understand the current presentation generation workflow (backend).
    - [ ] Understand the frontend structure (HTML template) where the button needs to be added.
    - [ ] Determine how to invoke the speech script generation (new API endpoint? existing mechanism?).
    - [ ] Design the prompt for the speech script generation.
- [ ] Phase 2: Backend Implementation
    - [ ] Create the logic to generate the speech script using the LLM.
    - [ ] Integrate with the existing `ai_designer.py` or create a new module.
    - [ ] Ensure it can access both the generated slide content and (optionally) the original document context.
- [ ] Phase 3: Frontend Implementation
    - [ ] Add the "Generate Speech Script" button to the HTML template.
    - [ ] Implement the JavaScript logic to trigger the generation and display the result.
- [ ] Phase 4: Integration & Testing
    - [ ] Verify the end-to-end flow.
    - [ ] Refine the prompt for better "oral" quality.

## Key Questions
1. Where is the HTML template for the presentation stored?
2. How is the data passed to the frontend?
3. Is there a server running to handle the "generate speech script" request, or is this a static HTML file?
    - If it's a static HTML file, how do we trigger the AI generation again?
    - *Hypothesis:* The user mentioned "application", but the output is an HTML file. If it's a standalone HTML, it might be hard to call back to the backend unless there is a backend server running. Or maybe the "application" is a local Python script that generates the HTML, and the user wants this feature *during* the generation process or as a separate step in the tool?
    - *Correction:* The user says "my application is based on user uploaded files...". It sounds like a web app or a local tool. The IDE file path `/Users/qibaoba/report2html2pdf2pptx/...` suggests a local project.
    - *Crucial Check:* If the output is a standalone HTML file opened in the browser, it can't easily call a local Python script unless there's a server. I need to check if there's a web server (Flask/FastAPI) or if this is a CLI tool that generates static files.
    - If it's a CLI tool generating static HTML, the "button" in the HTML might be tricky if it requires backend AI processing *after* the HTML is generated and opened.
    - *Alternative:* Maybe the button triggers a JavaScript call to an API if it's a hosted web app.
    - *Refined Question:* What is the architecture? CLI tool or Web Server?

## Status
**Completed** - All phases finished.

## Decisions Made
- **Architecture**: Implemented as a backend API (`/api/generate-speech`) triggered by a frontend button in the generated HTML.
- **Data Source**: Used `metadata.json` to store context (original document name, outline structure) alongside the generated HTML. This allows reconstructing the context without re-parsing the original document or parsing the HTML.
- **Prompt Strategy**: Combined the original document content (excerpt) with the slide outline (titles and key points) to generate the speech. This ensures the speech is grounded in the original data but structured according to the presentation.
- **UI**: Added a floating action button and a modal dialog directly into the generated HTML template (`output_renderer.py` and `v2/engine.py`). This ensures the feature travels with the HTML file (as long as it's hosted/accessed via the app server).
