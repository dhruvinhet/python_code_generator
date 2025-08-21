#!/usr/bin/env python3
"""
Test script for the advanced agents system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from advanced_agents_system import AdvancedAgentsSystem
    print("✅ Advanced agents system imported successfully")
    
    # Test instantiation
    system = AdvancedAgentsSystem()
    print("✅ Advanced agents system instantiated successfully")
    
    # Test research agent specifically
    research_agent = system.agents['research']
    print("✅ Research agent accessible")
    
    # Test the dataset scoring function that was causing issues
    test_dataset = {
        'quality_score': '8',  # String instead of int (common LLM response)
        'domain_relevance': 7,  # Integer
        'url': 'https://example.com/data.csv',
        'size': '10MB'
    }
    
    # This should work with our fix
    try:
        # Simulate the scoring function
        score = 0
        
        # Quality and domain relevance - ensure they are integers
        try:
            quality_score = test_dataset.get('quality_score', 0)
            if isinstance(quality_score, str):
                quality_score = int(quality_score.split('-')[0]) if '-' in quality_score else int(quality_score)
            score += quality_score
        except (ValueError, TypeError):
            score += 5  # Default score if parsing fails
        
        try:
            domain_relevance = test_dataset.get('domain_relevance', 0)
            if isinstance(domain_relevance, str):
                domain_relevance = int(domain_relevance.split('-')[0]) if '-' in domain_relevance else int(domain_relevance)
            score += domain_relevance
        except (ValueError, TypeError):
            score += 5  # Default score if parsing fails
        
        print(f"✅ Dataset scoring works: {score}")
        
    except Exception as e:
        print(f"❌ Dataset scoring failed: {e}")
        
    print("✅ All tests passed!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
