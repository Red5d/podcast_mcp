#!/usr/bin/env python3
"""Test script for the RSS parser using the sample RSS file."""

from jupiterbroadcasting_mcp.rss_parser import PodcastRSSParser
def test_local_file():
    """Test parsing the local sample RSS file."""
    # Use file:// URL to read the local sample
    feeds = {
        "Linux Unplugged": "file://tests/sample_rss.xml"
    }
    
    parser = PodcastRSSParser(feeds)
    
    print("Available shows:")
    shows = parser.get_shows()
    print(shows)
    
    print("\nSearching for episodes with 'Texas' in the title/description:")
    episodes = parser.search_episodes(text_search="Texas")
    for episode in episodes:
        print(f"- {episode['title']} (Episode {episode['episode_number']})")
        print(f"  Hosts: {', '.join(episode['hosts'])}")
        print(f"  Published: {episode['published_date']}")
        print(f"  Transcript URLs: {len(episode['transcript_urls'])}")
        if episode['transcript_urls']:
            for transcript in episode['transcript_urls']:
                print(f"    - {transcript['type']}: {transcript['url']}")
        print()

if __name__ == "__main__":
    test_local_file()