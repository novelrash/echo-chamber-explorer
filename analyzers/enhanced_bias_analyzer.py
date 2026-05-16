#!/usr/bin/env python3
"""
Enhanced Bias Analyzer
Improved conservative bias detection based on analysis of systematic under-detection
"""

import re
import nltk
from textblob import TextBlob
from collections import Counter
import json
import math

class EnhancedBiasAnalyzer:
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
        
        # REBALANCED methodology weights - increased sentiment and Columbia detection
        self.methodology_weights = {
            'harvard': 0.30,      # Reduced - less effective for conservative bias
            'columbia': 0.45,     # Increased - phrase detection is key
            'allsides': 0.10,     # Reduced - limited effectiveness
            'sentiment': 0.15     # Increased - emotional manipulation detection
        }
        
        # EXPANDED Columbia University partisan phrases
        self.columbia_partisan_phrases = {
            'left_phrases': {
                'strong': [
                    'corporate greed', 'working families', 'income inequality', 
                    'social justice', 'climate crisis', 'systemic racism',
                    'wealth gap', 'exploitation', 'progressive values',
                    'people-powered', 'grassroots movement', 'economic justice',
                    'reproductive rights', 'living wage', 'universal healthcare'
                ],
                'moderate': [
                    'affordable healthcare', 'public investment', 'community organizing',
                    'environmental protection', 'worker rights', 'inclusive growth',
                    'public education', 'social safety net', 'civil rights',
                    'climate action', 'green energy', 'social programs'
                ]
            },
            'right_phrases': {
                'strong': [
                    'traditional values', 'fiscal responsibility', 'constitutional rights',
                    'free market', 'individual liberty', 'personal responsibility',
                    'law and order', 'american dream', 'founding fathers',
                    'limited government', 'free enterprise', 'moral values',
                    # EXPANDED conservative phrases
                    'real americans', 'silent majority', 'urban crime', 'welfare state',
                    'government overreach', 'nanny state', 'political correctness',
                    'mainstream media bias', 'liberal elite', 'coastal elites',
                    'god-fearing', 'moral decay', 'family breakdown', 'traditional marriage',
                    'cancel culture', 'woke agenda', 'deep state', 'america first'
                ],
                'moderate': [
                    'economic growth', 'job creation', 'business friendly',
                    'competitive markets', 'innovation', 'entrepreneurship',
                    'national security', 'family values', 'local control',
                    # EXPANDED moderate conservative phrases
                    'taxpayers', 'hardworking families', 'law-abiding citizens',
                    'states rights', 'school choice', 'energy independence',
                    'border security', 'common sense', 'practical solutions',
                    'fiscal discipline', 'regulatory reform', 'merit-based'
                ]
            }
        }
        
        # NEW: Conservative bias patterns - COMPREHENSIVE
        self.conservative_patterns = {
            'question_framing': [
                r'why (won\'t|don\'t|can\'t) (democrats|liberals|the left)',
                r'how long will (americans|taxpayers) tolerate',
                r'when will (someone|anyone) stand up to',
                r'why are (democrats|liberals) (so|still)',
                r'how can (anyone|people) still (believe|support)',
                r'why (won\'t|don\'t) they (understand|see|admit)'
            ],
            'false_balance': [
                r'some (people|experts|critics) (say|argue|claim)',
                r'many (believe|think|argue) that',
                r'critics (argue|say|claim)',
                r'according to (some|many|critics)',
                r'sources (say|claim|argue)'
            ],
            'victimization': [
                r'under attack', r'being silenced', r'cancelled',
                r'discriminated against', r'persecuted',
                r'witch hunt', r'targeted', r'unfairly treated',
                r'suffer under', r'victims of', r'oppressed by'
            ],
            'statistical_manipulation': [
                r'\d+% of (americans|people) (believe|think|want)',
                r'studies show', r'research proves', r'data shows',
                r'according to (polls|surveys)', r'statistics reveal',
                r'the numbers (show|prove|demonstrate)'
            ],
            'moral_authority': [
                r'god-given', r'biblical', r'christian values',
                r'moral imperative', r'right thing to do',
                r'common decency', r'basic morality',
                r'traditional marriage', r'family values'
            ],
            'enemy_framing': [
                r'radical (democrats|liberals|left)',
                r'(liberal|leftist) (elite|elites)',
                r'(hate|destroy|attack) (america|traditional|values)',
                r'(socialist|communist) (agenda|mob)',
                r'indoctrinate (our|children)',
                r'immoral agenda'
            ]
        }
        
        # Harvard position weights
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
        
        # ENHANCED AllSides indicators - COMPREHENSIVE
        self.allsides_indicators = {
            'story_selection': {
                'patterns': [
                    r'breaking:?\s+', r'exclusive:?\s+', r'bombshell:?\s+',
                    r'shocking:?\s+', r'revealed:?\s+', r'exposed:?\s+'
                ],
                'weight': 1.0
            },
            'fact_opinion_balance': {
                'opinion_markers': [
                    'i believe', 'in my opinion', 'clearly', 'obviously',
                    'undoubtedly', 'certainly', 'without question',
                    'it\'s clear that', 'anyone can see', 'common sense tells us'
                ],
                'weight': 1.5
            },
            'bias_intensity_indicators': [
                # Conservative bias indicators
                'under attack', 'know that', 'the truth is', 'wake up',
                'liberal elite', 'woke agenda', 'real americans', 'traditional values',
                'radical democrats', 'hate', 'destroy', 'indoctrinate', 'immoral agenda',
                'hardworking taxpayers', 'suffer under', 'government tyranny',
                'constitutional rights', 'christian values', 'traditional marriage',
                'cancel culture', 'mainstream media bias', 'deep state',
                # Liberal bias indicators  
                'corporate greed', 'systemic racism', 'working families',
                'social justice', 'income inequality', 'capitalist oppression',
                'fascist', 'white supremacy', 'oligarchy', 'billionaire elites',
                'marginalized communities', 'progressive movements'
            ]
        }
    
    def analyze_bias(self, text, title="", url=""):
        """Enhanced bias analysis with improved conservative detection"""
        
        # Combine title and text for analysis
        full_text = f"{title} {text}".strip()
        
        # Calculate individual methodology scores
        harvard_score = self._calculate_harvard_score(full_text, title)
        columbia_score = self._calculate_columbia_score(full_text)
        allsides_score = self._calculate_allsides_score(full_text)
        sentiment_score = self._calculate_sentiment_score(full_text)
        
        # NEW: Conservative pattern bonus
        conservative_bonus = self._calculate_conservative_patterns(full_text)
        
        # Weighted combination
        final_score = (
            harvard_score * self.methodology_weights['harvard'] +
            columbia_score * self.methodology_weights['columbia'] +
            allsides_score * self.methodology_weights['allsides'] +
            sentiment_score * self.methodology_weights['sentiment'] +
            conservative_bonus * 0.25  # INCREASED from 0.1 - Additional weight for conservative patterns
        )
        
        # Ensure score stays within bounds
        final_score = max(-1.0, min(1.0, final_score))
        
        return {
            'bias_score': final_score,
            'sentiment_polarity': sentiment_score,
            'sentiment_subjectivity': self._get_subjectivity(full_text),
            'emotional_density': self._calculate_emotional_density(full_text),
            'certainty_ratio': self._calculate_certainty_ratio(full_text),
            'methodology_breakdown': {
                'harvard': harvard_score,
                'columbia': columbia_score,
                'allsides': allsides_score,
                'sentiment': sentiment_score,
                'conservative_patterns': conservative_bonus
            },
            'bias_description': self._get_bias_description(final_score),
            'scale_info': "Scale: -1.0 (Very Left) to +1.0 (Very Right)",
            'methodology': "Enhanced Multi-Source Analysis with Conservative Pattern Detection"
        }
    
    def _calculate_columbia_score(self, text):
        """Enhanced Columbia methodology with expanded phrase detection"""
        text_lower = text.lower()
        
        left_score = 0
        right_score = 0
        
        # Count partisan phrases with different weights
        for phrase in self.columbia_partisan_phrases['left_phrases']['strong']:
            count = text_lower.count(phrase.lower())
            left_score += count * 2.0  # Strong phrases weighted more
        
        for phrase in self.columbia_partisan_phrases['left_phrases']['moderate']:
            count = text_lower.count(phrase.lower())
            left_score += count * 1.0
        
        for phrase in self.columbia_partisan_phrases['right_phrases']['strong']:
            count = text_lower.count(phrase.lower())
            right_score += count * 2.0  # Strong phrases weighted more
        
        for phrase in self.columbia_partisan_phrases['right_phrases']['moderate']:
            count = text_lower.count(phrase.lower())
            right_score += count * 1.0
        
        # Normalize and return bias score
        total_phrases = left_score + right_score
        if total_phrases == 0:
            return 0.0
        
        # Return score between -1 and 1
        net_score = (right_score - left_score) / total_phrases
        return max(-1.0, min(1.0, net_score))
    
    def _calculate_conservative_patterns(self, text):
        """NEW: Detect conservative bias patterns - COMPREHENSIVE SENSITIVITY"""
        text_lower = text.lower()
        pattern_score = 0
        
        for category, patterns in self.conservative_patterns.items():
            category_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                category_matches += matches
            
            # INCREASED weights for pattern types
            if category == 'question_framing':
                pattern_score += category_matches * 0.8
            elif category == 'statistical_manipulation':
                pattern_score += category_matches * 0.9
            elif category == 'victimization':
                pattern_score += category_matches * 0.7
            elif category == 'moral_authority':
                pattern_score += category_matches * 0.8
            elif category == 'enemy_framing':  # NEW category
                pattern_score += category_matches * 1.0  # Highest weight
            else:
                pattern_score += category_matches * 0.6
        
        # INCREASED normalization range
        return min(1.0, pattern_score / 2.0)  # More sensitive denominator
    
    def _calculate_harvard_score(self, text, title):
        """Harvard position/attribution weighting - FIXED METHODOLOGY"""
        # Get phrase bias (this works correctly - returns 1.0 for extreme text)
        phrase_bias = self._get_phrase_bias(f"{title} {text}")
        
        # FIXED: Don't artificially divide - let the phrase bias speak for itself
        # If phrase detection finds strong bias, Harvard should reflect that
        return phrase_bias  # Was: (title_bias + text_bias) / 3.0
    
    def _calculate_allsides_score(self, text):
        """AllSides multi-dimensional assessment - COMPREHENSIVE"""
        text_lower = text.lower()
        
        # Story selection bias
        sensational_count = 0
        for pattern in self.allsides_indicators['story_selection']['patterns']:
            sensational_count += len(re.findall(pattern, text_lower))
        
        # Opinion markers
        opinion_count = 0
        for marker in self.allsides_indicators['fact_opinion_balance']['opinion_markers']:
            opinion_count += text_lower.count(marker)
        
        # COMPREHENSIVE: Bias intensity indicators
        bias_count = 0
        for indicator in self.allsides_indicators['bias_intensity_indicators']:
            bias_count += text_lower.count(indicator)
        
        # Combine scores with proper weighting
        total_indicators = sensational_count + opinion_count + bias_count
        if total_indicators == 0:
            return 0.0
        
        # Calculate bias intensity (more sensitive)
        bias_intensity = min(1.0, total_indicators / 2.0)  # Reduced denominator for higher sensitivity
        
        # Determine direction based on phrase content
        phrase_direction = self._get_phrase_bias(text)
        
        # If no clear phrase direction but bias indicators present, determine from context
        if phrase_direction == 0.0 and bias_count > 0:
            # Count conservative vs liberal indicators
            conservative_indicators = [
                'liberal elite', 'woke agenda', 'real americans', 'traditional values',
                'radical democrats', 'indoctrinate', 'immoral agenda', 'hardworking taxpayers',
                'government tyranny', 'constitutional rights', 'christian values',
                'traditional marriage', 'cancel culture', 'mainstream media bias', 'deep state'
            ]
            liberal_indicators = [
                'corporate greed', 'systemic racism', 'working families', 'social justice',
                'income inequality', 'capitalist oppression', 'fascist', 'white supremacy',
                'oligarchy', 'billionaire elites', 'marginalized communities', 'progressive movements'
            ]
            
            conservative_count = sum(1 for ind in conservative_indicators if ind in text_lower)
            liberal_count = sum(1 for ind in liberal_indicators if ind in text_lower)
            
            if conservative_count > liberal_count:
                phrase_direction = 0.7
            elif liberal_count > conservative_count:
                phrase_direction = -0.7
            else:
                phrase_direction = 0.3  # Default slight positive if unclear
        
        return phrase_direction * bias_intensity
    
    def _calculate_sentiment_score(self, text):
        """Political sentiment analysis - FIXED METHODOLOGY"""
        # TextBlob fails on political text - use political sentiment instead
        text_lower = text.lower()
        
        # Negative political sentiment (liberal bias indicators)
        negative_political = [
            'corporate greed', 'exploitation', 'oppression', 'inequality', 
            'systemic racism', 'fascist', 'destroy', 'attack', 'threat'
        ]
        
        # Positive political sentiment (conservative bias indicators)  
        positive_political = [
            'traditional values', 'patriot', 'freedom', 'liberty', 'god-fearing',
            'real america', 'constitutional', 'founding fathers', 'moral values'
        ]
        
        # Extreme emotional language (amplifies either direction)
        extreme_emotional = [
            'destroying', 'silenced', 'persecuted', 'corrupt', 'radical',
            'elite', 'agenda', 'crisis', 'under attack', 'hate'
        ]
        
        neg_count = sum(1 for term in negative_political if term in text_lower)
        pos_count = sum(1 for term in positive_political if term in text_lower)
        extreme_count = sum(1 for term in extreme_emotional if term in text_lower)
        
        # Calculate political sentiment
        if pos_count > neg_count:
            base_sentiment = 0.6  # Conservative lean
        elif neg_count > pos_count:
            base_sentiment = -0.6  # Liberal lean
        else:
            base_sentiment = 0.0  # Neutral
        
        # Amplify with extreme emotional language
        if extreme_count > 0:
            amplification = min(0.4, extreme_count * 0.1)
            if base_sentiment > 0:
                base_sentiment += amplification
            elif base_sentiment < 0:
                base_sentiment -= amplification
            else:
                # If neutral but has extreme language, assume slight positive bias
                base_sentiment = amplification
        
        return max(-1.0, min(1.0, base_sentiment))
    
    def _get_phrase_bias(self, text):
        """Helper to determine phrase bias direction"""
        text_lower = text.lower()
        
        left_count = 0
        right_count = 0
        
        # Count all phrases
        for phrase_list in self.columbia_partisan_phrases['left_phrases'].values():
            for phrase in phrase_list:
                left_count += text_lower.count(phrase.lower())
        
        for phrase_list in self.columbia_partisan_phrases['right_phrases'].values():
            for phrase in phrase_list:
                right_count += text_lower.count(phrase.lower())
        
        total = left_count + right_count
        if total == 0:
            return 0.0
        
        return (right_count - left_count) / total
    
    def _get_subjectivity(self, text):
        """Get text subjectivity"""
        blob = TextBlob(text)
        return blob.sentiment.subjectivity
    
    def _calculate_emotional_density(self, text):
        """Calculate emotional word density"""
        emotional_words = [
            'shocking', 'outrageous', 'devastating', 'incredible', 'amazing',
            'terrible', 'wonderful', 'horrible', 'fantastic', 'awful',
            'disgusting', 'brilliant', 'stupid', 'genius', 'insane'
        ]
        
        words = text.lower().split()
        emotional_count = sum(1 for word in words if word in emotional_words)
        
        return emotional_count / len(words) if words else 0.0
    
    def _calculate_certainty_ratio(self, text):
        """Calculate certainty language ratio"""
        certainty_words = [
            'always', 'never', 'all', 'none', 'every', 'completely',
            'totally', 'absolutely', 'definitely', 'certainly', 'obviously'
        ]
        
        words = text.lower().split()
        certainty_count = sum(1 for word in words if word in certainty_words)
        
        return certainty_count / len(words) if words else 0.0
    
    def _get_bias_description(self, score):
        """Get human-readable bias description"""
        if score <= -0.6:
            return "Very High Left Bias"
        elif score <= -0.3:
            return "High Left Bias"
        elif score <= -0.1:
            return "Low Left Bias"
        elif score <= 0.1:
            return "Minimal Bias"
        elif score <= 0.3:
            return "Low Right Bias"
        elif score <= 0.6:
            return "High Right Bias"
        else:
            return "Very High Right Bias"
