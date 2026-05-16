#!/usr/bin/env python3
"""
Improved Extreme Bias Detection and Accuracy Measurement
"""

import sys
sys.path.append('analyzers')

from integrated_bias_analyzer import IntegratedBiasAnalyzer
from enhanced_bias_analyzer import EnhancedBiasAnalyzer
import statistics

def test_extreme_detection():
    print("🔥 EXTREME BIAS DETECTION ANALYSIS")
    print("=" * 60)
    
    original = IntegratedBiasAnalyzer()
    enhanced = EnhancedBiasAnalyzer()
    
    # EXTREME test cases with manual expert ratings
    extreme_cases = {
        'extreme_conservative': {
            'target_score': 0.85,  # Should be 0.8-1.0
            'texts': [
                {
                    'text': "The deep state liberal elite are destroying real America with their woke cancel culture agenda while God-fearing patriots are being silenced and persecuted by mainstream media bias",
                    'expert_rating': 0.9
                },
                {
                    'text': "Radical Democrats hate traditional marriage and want to indoctrinate our children with their immoral agenda while hardworking taxpayers suffer under government tyranny",
                    'expert_rating': 0.85
                },
                {
                    'text': "Why won't the corrupt establishment admit that law-abiding citizens are under attack by the socialist mob trying to destroy our constitutional rights and Christian values",
                    'expert_rating': 0.9
                }
            ]
        },
        'extreme_liberal': {
            'target_score': -0.85,  # Should be -1.0 to -0.8
            'texts': [
                {
                    'text': "Corporate greed and systemic racism exploit working families while capitalist oppression destroys social justice and economic equality for marginalized communities",
                    'expert_rating': -0.9
                },
                {
                    'text': "The fascist right-wing agenda promotes white supremacy and environmental destruction while progressive movements fight against oligarchy and income inequality",
                    'expert_rating': -0.85
                },
                {
                    'text': "Billionaire elites hoard wealth while people-powered grassroots organizing challenges the patriarchal system that perpetuates climate crisis and worker exploitation",
                    'expert_rating': -0.9
                }
            ]
        }
    }
    
    def calculate_accuracy_metrics(predicted_scores, expert_ratings, target_range):
        """Calculate multiple accuracy metrics"""
        
        # 1. Mean Absolute Error (MAE)
        mae = statistics.mean(abs(p - e) for p, e in zip(predicted_scores, expert_ratings))
        
        # 2. Root Mean Square Error (RMSE)
        rmse = (statistics.mean((p - e)**2 for p, e in zip(predicted_scores, expert_ratings)))**0.5
        
        # 3. Range Accuracy (% within target range)
        min_target, max_target = target_range
        in_range = sum(1 for score in predicted_scores if min_target <= score <= max_target)
        range_accuracy = in_range / len(predicted_scores) * 100
        
        # 4. Extreme Detection Rate (% above threshold)
        threshold = abs(target_range[0]) * 0.8  # 80% of target extreme
        extreme_detected = sum(1 for score in predicted_scores if abs(score) >= threshold)
        extreme_rate = extreme_detected / len(predicted_scores) * 100
        
        # 5. Direction Accuracy (correct positive/negative)
        direction_correct = sum(1 for p, e in zip(predicted_scores, expert_ratings) 
                              if (p > 0) == (e > 0))
        direction_accuracy = direction_correct / len(predicted_scores) * 100
        
        return {
            'mae': mae,
            'rmse': rmse,
            'range_accuracy': range_accuracy,
            'extreme_detection_rate': extreme_rate,
            'direction_accuracy': direction_accuracy
        }
    
    print("📊 DETAILED EXTREME ANALYSIS:")
    print("-" * 40)
    
    for category, data in extreme_cases.items():
        print(f"\n🎯 {category.upper().replace('_', ' ')}")
        print(f"Target Score: {data['target_score']}")
        
        original_scores = []
        enhanced_scores = []
        expert_ratings = []
        
        for item in data['texts']:
            text = item['text']
            expert_rating = item['expert_rating']
            
            orig_result = original.analyze_bias(text)
            enh_result = enhanced.analyze_bias(text)
            
            original_scores.append(orig_result['bias_score'])
            enhanced_scores.append(enh_result['bias_score'])
            expert_ratings.append(expert_rating)
            
            print(f"\nText: {text[:60]}...")
            print(f"  Expert:   {expert_rating:+.2f}")
            print(f"  Original: {orig_result['bias_score']:+.2f}")
            print(f"  Enhanced: {enh_result['bias_score']:+.2f}")
        
        # Calculate target range
        if category == 'extreme_conservative':
            target_range = (0.8, 1.0)
        else:
            target_range = (-1.0, -0.8)
        
        # Calculate accuracy metrics
        orig_metrics = calculate_accuracy_metrics(original_scores, expert_ratings, target_range)
        enh_metrics = calculate_accuracy_metrics(enhanced_scores, expert_ratings, target_range)
        
        print(f"\n📈 ACCURACY METRICS:")
        print(f"                    Original  Enhanced  Improvement")
        print(f"MAE (lower better): {orig_metrics['mae']:.3f}     {enh_metrics['mae']:.3f}     {orig_metrics['mae']-enh_metrics['mae']:+.3f}")
        print(f"RMSE (lower better):{orig_metrics['rmse']:.3f}     {enh_metrics['rmse']:.3f}     {orig_metrics['rmse']-enh_metrics['rmse']:+.3f}")
        print(f"Range Accuracy:     {orig_metrics['range_accuracy']:.1f}%      {enh_metrics['range_accuracy']:.1f}%      {enh_metrics['range_accuracy']-orig_metrics['range_accuracy']:+.1f}%")
        print(f"Extreme Detection:  {orig_metrics['extreme_detection_rate']:.1f}%      {enh_metrics['extreme_detection_rate']:.1f}%      {enh_metrics['extreme_detection_rate']-orig_metrics['extreme_detection_rate']:+.1f}%")
        print(f"Direction Accuracy: {orig_metrics['direction_accuracy']:.1f}%      {enh_metrics['direction_accuracy']:.1f}%      {enh_metrics['direction_accuracy']-orig_metrics['direction_accuracy']:+.1f}%")
        
        # Assessment
        print(f"\n🎯 ASSESSMENT:")
        if enh_metrics['mae'] < orig_metrics['mae']:
            print("✅ Enhanced algorithm is more accurate (lower MAE)")
        else:
            print("❌ Enhanced algorithm is less accurate (higher MAE)")
            
        if enh_metrics['extreme_detection_rate'] > 80:
            print("✅ Good extreme detection rate")
        else:
            print("❌ Poor extreme detection rate - needs improvement")
    
    print(f"\n" + "=" * 60)
    print("🔍 EXTREME DETECTION RECOMMENDATIONS:")
    print("-" * 40)
    
    # Test what makes text more extreme
    test_amplifiers = [
        "deep state", "radical", "destroy", "hate", "corrupt", 
        "fascist", "socialist", "tyranny", "oppression", "elite"
    ]
    
    base_text = "Politicians support policies that affect the economy"
    
    print(f"\n📊 BIAS AMPLIFICATION TEST:")
    print(f"Base text: '{base_text}'")
    base_score = enhanced.analyze_bias(base_text)['bias_score']
    print(f"Base score: {base_score:.3f}")
    
    print(f"\nAmplifier effects:")
    for amplifier in test_amplifiers[:5]:  # Test top 5
        test_text = f"The {amplifier} politicians support policies that affect the economy"
        score = enhanced.analyze_bias(test_text)['bias_score']
        effect = score - base_score
        print(f"  '{amplifier}': {score:+.3f} ({effect:+.3f})")

if __name__ == "__main__":
    test_extreme_detection()
