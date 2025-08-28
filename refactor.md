# Alfred Task Manager - Architecture Refactoring Plan

## ✅ REFACTORING COMPLETED (2025-08-27)

**Status**: Successfully refactored to follow clean architecture principles
- All GraphQL queries moved to `clients/linear/` layer  
- LinearAdapter now only transforms data (no API calls)
- Core business logic is platform-agnostic
- All tests passing

## Executive Summary

The current codebase ~~violates~~ **violated** clean architecture principles by having GraphQL queries scattered across multiple layers. This document outlines the issues found and ~~provides a comprehensive refactoring plan~~ **documents the completed refactoring** to properly separate concerns.

## Architecture Issues Found

### 1. GraphQL Queries in Wrong Layer
**Location**: `src/alfred/adapters/linear_adapter.py`

**Problem**: The LinearAdapter contains raw GraphQL queries and mutations, violating the adapter pattern. Examples:
- Lines 474-488: `create_epic()` has raw GraphQL mutation
- Lines 714-727: `rename_epic()` has raw GraphQL mutation  
- Lines 777-783: `delete_epic()` has raw GraphQL mutation
- Lines 820-842: `get_epic_tasks()` has raw GraphQL query

**Impact**: 
- Tight coupling to Linear's GraphQL schema
- Difficult to test without mocking GraphQL responses
- Cannot easily swap Linear for another platform (e.g., Jira)

### 2. Duplication of Responsibilities
**Problem**: Multiple layers implementing the same functionality:
- `LinearClient.projects` (ProjectManager) handles project CRUD operations
- `LinearAdapter` re-implements the same operations with raw GraphQL
- Business logic layer also has GraphQL queries in some places

**Impact**:
- Code duplication and maintenance burden
- Inconsistent error handling
- Confusion about which layer to use

### 3. Incorrect Data Flow
**Current Flow**: 
```
Core Logic → LinearAdapter (with GraphQL) → Linear API
```

**Correct Flow**:
```
Core Logic → LinearAdapter (transform only) → LinearClient → Linear API
```

### 4. Mixed Responsibilities in Adapter
**Problem**: LinearAdapter is doing too much:
- Making direct API calls
- Handling GraphQL queries
- Transforming data models
- Managing error responses

**Should only do**:
- Transform between Linear models and Alfred models
- Delegate API calls to LinearClient

## Proper Architecture Pattern

### Layer Responsibilities

#### 1. **LinearClient + Managers** (`src/alfred/clients/linear/`)
- **Owns**: All GraphQL queries and mutations
- **Handles**: Direct API communication
- **Returns**: Linear domain models
- **Example**: `ProjectManager.create()`, `ProjectManager.update()`

#### 2. **LinearAdapter** (`src/alfred/adapters/linear_adapter.py`)
- **Owns**: Data transformation logic
- **Handles**: Converting between Linear models ↔ Alfred models
- **Uses**: LinearClient for all API operations
- **Example**: Converts `LinearProject` → `EpicDict`

#### 3. **Core Business Logic** (`src/alfred/core/`)
- **Owns**: Business rules and validation
- **Handles**: Platform-agnostic operations
- **Uses**: Adapter interfaces only
- **Example**: Epic management logic without knowing about Linear

## Detailed Refactoring Plan

### Phase 1: Fix LinearAdapter Methods

#### 1.1 Refactor `create_epic()`
**Current**: Contains raw GraphQL mutation
**Target**: Use `self.client.projects.create()`

```python
def create_epic(self, name: str, description: Optional[str] = None) -> EpicDict:
    try:
        # Use LinearClient's ProjectManager
        project = self.client.projects.create(
            name=name,
            description=description,
            team_name=self.team_name
        )
        # Transform LinearProject to EpicDict
        return self._map_linear_project_to_epic(project)
    except Exception as e:
        # Map Linear exceptions to Alfred exceptions
        raise self._map_exception(e)
```

#### 1.2 Refactor `rename_epic()`
**Current**: Contains raw GraphQL mutation
**Target**: Use `self.client.projects.update()`

```python
def rename_epic(self, epic_id: str, new_name: str) -> EpicDict:
    try:
        project = self.client.projects.update(
            project_id=epic_id,
            name=new_name
        )
        return self._map_linear_project_to_epic(project)
    except Exception as e:
        raise self._map_exception(e)
```

#### 1.3 Refactor `delete_epic()`
**Current**: Contains raw GraphQL mutation for archiving
**Target**: Add `archive()` method to ProjectManager or use existing delete

```python
def delete_epic(self, epic_id: str) -> bool:
    try:
        # Note: Linear "archives" projects, doesn't delete them
        return self.client.projects.archive(epic_id)
    except Exception as e:
        raise self._map_exception(e)
```

#### 1.4 Refactor `get_epic_tasks()`
**Current**: Contains raw GraphQL query
**Target**: Use LinearClient's issue filtering

```python
def get_epic_tasks(self, epic_id: str) -> List[TaskDict]:
    try:
        # Use LinearClient to get issues for a project
        issues = self.client.issues.get_by_project(epic_id)
        return [self._map_linear_issue_to_task(issue) for issue in issues]
    except Exception as e:
        raise self._map_exception(e)
```

### Phase 2: Extend LinearClient if Needed

#### 2.1 Add Missing Methods to ProjectManager
- Add `archive()` method if not present
- Add `get_issues()` method to get all issues in a project
- Ensure all needed operations are supported

#### 2.2 Improve Error Handling
- Standardize exception types across LinearClient
- Ensure consistent error messages

### Phase 3: Clean Up Business Logic Layer

#### 3.1 Remove Any Direct GraphQL Usage
- Scan `src/alfred/core/` for any GraphQL queries
- Replace with adapter method calls

#### 3.2 Ensure Platform Agnostic
- Business logic should not import anything from `clients/linear/`
- Only use adapter interfaces

### Phase 4: Testing & Validation

#### 4.1 Unit Tests
- Mock LinearClient for adapter tests
- Mock adapter for business logic tests
- No GraphQL mocking needed

#### 4.2 Integration Tests
- Test full flow: Business → Adapter → Client
- Verify error handling at each layer

## Migration Steps

1. **Backup Current Code** ✓ (git committed)
2. **Fix LinearAdapter Methods** ✓ (COMPLETED)
   - [x] create_epic() - Now uses client.projects.create()
   - [x] rename_epic() - Now uses client.projects.update()
   - [x] delete_epic() - Now uses client.projects.delete()
   - [x] get_epic_tasks() - Now uses client.issues.get_by_project()
3. **Extend ProjectManager if needed** ✓ (NOT NEEDED)
   - [x] ~~Add archive() method~~ - ProjectManager.delete() already handles this
   - [x] ~~Add get_issues_by_project() method~~ - IssueManager already has this
4. **Remove GraphQL from Core** ✓ (COMPLETED)
   - [x] Scan and identify instances
   - [x] Replace with adapter calls in delete.py (now uses adapter methods)
   - [x] Replace with adapter calls in duplicate.py (rewritten to use adapter only)
5. **Update Tests**
   - [x] Fix broken tests - All tests passing
   - [ ] Add new tests for refactored code
6. **Documentation**
   - [x] Update CLAUDE.md - Added comprehensive architecture rules
   - [ ] Update README.md

## Success Criteria

1. **No GraphQL queries outside of `clients/linear/`**
2. **LinearAdapter only transforms data, no API calls**
3. **All tests pass**
4. **Can mock LinearClient for testing adapter**
5. **Business logic has no Linear-specific imports**

## Risk Mitigation

1. **Risk**: Breaking existing functionality
   - **Mitigation**: Test each change thoroughly before moving to next

2. **Risk**: Missing LinearClient functionality
   - **Mitigation**: Extend LinearClient as needed, following existing patterns

3. **Risk**: Performance degradation
   - **Mitigation**: LinearClient has caching, ensure it's utilized

## Timeline Estimate

- Phase 1: 2-3 hours (fix adapter methods)
- Phase 2: 1-2 hours (extend LinearClient if needed)
- Phase 3: 1 hour (clean business logic)
- Phase 4: 2 hours (testing)

**Total**: ~6-8 hours

## Notes

- The LinearClient already has most functionality we need
- ProjectManager may need `archive()` method added
- Consider using LinearClient's caching capabilities
- Maintain backward compatibility during refactor