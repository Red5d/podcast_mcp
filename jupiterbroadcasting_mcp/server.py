"""FastMCP server for Jupiter Broadcasting podcast feeds."""
import asyncio
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from .rss_parser import PodcastRSSParser


# Jupiter Broadcasting podcast feeds
JB_FEEDS = {
    "Linux Unplugged": "https://feeds.jupiterbroadcasting.com/lup",
    "This Week in Bitcoin": "https://serve.podhome.fm/rss/55b53584-4219-4fb0-b916-075ce23f714e",
    "The Launch": "https://serve.podhome.fm/rss/04b078f9-b3e8-4363-a576-98e668231306",
    "Self-Hosted": "https://feeds.fireside.fm/selfhosted/rss",
    "Jupiter Extras": "https://extras.show/rss",
}

# Initialize the RSS parser with example feeds
rss_parser = PodcastRSSParser(JB_FEEDS)

# Create FastMCP instance
mcp = FastMCP("Jupiter Broadcasting Podcast Data MCP Server")


@mcp.tool()
def list_shows() -> List[str]:
    """List all available podcast shows.
    
    Returns:
        List of show names available for searching and episode retrieval.
    """
    return rss_parser.get_shows()


@mcp.tool()
def search_episodes(
    show_name: str,
    since_date: Optional[str] = None,
    before_date: Optional[str] = None,
    hosts: Optional[List[str]] = None,
    text_search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search for episodes based on various criteria. At least one search parameter must be provided.
    
    Args:
        show_name: Name of the specific show to search in (required)
        since_date: Only return episodes published on or after this date (YYYY-MM-DD or ISO format)
        before_date: Only return episodes published before this date (YYYY-MM-DD or ISO format)
        hosts: List of host names to filter by
        text_search: Search text to match against episode titles and descriptions
    
    Returns:
        List of episodes matching the search criteria.
    """
    try:
        return rss_parser.search_episodes(
            show_name=show_name,
            since_date=since_date,
            before_date=before_date,
            hosts=hosts,
            text_search=text_search,
        )
    except ValueError as e:
        return [{"error": str(e)}]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool()
def get_episode(show_name: str, episode_number: str) -> Dict[str, Any]:
    """Get detailed information about a specific episode.
    
    Args:
        show_name: Name of the show
        episode_number: Episode number
    
    Returns:
        Episode data including title, description, hosts, enclosures, etc.
    """
    try:
        episode = rss_parser.get_episode(show_name, episode_number)
        if episode:
            return episode
        else:
            return {"error": f"Episode '{episode_number}' not found in show '{show_name}'"}
    except Exception as e:
        return {"error": f"Failed to retrieve episode: {str(e)}"}


@mcp.tool()
def get_transcript(show_name: str, episode_number: str) -> Dict[str, Any]:
    """Get the transcript for a specific episode.
    
    Args:
        show_name: Name of the show
        episode_number: Episode number
    
    Returns:
        Dictionary containing the transcript text or error message.
    """
    try:
        transcript = rss_parser.get_transcript(show_name, episode_number)
        if transcript:
            return {"transcript": transcript}
        else:
            return {"error": f"Transcript not available for episode '{episode_number}' in show '{show_name}'"}
    except Exception as e:
        return {"error": f"Failed to retrieve transcript: {str(e)}"}


def main() -> None:
    """Main entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()