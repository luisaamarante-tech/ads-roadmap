# Enhancement Plan: Automatic Field Name Mapping

**Feature**: 004-cli-jira-field-mapping (Enhancement)
**Date**: December 29, 2025
**Type**: Enhancement to existing feature
**Branch**: `004-cli-jira-field-mapping`

## Summary

Enhance the `map-fields` command with automatic field name matching and project-scope filtering. When a custom field name closely matches a configuration key name (e.g., "Roadmap Title" → `roadmap_title`), automatically pre-select it. Only show fields that are scoped to the specific project (not global fields).

## User Request

> "I want a small change to map automatically the fields based on their name, if not found you can ask interactively. I also want only project-scope fields."

## Technical Context

**Language/Version**: Python 3.14 (existing)
**Primary Dependencies**: Flask, Click, Requests (existing)
**Storage**: JSON configuration (existing)
**Testing**: pytest (existing)
**Changes Required**: Modify existing `map-fields` command in `backend/app/cli/jira_setup.py`

## Enhancement Requirements

### 1. Automatic Name-Based Mapping

**Current Behavior**:
- User must manually select from numbered menu for all 13 fields
- No intelligent pre-selection

**New Behavior**:
- System attempts fuzzy name matching for each config key
- If high-confidence match found (>80% similarity), auto-select and display
- If no match or low confidence, fallback to interactive prompt
- User can override auto-selections before saving

**Matching Algorithm**:
```python
Config Key              → Expected Field Names (fuzzy match)
"roadmap_title"        → "Roadmap Title", "Public Title", "Title"
"roadmap_description"  → "Roadmap Description", "Public Description", "Description"
"roadmap_image_url_1"  → "Image URL 1", "Roadmap Image 1", "Image 1"
"public_roadmap"       → "Public Roadmap", "Show in Roadmap", "Public"
"roadmap_status"       → "Roadmap Status", "Delivery Status", "Status"
"module"               → "Module", "Product Module", "Area"
"release_year"         → "Release Year", "Year"
"release_quarter"      → "Release Quarter", "Quarter"
"release_month"        → "Release Month", "Month"
"documentation_url"    → "Documentation URL", "Docs URL", "Documentation"
```

**Implementation Approach**:
- Use difflib.SequenceMatcher for fuzzy string matching
- Normalize strings (lowercase, remove special chars, handle spaces)
- Set confidence threshold: 0.8 (80% match required for auto-selection)
- Display auto-matched fields with option to change

### 2. Project-Scope Field Filtering

**Current Behavior**:
- Returns all custom fields visible to the user
- May include global/shared fields across multiple projects

**New Behavior**:
- Filter fields to only those scoped specifically to the project
- Exclude global custom fields that appear across all projects

**JIRA API Context**:
The `/rest/api/3/field` endpoint returns ALL custom fields, including:
- **Project-scoped**: Field configured for specific project(s)
- **Global**: Field available across all projects

To determine field scope, we need to:
1. Call `/rest/api/3/field/{fieldId}/context` for each field
2. Check if contexts are project-specific or global
3. Filter to only fields with contexts matching the target project

**Alternative Approach** (simpler):
Check if field has `projectIds` or `issueTypeIds` restrictions. Global fields typically have no restrictions.

## Constitution Check

### Clean Code & Readability ✅
- Enhancement fits within existing function structure
- Uses helper functions for matching logic
- Maintains single responsibility

### Code Style Standards ✅
- Follows existing PEP 8 style
- Type hints for new functions
- Clear docstrings

### Naming Conventions ✅
- `fuzzy_match_field_name()` for matching logic
- `filter_project_scoped_fields()` for filtering
- `auto_map_fields()` for automatic mapping

### Testing & Quality ⚠️
- **REQUIRED**: Unit tests for fuzzy matching algorithm
- **REQUIRED**: Unit tests for project-scope filtering
- **REQUIRED**: CLI tests for auto-mapping flow
- Must maintain 80% coverage

### Impact Assessment ✅
- Non-breaking change (existing behavior preserved)
- Improves user experience (fewer manual selections)
- No changes to data models or API contracts

## Phase 0: Research

### Research Areas

#### 1. Fuzzy String Matching in Python

**Decision**: Use Python's built-in `difflib.SequenceMatcher`

**Rationale**:
- No additional dependencies required
- Proven algorithm (Ratcliff/Obershelp)
- Good balance of speed and accuracy
- Returns similarity ratio 0.0-1.0

**Implementation**:
```python
from difflib import SequenceMatcher

def fuzzy_match_score(str1: str, str2: str) -> float:
    """Calculate similarity between two strings (0.0-1.0)."""
    # Normalize strings
    s1 = str1.lower().replace("_", " ").replace("-", " ")
    s2 = str2.lower().replace("_", " ").replace("-", " ")

    return SequenceMatcher(None, s1, s2).ratio()
```

**Alternatives Considered**:
- **Levenshtein distance** (fuzzywuzzy library): More accurate but requires external dependency
- **Regex matching**: Too rigid, wouldn't handle variations well
- **Exact matching**: Already considered, too strict

#### 2. JIRA Custom Field Context API

**Decision**: Use `/rest/api/3/field/{fieldId}/context` to determine field scope

**Rationale**:
- Official JIRA API for checking field contexts
- Returns project restrictions for each field
- Can filter by isGlobalContext flag

**API Response Structure**:
```json
{
  "values": [
    {
      "id": "10100",
      "name": "Default context",
      "isGlobalContext": false,
      "projectIds": ["10000"],
      "issueTypeIds": ["10001"]
    }
  ]
}
```

**Filtering Logic**:
```python
def is_project_scoped(field_id: str, project_key: str, client: JiraClient) -> bool:
    """Check if field is scoped to specific project."""
    contexts = client.get_field_contexts(field_id)

    # Filter out global contexts
    project_contexts = [c for c in contexts if not c.get("isGlobalContext", True)]

    # Check if any context matches our project
    # Note: Would need to map project_key to project_id first
    return len(project_contexts) > 0
```

**Performance Consideration**:
- Each field requires separate API call
- For 50 fields, this is 50 API calls
- **Optimization**: Batch process or cache results
- **Alternative**: Accept this overhead as it's a one-time setup operation

**Simpler Alternative**:
Many JIRA instances use naming conventions or field descriptions to indicate project-specific fields. Could add a flag `--all-fields` to show global fields if needed, defaulting to showing all (current behavior) to avoid API overhead.

#### 3. User Experience Flow

**Decision**: Show auto-matched fields first, then prompt for unmatched

**Rationale**:
- Reduces cognitive load (user sees what was auto-detected)
- Allows verification before commitment
- Maintains control (user can override)

**Enhanced Flow**:
```
1. Retrieve custom fields
2. Filter to project-scoped (if requested)
3. Attempt automatic matching for all 13 config keys
4. Display summary:
   ✓ Auto-matched: 8 fields
   ? Need input: 5 fields
5. Show auto-matched fields with option to change
6. Prompt interactively for unmatched fields
7. Display final summary and confirm
```

## Phase 1: Design

### Data Model Changes

**No changes to existing data models** - Enhancement works with existing structures:
- `CustomFieldMetadata` (unchanged)
- `FieldMapping` (unchanged)
- `ProjectFieldConfiguration` (unchanged)

### New Helper Functions

```python
def normalize_string(s: str) -> str:
    """Normalize string for comparison."""
    return s.lower().replace("_", " ").replace("-", " ").strip()

def fuzzy_match_score(str1: str, str2: str) -> float:
    """Calculate similarity score between strings (0.0-1.0)."""
    from difflib import SequenceMatcher
    s1 = normalize_string(str1)
    s2 = normalize_string(str2)
    return SequenceMatcher(None, s1, s2).ratio()

def auto_match_field(config_key: str, available_fields: list) -> Optional[CustomFieldMetadata]:
    """
    Automatically match a config key to a custom field by name.

    Returns:
        Best matching field if confidence > 0.8, None otherwise
    """
    # Generate expected field names for config key
    expected_names = generate_expected_names(config_key)

    best_match = None
    best_score = 0.0

    for field in available_fields:
        for expected in expected_names:
            score = fuzzy_match_score(field.name, expected)
            if score > best_score:
                best_score = score
                best_match = field

    # Return match only if confidence is high
    return best_match if best_score >= 0.8 else None

def generate_expected_names(config_key: str) -> list[str]:
    """Generate list of expected field names for a config key."""
    mappings = {
        "roadmap_title": ["Roadmap Title", "Public Title", "Title"],
        "roadmap_description": ["Roadmap Description", "Public Description", "Description"],
        "roadmap_image_url_1": ["Image URL 1", "Roadmap Image 1", "Image 1"],
        "roadmap_image_url_2": ["Image URL 2", "Roadmap Image 2", "Image 2"],
        "roadmap_image_url_3": ["Image URL 3", "Roadmap Image 3", "Image 3"],
        "roadmap_image_url_4": ["Image URL 4", "Roadmap Image 4", "Image 4"],
        "public_roadmap": ["Public Roadmap", "Show in Roadmap", "Public"],
        "roadmap_status": ["Roadmap Status", "Delivery Status", "Status"],
        "module": ["Module", "Product Module", "Area", "Component"],
        "release_year": ["Release Year", "Year"],
        "release_quarter": ["Release Quarter", "Quarter"],
        "release_month": ["Release Month", "Month"],
        "documentation_url": ["Documentation URL", "Docs URL", "Documentation", "Docs"],
    }
    return mappings.get(config_key, [config_key.replace("_", " ").title()])

def get_field_context(client: JiraClient, field_id: str) -> dict:
    """Get field context information from JIRA."""
    endpoint = f"/rest/api/3/field/{field_id}/context"
    try:
        return client._make_request(endpoint)
    except:
        return {"values": []}

def is_project_scoped_field(field_id: str, project_key: str, client: JiraClient) -> bool:
    """Check if custom field is scoped to specific project."""
    context = get_field_context(client, field_id)

    for ctx in context.get("values", []):
        # Global context = available everywhere
        if ctx.get("isGlobalContext", True):
            return False

        # Check if project is in the context's project list
        project_ids = ctx.get("projectIds", [])
        # Note: This requires mapping project_key to project_id
        # Simplified: if has project restrictions, consider it project-scoped
        if project_ids:
            return True

    return True  # If no contexts, assume project-scoped (conservative)
```

### Modified Command Flow

```python
@jira_cli.command("map-fields")
# ... existing parameters ...
@click.option("--no-auto-match", is_flag=True, help="Disable automatic field name matching")
@click.option("--include-global", is_flag=True, help="Include global custom fields (default: project-scoped only)")
def map_fields(..., no_auto_match: bool, include_global: bool):
    """Map custom fields with automatic name matching."""

    # 1. Retrieve fields (existing)
    fields = client.get_custom_fields(proj_key)

    # 2. NEW: Filter to project-scoped fields
    if not include_global:
        click.echo("Filtering to project-scoped fields...")
        fields = [f for f in fields if is_project_scoped_field(f.id, proj_key, client)]

    # 3. Filter by type (existing)
    if not show_all_types:
        fields = client.filter_text_fields(fields)

    # 4. NEW: Attempt automatic matching
    auto_matched = {}
    unmatched = []

    if not no_auto_match:
        click.echo("\nAttempting automatic field matching...")
        for config_key in config_keys:
            match = auto_match_field(config_key, fields)
            if match:
                auto_matched[config_key] = match
                click.echo(f"  ✓ {config_key}: {match.name} ({match.id}) [confidence: {fuzzy_match_score(config_key, match.name):.0%}]")
            else:
                unmatched.append(config_key)

        click.echo(f"\nAuto-matched: {len(auto_matched)} fields")
        click.echo(f"Need input: {len(unmatched)} fields")
        click.echo()

        # 5. Review auto-matched fields
        if auto_matched and click.confirm("Review auto-matched fields?", default=False):
            for config_key, field in auto_matched.items():
                if not click.confirm(f"  Use {field.name} for {config_key}?", default=True):
                    unmatched.append(config_key)
                    auto_matched.pop(config_key)
    else:
        unmatched = config_keys

    # 6. Interactive prompts for unmatched (existing logic)
    mappings = []

    # Add auto-matched fields
    for config_key, field in auto_matched.items():
        mapping = FieldMapping(
            config_key=config_key,
            field_id=field.id,
            field_name=field.name,
            is_selected=True
        )
        mappings.append(mapping)

    # Prompt for unmatched fields (existing interactive logic)
    for config_key in unmatched:
        # ... existing prompt logic ...
        pass

    # 7. Continue with existing confirmation and save logic
    # ...
```

## Contract Changes

### CLI Command Updates

**New Flags**:
```bash
flask jira map-fields PROJECT_KEY [OPTIONS]

OPTIONS:
  --no-auto-match         Disable automatic field name matching
  --include-global        Include global custom fields (default: project-scoped only)
  --show-all-types        Show all field types (not just text) [existing]
  --dry-run              Preview changes without writing [existing]
  --all                  Map fields for all projects [existing]
```

**Backward Compatibility**: ✅
- All new flags are optional
- Default behavior is enhanced (auto-matching enabled)
- Users can opt-out with `--no-auto-match`
- Existing scripts continue to work

## Testing Requirements

### New Test Cases

1. **Fuzzy Matching Tests**:
   - Test exact name matches (100% confidence)
   - Test close matches (>80% confidence)
   - Test no matches (<80% confidence)
   - Test with special characters and spacing

2. **Project Scope Tests**:
   - Test filtering project-scoped fields
   - Test excluding global fields
   - Test with `--include-global` flag

3. **CLI Integration Tests**:
   - Test auto-matching flow
   - Test review and override flow
   - Test fallback to interactive mode
   - Test with `--no-auto-match` flag

### Test Coverage Target

- Maintain 80% coverage (constitution requirement)
- New functions must have dedicated unit tests
- CLI flow must have integration tests

## Implementation Estimate

**Complexity**: Small (Enhancement)
**Estimated Effort**: 4-6 hours

**Breakdown**:
- Helper functions (fuzzy matching, scope filtering): 1-2 hours
- Command flow modification: 1-2 hours
- Testing: 1-2 hours
- Documentation: 30 minutes

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fuzzy matching false positives | Medium | Set high confidence threshold (0.8), allow review |
| API overhead for scope checking | Low | Make it optional, cache results |
| Breaking existing workflows | Low | All new features are opt-in flags |
| Test coverage drops | Medium | Write tests first (TDD) |

## Success Criteria

1. ✅ Auto-matching correctly identifies >70% of fields in typical JIRA setup
2. ✅ User can complete mapping in <1 minute (vs 2-3 minutes currently)
3. ✅ Project-scoped filtering reduces field list by >30% in multi-project environments
4. ✅ Zero breaking changes to existing functionality
5. ✅ Test coverage remains >80%

## Rollout Plan

1. **Development**: Implement enhancement on `004-cli-jira-field-mapping` branch
2. **Testing**: Unit tests + manual testing with real JIRA
3. **Documentation**: Update quickstart.md with new flags
4. **Review**: Code review focusing on backward compatibility
5. **Merge**: Merge to main after approval
6. **Deploy**: Release as part of next version

## Alternatives Considered

### Alternative 1: ML-Based Matching
**Rejected**: Overkill for this use case, adds complexity

### Alternative 2: Configuration File for Mappings
**Rejected**: Fuzzy matching is more flexible and requires no setup

### Alternative 3: API Call to Get Field Contexts
**Accepted**: But made optional via flag to reduce API overhead

## Open Questions

1. **Q**: Should auto-matching be enabled by default?
   **A**: Yes, with option to disable via `--no-auto-match`

2. **Q**: What confidence threshold for auto-matching?
   **A**: 0.8 (80%) - balances accuracy and automation

3. **Q**: Handle project-scope checking performance?
   **A**: Make optional with `--include-global` flag (default excludes global)

## Next Steps

1. ✅ Create this enhancement plan
2. ⏭️ Run `/speckit.tasks` to generate implementation tasks
3. ⏭️ Implement changes to `map-fields` command
4. ⏭️ Write unit and integration tests
5. ⏭️ Update documentation
6. ⏭️ Test with real JIRA instance
7. ⏭️ Submit for review

---

**This enhancement improves the user experience of the already-complete CLI JIRA field mapping feature by reducing manual input through intelligent auto-matching and focusing on project-relevant fields.**
