# MCP Server Testing Guide

This guide explains how to test your MCP server endpoints properly.

## The Problem

The MCP server uses SSE (Server-Sent Events) transport, which requires a valid session ID for API calls. You can't use arbitrary session IDs - they must be obtained from the SSE endpoint first.

## Quick Testing Steps

### 1. Get a Session ID

Run this command to get a session ID:

```bash
curl -N http://localhost:13500/sse | grep "data: /messages" | head -1
```

This will output something like:
```
data: /messages/?session_id=5ffc739597d84fd2bf9574fba1380832
```

Copy the session ID part: `5ffc739597d84fd2bf9574fba1380832`

### 2. Update test.rest

Open `tests/test.rest` and replace all instances of `YOUR_SESSION_ID_HERE` with your actual session ID.

### 3. Run Tests

Now you can run the individual tests in your REST client (like VS Code REST Client extension).

## Alternative: One-liner to get session ID

```bash
curl -N http://localhost:13500/sse 2>/dev/null | grep -o 'session_id=[a-f0-9]*' | head -1 | cut -d= -f2
```

This will output just the session ID, which you can copy directly.

## Expected Results

- **Steps 2-3**: Will return 404 (these endpoints don't exist in FastMCP)
- **Step 4 (Initialize)**: Should return a successful initialization response
- **Step 5 (Tools List)**: Should list available tools: `add_allergy`, `get_files`, `get_system_info`
- **Step 6 (Resources List)**: Should list available resources
- **Steps 7-9**: Should execute the respective tools and return results

## Troubleshooting

- **"Invalid session ID"**: Get a fresh session ID from the SSE endpoint
- **Connection refused**: Make sure the Docker container is running (`docker-compose ps`)
- **404 errors on /messages/**: Check that you're using `/messages/` (with trailing slash) and the correct session ID
