"""Tests for the Jupiter Broadcasting MCP server."""
import pytest
from jupiterbroadcasting_mcp.rss_parser import PodcastRSSParser


def test_podcast_rss_parser_init():
    """Test RSS parser initialization."""
    feeds = {"Test Show": "https://example.com/feed.rss"}
    parser = PodcastRSSParser(feeds)
    assert parser.get_shows() == ["Test Show"]


def test_search_episodes_requires_parameter():
    """Test that search_episodes requires at least one parameter."""
    feeds = {"Test Show": "https://example.com/feed.rss"}
    parser = PodcastRSSParser(feeds)
    
    with pytest.raises(ValueError, match="At least one search parameter must be provided"):
        parser.search_episodes()


def test_get_episode_invalid_show():
    """Test getting episode from invalid show."""
    feeds = {"Test Show": "https://example.com/feed.rss"}
    parser = PodcastRSSParser(feeds)
    
    result = parser.get_episode("Invalid Show", "episode-123")
    assert result is None