# Feature Specification: Weni Public Roadmap

**Feature Branch**: `001-public-roadmap`
**Created**: December 22, 2025
**Status**: Draft
**Input**: User description: "Create a public roadmap page for Weni customers and stakeholders to see upcoming and delivered features, integrated with JIRA epics backend"

## Overview

A public-facing roadmap page where Weni customers and stakeholders can view upcoming features and delivered improvements. The design follows a similar pattern to [Synerise Roadmap](https://roadmap.synerise.com/roadmap) with status-based navigation tabs and time-based filtering.

The page displays product roadmap items sourced from JIRA epics, with careful security controls to ensure only explicitly published items are visible. Product Managers control what appears on the roadmap through a dedicated field in JIRA that marks an epic as "public."

### Key UI Concepts (inspired by Synerise)

- **Status Tabs**: Primary navigation using status categories (e.g., "Delivered", "Now", "Next", "Future")
- **Time Filters**: Year selector and quarterly filters (Q1, Q2, Q3, Q4) to narrow down items
- **Module/Area Filter**: Dropdown to filter by product module
- **Expandable Cards**: Items display as cards with title and module badge; clicking/tapping reveals full description, images, and documentation link

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse Roadmap by Status (Priority: P1)

As a customer or stakeholder, I want to view the product roadmap organized by delivery status so that I can understand what has been delivered, what's being worked on now, and what's planned for the future.

**Why this priority**: This is the core value proposition - stakeholders need to see what's coming and when. Status-based navigation provides immediate clarity about the product direction.

**Independent Test**: Can be fully tested by loading the roadmap page and verifying items are displayed organized by status tabs. Delivers immediate value by showing stakeholders the product trajectory.

**Acceptance Scenarios**:

1. **Given** I am on the roadmap page, **When** the page loads, **Then** I see status tabs for navigating between "Delivered", "Now", "Next", and "Future" items
2. **Given** I am viewing the roadmap, **When** I click on a status tab (e.g., "Delivered"), **Then** I see all items with that status
3. **Given** I am viewing a status tab, **When** I apply a year filter, **Then** only items from that year are displayed within the selected status
4. **Given** I am viewing a status tab with a year selected, **When** I click a quarter button (Q1, Q2, Q3, Q4), **Then** only items from that quarter are displayed
5. **Given** I am on any status tab, **When** I view the page header, **Then** I see a count of how many items are in the current view

---

### User Story 2 - View Feature Details (Priority: P1)

As a customer, I want to see detailed information about each roadmap item so that I can understand what the feature entails and how it benefits me.

**Why this priority**: Feature details are essential for stakeholders to understand the value and scope of upcoming changes. Without details, the roadmap is just a list of titles.

**Independent Test**: Can be fully tested by clicking/expanding any roadmap item card and verifying the expanded view displays all required information. Delivers value by informing stakeholders about feature specifics.

**Acceptance Scenarios**:

1. **Given** I am viewing the roadmap, **When** I see a roadmap item card, **Then** I can see the item's title and module/product badge in the collapsed state
2. **Given** I am viewing a roadmap item card, **When** I click to expand it, **Then** I see the full description and additional information
3. **Given** I have expanded a roadmap item, **When** the item has images attached, **Then** I can view up to 4 images showing the feature (in a gallery or carousel format)
4. **Given** I have expanded a roadmap item with a documentation link, **When** I want more information, **Then** I can click a "Read More" button to access additional documentation
5. **Given** I have expanded a roadmap item, **When** no documentation link exists, **Then** the "Read More" button is not shown
6. **Given** I have expanded a roadmap item, **When** I click the item again or click a collapse control, **Then** the card collapses back to its summary state

---

### User Story 3 - Filter by Module/Product (Priority: P2)

As a stakeholder interested in specific products, I want to filter the roadmap by module or product so that I can focus on features relevant to my area of interest.

**Why this priority**: Filtering enhances usability but the roadmap provides value even without it. This is an enhancement to the core browsing experience.

**Independent Test**: Can be fully tested by selecting a module/product filter and verifying only items matching that filter are displayed. Delivers focused viewing for users with specific interests.

**Acceptance Scenarios**:

1. **Given** I am on the roadmap page, **When** I select a specific module/product from the filter, **Then** only roadmap items belonging to that module are displayed
2. **Given** I have applied a filter, **When** I want to see all items again, **Then** I can clear the filter to return to the full roadmap view
3. **Given** multiple modules exist, **When** I view the filter options, **Then** I see a list of all modules that have at least one public roadmap item

---

### User Story 4 - Product Manager Publishes Epic to Roadmap (Priority: P1)

As a Product Manager, I want to mark specific JIRA epics as "public" so that they appear on the customer-facing roadmap while keeping internal-only items hidden.

**Why this priority**: This is the security control mechanism. Without explicit publishing, either nothing shows on the roadmap or everything does (security risk).

**Independent Test**: Can be fully tested by marking an epic as public in JIRA and verifying it appears on the roadmap, then unmarking it and verifying it disappears. Delivers security and control for Product Managers.

**Acceptance Scenarios**:

1. **Given** I am a Product Manager with a JIRA epic, **When** I set the "public roadmap" field to enabled, **Then** the epic becomes visible on the public roadmap (after the next sync)
2. **Given** an epic is marked as public, **When** I remove the public flag, **Then** the epic is no longer visible on the public roadmap
3. **Given** an epic is not marked as public, **When** a customer views the roadmap, **Then** they cannot see any information about that epic
4. **Given** I am marking an epic as public, **When** required fields (title, description, release timing) are missing, **Then** the system indicates which fields need to be completed

---

### Edge Cases

- What happens when an epic has no release date set?
  - The item should not appear on the roadmap until a release period is defined
- What happens when an epic's release date changes?
  - The item moves to its new position in the timeline on the next sync
- How does the system handle epics with incomplete information?
  - Items missing required fields (title, description, release timing) should not appear on the public roadmap
- What happens when there are no public roadmap items?
  - The page displays a friendly message indicating the roadmap is being updated
- What happens when JIRA is unavailable?
  - The roadmap displays cached/previously synced data with a discrete indicator that data may not be current
- What happens when an image URL from JIRA becomes invalid?
  - The system gracefully handles missing images without breaking the item display

## Requirements *(mandatory)*

### Functional Requirements

**Public Roadmap Page**

- **FR-001**: The roadmap page MUST be accessible without authentication (public access)
- **FR-002**: The roadmap MUST provide status-based navigation tabs: "Delivered", "Now", "Next", and "Future"
- **FR-003**: The roadmap MUST allow filtering by year using a dropdown selector
- **FR-004**: The roadmap MUST allow filtering by quarter using clickable buttons (Q1, Q2, Q3, Q4)
- **FR-005**: Users MUST be able to filter roadmap items by module/product using a dropdown
- **FR-006**: Each roadmap item MUST be displayed as an expandable card showing title and module badge in collapsed state
- **FR-007**: Expanded cards MUST display: full description, images (up to 4), and documentation link (when available)
- **FR-008**: The page MUST show a count of items in the current filtered view
- **FR-009**: The roadmap page MUST be the only tab affected; the existing Changelog functionality remains unchanged

**JIRA Integration Backend**

- **FR-010**: The backend MUST only retrieve and expose JIRA epics that are explicitly marked as "public" by Product Managers
- **FR-011**: The backend MUST NOT expose any JIRA data (fields, comments, attachments) that are not part of the defined public roadmap fields
- **FR-012**: The backend MUST sync the following fields from JIRA epics:
  - Title (summary)
  - Description
  - Up to 4 images
  - Documentation/learn more link
  - Module/Product
  - Release month
  - Release quarter
  - Release year
  - Status (mapped to: Delivered, Now, Next, Future)
- **FR-013**: The backend MUST provide a mechanism for periodic data synchronization from JIRA
- **FR-014**: The backend MUST cache roadmap data to serve requests when JIRA is temporarily unavailable
- **FR-015**: The backend MUST validate that all required fields are present before including an epic in the public roadmap data

**Security Requirements**

- **FR-016**: The backend MUST authenticate with JIRA using secure credentials that are never exposed to the frontend
- **FR-017**: The backend MUST implement rate limiting to prevent abuse
- **FR-018**: The backend MUST log all data sync operations for audit purposes
- **FR-019**: The frontend MUST NOT make direct calls to JIRA; all data comes through the backend

### Key Entities

- **Roadmap Item**: Represents a public epic with title, description, images (0-4), documentation link, module/product, release month, release quarter, release year, and delivery status
- **Delivery Status**: One of four states that determines which tab the item appears under: "Delivered" (completed), "Now" (currently in progress), "Next" (planned for near-term), "Future" (planned for longer-term)
- **Module/Product**: Categorization of roadmap items by product area or module (e.g., "Flows", "Agents", "Integrations")
- **Release Period**: Time-based grouping consisting of year, quarter, and optionally month
- **Publication Flag**: Boolean indicating whether an epic should be visible on the public roadmap (controlled by Product Managers in JIRA)

## Assumptions

- JIRA provides an API that allows querying epics with custom field filtering
- A custom field can be created in JIRA to mark epics as "public roadmap visible"
- Product Managers have the necessary JIRA permissions to edit the public visibility field
- Images attached to epics are accessible via URL (or can be proxied through the backend)
- The roadmap page is part of an existing web application (the Changelog app) and this feature adds/modifies only the "Roadmap" tab

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Stakeholders can view the complete public roadmap within 3 seconds of page load
- **SC-002**: 100% of non-public epics remain invisible to roadmap visitors (zero information leakage)
- **SC-003**: Product Managers can publish an epic to the roadmap within 5 minutes of marking it as public in JIRA (sync frequency)
- **SC-004**: The roadmap remains accessible (showing cached data) even during JIRA outages
- **SC-005**: 90% of visitors can find a specific feature they're interested in within 30 seconds using the filter/browse functionality
- **SC-006**: The roadmap displays correctly on desktop and mobile devices

## Out of Scope

- Changelog tab modifications (explicitly excluded per requirements)
- User accounts or authentication for viewing the roadmap
- Comments or feedback submission from stakeholders on roadmap items
- Email notifications about roadmap updates
- Integration with project management tools other than JIRA
