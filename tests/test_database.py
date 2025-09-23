#!/usr/bin/env python3
"""
Quick test to check priority games database loading
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.game_filters import PriorityGameFilter

def test_database():
    print("Testing priority games database...")
    
    pf = PriorityGameFilter()
    stats = pf.get_database_stats()
    
    print(f"Total games loaded: {stats['total_games']}")
    
    if stats['total_games'] > 0:
        print("\nFirst 10 games:")
        for i, game in enumerate(pf.priority_games[:10], 1):
            print(f"  {i}. {game['title']} (Priority: {game['priority']})")
        
        # Test matching
        print(f"\nTesting game matching:")
        test_titles = ["Baldur's Gate 3", "Elden Ring", "The Witcher 3", "Cyberpunk 2077"]
        for title in test_titles:
            matches = pf.find_matching_games(title)
            if matches:
                best_match = matches[0]
                print(f"  '{title}' -> '{best_match[0]['title']}' (Score: {best_match[1]:.2f}, Priority: {best_match[0]['priority']})")
            else:
                print(f"  '{title}' -> No matches found")
    else:
        print("❌ No games loaded - database issue!")

if __name__ == "__main__":
    test_database()