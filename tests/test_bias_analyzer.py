#!/usr/bin/env python3
"""
Tests for the integrated bias analyzer
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from analyzers.integrated_bias_analyzer import IntegratedBiasAnalyzer


class TestIntegratedBiasAnalyzer:
    """Test cases for the IntegratedBiasAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return IntegratedBiasAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'methodology_weights')
        assert analyzer.methodology_weights['harvard'] == 0.40
        assert analyzer.methodology_weights['columbia'] == 0.35
        assert analyzer.methodology_weights['allsides'] == 0.20
        assert analyzer.methodology_weights['sentiment'] == 0.05
    
    def test_neutral_content(self, analyzer):
        """Test analysis of neutral content"""
        neutral_text = "The Federal Reserve announced its decision on interest rates today. The committee voted 7-3 to maintain current rates."
        
        result = analyzer.analyze_bias(neutral_text)
        
        assert 'bias_score' in result
        assert 'bias_description' in result
        assert abs(result['bias_score']) < 0.2  # Should be minimal bias
        assert 'neutral' in result['bias_description'].lower()
    
    def test_left_leaning_content(self, analyzer):
        """Test analysis of left-leaning content"""
        left_text = "Corporate greed continues to hurt working families while income inequality grows. Social justice demands immediate action."
        
        result = analyzer.analyze_bias(left_text)
        
        assert result['bias_score'] < 0  # Should be negative (left-leaning)
        assert 'left' in result['bias_description'].lower()
    
    def test_right_leaning_content(self, analyzer):
        """Test analysis of right-leaning content"""
        right_text = "Traditional values and fiscal responsibility remain essential. Free market principles and individual liberty built this nation."
        
        result = analyzer.analyze_bias(right_text)
        
        assert result['bias_score'] > 0  # Should be positive (right-leaning)
        assert 'right' in result['bias_description'].lower()
    
    def test_empty_content(self, analyzer):
        """Test analysis of empty content"""
        result = analyzer.analyze_bias("")
        
        assert result['bias_score'] == 0.0
        assert 'No content to analyze' in result['bias_description']
    
    def test_score_range(self, analyzer):
        """Test that scores stay within expected range"""
        test_cases = [
            "Neutral content about weather today.",
            "Corporate greed exploits working families through systemic inequality.",
            "Traditional values and fiscal responsibility protect individual liberty.",
            "BREAKING: Shocking revelations about controversial policy decisions."
        ]
        
        for text in test_cases:
            result = analyzer.analyze_bias(text)
            assert -1.0 <= result['bias_score'] <= 1.0
    
    def test_methodology_breakdown(self, analyzer):
        """Test that methodology breakdown is included in results"""
        text = "The controversial policy affects working families and fiscal responsibility."
        
        result = analyzer.analyze_bias(text)
        
        assert 'analysis_details' in result
        assert 'methodology_scores' in result['analysis_details']
        assert 'methodology_weights' in result['analysis_details']
        
        # Check all methodologies are present
        methodologies = result['analysis_details']['methodology_scores']
        assert 'harvard' in methodologies
        assert 'columbia' in methodologies
        assert 'allsides' in methodologies
        assert 'sentiment' in methodologies
    
    def test_significant_figures(self, analyzer):
        """Test that scores are formatted to 3 significant figures"""
        text = "Some test content for bias analysis."
        
        result = analyzer.analyze_bias(text)
        score = result['bias_score']
        
        # Check that score has appropriate precision
        if score != 0:
            score_str = str(abs(score))
            if '.' in score_str:
                # Count significant digits
                digits = score_str.replace('.', '').lstrip('0')
                assert len(digits) <= 3 or score_str.endswith('0')


if __name__ == '__main__':
    pytest.main([__file__])
