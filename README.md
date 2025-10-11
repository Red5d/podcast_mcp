# Jupiter Broadcasting Podcast Data MCP Server

A FastMCP server that parses Podcast 2.0 RSS feeds from Jupiter Broadcasting shows and provides access to episode data through MCP tools.

## Features

This MCP server provides four main tools:

1. **List Shows** - Returns a list of available podcast shows
2. **Search Episodes** - Search episodes by show, date range, hosts, or text content
3. **Get Episode** - Retrieve detailed information about a specific episode
4. **Get Transcript** - Fetch episode transcripts when available

## Installation

This project uses the `uv` package manager for Python dependency management.

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone and Setup

```bash
git clone <repository-url>
cd jupiterbroadcasting_mcp
uv sync
```

## Usage

### Running the Server

To start the MCP server:

```bash
uv run jupiterbroadcasting-mcp
```

Or alternatively:

```bash
uv run python -m jupiterbroadcasting_mcp.server
```

### MCP Tools

#### 1. List Shows

Returns an array of available podcast show names.

```json
{
  "tool": "list_shows",
  "arguments": {}
}
```

**Returns:** Array of show names (e.g., `["Linux Unplugged", "This Week in Bitcoin", ...]`)

#### 2. Search Episodes

Search for episodes using various criteria. At least one parameter must be provided.

```json
{
  "tool": "search_episodes",
  "arguments": {
    "show_name": "Linux Unplugged",
    "since_date": "2024-01-01",
    "before_date": "2024-12-31",
    "hosts": ["Chris Fisher", "Wes Payne"],
    "text_search": "kubernetes"
  }
}
```

**Parameters:**
- `show_name` (optional): Filter by specific show
- `since_date` (optional): Episodes published on or after this date (YYYY-MM-DD or ISO format)
- `before_date` (optional): Episodes published before this date (YYYY-MM-DD or ISO format)
- `hosts` (optional): Array of host names to filter by
- `text_search` (optional): Search text in episode titles and descriptions

**Returns:** Array of episode objects with metadata

#### 3. Get Episode

Retrieve detailed information about a specific episode.

```json
{
  "tool": "get_episode",
  "arguments": {
    "show_name": "Linux Unplugged",
    "episode_number": "635"
  }
}
```

**Parameters:**
- `show_name` (required): Name of the show
- `episode_number` (required): Episode number

**Returns:** Episode object with full metadata including:
- Title and description
- Publication date
- Host information
- Audio file URLs
- Transcript URL (if available)
- Duration
- Hosts

#### 4. Get Transcript

Fetch the transcript content for an episode.

```json
{
  "tool": "get_transcript",
  "arguments": {
    "show_name": "Linux Unplugged",
    "episode_number": "635"
  }
}
```

**Parameters:**
- `show_name` (required): Name of the show
- `episode_number` (required): Episode number

**Returns:** Object containing transcript text or error message

## Configuration

### Adding New Feeds

To add or modify RSS feeds, edit the `JB_FEEDS` dictionary in `jupiterbroadcasting_mcp/server.py`:

```python
JB_FEEDS = {
    "Show Name": "https://example.com/feed.rss",
    "Another Show": "https://example.com/another-feed.rss",
}
```

### Podcast 2.0 Namespace Support

This server supports Podcast 2.0 namespace elements including:
- `<podcast:person>` for host information
- `<podcast:transcript>` for transcript URLs
- Standard RSS elements for titles, descriptions, and enclosures

## Development

### Setting up Development Environment

```bash
# Install with development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

### Project Structure

```
jupiterbroadcasting_mcp/
├── jupiterbroadcasting_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   └── rss_parser.py      # RSS feed parsing logic
├── tests/                 # Test files
├── pyproject.toml         # Project configuration
└── README.md
```

## Error Handling

The server includes comprehensive error handling:
- Invalid search parameters return error messages
- Network failures when fetching feeds are logged
- Missing episodes or transcripts return appropriate error responses
- Malformed RSS feeds are handled gracefully

## Dependencies

- **fastmcp**: FastMCP framework for building MCP servers
- **lxml**: High-performance XML parsing with full Podcast 2.0 namespace support
- **requests**: HTTP client for fetching feeds and transcripts

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.