# utils/game_filters.py
"""
Game quality filtering utilities for GameDealer bot.
Uses a curated database of prioritized games for accurate filtering.
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple, Union, Pattern
import re
from models import Deal, PriorityGame, FilterResult, DatabaseStats


class PriorityGameFilter:
    """
    Filters games based on a curated priority database.
    This approach is more reliable than keyword filtering.
    """
    
    def __init__(self, priority_db_path: Optional[str] = None) -> None:
        """
        Initialize the priority game filter.
        
        Args:
            priority_db_path: Path to the priority games JSON file
        """
        if priority_db_path is None:
            # Default path relative to project root
            project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            priority_db_path = os.path.join(project_root, "data", "priority_games.json")
        
        self.priority_db_path: str = priority_db_path
        self.priority_games: List[PriorityGame] = self._load_priority_games()
        
    def _load_priority_games(self) -> List[PriorityGame]:
        """Load the priority games database from JSON file."""
        try:
            if not os.path.exists(self.priority_db_path):
                print(f"Warning: Priority games database not found at {self.priority_db_path}")
                return []
            
            # Try multiple encoding strategies to handle BOM and encoding issues
            encodings_to_try: List[str] = ['utf-8-sig', 'utf-8', 'ascii', 'latin-1']
            
            for encoding in encodings_to_try:
                try:
                    with open(self.priority_db_path, 'r', encoding=encoding) as f:
                        data = json.load(f)
                        return data.get('games', [])
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            
            # If all encodings fail, try reading as binary and removing BOM manually
            with open(self.priority_db_path, 'rb') as f:
                content = f.read()
                # Remove UTF-8 BOM if present
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                # Try to decode and parse
                data = json.loads(content.decode('utf-8'))
                return data.get('games', [])
                
        except Exception as e:
            print(f"Error loading priority games database: {e}")
            return []
    
    def reload_database(self) -> bool:
        """Reload the priority games database. Returns True if successful."""
        try:
            self.priority_games = self._load_priority_games()
            return True
        except Exception as e:
            print(f"Error reloading priority games database: {e}")
            return False
    
    def find_matching_games(self, game_title: str) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find games in the priority database that match the given title.
        
        Args:
            game_title: The game title to search for
            
        Returns:
            List of tuples (game_data, match_score) sorted by priority then match score
        """
        if not self.priority_games:
            return []
        
        matches = []
        title_lower = game_title.lower().strip()
        
        for game in self.priority_games:
            game_title_lower = game['title'].lower().strip()
            
            # Calculate match score
            match_score = self._calculate_match_score(title_lower, game_title_lower)
            
            if match_score > 0:
                matches.append((game, match_score))
        
        # Sort by priority (descending) then by match score (descending)
        matches.sort(key=lambda x: (x[0]['priority'], x[1]), reverse=True)
        
        return matches
    
    def _calculate_match_score(self, search_title: str, db_title: str) -> float:
        """
        Calculate how well two titles match.
        
        Returns:
            0.0: No match
            0.1-0.5: Partial word match
            0.6-0.8: Good partial match
            0.9-1.0: Excellent match
        """
        # Exact match
        if search_title == db_title:
            return 1.0
        
        # One title contains the other completely
        if db_title in search_title:
            return 0.9
        if search_title in db_title:
            return 0.85
        
        # Split into words for word-based matching
        search_words = set(re.findall(r'\w+', search_title))
        db_words = set(re.findall(r'\w+', db_title))
        
        if not search_words or not db_words:
            return 0.0
        
        # Calculate word overlap
        common_words = search_words.intersection(db_words)
        
        if not common_words:
            return 0.0
        
        # Score based on word overlap percentage
        overlap_ratio = len(common_words) / min(len(search_words), len(db_words))
        
        if overlap_ratio >= 0.8:
            return 0.8
        elif overlap_ratio >= 0.6:
            return 0.7
        elif overlap_ratio >= 0.4:
            return 0.6
        elif overlap_ratio >= 0.2:
            return 0.4
        else:
            return 0.1
    
    def is_priority_game(self, game_title: str, min_priority: int = 1, min_match_score: float = 0.6) -> bool:
        """
        Check if a game is in the priority database with sufficient priority and match score.
        
        Args:
            game_title: The game title to check
            min_priority: Minimum priority score required (1-10)
            min_match_score: Minimum match score required (0.0-1.0)
            
        Returns:
            True if the game meets the criteria
        """
        matches = self.find_matching_games(game_title)
        
        for game_data, match_score in matches:
            if game_data['priority'] >= min_priority and match_score >= min_match_score:
                return True
        
        return False
    
    def get_game_priority(self, game_title: str, min_match_score: float = 0.6) -> Optional[int]:
        """
        Get the priority score for a game.
        
        Args:
            game_title: The game title to check
            min_match_score: Minimum match score required
            
        Returns:
            Priority score (1-10) or None if not found
        """
        matches = self.find_matching_games(game_title)
        
        for game_data, match_score in matches:
            if match_score >= min_match_score:
                return game_data['priority']
        
        return None
    
    def filter_deals_by_priority(self, deals: List[Deal], 
                                min_priority: int = 5, 
                                min_match_score: float = 0.6,
                                max_results: Optional[int] = None,
                                strict_mode: bool = True) -> List[Deal]:
        """
        Filter a list of deals to only include priority games.
        
        Args:
            deals: List of deal dictionaries with 'title' key
            min_priority: Minimum priority score required (1-10)
            min_match_score: Minimum match score required (0.0-1.0)
            max_results: Maximum number of results to return
            strict_mode: If True, only return games that match priority database
            
        Returns:
            Filtered list of deals, sorted by priority then original order
        """
        priority_deals = []
        
        for deal in deals:
            game_title = deal.get('title', '')
            matches = self.find_matching_games(game_title)
            
            best_match = None
            best_priority = 0
            
            for game_data, match_score in matches:
                if (game_data['priority'] >= min_priority and 
                    match_score >= min_match_score and 
                    game_data['priority'] > best_priority):
                    
                    best_match = (game_data, match_score)
                    best_priority = game_data['priority']
            
            if best_match:
                # Add priority info to the deal
                deal_copy = deal.copy()
                deal_copy['_priority'] = best_match[0]['priority']
                deal_copy['_match_score'] = best_match[1]
                deal_copy['_priority_game'] = best_match[0]
                priority_deals.append(deal_copy)
            elif not strict_mode:
                # In non-strict mode, include non-priority games but mark them
                deal_copy = deal.copy()
                deal_copy['_priority'] = 0
                deal_copy['_match_score'] = 0.0
                deal_copy['_priority_game'] = None
                priority_deals.append(deal_copy)
        
        # Custom sorting: Priority takes precedence over discount only if discount is above 50%
        def sort_key(deal):
            priority = deal.get('_priority', 0)
            discount_str = deal.get('discount', '0%')
            
            # Extract numeric discount value
            try:
                discount_num = int(discount_str.replace('%', '')) if discount_str else 0
            except (ValueError, AttributeError):
                discount_num = 0
            
            # If discount is above 50%, sort by priority first, then by discount
            if discount_num > 50:
                return (priority, discount_num, deal.get('_match_score', 0))
            else:
                # If discount is 50% or below, sort by discount first, then by priority
                return (discount_num, priority, deal.get('_match_score', 0))
        
        priority_deals.sort(key=sort_key, reverse=True)
        
        if max_results:
            priority_deals = priority_deals[:max_results]
        
        return priority_deals
    
    def debug_game_matching(self, game_title: str) -> Dict[str, Any]:
        """
        Debug method to see how a game title matches against the priority database.
        
        Args:
            game_title: The game title to debug
            
        Returns:
            Debug information about matching
        """
        matches = self.find_matching_games(game_title)
        
        debug_info = {
            "search_title": game_title,
            "total_matches": len(matches),
            "matches": []
        }
        
        for game_data, match_score in matches[:5]:  # Show top 5 matches
            debug_info["matches"].append({
                "db_title": game_data['title'],
                "priority": game_data['priority'],
                "match_score": match_score,
                "category": game_data.get('category', 'Unknown')
            })
        
        return debug_info

    def get_database_stats(self) -> DatabaseStats:
        """Get statistics about the priority games database."""
        if not self.priority_games:
            return {"total_games": 0, "priority_distribution": {}, "categories": []}
        
        priority_distribution = {}
        categories = {}
        
        for game in self.priority_games:
            priority = game.get('priority', 0)
            category = game.get('category', 'Unknown')
            
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_games": len(self.priority_games),
            "priority_distribution": priority_distribution,
            "categories": list(categories.keys())
        }


# Convenience functions for backward compatibility and easy usage
def is_priority_game(game_title: str, min_priority: int = 5) -> bool:
    """
    Quick check if a game is in the priority database.
    
    Args:
        game_title: The game title to check
        min_priority: Minimum priority score required (1-10)
        
    Returns:
        True if the game is a priority game
    """
    filter_obj = PriorityGameFilter()
    return filter_obj.is_priority_game(game_title, min_priority)


def filter_priority_games(deals: List[Dict[str, Any]], 
                         min_priority: int = 5, 
                         max_results: int = None) -> List[Dict[str, Any]]:
    """
    Filter deals to only include priority games.
    
    Args:
        deals: List of deal dictionaries
        min_priority: Minimum priority score required (1-10)
        max_results: Maximum number of results to return
        
    Returns:
        Filtered and sorted list of priority game deals
    """
    filter_obj = PriorityGameFilter()
    return filter_obj.filter_deals_by_priority(deals, min_priority, max_results=max_results)


def get_priority_score(game_title: str) -> Optional[int]:
    """
    Get the priority score for a game.
    
    Args:
        game_title: The game title to check
        
    Returns:
        Priority score (1-10) or None if not found
    """
    filter_obj = PriorityGameFilter()
    return filter_obj.get_game_priority(game_title)


# Legacy GameQualityFilter class for backward compatibility
class GameQualityFilter:
    """
    Legacy class that now uses the priority-based filtering system.
    Maintained for backward compatibility.
    """
    
    def __init__(self):
        self.priority_filter = PriorityGameFilter()
    
    def is_quality_game(self, title: str, store: str = None) -> bool:
        """Check if a game is considered quality based on priority database."""
        return self.priority_filter.is_priority_game(title, min_priority=4)  # Lower threshold for compatibility
    
    def is_quality_store(self, store: str) -> bool:
        """Check if a store is considered quality - always returns True now."""
        # Since we're using curated games, store quality is less important
        return True

    def is_asset_flip(self, title: str, price: float = 0, discount: int = 0) -> bool:
        """
        Detect potential asset flip games based on common patterns.
        
        Args:
            title: Game title to check
            price: Current price (optional)
            discount: Discount percentage (optional)
            
        Returns:
            True if the game appears to be an asset flip
        """
        title_lower = title.lower().strip()
        
        # Common asset flip patterns
        asset_flip_indicators = [
            # Common prefixes used by asset flip publishers
            r'^living\w+',  # LivingForest, LivingBattle, etc.
            r'^pixel\s+\w+',  # Pixel + random word combinations
            r'^super\s+\w+\s+simulator',  # Super X Simulator games
            r'^ultimate\s+\w+',  # Ultimate X games
            r'^extreme\s+\w+',  # Extreme X games
            
            # Suspicious word combinations
            r'\b(baton|bandage|bustop)\b',  # Weird random objects
            r'\b(muscle|sniper hunting rifle)\b',  # Odd combinations
            r'\bmeat\s*(ball|stick|punch)\b',  # Meat-themed games
            
            # Games with numbers/versions that seem inflated
            r'\bhd\s+remaster\b',  # HD Remaster of simple games
            r'\bdeluxe\s+edition\b.*\bsimulator\b',  # Deluxe Edition Simulators
            
            # Suspiciously generic titles
            r'^(grab|kill|play)\s+(and|with)\s+(guts|my|kill)\b',  # Violent/crude titles
            r'^(skidaddle|skidoodle)\b',  # Nonsensical names
        ]
        
        # Check for asset flip patterns
        for pattern in asset_flip_indicators:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return True
        
        # Additional heuristics based on pricing
        if discount >= 90 and price < 2.0:
            # Very high discounts on very cheap games are suspicious
            # Many asset flips use fake high original prices with 90%+ discounts
            suspicious_cheap_patterns = [
                r'\b(simulator|remaster|deluxe|ultimate|extreme)\b',
                r'^[a-z]+\s+[a-z]+$',  # Simple two-word titles
            ]
            
            for pattern in suspicious_cheap_patterns:
                if re.search(pattern, title_lower, re.IGNORECASE):
                    return True
        
        return False