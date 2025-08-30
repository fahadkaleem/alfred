# Run Tests

## Purpose
Validate implementation integrity by running full test suite and fixing any regressions.

## What to tell the user
"Running full test suite..."

## Phase 1: Run Full Test Suite

```bash
# Find and run the test command (check package.json, Makefile, or README)
npm test
# or
pytest
# or
make test
# or appropriate command for the project
```

## Phase 2: Handle Results

### All Tests Pass
Present success report:
```
✓ Test Suite Results:
  - Total tests: 245
  - All passing
  - Execution time: 12.3s
  - No issues found
```

### Tests Fail

1. **Present Failure Report**
   ```
   ✗ Test Suite Results:
     - Total tests: 245
     - Passing: 242
     - Failing: 3
     
   Failed tests:
   1. UserService > authentication > should reject invalid tokens
      Expected: 401
      Received: 200
      
   2. APIController > rate limiting > should block after 100 requests
      Expected: 429
      Received: 200
   ```

2. **Fix Strategy**
   - If your code broke existing tests: Fix your implementation
   - If tests need updating due to valid changes: Update the tests
   - If unrelated failures: Investigate with user

3. **Get User Input**
   For test updates:
   "Test X expects old behavior Y but we now do Z. Should I update the test to expect the new behavior?"

## Phase 3: Verify Fix

After fixing:
```bash
# Run full suite again
npm test

# If still failing, repeat fix cycle
```

Present final report:
```
✓ Test Suite Results (After Fix):
  - Total tests: 245
  - All passing
  - Fixed: 3 test updates
  - Ready for documentation
```

## Validation Checklist

Before proceeding:
- [ ] Full test suite executed
- [ ] All tests passing
- [ ] Any test updates approved by user
- [ ] Failure root causes understood
- [ ] No tests disabled or skipped

## Self-Check Questions

Ask yourself:
1. Do I understand WHY each test failed?
2. Are my fixes addressing root causes?
3. Will these changes break in future?

If ANY answer is "no", investigate further.

## Next Step
Only after ALL tests pass → Proceed to "Document implementation"