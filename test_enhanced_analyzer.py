#!/usr/bin/env python3
"""
Test Enhanced Bias Analyzer vs Original
"""

import sys
sys.path.append('analyzers')

from integrated_bias_analyzer import IntegratedBiasAnalyzer
from enhanced_bias_analyzer import EnhancedBiasAnalyzer

def test_analyzers():
    print("🔍 Testing Enhanced vs Original Bias Analyzer")
    print("=" * 60)
    
    # Initialize both analyzers
    original = IntegratedBiasAnalyzer()
    enhanced = EnhancedBiasAnalyzer()
    
    # Test cases - conservative-leaning articles
    test_cases = [
        {
            'title': 'Real Americans Stand Up Against Liberal Elite Agenda',
            'content': '''
            Hardworking taxpayers are finally saying enough is enough to the coastal elites 
            who want to destroy our traditional values. How long will law-abiding citizens 
            tolerate this government overreach? Studies show that 75% of Americans believe 
            in common sense solutions, not the woke agenda being pushed by mainstream media.
            
            It's time to restore fiscal responsibility and constitutional rights. The silent 
            majority knows that individual liberty and personal responsibility built this 
            great nation. God-fearing families understand that moral decay threatens our 
            American dream.
            '''
        },
        {
            'title': 'Border Security Crisis Threatens National Safety',
            'content': '''
            According to polls, most Americans want secure borders and merit-based immigration. 
            Why won't Democrats listen to the people? Law enforcement officials say the current 
            system puts law-abiding citizens at risk. 
            
            Common sense tells us that energy independence and regulatory reform would create 
            jobs for hardworking families. Instead, we get more government overreach and 
            political correctness from the liberal elite.
            '''
        },
        {
            'title': 'Traditional Marriage Under Attack by Cancel Culture',
            'content': '''
            Christian values and biblical principles are being silenced by the woke mob. 
            How can anyone still believe that moral relativism is good for society? 
            Family breakdown and moral decay are obvious results of abandoning traditional values.
            
            Real Americans know that God-given rights come from our founding fathers, not 
            government bureaucrats. The deep state wants to destroy everything that made 
            America great.
            '''
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📰 TEST CASE {i}: {test_case['title']}")
        print("-" * 40)
        
        # Analyze with original
        original_result = original.analyze_bias(test_case['content'], test_case['title'])
        
        # Analyze with enhanced
        enhanced_result = enhanced.analyze_bias(test_case['content'], test_case['title'])
        
        print(f"Original Score: {original_result['bias_score']:.3f} ({original_result.get('bias_description', 'N/A')})")
        print(f"Enhanced Score: {enhanced_result['bias_score']:.3f} ({enhanced_result['bias_description']})")
        
        # Show improvement
        improvement = enhanced_result['bias_score'] - original_result['bias_score']
        print(f"Improvement: {improvement:+.3f} (more sensitive to conservative bias)")
        
        if 'methodology_breakdown' in enhanced_result:
            print("Enhanced Breakdown:")
            for method, score in enhanced_result['methodology_breakdown'].items():
                print(f"  {method}: {score:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete - Enhanced analyzer should show higher conservative bias scores")

if __name__ == "__main__":
    test_analyzers()
