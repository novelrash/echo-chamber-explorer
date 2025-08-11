#!/usr/bin/env python3
"""
Integrated Bias Analyzer
Combines Harvard/PNAS, Columbia, and AllSides methodologies with rebalanced weights
Harvard (40%) + Columbia (35%) + AllSides (20%) + Sentiment (5%)
"""

import re
import nltk
from textblob import TextBlob
from collections import Counter
import json
import math

class IntegratedBiasAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('punkt_tab')
        
        # Methodology weights (rebalanced)
        self.methodology_weights = {
            'harvard': 0.40,      # Position/attribution weighting (increased from 15%)
            'columbia': 0.35,     # Partisan phrase detection (increased from 25%)
            'allsides': 0.20,     # Multi-dimensional assessment (decreased from 55%)
            'sentiment': 0.05     # Overall sentiment (same)
        }
        
        # Columbia University partisan phrases (Gentzkow & Shapiro methodology)
        self.columbia_partisan_phrases = {
            'left_phrases': {
                'strong': [
                    'corporate greed', 'working families', 'income inequality', 
                    'social justice', 'climate crisis', 'systemic racism',
                    'wealth gap', 'exploitation', 'progressive values',
                    'people-powered', 'grassroots movement', 'economic justice'
                ],
                'moderate': [
                    'affordable healthcare', 'public investment', 'community organizing',
                    'environmental protection', 'worker rights', 'inclusive growth',
                    'public education', 'social safety net', 'civil rights'
                ]
            },
            'right_phrases': {
                'strong': [
                    'traditional values', 'fiscal responsibility', 'constitutional rights',
                    'free market', 'individual liberty', 'personal responsibility',
                    'law and order', 'american dream', 'founding fathers',
                    'limited government', 'free enterprise', 'moral values'
                ],
                'moderate': [
                    'economic growth', 'job creation', 'business friendly',
                    'competitive markets', 'innovation', 'entrepreneurship',
                    'national security', 'family values', 'local control'
                ]
            }
        }
        
        # Harvard position weights (from previous implementation)
        self.harvard_position_weights = {
            'headline': 2.0,
            'lead': 1.5,
            'early': 1.2,
            'middle': 1.0,
            'late': 0.8
        }
        
        # Harvard attribution weights
        self.harvard_attribution_weights = {
            'direct_quote': 2.0,
            'indirect_quote': 1.5,
            'paraphrase': 1.0,
            'background': 0.8
        }
        
        # AllSides multi-dimensional indicators (simplified without study group data)
        self.allsides_indicators = {
            'story_selection': {
                'patterns': [
                    r'breaking:?\s+',
                    r'exclusive:?\s+',
                    r'bombshell:?\s+',
                    r'shocking:?\s+'
                ],
                'weight': 1.0
            },
            'fact_opinion_balance': {
                'opinion_markers': [
                    'i believe', 'in my opinion', 'clearly', 'obviously',
                    'undoubtedly', 'certainly', 'without question'
                ],
                'weight': 1.5
            },
            'source_selection': {
                'single_source_indicators': [
                    'according to one source', 'a source said', 'sources close to'
                ],
                'multiple_source_indicators': [
                    'multiple sources', 'several officials', 'various experts'
                ],
                'weight': 1.2
            }
        }

    def analyze_bias(self, text, title="", url=""):
        """
        Comprehensive bias analysis using integrated methodology
        Returns bias score on -1.0 to +1.0 scale with 3 significant figures
        """
        if not text.strip():
            return self._format_result(0.0, "No content to analyze", {})
        
        # Initialize analysis components
        analysis_details = {
            'methodology_scores': {},
            'methodology_weights': self.methodology_weights,
            'component_analysis': {}
        }
        
        # 1. Harvard methodology (40% weight)
        harvard_score = self._analyze_harvard_methodology(text, title)
        analysis_details['methodology_scores']['harvard'] = harvard_score
        analysis_details['component_analysis']['harvard'] = harvard_score['details']
        
        # 2. Columbia methodology (35% weight)
        columbia_score = self._analyze_columbia_methodology(text)
        analysis_details['methodology_scores']['columbia'] = columbia_score
        analysis_details['component_analysis']['columbia'] = columbia_score['details']
        
        # 3. AllSides methodology (20% weight)
        allsides_score = self._analyze_allsides_methodology(text)
        analysis_details['methodology_scores']['allsides'] = allsides_score
        analysis_details['component_analysis']['allsides'] = allsides_score['details']
        
        # 4. Sentiment analysis (5% weight)
        sentiment_score = self._analyze_sentiment(text)
        analysis_details['methodology_scores']['sentiment'] = sentiment_score
        analysis_details['component_analysis']['sentiment'] = sentiment_score['details']
        
        # Calculate weighted final score
        final_score = (
            harvard_score['score'] * self.methodology_weights['harvard'] +
            columbia_score['score'] * self.methodology_weights['columbia'] +
            allsides_score['score'] * self.methodology_weights['allsides'] +
            sentiment_score['score'] * self.methodology_weights['sentiment']
        )
        
        # Ensure bounds and format to 3 sig figs
        final_score = max(-1.0, min(1.0, final_score))
        formatted_score = self._format_to_3_sig_figs(final_score)
        
        return self._format_result(formatted_score, self._get_bias_description(formatted_score), analysis_details)
    
    def _analyze_harvard_methodology(self, text, title):
        """Harvard/PNAS position and attribution weighting"""
        sentences = nltk.sent_tokenize(text)
        total_sentences = len(sentences)
        
        position_scores = []
        attribution_scores = []
        
        # Position-based analysis
        for i, sentence in enumerate(sentences):
            # Determine position weight
            if i == 0 or (title and sentence in title):
                weight = self.harvard_position_weights['headline']
            elif i < 3:
                weight = self.harvard_position_weights['lead'] if i == 1 else self.harvard_position_weights['early']
            elif i < total_sentences * 0.7:
                weight = self.harvard_position_weights['middle']
            else:
                weight = self.harvard_position_weights['late']
            
            sentence_bias = self._get_sentence_bias(sentence)
            position_scores.append(sentence_bias * weight)
        
        # Attribution analysis
        quote_patterns = {
            'direct': r'"([^"]+)",?\s+(?:said|stated|declared|claimed)\s+([^.]+)',
            'indirect': r'([A-Z][^.]+?)\s+(?:said|stated|declared|claimed)\s+(?:that\s+)?([^.]+)',
            'background': r'(?:according to|sources say|officials said)\s+([^.]+)'
        }
        
        for pattern_type, pattern in quote_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                quote_text = match.group(1) if match.group(1) else match.group(0)
                bias = self._get_sentence_bias(quote_text)
                weight = self.harvard_attribution_weights.get(pattern_type + '_quote', 1.0)
                attribution_scores.append(bias * weight)
        
        # Calculate Harvard component score
        all_scores = position_scores + attribution_scores
        harvard_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return {
            'score': max(-0.5, min(0.5, harvard_score)),
            'details': {
                'position_scores': len(position_scores),
                'attribution_scores': len(attribution_scores),
                'total_weighted_elements': len(all_scores)
            }
        }
    
    def _analyze_columbia_methodology(self, text):
        """Columbia University partisan phrase detection"""
        text_lower = text.lower()
        left_score = 0.0
        right_score = 0.0
        
        # Count partisan phrases with weights
        for category, phrases in self.columbia_partisan_phrases['left_phrases'].items():
            weight = 2.0 if category == 'strong' else 1.0
            for phrase in phrases:
                count = text_lower.count(phrase.lower())
                left_score += count * weight
        
        for category, phrases in self.columbia_partisan_phrases['right_phrases'].items():
            weight = 2.0 if category == 'strong' else 1.0
            for phrase in phrases:
                count = text_lower.count(phrase.lower())
                right_score += count * weight
        
        # Calculate directional score
        total_partisan = left_score + right_score
        if total_partisan == 0:
            columbia_score = 0.0
        else:
            # Normalize to -1 to +1 range
            net_score = (right_score - left_score) / total_partisan
            columbia_score = net_score * min(1.0, total_partisan / 5.0)  # Scale by intensity
        
        return {
            'score': max(-0.5, min(0.5, columbia_score)),
            'details': {
                'left_phrase_score': left_score,
                'right_phrase_score': right_score,
                'total_partisan_phrases': total_partisan,
                'net_direction': 'left' if columbia_score < 0 else 'right' if columbia_score > 0 else 'neutral'
            }
        }
    
    def _analyze_allsides_methodology(self, text):
        """AllSides multi-dimensional assessment (simplified)"""
        text_lower = text.lower()
        
        # Story selection bias
        story_selection_score = 0.0
        for pattern in self.allsides_indicators['story_selection']['patterns']:
            matches = len(re.findall(pattern, text_lower))
            story_selection_score += matches * 0.1
        
        # Fact vs opinion balance
        opinion_score = 0.0
        for marker in self.allsides_indicators['fact_opinion_balance']['opinion_markers']:
            count = text_lower.count(marker)
            opinion_score += count * 0.15
        
        # Source selection diversity
        single_source_count = 0
        multiple_source_count = 0
        
        for indicator in self.allsides_indicators['source_selection']['single_source_indicators']:
            single_source_count += text_lower.count(indicator)
        
        for indicator in self.allsides_indicators['source_selection']['multiple_source_indicators']:
            multiple_source_count += text_lower.count(indicator)
        
        # Calculate source diversity score (more diverse = less biased)
        if single_source_count + multiple_source_count > 0:
            source_diversity = multiple_source_count / (single_source_count + multiple_source_count)
            source_bias = (1.0 - source_diversity) * 0.2  # Less diverse = more biased
        else:
            source_bias = 0.0
        
        # Combine AllSides components
        allsides_total = story_selection_score + opinion_score + source_bias
        allsides_score = min(0.3, allsides_total)  # Cap at 0.3 for this component
        
        return {
            'score': allsides_score,
            'details': {
                'story_selection_score': story_selection_score,
                'opinion_markers_found': opinion_score,
                'source_diversity_score': source_diversity if 'source_diversity' in locals() else 0.0,
                'total_allsides_score': allsides_total
            }
        }
    
    def _analyze_sentiment(self, text):
        """Basic sentiment analysis component"""
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Weight sentiment by subjectivity
        weighted_sentiment = sentiment.polarity * sentiment.subjectivity * 0.5
        
        return {
            'score': weighted_sentiment,
            'details': {
                'polarity': sentiment.polarity,
                'subjectivity': sentiment.subjectivity,
                'weighted_score': weighted_sentiment
            }
        }
    
    def _get_sentence_bias(self, sentence):
        """Get bias score for individual sentence"""
        # Simple bias detection for sentence-level analysis
        sentence_lower = sentence.lower()
        bias_score = 0.0
        
        # Check for partisan phrases
        for phrases in self.columbia_partisan_phrases['left_phrases'].values():
            for phrase in phrases:
                if phrase.lower() in sentence_lower:
                    bias_score -= 0.1
        
        for phrases in self.columbia_partisan_phrases['right_phrases'].values():
            for phrase in phrases:
                if phrase.lower() in sentence_lower:
                    bias_score += 0.1
        
        return max(-0.3, min(0.3, bias_score))
    
    def _format_to_3_sig_figs(self, score):
        """Format score to 3 significant figures"""
        if score == 0:
            return 0.000
        
        sign = -1 if score < 0 else 1
        abs_score = abs(score)
        
        if abs_score >= 1:
            return sign * round(abs_score, 2)
        else:
            order = -math.floor(math.log10(abs_score))
            factor = 10 ** (order + 2)
            rounded = round(abs_score * factor) / factor
            return sign * rounded
    
    def _get_bias_description(self, score):
        """Get human-readable bias description"""
        abs_score = abs(score)
        direction = "left-leaning" if score < 0 else "right-leaning" if score > 0 else "neutral"
        
        if abs_score < 0.1:
            return f"Minimal bias ({direction})"
        elif abs_score < 0.3:
            return f"Low bias ({direction})"
        elif abs_score < 0.6:
            return f"Moderate bias ({direction})"
        elif abs_score < 0.8:
            return f"High bias ({direction})"
        else:
            return f"Very high bias ({direction})"
    
    def _format_result(self, score, description, details):
        """Format the final analysis result"""
        return {
            'bias_score': score,
            'bias_description': description,
            'scale_info': 'Score range: -1.000 (strong left bias) to +1.000 (strong right bias)',
            'methodology': 'Integrated analysis: Harvard (40%) + Columbia (35%) + AllSides (20%) + Sentiment (5%)',
            'analysis_details': details
        }

# Test function
def test_integrated_analyzer():
    analyzer = IntegratedBiasAnalyzer()
    
    test_cases = [
        {
            'name': 'Neutral Content',
            'text': 'The Federal Reserve announced its decision on interest rates. The committee reviewed economic data and voted on the proposal.'
        },
        {
            'name': 'Left-Leaning Content',
            'text': '"Corporate greed is hurting working families," said the progressive advocate. Income inequality continues to grow while social justice remains elusive.'
        },
        {
            'name': 'Right-Leaning Content',
            'text': '"We must return to traditional values and fiscal responsibility," declared the leader. Free market principles and individual liberty built this nation.'
        },
        {
            'name': 'Mixed Methodology Test',
            'text': 'BREAKING: The controversial policy affects working families, according to multiple sources. "Fiscal responsibility is essential," officials stated, while progressive advocates argue for social justice.'
        }
    ]
    
    print("=== INTEGRATED BIAS ANALYZER TEST ===")
    print("Methodology Weights: Harvard (40%) + Columbia (35%) + AllSides (20%) + Sentiment (5%)")
    print()
    
    for test in test_cases:
        print(f"--- {test['name']} ---")
        result = analyzer.analyze_bias(test['text'])
        print(f"Score: {result['bias_score']:+.3f} ({result['bias_description']})")
        print(f"Components:")
        for method, data in result['analysis_details']['methodology_scores'].items():
            weight = result['analysis_details']['methodology_weights'][method]
            print(f"  {method.capitalize()}: {data['score']:+.3f} (weight: {weight:.0%})")
        print()

if __name__ == "__main__":
    test_integrated_analyzer()
