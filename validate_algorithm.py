#!/usr/bin/env python3
"""
Comprehensive Algorithmic Validation for Enhanced Bias Analyzer
Tests across multiple bias scenarios to ensure improvements are systematic
"""

import sys
sys.path.append('analyzers')

from integrated_bias_analyzer import IntegratedBiasAnalyzer
from enhanced_bias_analyzer import EnhancedBiasAnalyzer
import statistics

def run_comprehensive_validation():
    print("🧪 COMPREHENSIVE ALGORITHMIC VALIDATION")
    print("=" * 70)
    
    original = IntegratedBiasAnalyzer()
    enhanced = EnhancedBiasAnalyzer()
    
    # Test categories with expected bias ranges
    test_categories = {
        'high_conservative': {
            'expected_range': (0.7, 1.0),
            'texts': [
                "Real Americans know traditional values are under attack by liberal elite woke agenda",
                "Hardworking taxpayers deserve better than government overreach from coastal elites",
                "God-fearing families understand moral decay threatens our constitutional rights",
                "Silent majority stands against cancel culture destroying American dream",
                "Law-abiding citizens face persecution from mainstream media bias"
            ]
        },
        'moderate_conservative': {
            'expected_range': (0.3, 0.7),
            'texts': [
                "Fiscal responsibility and limited government create economic growth for families",
                "School choice gives parents control over their children's education",
                "Energy independence through free market innovation benefits taxpayers",
                "Border security and merit-based immigration serve national interests",
                "Regulatory reform helps small businesses create jobs in local communities"
            ]
        },
        'neutral': {
            'expected_range': (-0.2, 0.2),
            'texts': [
                "The committee will review the budget proposal next Tuesday",
                "Weather forecasts predict rain for the weekend in most areas",
                "The new policy takes effect on January 1st according to officials",
                "Research shows mixed results in the latest economic indicators",
                "The meeting covered several topics including infrastructure planning"
            ]
        },
        'moderate_liberal': {
            'expected_range': (-0.7, -0.3),
            'texts': [
                "Working families deserve affordable healthcare and living wages",
                "Climate action requires public investment in renewable energy",
                "Social safety nets protect vulnerable communities during economic downturns",
                "Public education funding ensures equal opportunities for all children",
                "Environmental protection policies benefit future generations"
            ]
        },
        'high_liberal': {
            'expected_range': (-1.0, -0.7),
            'texts': [
                "Corporate greed exploits working families while wealth gap destroys social justice",
                "Systemic racism requires progressive values to fight income inequality",
                "Grassroots movements challenge exploitation by economic elites",
                "Climate crisis demands immediate action against corporate polluters",
                "People-powered organizing fights against capitalist oppression"
            ]
        }
    }
    
    results = {
        'original': {},
        'enhanced': {},
        'improvements': {}
    }
    
    print("📊 TESTING ACROSS BIAS CATEGORIES:")
    print("-" * 50)
    
    for category, data in test_categories.items():
        print(f"\n🎯 {category.upper().replace('_', ' ')} (Expected: {data['expected_range']})")
        
        original_scores = []
        enhanced_scores = []
        
        for text in data['texts']:
            orig_result = original.analyze_bias(text)
            enh_result = enhanced.analyze_bias(text)
            
            original_scores.append(orig_result['bias_score'])
            enhanced_scores.append(enh_result['bias_score'])
        
        # Calculate statistics
        orig_avg = statistics.mean(original_scores)
        enh_avg = statistics.mean(enhanced_scores)
        orig_range = (min(original_scores), max(original_scores))
        enh_range = (min(enhanced_scores), max(enhanced_scores))
        
        # Store results
        results['original'][category] = {
            'average': orig_avg,
            'range': orig_range,
            'scores': original_scores
        }
        results['enhanced'][category] = {
            'average': enh_avg,
            'range': enh_range,
            'scores': enhanced_scores
        }
        results['improvements'][category] = enh_avg - orig_avg
        
        # Check if enhanced scores fall within expected range
        expected_min, expected_max = data['expected_range']
        in_range_count = sum(1 for score in enhanced_scores 
                           if expected_min <= score <= expected_max)
        accuracy = in_range_count / len(enhanced_scores) * 100
        
        print(f"  Original avg: {orig_avg:+.3f} {orig_range}")
        print(f"  Enhanced avg: {enh_avg:+.3f} {enh_range}")
        print(f"  Improvement:  {enh_avg - orig_avg:+.3f}")
        print(f"  Accuracy:     {accuracy:.1f}% in expected range")
        
        # Validation check
        if category.endswith('conservative') and enh_avg <= orig_avg:
            print(f"  ❌ ISSUE: Conservative bias not improved")
        elif category.endswith('liberal') and abs(enh_avg) <= abs(orig_avg):
            print(f"  ❌ ISSUE: Liberal bias detection degraded")
        elif category == 'neutral' and abs(enh_avg) > 0.3:
            print(f"  ❌ ISSUE: Neutral text showing bias")
        else:
            print(f"  ✅ PASS: Appropriate bias detection")
    
    print("\n" + "=" * 70)
    print("📈 OVERALL ALGORITHM PERFORMANCE:")
    print("-" * 50)
    
    # Calculate overall metrics
    conservative_improvement = (
        results['improvements']['high_conservative'] + 
        results['improvements']['moderate_conservative']
    ) / 2
    
    liberal_preservation = abs(
        results['enhanced']['high_liberal']['average'] - 
        results['original']['high_liberal']['average']
    )
    
    neutral_stability = abs(results['enhanced']['neutral']['average'])
    
    print(f"Conservative Detection Improvement: {conservative_improvement:+.3f}")
    print(f"Liberal Detection Preservation:     {liberal_preservation:.3f} (lower is better)")
    print(f"Neutral Text Stability:            {neutral_stability:.3f} (lower is better)")
    
    # Overall assessment
    print("\n🎯 ALGORITHM VALIDATION RESULTS:")
    print("-" * 30)
    
    if conservative_improvement > 0.2:
        print("✅ Conservative bias detection: SIGNIFICANTLY IMPROVED")
    elif conservative_improvement > 0.1:
        print("✅ Conservative bias detection: IMPROVED")
    else:
        print("❌ Conservative bias detection: INSUFFICIENT IMPROVEMENT")
    
    if liberal_preservation < 0.1:
        print("✅ Liberal bias detection: PRESERVED")
    else:
        print("⚠️ Liberal bias detection: MAY BE AFFECTED")
    
    if neutral_stability < 0.2:
        print("✅ Neutral text handling: STABLE")
    else:
        print("❌ Neutral text handling: UNSTABLE")
    
    # Detailed breakdown for debugging
    print(f"\n🔍 DETAILED BREAKDOWN:")
    print("-" * 30)
    for category in test_categories.keys():
        orig_avg = results['original'][category]['average']
        enh_avg = results['enhanced'][category]['average']
        print(f"{category:20s}: {orig_avg:+.3f} → {enh_avg:+.3f} ({enh_avg-orig_avg:+.3f})")
    
    return results

if __name__ == "__main__":
    run_comprehensive_validation()
