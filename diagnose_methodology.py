#!/usr/bin/env python3
"""
Methodology Diagnostic Tool
Analyzes WHY scores are low by examining each component
"""

import sys
sys.path.append('analyzers')
from enhanced_bias_analyzer import EnhancedBiasAnalyzer

def diagnose_methodology():
    print("🔬 METHODOLOGY DIAGNOSTIC")
    print("=" * 50)
    
    analyzer = EnhancedBiasAnalyzer()
    
    # Extreme test case that should score 0.9+
    extreme_text = "The deep state liberal elite are destroying real America with their woke cancel culture agenda while God-fearing patriots are being silenced and persecuted by mainstream media bias"
    
    print(f"Text: {extreme_text}")
    print(f"Expected Score: 0.9+")
    print()
    
    # Get detailed breakdown
    result = analyzer.analyze_bias(extreme_text)
    
    print("🔍 COMPONENT ANALYSIS:")
    print("-" * 30)
    
    # Manually call each method to see what's happening
    harvard_score = analyzer._calculate_harvard_score(extreme_text, "")
    columbia_score = analyzer._calculate_columbia_score(extreme_text)
    allsides_score = analyzer._calculate_allsides_score(extreme_text)
    sentiment_score = analyzer._calculate_sentiment_score(extreme_text)
    conservative_patterns = analyzer._calculate_conservative_patterns(extreme_text)
    
    print(f"Harvard Score:     {harvard_score:.3f} (weight: 30%)")
    print(f"Columbia Score:    {columbia_score:.3f} (weight: 45%)")
    print(f"AllSides Score:    {allsides_score:.3f} (weight: 10%)")
    print(f"Sentiment Score:   {sentiment_score:.3f} (weight: 15%)")
    print(f"Pattern Bonus:     {conservative_patterns:.3f} (weight: 25%)")
    
    # Calculate weighted contributions
    harvard_contrib = harvard_score * 0.30
    columbia_contrib = columbia_score * 0.45
    allsides_contrib = allsides_score * 0.10
    sentiment_contrib = sentiment_score * 0.15
    pattern_contrib = conservative_patterns * 0.25
    
    print(f"\n📊 WEIGHTED CONTRIBUTIONS:")
    print(f"Harvard:     {harvard_contrib:.3f}")
    print(f"Columbia:    {columbia_contrib:.3f}")
    print(f"AllSides:    {allsides_contrib:.3f}")
    print(f"Sentiment:   {sentiment_contrib:.3f}")
    print(f"Patterns:    {pattern_contrib:.3f}")
    print(f"TOTAL:       {sum([harvard_contrib, columbia_contrib, allsides_contrib, sentiment_contrib, pattern_contrib]):.3f}")
    
    print(f"\n🎯 ISSUES IDENTIFIED:")
    print("-" * 20)
    
    # Identify what's limiting the score
    if harvard_score < 0.8:
        print(f"❌ Harvard method too low: {harvard_score:.3f} (should be 0.8+)")
        
        # Debug Harvard method
        phrase_bias = analyzer._get_phrase_bias(extreme_text)
        print(f"   Phrase bias detected: {phrase_bias:.3f}")
        
        # Check what phrases are being found
        text_lower = extreme_text.lower()
        found_phrases = []
        for phrase_list in analyzer.columbia_partisan_phrases['right_phrases'].values():
            for phrase in phrase_list:
                if phrase.lower() in text_lower:
                    found_phrases.append(phrase)
        print(f"   Conservative phrases found: {found_phrases}")
    
    if columbia_score < 0.8:
        print(f"❌ Columbia method too low: {columbia_score:.3f} (should be 0.8+)")
    
    if sentiment_score < 0.5:
        print(f"❌ Sentiment too low: {sentiment_score:.3f} (should be 0.5+ for extreme)")
        
        # Debug sentiment
        from textblob import TextBlob
        blob = TextBlob(extreme_text)
        raw_polarity = blob.sentiment.polarity
        print(f"   Raw sentiment polarity: {raw_polarity:.3f}")
        print(f"   After amplification: {sentiment_score:.3f}")
    
    if conservative_patterns < 0.5:
        print(f"❌ Pattern detection too low: {conservative_patterns:.3f} (should be 0.5+)")
        
        # Debug patterns
        text_lower = extreme_text.lower()
        for category, patterns in analyzer.conservative_patterns.items():
            matches = []
            for pattern in patterns:
                import re
                found = re.findall(pattern, text_lower)
                if found:
                    matches.extend(found)
            if matches:
                print(f"   {category}: {matches}")
    
    print(f"\n💡 METHODOLOGY FIXES NEEDED:")
    print("-" * 30)
    
    # Calculate what each component needs to be to reach 0.9
    target_score = 0.9
    current_total = sum([harvard_contrib, columbia_contrib, allsides_contrib, sentiment_contrib, pattern_contrib])
    deficit = target_score - current_total
    
    print(f"Current total: {current_total:.3f}")
    print(f"Target score:  {target_score:.3f}")
    print(f"Deficit:       {deficit:.3f}")
    
    # Suggest which methods need improvement
    if harvard_contrib < 0.24:  # 30% of 0.8
        needed_harvard = 0.8
        print(f"• Harvard needs to reach {needed_harvard:.3f} (currently {harvard_score:.3f})")
    
    if columbia_contrib < 0.36:  # 45% of 0.8  
        needed_columbia = 0.8
        print(f"• Columbia needs to reach {needed_columbia:.3f} (currently {columbia_score:.3f})")
    
    if sentiment_contrib < 0.12:  # 15% of 0.8
        needed_sentiment = 0.8
        print(f"• Sentiment needs to reach {needed_sentiment:.3f} (currently {sentiment_score:.3f})")

if __name__ == "__main__":
    diagnose_methodology()
