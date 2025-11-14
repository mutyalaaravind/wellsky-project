# Claude Code Installation Guide

Welcome to Claude Code! This guide will help you install and set up Claude Code for AI-powered coding assistance.

## Before You Begin

Make sure you have:
- A terminal or command prompt open
- A code project to work with
- A [Claude.ai](https://claude.ai) (recommended) or [Anthropic Console](https://console.anthropic.com/) account

## Step 1: Install Claude Code

### NPM Install

If you have [Node.js 18 or newer installed](https://nodejs.org/en/download/):

```bash
npm install -g @anthropic-ai/claude-code
```

### Native Install (Beta)

Alternatively, try our new native install, now in beta.

**macOS, Linux, WSL:**
```bash
curl -fsSL claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

## Step 2: Configure Claude Code for VertexAI

Claude Code can be configured to use Google Cloud's VertexAI instead of direct Anthropic API access. Add the following environment variables to your system:

### Linux/macOS/WSL

Add these lines to your shell profile file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`):

```bash
# Claude Code
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID=viki-dev-app-wsky

# Optional: Disable prompt caching if needed
export DISABLE_PROMPT_CACHING=1

# Optional: Override regions for specific models
export VERTEX_REGION_CLAUDE_3_5_HAIKU=us-central1
export VERTEX_REGION_CLAUDE_3_5_SONNET=us-east5
export VERTEX_REGION_CLAUDE_3_7_SONNET=us-east5
export VERTEX_REGION_CLAUDE_4_0_OPUS=europe-west4
export VERTEX_REGION_CLAUDE_4_0_SONNET=us-east5
```

Then reload your shell configuration:
```bash
source ~/.bashrc  # or ~/.zshrc, ~/.profile, etc.
```

### Windows PowerShell

Set environment variables using PowerShell (run as Administrator):

```powershell
# Claude Code
[Environment]::SetEnvironmentVariable("CLAUDE_CODE_USE_VERTEX", "1", "Machine")
[Environment]::SetEnvironmentVariable("CLOUD_ML_REGION", "us-east5", "Machine")
[Environment]::SetEnvironmentVariable("ANTHROPIC_VERTEX_PROJECT_ID", "viki-dev-app-wsky", "Machine")

# Optional: Disable prompt caching if needed
[Environment]::SetEnvironmentVariable("DISABLE_PROMPT_CACHING", "1", "Machine")

# Optional: Override regions for specific models
[Environment]::SetEnvironmentVariable("VERTEX_REGION_CLAUDE_3_5_HAIKU", "us-central1", "Machine")
[Environment]::SetEnvironmentVariable("VERTEX_REGION_CLAUDE_3_5_SONNET", "us-east5", "Machine")
[Environment]::SetEnvironmentVariable("VERTEX_REGION_CLAUDE_3_7_SONNET", "us-east5", "Machine")
[Environment]::SetEnvironmentVariable("VERTEX_REGION_CLAUDE_4_0_OPUS", "europe-west4", "Machine")
[Environment]::SetEnvironmentVariable("VERTEX_REGION_CLAUDE_4_0_SONNET", "us-east5", "Machine")
```

Restart your terminal after setting environment variables.

### Windows Command Prompt

Alternatively, you can set environment variables through System Properties:
1. Right-click "This PC" → Properties → Advanced system settings
2. Click "Environment Variables"
3. Under "System variables", click "New" and add each variable:
   - `CLAUDE_CODE_USE_VERTEX` = `1`
   - `CLOUD_ML_REGION` = `us-east5`
   - `ANTHROPIC_VERTEX_PROJECT_ID` = `viki-dev-app-wsky`
   - (Add optional variables as needed)

> **Note:** Make sure you have proper Google Cloud authentication configured (e.g., through `gcloud auth application-default login`) and necessary permissions for the VertexAI project.

## Step 3: Start Your First Session

Open your terminal in any project directory and start Claude Code:

```bash
cd /path/to/your/project
claude
```

You'll see the Claude Code prompt inside a new interactive session:

```
; Welcome to Claude Code!
...
> Try "create a util logging.py that..."
```

> **Tip:** After logging in (Step 2), your credentials are stored on your system. Learn more in [Credential Management](https://docs.anthropic.com/en/docs/claude-code/iam#credential-management).

## Installing Playwright MCP Server (Optional)

The Playwright MCP server enables Claude Code to interact with web browsers for testing, automation, and web scraping tasks. To install it:

```bash
claude mcp add playwright npx '@playwright/mcp@latest'
```

This will:
- Add the Playwright MCP server to your Claude Code configuration
- Enable browser automation capabilities within Claude Code sessions
- Allow Claude to navigate websites, interact with web elements, and take screenshots

Once installed, you can use commands like:
- "Navigate to example.com and take a screenshot"
- "Fill out the login form on this website"
- "Click the submit button and wait for the page to load"

> **Note:** The Playwright MCP server requires Node.js and will automatically install necessary browser dependencies when first used.

## Essential Commands

Here are the most important commands for daily use:

| Command | What it does | Example |
|---------|-------------|---------|
| `claude` | Start interactive mode | `claude` |
| `claude "task"` | Run a one-time task | `claude "fix the build error"` |
| `claude -p "query"` | Run one-off query, then exit | `claude -p "explain this function"` |
| `claude -c` | Continue most recent conversation | `claude -c` |
| `claude -r` | Resume a previous conversation | `claude -r` |
| `claude commit` | Create a Git commit | `claude commit` |
| `/clear` | Clear conversation history | `> /clear` |
| `/help` | Show available commands | `> /help` |
| `exit` or Ctrl+C | Exit Claude Code | `> exit` |

## Getting Help

- **In Claude Code**: Type `/help` or ask "how do I&"
- **Documentation**: Browse the [official documentation](https://docs.anthropic.com/en/docs/claude-code)
- **Community**: Join our [Discord](https://www.anthropic.com/discord) for tips and support

## What's Next?

Now that you've installed Claude Code, explore more advanced features:
- [Common workflows](https://docs.anthropic.com/en/docs/claude-code/common-workflows) - Step-by-step guides for common tasks
- [CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-reference) - Master all commands and options
- [Configuration](https://docs.anthropic.com/en/docs/claude-code/settings) - Customize Claude Code for your workflow