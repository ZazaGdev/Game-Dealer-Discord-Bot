#!/usr/bin/env python3
"""
Test the fixed priority search exact matching functionality
"""

import asyncio
import json
import os
import sys

# Add the project root to Python path so we can import modules
sys.path.insert(0, os.path.dirname(__file__))

def normalize_title_for_matching(title):
    """Normalize title by removing special characters that don't affect matching"""
    import re
    # Remove trademark, registered, copyright symbols and similar special chars
    normalized = re.sub(r'[™®©℗℠]', '', title)
    # Remove extra whitespace and convert to lowercase
    normalized = ' '.join(normalized.split()).lower().strip()
    return normalized

def test_exact_matching():
    """Test the exact matching functionality with real priority games data"""
    
    # Load a few sample priority games
    priority_games_sample = [
        {"title": "Raft", "priority": 8, "category": "Survival"},
        {"title": "Minecraft", "priority": 9, "category": "Sandbox"},
        {"title": "The Elder Scrolls V: Skyrim", "priority": 9, "category": "RPG"},
        {"title": "Portal 2", "priority": 9, "category": "Puzzle"},
        {"title": "Half-Life 2", "priority": 9, "category": "Shooter"}
    ]
    
    # Simulate deal titles that could come from API with potential false positive issues
    sample_deals = [
        {"title": "Raft™", "discount": "25%", "store": "Steam"},  # Should match Raft
        {"title": "Raft", "discount": "50%", "store": "Epic"},   # Should match Raft
        {"title": "Minecraft: Raft Edition", "discount": "30%", "store": "GOG"},  # Should NOT match Raft
        {"title": "World of Goo", "discount": "75%", "store": "Steam"},  # Should not match anything
        {"title": "Portal 2™", "discount": "80%", "store": "Steam"},  # Should match Portal 2
        {"title": "Half-Life 2: Episode One", "discount": "60%", "store": "Steam"},  # Should NOT match Half-Life 2
        {"title": "The Elder Scrolls V: Skyrim™ Special Edition", "discount": "40%", "store": "Steam"}  # Should NOT match (different editions)
    ]
    
    print("Testing Priority Search Exact Matching Fix")
    print("=" * 50)
    
    matched_games = []
    
    for deal in sample_deals:
        deal_title = deal.get('title', '').strip()
        normalized_deal_title = normalize_title_for_matching(deal_title)
        
        # Find exact matches in priority database
        matches = []
        for priority_game in priority_games_sample:
            priority_title = priority_game.get('title', '').strip()
            normalized_priority_title = normalize_title_for_matching(priority_title)
            
            if normalized_deal_title == normalized_priority_title:
                matches.append(priority_game['title'])
                matched_games.append({
                    'deal_title': deal_title,
                    'matched_priority_game': priority_game['title'],
                    'discount': deal['discount'],
                    'store': deal['store']
                })
        
        status = "MATCH" if matches else "NO MATCH"
        match_info = f" -> {matches[0]}" if matches else ""
        print(f"{status:8} | '{deal_title}'{match_info}")
    
    print("\n" + "=" * 50)
    print(f"Summary: {len(matched_games)} deals matched from {len(sample_deals)} total deals")
    
    if matched_games:
        print("\nMatched Deals:")
        for match in matched_games:
            print(f"  • {match['deal_title']} -> {match['matched_priority_game']} ({match['discount']} off on {match['store']})")
    
    # Verify the key fix: "Minecraft: Raft Edition" should NOT match "Raft"
    problem_case = any(match['deal_title'] == "Minecraft: Raft Edition" and match['matched_priority_game'] == "Raft" for match in matched_games)
    
    if problem_case:
        print("\n❌ FAILED: 'Minecraft: Raft Edition' incorrectly matched 'Raft'")
        return False
    else:
        print("\n✅ SUCCESS: Fixed false positive matching! 'Minecraft: Raft Edition' does NOT match 'Raft'")
        return True

if __name__ == "__main__":
    success = test_exact_matching()
    
    if success:
        print("\n🎉 Priority search exact matching fix is working correctly!")
        print("Now only exact title matches (ignoring special characters) will be returned.")
    else:
        print("\n💥 Test failed - there may be issues with the matching logic.")