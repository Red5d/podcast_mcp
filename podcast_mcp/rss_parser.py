"""RSS feed parser for Podcast 2.0 specification."""
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from lxml import etree
import re


class PodcastRSSParser:
    """Parser for Podcast 2.0 RSS feeds."""
    
    def __init__(self, feeds: Dict[str, str]):
        """Initialize with a dictionary of show_name -> feed_url mappings."""
        self.feeds = feeds
        self._cached_feeds: Dict[str, Any] = {}
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats commonly found in RSS feeds."""
        if not date_string:
            return None
        
        date_string = date_string.strip()
        
        # Common RSS date formats to try
        formats = [
            # RFC 2822 format (most common in RSS)
            "%a, %d %b %Y %H:%M:%S %z",      # "Sun, 05 Oct 2025 19:25:37 -0700"
            "%a, %d %b %Y %H:%M:%S %Z",      # "Sun, 05 Oct 2025 19:25:37 PDT"
            "%a, %d %b %Y %H:%M:%S",         # "Sun, 05 Oct 2025 19:25:37"
            # ISO 8601 formats
            "%Y-%m-%dT%H:%M:%S%z",           # "2025-10-05T19:25:37-0700"
            "%Y-%m-%dT%H:%M:%SZ",            # "2025-10-05T19:25:37Z"
            "%Y-%m-%dT%H:%M:%S",             # "2025-10-05T19:25:37"
            "%Y-%m-%d %H:%M:%S",             # "2025-10-05 19:25:37"
            "%Y-%m-%d",                      # "2025-10-05"
            # Other common formats
            "%d %b %Y %H:%M:%S %z",          # "05 Oct 2025 19:25:37 -0700"
            "%d %b %Y",                      # "05 Oct 2025"
        ]
        
        # Clean up timezone offset format for Python compatibility
        # Convert "-0700" to "-07:00" format if needed
        if re.search(r'[+-]\d{4}$', date_string):
            date_string = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', date_string)
        
        parsed_dt = None
        for fmt in formats:
            try:
                parsed_dt = datetime.strptime(date_string, fmt)
                break
            except ValueError:
                continue
        
        # If all else fails, try to extract just the date part
        if parsed_dt is None:
            date_match = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_string)
            if date_match:
                try:
                    day, month, year = date_match.groups()
                    month_map = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    if month in month_map:
                        parsed_dt = datetime(int(year), month_map[month], int(day))
                except (ValueError, KeyError):
                    pass
        
        if parsed_dt is None:
            print(f"Warning: Could not parse date: {date_string}")
            return None
        
        # Ensure all datetime objects are timezone-aware for consistent comparison
        # If no timezone info, assume UTC
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        
        return parsed_dt
    
    def _get_feed(self, show_name: str) -> Optional[etree._Element]:
        """Get parsed feed data, with caching."""
        if show_name not in self.feeds:
            return None
            
        if show_name not in self._cached_feeds:
            try:
                feed_url = self.feeds[show_name]
                
                # Handle file:// URLs for local testing
                if feed_url.startswith('file://'):
                    file_path = feed_url[7:]  # Remove 'file://' prefix
                    with open(file_path, 'rb') as f:
                        content = f.read()
                else:
                    # Handle HTTP/HTTPS URLs
                    response = requests.get(feed_url, timeout=30)
                    response.raise_for_status()
                    content = response.content
                
                # Parse XML with lxml
                parser = etree.XMLParser(strip_cdata=False)
                root = etree.fromstring(content, parser)
                self._cached_feeds[show_name] = root
            except Exception as e:
                print(f"Error parsing feed for {show_name}: {e}")
                return None
                
        return self._cached_feeds[show_name]
    
    def get_shows(self) -> List[str]:
        """Get list of available show names."""
        return list(self.feeds.keys())
    
    def search_episodes(
        self,
        show_name: Optional[str] = None,
        since_date: Optional[str] = None,
        before_date: Optional[str] = None,
        hosts: Optional[List[str]] = None,
        text_search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search episodes based on provided criteria."""
        if not any([show_name, since_date, before_date, hosts, text_search]):
            raise ValueError("At least one search parameter must be provided")
        
        results = []
        
        # Determine which shows to search
        shows_to_search = [show_name] if show_name else self.get_shows()
        
        # Parse date filters
        since_dt = None
        before_dt = None
        if since_date:
            since_dt = self._parse_date(since_date)
        if before_date:
            before_dt = self._parse_date(before_date)
        
        for show in shows_to_search:
            feed_root = self._get_feed(show)
            if feed_root is None:
                continue
                
            # Find all item elements (episodes)
            items = feed_root.xpath('//item')
            for item in items:
                episode_data = self._parse_episode(show, item)
                
                # Apply filters
                if since_dt and episode_data.get("published_date"):
                    episode_dt = self._parse_date(episode_data["published_date"])
                    if episode_dt and episode_dt < since_dt:
                        continue
                
                if before_dt and episode_data.get("published_date"):
                    episode_dt = self._parse_date(episode_data["published_date"])
                    if episode_dt and episode_dt > before_dt:
                        continue
                
                if hosts:
                    episode_hosts = episode_data.get("hosts", [])
                    if not any(host.lower() in [h.lower() for h in episode_hosts] for host in hosts):
                        continue
                
                if text_search:
                    search_text = text_search.lower()
                    title = episode_data.get("title", "").lower()
                    description = episode_data.get("description", "").lower()
                    if search_text not in title and search_text not in description:
                        continue
                
                results.append(episode_data)
        
        return results
    
    def get_episode(self, show_name: str, episode_number: str) -> Optional[Dict[str, Any]]:
        """Get specific episode data."""
        feed_root = self._get_feed(show_name)
        if feed_root is None:
            return None
        
        # Find all item elements (episodes)
        items = feed_root.xpath('//item')
        for item in items:
            # Check GUID
            guid_elem = item.find('guid')
            if guid_elem is not None and guid_elem.text == episode_number:
                return self._parse_episode(show_name, item)
            
            # Check podcast:episode number
            episode_elem = item.find('.//{https://podcastindex.org/namespace/1.0}episode')
            if episode_elem is not None and episode_elem.text == episode_number:
                return self._parse_episode(show_name, item)
        
        return None

    def get_transcript(self, show_name: str, episode_number: str) -> Optional[str]:
        """Get transcript for an episode."""
        episode = self.get_episode(show_name, episode_number)
        if not episode:
            return None
        
        transcript_url = episode.get("transcript_url")
        if not transcript_url:
            return None
        
        try:
            response = requests.get(transcript_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None
    
    def _parse_episode(self, show_name: str, item: etree._Element) -> Dict[str, Any]:
        """Parse a single episode entry from XML."""
        
        # Helper function to get text content safely
        def get_text(element):
            return element.text if element is not None else ""
        
        # Helper function to get CDATA content safely
        def get_cdata_content(element):
            if element is not None:
                # Handle CDATA content
                if element.text:
                    return element.text.strip()
            return ""
        
        # Basic episode information
        title_elem = item.find('title')
        guid_elem = item.find('guid')
        link_elem = item.find('link')
        pubdate_elem = item.find('pubDate')
        description_elem = item.find('description')
        
        # iTunes elements
        duration_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
        
        # Podcast namespace elements
        episode_num_elem = item.find('.//{https://podcastindex.org/namespace/1.0}episode')
        
        episode_data = {
            "show_name": show_name,
            "id": get_text(guid_elem) or get_text(episode_num_elem),
            "episode_number": get_text(episode_num_elem),
            "title": get_text(title_elem),
            "description": get_cdata_content(description_elem),
            "published_date": get_text(pubdate_elem),
            "link": get_text(link_elem),
            "duration": get_text(duration_elem),
            "hosts": [],
            "transcript_urls": [],
            "enclosures": [],
            "chapters_url": None,
        }
        
        # Parse enclosures (audio files)
        enclosure_elems = item.findall('enclosure')
        for enclosure in enclosure_elems:
            episode_data["enclosures"].append({
                "url": enclosure.get("url", ""),
                "type": enclosure.get("type", ""),
                "length": enclosure.get("length", "0"),
            })
        
        # Parse podcast:person elements (hosts, guests, etc.)
        person_elems = item.findall('.//{https://podcastindex.org/namespace/1.0}person')
        for person in person_elems:
            role = person.get("role", "")
            if role == "host":
                person_name = person.text
                if person_name:
                    episode_data["hosts"].append(person_name.strip())
        
        # Parse podcast:transcript elements
        transcript_elems = item.findall('.//{https://podcastindex.org/namespace/1.0}transcript')
        for transcript in transcript_elems:
            transcript_url = transcript.get("url")
            transcript_type = transcript.get("type", "")
            if transcript_url:
                episode_data["transcript_urls"].append({
                    "url": transcript_url,
                    "type": transcript_type,
                    "language": transcript.get("language", "en-us")
                })
        
        # For backward compatibility, set transcript_url to the first available transcript
        if episode_data["transcript_urls"]:
            episode_data["transcript_url"] = episode_data["transcript_urls"][0]["url"]
        else:
            episode_data["transcript_url"] = None
        
        # Parse podcast:chapters
        chapters_elem = item.find('.//{https://podcastindex.org/namespace/1.0}chapters')
        if chapters_elem is not None:
            episode_data["chapters_url"] = chapters_elem.get("url")
        
        return episode_data