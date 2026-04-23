"""
Mock JIRA API response fixtures for testing.

These fixtures simulate actual JIRA REST API v3 responses
for custom field retrieval and management.
"""

# Sample custom fields response from /rest/api/3/field
MOCK_CUSTOM_FIELDS_RESPONSE = [
    {
        "id": "customfield_10001",
        "name": "Epic Title",
        "description": "Internal epic title",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            "customId": 10001,
        },
    },
    {
        "id": "customfield_10101",
        "name": "Roadmap Title",
        "description": "Public-facing title for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            "customId": 10101,
        },
    },
    {
        "id": "customfield_10102",
        "name": "Roadmap Description",
        "description": "Public-facing description for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            "customId": 10102,
        },
    },
    {
        "id": "customfield_10103",
        "name": "Image URL 1",
        "description": "First image URL for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "customId": 10103,
        },
    },
    {
        "id": "customfield_10104",
        "name": "Image URL 2",
        "description": "Second image URL for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "customId": 10104,
        },
    },
    {
        "id": "customfield_10105",
        "name": "Image URL 3",
        "description": "Third image URL for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "customId": 10105,
        },
    },
    {
        "id": "customfield_10106",
        "name": "Image URL 4",
        "description": "Fourth image URL for roadmap display",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "customId": 10106,
        },
    },
    {
        "id": "customfield_14619",
        "name": "Show in Roadmap",
        "description": "Checkbox to mark epic as public",
        "custom": True,
        "schema": {
            "type": "array",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes",
            "customId": 14619,
        },
    },
    {
        "id": "customfield_14621",
        "name": "Delivery Status",
        "description": "Current delivery status",
        "custom": True,
        "schema": {
            "type": "option",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:select",
            "customId": 14621,
        },
    },
    {
        "id": "customfield_14622",
        "name": "Product Module",
        "description": "Product area or module",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            "customId": 14622,
        },
    },
    {
        "id": "customfield_14623",
        "name": "Release Year",
        "description": "Expected release year",
        "custom": True,
        "schema": {
            "type": "number",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float",
            "customId": 14623,
        },
    },
    {
        "id": "customfield_14624",
        "name": "Release Quarter",
        "description": "Expected release quarter",
        "custom": True,
        "schema": {
            "type": "option",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:select",
            "customId": 14624,
        },
    },
    {
        "id": "customfield_14625",
        "name": "Release Month",
        "description": "Expected release month",
        "custom": True,
        "schema": {
            "type": "number",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:float",
            "customId": 14625,
        },
    },
    {
        "id": "customfield_14626",
        "name": "Documentation URL",
        "description": "Link to documentation",
        "custom": True,
        "schema": {
            "type": "string",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "customId": 14626,
        },
    },
    # System field (should be filtered out)
    {
        "id": "summary",
        "name": "Summary",
        "custom": False,
        "schema": {"type": "string", "system": "summary"},
    },
]

# Mock response for authentication check (/rest/api/3/myself)
MOCK_AUTH_SUCCESS = {
    "accountId": "5b10ac8d82e05b22cc7d4ef5",
    "accountType": "atlassian",
    "emailAddress": "test@example.com",
    "displayName": "Test User",
    "active": True,
}

# Mock error responses
MOCK_AUTH_FAILURE = {
    "errorMessages": ["Client must be authenticated to access this resource."],
    "errors": {},
}

MOCK_PROJECT_NOT_FOUND = {
    "errorMessages": ["Project 'XYZ' does not exist."],
    "errors": {},
}

MOCK_RATE_LIMIT_ERROR = {
    "errorMessages": ["Rate limit exceeded. Please wait before making more requests."],
    "errors": {},
}

# Text-only custom fields (filtered subset)
MOCK_TEXT_FIELDS_ONLY = [
    field
    for field in MOCK_CUSTOM_FIELDS_RESPONSE
    if field.get("custom", False)
    and "textfield" in field.get("schema", {}).get("custom", "")
    or "textarea" in field.get("schema", {}).get("custom", "")
    or "url" in field.get("schema", {}).get("custom", "")
]
