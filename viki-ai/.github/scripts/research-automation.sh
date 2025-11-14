#!/bin/bash

set -euo pipefail

# JIRA Research Automation Script
# This script analyzes JIRA tickets and generates research documentation
# using Claude Code to analyze the codebase

echo "Starting JIRA research automation..."
echo "Ticket: $TICKET_KEY"
echo "Title: $TICKET_TITLE"

# Create research prompt file
cat > research-prompt.md << 'EOF'
# JIRA Ticket Research Task

Please analyze the following JIRA ticket and conduct comprehensive research on the codebase to identify relevant files, components, and implementation approaches.

## Ticket Information
**Key:** ${TICKET_KEY}
**Title:** ${TICKET_TITLE}

**Description:**
${TICKET_DESCRIPTION}

**Acceptance Criteria:**
${TICKET_ACCEPTANCE_CRITERIA}

## Research Requirements

Please provide a detailed research document in markdown format that includes:

1. **Codebase Analysis**
   - Identify all relevant files and their locations (with line numbers where applicable)
   - Key classes, functions, and components related to this feature
   - Existing patterns and architectures that should be followed

2. **Dependencies and Integrations**
   - External services, APIs, or libraries that will be involved
   - Database schema changes or considerations
   - Configuration files that may need updates

3. **Architecture Overview**
   - How this feature fits into the existing system architecture
   - Affected microservices and their interactions
   - Frontend components that will need changes

4. **Implementation Approach**
   - Recommended implementation strategy
   - Potential challenges and risks
   - Suggested file structure for new components

5. **Testing Considerations**
   - Existing test patterns to follow
   - Areas that will need new test coverage
   - Integration test requirements

Please search the codebase thoroughly and provide specific file paths and line numbers where relevant. Focus on actionable insights that will help with the planning and implementation phases.
EOF

# Substitute environment variables in the prompt
envsubst < research-prompt.md > research-prompt-final.md

echo "Generated research prompt. Running Claude Code analysis..."

# Run Claude Code with the research prompt
claude chat --file research-prompt-final.md --output research-output.md

echo "Research analysis completed. Posting to JIRA..."

# Create JIRA comment payload
RESEARCH_CONTENT=$(cat research-output.md)

# Escape special characters for JSON
ESCAPED_CONTENT=$(echo "$RESEARCH_CONTENT" | jq -Rs .)

# Create JIRA comment JSON payload
cat > jira-comment.json << EOF
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "heading",
        "attrs": {
          "level": 2
        },
        "content": [
          {
            "type": "text",
            "text": "RESEARCH"
          }
        ]
      },
      {
        "type": "codeBlock",
        "attrs": {
          "language": "markdown"
        },
        "content": [
          {
            "type": "text",
            "text": $ESCAPED_CONTENT
          }
        ]
      },
      {
        "type": "rule"
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Generated automatically by GitHub Actions researcher workflow",
            "marks": [
              {
                "type": "em"
              }
            ]
          }
        ]
      }
    ]
  }
}
EOF

# Post comment to JIRA
JIRA_COMMENT_URL="${JIRA_BASE_URL}/rest/api/3/issue/${TICKET_KEY}/comment"

curl -X POST \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d @jira-comment.json \
  "$JIRA_COMMENT_URL"

if [ $? -eq 0 ]; then
  echo "Successfully posted research to JIRA ticket $TICKET_KEY"
else
  echo "Failed to post research to JIRA ticket $TICKET_KEY"
  exit 1
fi

# Clean up temporary files
rm -f research-prompt.md research-prompt-final.md jira-comment.json

echo "Research automation completed successfully!"