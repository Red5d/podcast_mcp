#!/usr/bin/env python3
"""Test script for date parsing functionality."""

from jupiterbroadcasting_mcp.rss_parser import PodcastRSSParser

def test_date_parsing():
    """Test date parsing functionality."""
    feeds = {
        "Linux Unplugged": "file://tests/sample_rss.xml"
    }
    
    parser = PodcastRSSParser(feeds)
    
    print("Testing date parsing:")
    
    # Test parsing various date formats
    test_dates = [
        "Sun, 05 Oct 2025 19:25:37 -0700",
        "2025-10-05",
        "2025-10-05T19:25:37Z",
        "05 Oct 2025",
    ]
    
    for date_str in test_dates:
        parsed = parser._parse_date(date_str)
        print(f"'{date_str}' -> {parsed}")
    
    print("\nTesting date filtering:")
    
    # Test searching with date filters
    print("Episodes since 2025-10-01:")
    episodes = parser.search_episodes(since_date="2025-10-01")
    for episode in episodes:
        print(f"- {episode['title']} - {episode['published_date']}")
    
    print("\nEpisodes before 2025-10-10:")
    episodes = parser.search_episodes(before_date="2025-10-10")
    for episode in episodes:
        print(f"- {episode['title']} - {episode['published_date']}")

if __name__ == "__main__":
    test_date_parsing()