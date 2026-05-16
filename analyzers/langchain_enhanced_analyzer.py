#!/usr/bin/env python3
"""
LangChain Enhanced Bias Analyzer
Integrates AI agents with existing bias analysis
"""

import sys
import os
sys.path.append('/mnt/c/Users/User')

from .integrated_bias_analyzer import IntegratedBiasAnalyzer
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from collections import Counter

class LangChainEnhancedAnalyzer(IntegratedBiasAnalyzer):
    """Enhanced analyzer with LangChain agents"""
    
    def __init__(self):
        super().__init__()
        try:
            self.search = DuckDuckGoSearchRun()
            self.agents_available = True
        except Exception as e:
            print(f"Warning: LangChain agents not available: {e}")
            self.agents_available = False
    
    def analyze_with_agents(self, content, url=None, title=None):
        """Enhanced analysis with AI agents"""
        # Get base analysis using the correct method name
        base_results = self.analyze_bias(content, title or "", url or "")
        
        if not self.agents_available:
            return base_results
        
        # Add agent enhancements
        enhanced_results = base_results.copy()
        
        try:
            # Extract key topics for research
            key_topics = self._extract_key_topics(content, title)
            
            # Research context
            enhanced_results['agent_research'] = self._research_context(key_topics)
            
            # Source credibility (if URL provided)
            if url:
                enhanced_results['source_credibility'] = self._analyze_source_credibility(url)
            
            # Fact-check key claims
            enhanced_results['fact_check'] = self._basic_fact_check(content)
            
            # Enhanced bias indicators
            enhanced_results['enhanced_bias_indicators'] = self._detect_enhanced_bias(content)
            
        except Exception as e:
            enhanced_results['agent_error'] = str(e)
        
        return enhanced_results
    
    def _extract_key_topics(self, content, title=None):
        """Extract key topics for research"""
        text = f"{title or ''} {content}".lower()
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-z]{4,}\b', text)
        word_freq = Counter(words)
        
        # Filter common words
        stop_words = {'that', 'this', 'with', 'from', 'they', 'have', 'been', 'said', 'will', 'would', 'could', 'should'}
        keywords = [word for word, freq in word_freq.most_common(10) 
                   if word not in stop_words and freq > 1]
        
        return keywords[:3]  # Top 3 topics
    
    def _research_context(self, topics):
        """Research topics for additional context"""
        if not topics:
            return []
        
        research_results = []
        for topic in topics:
            try:
                query = f"{topic} different perspectives analysis"
                result = self.search.run(query)
                research_results.append({
                    'topic': topic,
                    'context': result[:200],  # Limit length
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                research_results.append({
                    'topic': topic,
                    'error': str(e)
                })
        
        return research_results
    
    def _analyze_source_credibility(self, url):
        """Analyze source credibility"""
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            score = 0.5  # Neutral start
            indicators = []
            
            # Check for author
            if soup.find('meta', attrs={'name': 'author'}) or soup.find(class_=re.compile('author')):
                score += 0.15
                indicators.append("Author identified")
            
            # Check for date
            if soup.find('meta', attrs={'name': 'date'}) or soup.find('time'):
                score += 0.1
                indicators.append("Publication date found")
            
            # Check domain reputation
            domain = url.split('/')[2].lower()
            trusted_indicators = ['reuters', 'ap.org', 'bbc', 'npr', 'pbs']
            if any(trusted in domain for trusted in trusted_indicators):
                score += 0.2
                indicators.append("Trusted domain")
            
            # Check for external links
            external_links = len([a for a in soup.find_all('a', href=True) 
                                if 'http' in a['href'] and domain not in a['href']])
            if external_links > 3:
                score += 0.1
                indicators.append(f"{external_links} external references")
            
            return {
                'score': min(score, 1.0),
                'indicators': indicators,
                'domain': domain
            }
        except Exception as e:
            return {'score': 0.5, 'error': str(e)}
    
    def _basic_fact_check(self, content):
        """Basic fact-checking of claims"""
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 30]
        
        fact_checks = []
        for sentence in sentences[:2]:  # Check first 2 substantial sentences
            try:
                # Look for factual claims (numbers, specific statements)
                if any(char.isdigit() for char in sentence) or any(word in sentence.lower() 
                      for word in ['study', 'research', 'report', 'data', 'statistics']):
                    
                    query = f'"{sentence[:50]}" fact check verification'
                    result = self.search.run(query)
                    fact_checks.append({
                        'claim': sentence[:100],
                        'verification_search': result[:150]
                    })
            except Exception as e:
                fact_checks.append({
                    'claim': sentence[:100],
                    'error': str(e)
                })
        
        return fact_checks
    
    def _detect_enhanced_bias(self, content):
        """Enhanced bias detection using AI insights"""
        indicators = {
            'emotional_manipulation': [],
            'false_dichotomy': [],
            'appeal_to_fear': [],
            'loaded_questions': []
        }
        
        text_lower = content.lower()
        
        # Emotional manipulation
        emotional_phrases = ['you should be outraged', 'this is shocking', 'unbelievable truth', 'wake up']
        for phrase in emotional_phrases:
            if phrase in text_lower:
                indicators['emotional_manipulation'].append(phrase)
        
        # False dichotomy
        dichotomy_patterns = ['either.*or', 'only two', 'you\'re either', 'no middle ground']
        for pattern in dichotomy_patterns:
            if re.search(pattern, text_lower):
                indicators['false_dichotomy'].append(pattern)
        
        # Appeal to fear
        fear_words = ['dangerous', 'threat', 'destroy', 'catastrophe', 'crisis', 'emergency']
        fear_count = sum(1 for word in fear_words if word in text_lower)
        if fear_count > 2:
            indicators['appeal_to_fear'] = fear_words[:fear_count]
        
        # Loaded questions
        if '?' in content:
            questions = [q.strip() for q in content.split('?') if q.strip()]
            loaded_indicators = ['don\'t you think', 'isn\'t it obvious', 'how can anyone']
            for question in questions:
                if any(indicator in question.lower() for indicator in loaded_indicators):
                    indicators['loaded_questions'].append(question[:100])
        
        return indicators
