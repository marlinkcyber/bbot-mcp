# BBOT MCP Server

A Model Context Protocol (MCP) server for running [BBOT](https://github.com/blacklanternsecurity/bbot) security scans. This server provides tools to manage and execute bbot scans through the MCP interface.

## Features

- **Module Management**: List and explore available bbot modules
- **Preset Management**: List and use predefined scan configurations
- **Scan Execution**: Start and manage long-running bbot scans
- **Real-time Monitoring**: Check scan status and retrieve results
- **Wait & Progress Tracking**: Wait for scan completion with timeout and progress reporting
- **Concurrent Scans**: Support for multiple simultaneous scans
- **Dependency Management**: Comprehensive sudo prevention and no-deps functionality

## Installation

### From PyPI (Recommended)
```bash
pip install bbot-mcp
```

### From Source
```bash
git clone https://github.com/marlinkcyber/bbot-mcp.git
cd bbot-mcp
pip install -e .
```

### Using uvx (Run without installing)
```bash
uvx bbot-mcp
```

## Install dependencies

It is recommended to install all BBOT dependencies before invoking BBOT MCP server:

```bash
bbot --install-all-deps
```

## Usage

### Running the MCP Server

After installation, the server can be started using the `bbot-mcp-server` command:

```bash
bbot-mcp-server
```

Or directly with Python:
```bash
python -m bbot_mcp.server
```

### Available Tools

The MCP server provides **8 tools** for comprehensive bbot scan management:

#### 1. `list_bbot_modules()`
Lists all available bbot modules categorized by type (scan, output, internal).

#### 2. `list_bbot_presets()`  
Lists all available bbot presets for quick scan configuration.

#### 3. `start_bbot_scan(targets, modules="", presets="", flags="", no_deps=True)`
Starts a new bbot scan with the specified parameters.

**Parameters:**
- `targets`: Comma-separated list of targets (domains, IPs, URLs)
- `modules`: Optional comma-separated list of modules to use
- `presets`: Optional comma-separated list of presets to apply
- `flags`: Optional comma-separated list of flags
- `no_deps`: Disable dependency installation to prevent sudo prompts (default: True)

**Example:**
```
start_bbot_scan("example.com,google.com", "httpx,nmap", "web-basic", "safe", True)
```

**Important:** The `no_deps=True` parameter prevents bbot from attempting to install missing dependencies, which would cause sudo password prompts that hang the MCP server.

#### 4. `get_scan_status(scan_id)`
Retrieves the current status of a specific scan.

#### 5. `get_scan_results(scan_id, limit=100)`
Retrieves results from a completed or running scan.

**Parameters:**
- `scan_id`: The unique identifier of the scan
- `limit`: Maximum number of results to return (default: 100)

#### 6. `list_active_scans()`
Lists all currently active scans with their basic information.

#### 7. `wait_for_scan_completion(scan_id, timeout=300, poll_interval=5, include_progress=True)`
Waits for a scan to complete with timeout and progress reporting.

**Parameters:**
- `scan_id`: The ID of the scan to wait for
- `timeout`: Maximum time to wait in seconds (default: 300 = 5 minutes)
- `poll_interval`: How often to check scan status in seconds (default: 5)
- `include_progress`: Whether to include progress updates in the response (default: True)

**Returns:**
- Success response with completion details, elapsed time, and progress updates
- Timeout response if scan doesn't complete within the specified time
- Error response for invalid scan IDs or other issues

**Example:**
```python
# Wait for scan to complete with custom timeout
result = wait_for_scan_completion("scan-123", timeout=600, poll_interval=10)
```

#### 8. `get_dependency_info()`
Provides information about bbot's dependency management system and how the MCP server handles dependencies.

## Scan Management

### Scan Lifecycle
1. **Starting**: Scan is being initialized
2. **Running**: Scan is actively executing
3. **Completed**: Scan finished successfully
4. **Error**: Scan encountered an error

### Long-running Scans
Scans run in separate threads to avoid blocking the MCP server. You can:
- Start multiple scans concurrently
- Check status while scans are running
- Retrieve partial results from ongoing scans

## Development

### Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest

# Run specific test categories
python tests/test_server.py
python tests/simple_test.py
python tests/test_imports.py

# Test the binary command
bbot-mcp-server --help
```

### Project Structure

```
bbot-mcp/
├── bbot_mcp/              # Main package
│   ├── __init__.py        # Package initialization
│   └── server.py          # MCP server implementation
├── tests/                 # Test suite
├── pyproject.toml         # Package configuration
├── README.md             # This file
└── requirements.txt      # Development dependencies
```

## Example MCP Client Usage

```python
# Connect to the MCP server and use the tools
client = MCPClient("bbot-scanner")

# List available modules
modules = client.call_tool("list_bbot_modules")

# Start a scan
scan_result = client.call_tool("start_bbot_scan", {
    "targets": "example.com",
    "presets": "web-basic"
})

# Check scan status
status = client.call_tool("get_scan_status", {
    "scan_id": scan_result["scan_id"]
})

# Wait for scan to complete
completion = client.call_tool("wait_for_scan_completion", {
    "scan_id": scan_result["scan_id"],
    "timeout": 300
})

# Get results when complete
results = client.call_tool("get_scan_results", {
    "scan_id": scan_result["scan_id"],
    "limit": 50
})
```

## Security Considerations

- This tool is designed for authorized security testing only
- Always ensure you have permission to scan target systems
- Be aware that bbot scans can be resource-intensive and may take significant time
- Some modules may be considered intrusive - use the `--allow-deadly` equivalent flags carefully

## Dependency Management

The MCP server includes comprehensive dependency management to prevent sudo password prompts:

### Automatic Protection Measures
- **Default Behavior**: `no_deps=True` - Dependencies are disabled by default
- **Environment Variables**: Multiple layers of sudo prevention (SUDO_ASKPASS, DEBIAN_FRONTEND, etc.)
- **Stdin Redirection**: Blocks all interactive input to prevent hanging
- **Module Exclusions**: Problematic modules (sslcert, trufflehog) are automatically excluded
- **Force Configuration**: Modules run even if dependencies fail

### Key Features
- **Comprehensive Sudo Prevention**: Multiple environment variables and configurations prevent any sudo prompts
- **Graceful Degradation**: Scans continue even when some modules can't load dependencies
- **Pre-installation Support**: Install dependencies manually if needed: `pip install <module-deps>`
- **macOS Compatibility**: Special handling for Homebrew vs APT package manager conflicts

### Excluded Modules

You can exclude problematic modules by setting following environment variable:
```bash
export BBOT_EXCLUDE_MODULES="trufflehog,sslcert"
```

Example exclude mentioned modules if you have any dependency issues (i.e. on Mac OS X):
- `sslcert`: APT dependency incompatible with macOS Homebrew
- `trufflehog`: Dependency installation conflicts

**Override Option**: Set `no_deps=False` only if you're certain no sudo prompts will occur

For more information about bbot itself, visit: https://github.com/blacklanternsecurity/bbot
