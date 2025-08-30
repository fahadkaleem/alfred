# Workflow Tools Migration Plan

## Overview
Migrate workflow tools from alfred-mcp to alfred-task-manager following the established architecture pattern.

## Current State
- Workflow logic files copied to `src/alfred/tools/workflow/` (incorrect location)
- These files contain `*_logic()` functions that should be in `core/`
- MCP tool wrappers are missing (they're in alfred-mcp's server.py)

## Target Architecture
```
src/alfred/core/workflow/operations/     # Business logic functions
src/alfred/tools/workflow/               # MCP tool wrappers with register()
```

## Migration Steps

### Phase 1: Create Directory Structure
```bash
mkdir -p src/alfred/core/workflow/operations
```

### Phase 2: Move Logic Files to Core
Move all logic files from tools to core/workflow/operations using mv command:

```bash
# Move each file from tools/workflow/ to core/workflow/operations/
mv src/alfred/tools/workflow/load_instructions.py src/alfred/core/workflow/operations/load_instructions.py
mv src/alfred/tools/workflow/list_workflows.py src/alfred/core/workflow/operations/list_workflows.py
mv src/alfred/tools/workflow/describe_workflow.py src/alfred/core/workflow/operations/describe_workflow.py
mv src/alfred/tools/workflow/assign_workflow.py src/alfred/core/workflow/operations/assign_workflow.py
mv src/alfred/tools/workflow/get_next_phase.py src/alfred/core/workflow/operations/get_next_phase.py
mv src/alfred/tools/workflow/execute_phase.py src/alfred/core/workflow/operations/execute_phase.py
mv src/alfred/tools/workflow/complete_phase.py src/alfred/core/workflow/operations/complete_phase.py
mv src/alfred/tools/workflow/get_progress.py src/alfred/core/workflow/operations/get_progress.py
```

### Phase 3: Rename Functions (if needed)
The functions already have `_logic` suffix, so no renaming needed. Files contain:
- `load_instructions_logic()`
- `list_workflows_logic()`
- `describe_workflow_logic()`
- `assign_workflow_logic()`
- `get_next_phase_logic()`
- `execute_phase_logic()`
- `complete_phase_logic()`
- `get_progress_logic()`

### Phase 4: Copy server.py for Reference
```bash
cp /Users/mohammedfahadkaleem/Documents/ImportantWorkspace/alfred-mcp/src/alfred/server.py src/alfred/tools/workflow/server_reference.py
```

This gives us access to:
- Exact tool descriptions
- Parameter documentation
- Return value documentation
- Examples
- Error conditions
- All docstrings AS IS

### Phase 5: Extract Context Functions from server.py
Since `save_context` and `load_context` don't have separate logic files, we need to:

1. Create logic functions in core:
   - `src/alfred/core/workflow/operations/save_context.py` 
   - `src/alfred/core/workflow/operations/load_context.py`

2. Extract the logic from server.py lines:
   - `save_context`: lines 56-145
   - `load_context`: lines 148-205

### Phase 6: Create MCP Tool Wrappers
Create new tool wrapper files in `src/alfred/tools/workflow/` following the pattern:

```python
def register(server) -> int:
    """Register the [tool_name] tool."""
    
    @server.tool
    def [tool_name](...params...) -> dict:
        """
        [EXACT DOCSTRING FROM server.py INCLUDING ALL SECTIONS]
        """
        result = await [tool_name]_logic(...params...)
        return result.model_dump()
    
    return 1  # Number of tools registered
```

Files to create:
1. `src/alfred/tools/workflow/save_context.py` - Extract from server.py lines 56-145
2. `src/alfred/tools/workflow/load_context.py` - Extract from server.py lines 148-205
3. `src/alfred/tools/workflow/load_instructions.py` - Extract from server.py lines 208-269
4. `src/alfred/tools/workflow/list_workflows.py` - Extract from server.py lines 364-423
5. `src/alfred/tools/workflow/describe_workflow.py` - Extract from server.py lines 424-480
6. `src/alfred/tools/workflow/assign_workflow.py` - Extract from server.py lines 481-567
7. `src/alfred/tools/workflow/get_next_phase.py` - Extract from server.py lines 568-634
8. `src/alfred/tools/workflow/execute_phase.py` - Extract from server.py lines 635-727
9. `src/alfred/tools/workflow/complete_phase.py` - Extract from server.py lines 728-815
10. `src/alfred/tools/workflow/get_progress.py` - Extract from server.py lines 816-904

### Phase 7: Import Updates
After moving files, update imports:

**In core/workflow/operations files:**
- Change `from alfred.core.workflow_engine` to `from alfred.core.workflow.engine`
- Change `from alfred.models.core` to `from alfred.models.workflow`

**In tools/workflow files:**
- Import from `alfred.core.workflow.operations.[module]`
- Import `get_config` from `alfred.config`
- Follow existing pattern from `src/alfred/tools/tasks/`

### Phase 8: Cleanup
```bash
rm src/alfred/tools/workflow/server_reference.py  # Remove temporary reference file
```

## Important Notes

### Preserve ALL Documentation
When creating MCP tool wrappers, preserve EXACTLY:
- Full docstrings with all sections (Parameters, Returns, Examples, Usage notes, Error conditions)
- Parameter descriptions word-for-word
- Example code blocks
- All metadata and type hints

### Tool Registration Pattern
Each tool file must:
1. Import the logic function from `core/workflow/operations/`
2. Define `register(server) -> int` function
3. Use `@server.tool` decorator
4. Return the logic result with `.model_dump()`
5. Return `1` from register function

### Async Handling
- If logic function is async, tool wrapper must be async
- Use `await` when calling logic functions
- Follow the same pattern as existing task tools

## Verification Checklist
- [ ] All logic functions moved to `core/workflow/operations/`
- [ ] All MCP wrappers created in `tools/workflow/`
- [ ] All docstrings preserved exactly from server.py
- [ ] All imports updated to new locations
- [ ] server_reference.py removed after completion
- [ ] All 10 workflow tools properly registered