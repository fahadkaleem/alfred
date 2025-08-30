# Analyze the Codebase

## Goal
Extract COMPREHENSIVE implementation context from the codebase. The developer implementing this task will have ONLY your Plan Artifact - they will NEVER explore the codebase themselves.

## Instructions

### Phase 1: Architecture Overview (PARALLEL EXECUTION)
Execute these searches simultaneously:

```
1. Glob for structure:
   - "**/*.md" (documentation)
   - "**/package.json" or "**/pom.xml" or "**/Gemfile" (dependencies)
   - "**/*config*" (configuration patterns)
   - "**/src/*" or "**/app/*" (source structure)

2. Grep for architecture markers:
   - "class|interface|struct" with context lines
   - "export|module|namespace"
   - "router|controller|service|repository"
```

### Phase 2: Feature-Specific Deep Dive (PARALLEL EXECUTION)
Analyze the ticket and generate comprehensive search patterns using this thinking process:

```
STEP 1: Decompose the feature
Ask yourself:
- What is the core functionality? (e.g., "toggle between themes", "track user activity", "validate input")
- What technical concepts are involved? (e.g., state management, persistence, UI updates)
- What existing patterns might this follow? (e.g., settings, preferences, configuration)

STEP 2: Generate search categories
For YOUR SPECIFIC TASK, create categories like:
- Core functionality terms (what it does)
- Technical implementation terms (how it's built)
- User-facing terms (what users call it)
- Framework/library terms (what tools implement it)
- Related system terms (what it connects to)

STEP 3: Expand each category
For each category, generate:
- Primary terms
- Common synonyms and variations
- Technical abbreviations
- Framework-specific nomenclature
- Related configuration keys
```

Example thinking process:
- Task: "Add dark mode toggle"
- Categories: theme, appearance, dark/light, toggle, switch, preference, persist, CSS variables, localStorage
- Expansions: theme|themes|theming, dark|light|mode, toggle|switch|swap, var|variable|custom-property

Generate AT LEAST 15-20 search terms, but let the task complexity guide you. A simple UI change might need 15 terms, while a complex integration might need 30+.

### Phase 3: Code Pattern Analysis
For EVERY relevant file found:

1. Read the file to understand its structure
2. Document as a NAVIGATION GUIDE:
   ```
   path/to/file.ext:
   - functionName(): Lines X-Y
     - Purpose: What it does in plain English
     - Key details: Important parameters, return values, side effects
     - Dependencies: What it imports/requires
     - Used by: Where this is called from
   ```

3. Focus on UNDERSTANDING, not COPYING:
   - Map the architecture, don't duplicate it
   - Note patterns and conventions with examples
   - Identify integration points with line references
   - Highlight configuration requirements

### Phase 4: Integration Analysis
Identify and document:
- Entry points (routes, controllers, event handlers)
- Data flow (request → validation → business logic → response)
- External dependencies (databases, APIs, services)
- Configuration requirements (env vars, settings)

## Acceptance Criteria

You CANNOT proceed until you have:

- [ ] Found and analyzed ALL relevant source files
- [ ] Created a clear navigation map with file paths and line numbers
- [ ] Documented the complete data flow from entry to exit
- [ ] Identified ALL integration points with precise locations
- [ ] Found and mapped relevant test files and patterns
- [ ] Captured framework-specific patterns and conventions
- [ ] Noted ALL configuration requirements with locations

## Validation Checklist

Ask yourself:
1. Could a developer navigate to every important piece of code using my notes?
2. Have I explained the PURPOSE and PATTERNS, not just copied code?
3. Did I explore beyond the obvious files? (check imports, check callers, check tests)
4. Are there any "magic" conventions I'm assuming the developer knows?
5. Is my artifact reviewable by a human in under 10 minutes?

If ANY answer is "no", continue searching.

## Output Format

Structure your findings as:

```
### Architecture Overview
[Project structure, key patterns, conventions]

### Feature Implementation
[File-by-file breakdown with code examples]

### Integration Points
[How to connect to existing code with examples]

### Testing Patterns
[How similar features are tested with examples]

### Configuration Requirements
[All env vars, settings, with examples]
```

## Next Step
ONLY after meeting ALL acceptance criteria, mark this task as completed and proceed to "Check for existing plans in comments".