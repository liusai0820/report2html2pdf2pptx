# Task Plan: AI Designer Prompt Optimization & Layout Fixes

## Goal
Fix image overflow issues and optimize prompt length using "high information density compression" techniques in `ai_designer.py`.

## Phases
- [ ] Phase 1: Analyze current prompts and overflow issues
- [ ] Phase 2: Design compressed prompts (Prompt Engineering)
- [ ] Phase 3: Implement prompt changes in `ai_designer.py`
- [ ] Phase 4: Verify fixes (Simulation/Review)

## Key Questions
1. Why are images/charts overflowing despite `max-width` constraints?
2. Which parts of the `DESIGNER_SYSTEM_PROMPT` can be replaced with high-level concepts?
3. How to enforce strict layout constraints more effectively?

## Decisions Made
- [Decision]: Use "Concept Compression" (e.g., "Pyramid Principle", "Grid System") to reduce token count.
- [Decision]: Prioritize layout stability (overflow: hidden) over content completeness if necessary.

## Status
**Completed** - Final Polish implemented.

## Decisions Made
- [Decision]: **Language**: Enforced Simplified Chinese for all output (except proper nouns).
- [Decision]: **Layout**: Unified "Top-Left" header style for Content and Agenda pages. **Section Pages** use distinct "Centered Transition" style.
- [Decision]: **Scrollbars**: Globally disabled via injected CSS (`::-webkit-scrollbar { display: none; }`) and System Prompt.
- [Decision]: **Footers**: Removed all "Confidential", "Page X/Y" instructions. Bottom 80px is strictly whitespace.
- [Decision]: **System Prompt**: Further compressed and refined to enforce these strict constraints.

## Completion Notes
- `DESIGNER_SYSTEM_PROMPT` updated with strict bans on scrollbars and footers.
- `_build_outline_prompt` refined for Chinese structure.
- `_build_agenda_prompt` and `_build_section_prompt` aligned with content page headers.
- `_clean_html` now injects global no-scrollbar CSS.
- Syntax verified.

