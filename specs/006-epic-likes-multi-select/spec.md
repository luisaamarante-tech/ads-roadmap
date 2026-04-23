# Feature Specification: Epic Likes and Multi-Module Selection

**Feature Branch**: `006-epic-likes-multi-select`
**Created**: 2026-01-20
**Status**: Draft
**Input**: User description: "I want you to implement the "Like" functionality where users can click on like in the epics and we update a JIRA epic field for this. In the same way when we're retrieving data from JIRA it should retrieve the number of likes and show to the user based on how much is there in JIRA. Remember, no databases, JIRA is the database. Also update the map field to map this new field that will be called "Roadmap Likes". The other thing to implement is enable multi-selection for modules instead of single selection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Like Count on Epics (Priority: P1)

Users can see how many likes each roadmap epic has received, helping them understand which features are most popular with the community.

**Why this priority**: This is the foundation for the likes feature - users need to see existing like counts before they can interact with them. It's the most basic value delivery and can be independently tested.

**Independent Test**: Can be fully tested by loading the roadmap and verifying that like counts from JIRA are displayed on each epic card, even without the ability to add new likes.

**Acceptance Scenarios**:

1. **Given** a roadmap epic has 15 likes in JIRA, **When** the user views the roadmap, **Then** the epic card displays "15 likes"
2. **Given** a roadmap epic has 0 likes in JIRA, **When** the user views the roadmap, **Then** the epic card displays "0 likes" or hides the like count
3. **Given** the roadmap data is synced from JIRA, **When** like counts are updated in JIRA, **Then** the next sync reflects the updated counts

---

### User Story 2 - Like an Epic (Priority: P2)

Users can express interest in a roadmap epic by clicking a like button, which increments the like count both in the UI and in JIRA.

**Why this priority**: This enables user engagement and feedback collection. It depends on P1 (viewing likes) but delivers independent value by allowing users to vote on features.

**Independent Test**: Can be tested by clicking the like button on an epic, verifying the count increments in the UI, and confirming the JIRA custom field is updated.

**Acceptance Scenarios**:

1. **Given** an epic with 5 likes, **When** a user clicks the like button, **Then** the count increases to 6 and the JIRA field is updated
2. **Given** a user clicks the like button, **When** the update succeeds, **Then** the button shows visual feedback (e.g., filled heart icon)
3. **Given** a user has already liked an epic, **When** they click the like button again, **Then** the like is removed (count decreases by 1)
4. **Given** the JIRA API is unavailable, **When** a user tries to like an epic, **Then** an error message is shown and the count doesn't change

---

### User Story 3 - Filter by Multiple Modules (Priority: P3)

Users can select multiple product modules simultaneously to view epics from several areas at once, making it easier to track features across different products.

**Why this priority**: This improves the filtering experience but is independent of the likes feature. It's lower priority because single-module filtering already works.

**Independent Test**: Can be tested by selecting multiple modules in the filter and verifying that epics from all selected modules are displayed.

**Acceptance Scenarios**:

1. **Given** the user is on the roadmap page, **When** they select "Flows" and "Integrations" modules, **Then** epics from both modules are displayed
2. **Given** the user has selected 2 modules, **When** they deselect one module, **Then** only epics from the remaining module are shown
3. **Given** the user has selected multiple modules, **When** they click "Clear filters", **Then** all modules are shown again
4. **Given** no modules are selected, **When** the page loads, **Then** all epics from all modules are displayed

---

### Edge Cases

- What happens when a user rapidly clicks the like button multiple times (debouncing)?
- How does the system handle like count updates when the JIRA API is slow or times out?
- What happens if the JIRA custom field "Roadmap Likes" doesn't exist for a project?
- How does the system handle concurrent like updates from multiple users?
- What happens when a user selects all modules vs. selecting no modules (should they show the same results)?
- How does the system handle projects that don't have the "Roadmap Likes" field configured?

## Requirements *(mandatory)*

### Functional Requirements

**Like Functionality:**

- **FR-001**: System MUST display the current like count for each roadmap epic retrieved from the JIRA "Roadmap Likes" custom field
- **FR-002**: System MUST provide a like button on each epic card that users can click to like or unlike the epic
- **FR-003**: System MUST update the JIRA "Roadmap Likes" custom field when a user likes or unlikes an epic
- **FR-004**: System MUST prevent duplicate like submissions while a like request is in progress (debouncing)
- **FR-005**: System MUST show visual feedback when a like action succeeds or fails
- **FR-006**: System MUST handle cases where the "Roadmap Likes" field is not configured for a project by defaulting to 0 likes
- **FR-007**: System MUST sync like counts from JIRA during regular data synchronization cycles
- **FR-008**: System MUST store like counts as integers (non-negative numbers) in JIRA

**Multi-Module Selection:**

- **FR-009**: System MUST allow users to select multiple modules simultaneously in the filter interface
- **FR-010**: System MUST display epics from all selected modules when multiple modules are chosen
- **FR-011**: System MUST update the displayed epics when users add or remove module selections
- **FR-012**: System MUST maintain other active filters (year, quarter, status) when module selection changes
- **FR-013**: System MUST show all modules when no specific modules are selected
- **FR-014**: System MUST persist module selections in the URL query parameters for shareable links

**Configuration:**

- **FR-015**: System MUST add "roadmap_likes" field to the JIRA projects configuration schema
- **FR-016**: System MUST update the CLI tool to support mapping the "Roadmap Likes" custom field
- **FR-017**: System MUST validate that the "roadmap_likes" field follows the pattern `customfield_\d{5,}`

### Key Entities

- **Like Count**: An integer value stored in JIRA representing how many times an epic has been liked. Stored in the "Roadmap Likes" custom field per project.
- **Module Selection**: A collection of module IDs that users want to filter by. Can be empty (show all), single (current behavior), or multiple (new behavior).
- **Roadmap Likes Field Mapping**: Configuration entry in `jira_projects.json` mapping the "roadmap_likes" key to a project-specific custom field ID.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can see like counts on all roadmap epics within 2 seconds of page load
- **SC-002**: Like button clicks update the JIRA field within 3 seconds under normal network conditions
- **SC-003**: Users can select up to 10 modules simultaneously without performance degradation
- **SC-004**: Multi-module filtering returns results in under 1 second for datasets up to 500 epics
- **SC-005**: Like count synchronization from JIRA completes within the existing sync interval (5 minutes default)
- **SC-006**: 95% of like actions complete successfully without errors
- **SC-007**: Users can share URLs with multiple module selections and recipients see the same filtered view

## Assumptions *(mandatory)*

1. **User Authentication**: Users do not need to be authenticated to like epics - likes are anonymous and tracked only by count
2. **Like Persistence**: The system does not track which individual users have liked which epics, only the total count per epic
3. **JIRA Field Type**: The "Roadmap Likes" custom field in JIRA is a number field that accepts integer values
4. **Concurrent Updates**: JIRA handles concurrent updates to the likes field using optimistic locking or last-write-wins
5. **Module Data**: Module data structure and retrieval logic remains unchanged - only the filtering logic changes
6. **Browser Support**: Multi-select UI works in modern browsers (Chrome, Firefox, Safari, Edge) from the last 2 years
7. **API Endpoint**: A new API endpoint will be created for updating like counts (e.g., `POST /api/v1/roadmap/items/{id}/like`)
8. **Rate Limiting**: Existing rate limiting mechanisms are sufficient to prevent like spam
9. **Default Value**: Epics without a configured "Roadmap Likes" field default to 0 likes and cannot be liked
10. **URL Length**: URLs with multiple module selections stay within browser URL length limits (typically 2000 characters)

## Out of Scope *(optional)*

- User authentication or tracking of individual users who liked epics
- Unlike functionality (removing a like) - initially likes are additive only
- Like history or audit trail
- Sorting epics by like count
- Like count analytics or reporting beyond displaying the count
- Email notifications when epics are liked
- Like count badges or highlighting for highly-liked epics
- Limiting the number of likes per user or per IP address
- Module selection persistence across browser sessions (beyond URL parameters)
- Drag-and-drop or reordering of selected modules

## Dependencies *(optional)*

- **JIRA Custom Field Creation**: The "Roadmap Likes" custom field must be created in JIRA for each project before the feature can be used
- **JIRA API Permissions**: The JIRA API credentials must have write permissions to update custom fields on epics
- **Existing Sync Service**: The feature relies on the existing JIRA sync service to retrieve like counts
- **Existing Filter System**: Multi-module selection builds on the existing filter infrastructure in `RoadmapFilters.vue`
- **Configuration Schema**: Changes to `jira_projects.schema.json` must be backward compatible with existing project configurations

## Technical Constraints *(optional)*

- **No Database**: All like counts must be stored in JIRA custom fields - no local database storage
- **JIRA API Rate Limits**: Like updates are subject to JIRA Cloud API rate limits (typically 10 requests per second)
- **Stateless Backend**: The backend API remains stateless - no session storage for like tracking
- **JSON Schema Validation**: All configuration changes must pass JSON schema validation
- **Backward Compatibility**: Existing projects without the "Roadmap Likes" field must continue to work without errors
- **Frontend Framework**: Implementation must use Vue 3 Composition API and TypeScript
- **CSS Methodology**: UI components must follow BEM naming conventions
- **API Versioning**: New endpoints must follow the existing `/api/v1/` versioning pattern
