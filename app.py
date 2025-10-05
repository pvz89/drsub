import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import pandas as pd
from typing import List, Dict
import json

# Page configuration
st.set_page_config(
    page_title="Manchester Solicitors SEO Content Strategist",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1f77b4;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #2e86ab;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class SEOContentStrategist:
    def __init__(self):
        self.sitemap_url = "https://solicitorsinmanchester.co.uk/page-sitemap.xml"
        self.mandatory_links = {
            "Immigration solicitors in Manchester": "https://solicitorsinmanchester.co.uk/",
            "Home Office": "https://www.gov.uk/government/organisations/home-office",
            "UKVI": "https://www.gov.uk/government/organisations/uk-visas-and-immigration",
            "ILR": "https://solicitorsinmanchester.co.uk/indefinite-leave-to-remain/",
            "Life in the UK test": "https://en.wikipedia.org/wiki/Life_in_the_United_Kingdom_test",
            "NHS": "https://www.nhs.uk/",
            "UK Visas & Immigration Services": "https://solicitorsinmanchester.co.uk/uk-visas-immigration-services/"
        }
    
    def fetch_sitemap(self) -> List[Dict]:
        """Fetch and parse sitemap for internal linking opportunities"""
        try:
            response = requests.get(self.sitemap_url)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            pages = []
            for url in root.findall('ns:url', namespaces):
                loc = url.find('ns:loc', namespaces).text
                # Extract page title from URL for display
                page_name = loc.split('/')[-2].replace('-', ' ').title() if loc.split('/')[-2] else "Home"
                pages.append({
                    'url': loc,
                    'title': page_name,
                    'anchor_text': self.generate_anchor_text(page_name)
                })
            
            return pages[:15]  # Return first 15 pages
        except Exception as e:
            st.error(f"Error fetching sitemap: {e}")
            return []
    
    def generate_anchor_text(self, page_title: str) -> str:
        """Generate natural anchor text from page title"""
        anchor_map = {
            "Home": "immigration solicitors in Manchester",
            "Uk Visas Immigration Services": "UK visas and immigration services",
            "Indefinite Leave To Remain": "indefinite leave to remain",
            "British Citizenship": "British citizenship application",
            "Spouse Visa": "spouse visa requirements",
            "Family Visa": "family visa application",
            "Skilled Worker Visa": "Skilled Worker visa",
            "Student Visa": "student visa requirements"
        }
        return anchor_map.get(page_title, page_title.lower())
    
    def analyze_competitor_content(self, content: str) -> Dict:
        """Analyze competitor content and extract key insights"""
        # Basic keyword extraction (simplified - in practice you'd use more sophisticated NLP)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        for word in words:
            if word not in ['that', 'with', 'this', 'have', 'from', 'they', 'what', 'when', 'your', 'will']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        main_keyword = sorted_words[0][0] if sorted_words else "immigration"
        
        return {
            'main_keyword': main_keyword,
            'secondary_keywords': [word for word, freq in sorted_words[1:11]],
            'word_count': len(content.split()),
            'top_terms': sorted_words[:20]
        }
    
    def generate_content_brief(self, analysis: Dict, sitemap_pages: List[Dict]) -> Dict:
        """Generate comprehensive SEO content brief"""
        
        main_keyword = analysis['main_keyword']
        
        # Heading structure
        heading_structure = {
            'H1': f"Complete Guide to {main_keyword.title()} in the UK 2025",
            'H2s': [
                f"What Is {main_keyword.title()}?",
                f"Who Needs {main_keyword.title()}?",
                f"How Does {main_keyword.title()} Work?",
                f"Eligibility Requirements for {main_keyword.title()}",
                f"Application Process Step by Step",
                f"Common Mistakes to Avoid",
                f"Costs and Processing Times 2025",
                f"{main_keyword.title()} vs Alternative Options",
                "Real-Life Case Studies and Examples",
                "Frequently Asked Questions"
            ]
        }
        
        # Featured snippet opportunities
        snippet_opportunities = [
            f"What is {main_keyword}?",
            f"How long does {main_keyword} take?",
            f"How much does {main_keyword} cost?",
            f"Who is eligible for {main_keyword}?",
            f"What documents are needed for {main_keyword}?"
        ]
        
        # PAA questions
        paa_questions = [
            f"What are the requirements for {main_keyword}?",
            f"How do I apply for {main_keyword}?",
            f"What is the success rate for {main_keyword}?",
            f"Can I work with {main_keyword}?",
            f"Can my family join me with {main_keyword}?",
            f"What happens if my {main_keyword} is refused?",
            f"How long can I stay with {main_keyword}?",
            f"Can I extend my {main_keyword}?"
        ]
        
        # Semantic keywords
        semantic_keywords = [
            main_keyword, "UK visa", "immigration", "application", "requirements",
            "documents", "processing time", "cost", "fee", "eligibility",
            "criteria", "guidance", "advice", "solicitor", "legal",
            "home office", "UKVI", "decision", "approval", "refusal",
            "appeal", "extension", "switch", "change", "status"
        ]
        
        # Internal linking strategy
        internal_links = []
        for page in sitemap_pages[:12]:
            internal_links.append({
                'anchor_text': page['anchor_text'],
                'url': page['url'],
                'placement': f"Natural context in relevant sections about {page['title']}"
            })
        
        # Add mandatory links
        for text, url in self.mandatory_links.items():
            internal_links.append({
                'anchor_text': text,
                'url': url,
                'placement': "Contextual placement in relevant content sections"
            })
        
        return {
            'heading_structure': heading_structure,
            'snippet_opportunities': snippet_opportunities,
            'paa_questions': paa_questions,
            'semantic_keywords': semantic_keywords,
            'internal_links': internal_links,
            'content_gaps': [
                "Lack of real-life case studies",
                "Missing current 2025 processing times",
                "Inadequate cost breakdown",
                "Limited information on refusal handling",
                "Not enough practical examples"
            ],
            'user_intent': "Mixed - informational (understanding requirements) and transactional (seeking legal help)"
        }

def main():
    st.markdown('<div class="main-header">Manchester Solicitors SEO Content Strategist</div>', unsafe_allow_html=True)
    
    strategist = SEOContentStrategist()
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_step = st.sidebar.radio("Select Step:", ["Step 1: Competitor Analysis", "Step 2: Content Writing", "Step 3: SEO Metadata"])
    
    # Step 1: Competitor Analysis
    if app_step == "Step 1: Competitor Analysis":
        st.markdown('<div class="section-header">📊 Competitor Content Analysis</div>', unsafe_allow_html=True)
        
        # Fetch sitemap
        with st.spinner("Fetching sitemap for internal linking opportunities..."):
            sitemap_pages = strategist.fetch_sitemap()
        
        if sitemap_pages:
            st.success(f"✅ Successfully fetched {len(sitemap_pages)} pages from sitemap")
        
        # Competitor content input
        st.markdown('<div class="subsection-header">Competitor Content Input</div>', unsafe_allow_html=True)
        competitor_content = st.text_area(
            "Paste competitor content here:",
            height=200,
            placeholder="Paste the competitor article content you want to analyze..."
        )
        
        if st.button("Analyze Competitor Content") and competitor_content:
            with st.spinner("Analyzing competitor content..."):
                # Analyze content
                analysis = strategist.analyze_competitor_content(competitor_content)
                brief = strategist.generate_content_brief(analysis, sitemap_pages)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="subsection-header">Keyword Analysis</div>', unsafe_allow_html=True)
                    st.write(f"**Main Focus Keyword:** {analysis['main_keyword']}")
                    st.write("**Secondary Keywords:**")
                    for i, keyword in enumerate(analysis['secondary_keywords'][:8], 1):
                        st.write(f"{i}. {keyword}")
                    
                    st.markdown('<div class="subsection-header">Content Metrics</div>', unsafe_allow_html=True)
                    st.write(f"**Competitor Word Count:** {analysis['word_count']}")
                    st.write(f"**Target Word Count:** 1,500+")
                    
                with col2:
                    st.markdown('<div class="subsection-header">Top Terms Found</div>', unsafe_allow_html=True)
                    terms_df = pd.DataFrame(analysis['top_terms'][:15], columns=['Term', 'Frequency'])
                    st.dataframe(terms_df, use_container_width=True)
                
                # Detailed SEO Brief
                st.markdown('<div class="subsection-header">📋 Detailed SEO Content Brief</div>', unsafe_allow_html=True)
                
                # Heading Structure
                st.write("**Optimised Heading Structure:**")
                st.write(f"H1: {brief['heading_structure']['H1']}")
                for i, h2 in enumerate(brief['heading_structure']['H2s'], 1):
                    st.write(f"H2 {i}: {h2}")
                
                # Featured Snippets
                st.write("**Featured Snippet Opportunities:**")
                for snippet in brief['snippet_opportunities']:
                    st.write(f"• {snippet}")
                
                # PAA Questions
                st.write("**People Also Ask Questions to Target:**")
                for question in brief['paa_questions']:
                    st.write(f"• {question}")
                
                # Semantic Keywords
                st.write("**Semantic/LSI/Entity Keywords (20+ terms):**")
                keywords_text = ", ".join(brief['semantic_keywords'])
                st.write(keywords_text)
                
                # Internal Linking Strategy
                st.write("**Internal Linking Strategy:**")
                links_df = pd.DataFrame(brief['internal_links'])
                st.dataframe(links_df, use_container_width=True)
                
                # Content Gaps
                st.write("**Content Gaps Identified:**")
                for gap in brief['content_gaps']:
                    st.write(f"• {gap}")
                
                st.write(f"**User Intent Analysis:** {brief['user_intent']}")
    
    # Step 2: Content Writing
    elif app_step == "Step 2: Content Writing":
        st.markdown('<div class="section-header">✍️ Content Writing Assistant</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning">
        <strong>Writing Guidelines:</strong><br>
        ✅ Plain UK English (British spelling)<br>
        ✅ Conversational, human, personable tone<br>
        ✅ Write like speaking to a friend<br>
        ✅ Use "you" and "your" directly<br>
        ✅ Short paragraphs (2-4 sentences max)<br>
        ❌ NO em dashes (—)<br>
        ❌ NO words: "expert", "explore", "navigate", "unravel", "delve", "comprehensive", "robust"<br>
        ❌ NO excessive adjectives or marketing fluff
        </div>
        """, unsafe_allow_html=True)
        
        # Content planning inputs
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Main Topic/Keyword:", placeholder="e.g., Spouse Visa Extension")
            target_audience = st.selectbox(
                "Target Audience:",
                ["Non-British nationals seeking UK immigration advice", 
                 "Existing visa holders looking to extend/switch",
                 "Families navigating UK immigration system",
                 "Employers sponsoring workers",
                 "Individuals considering settlement/citizenship"]
            )
        
        with col2:
            word_count = st.slider("Target Word Count:", min_value=1500, max_value=3000, value=1800)
            include_case_studies = st.checkbox("Include Real-Life Case Studies", value=True)
        
        # Article structure preview
        st.markdown('<div class="subsection-header">Article Structure Preview</div>', unsafe_allow_html=True)
        
        article_structure = """
        **Introduction** (150-200 words)
        - Hook with relatable scenario
        - Clear topic definition
        - What reader will learn
        
        **Main Body Sections:**
        - What Is [Topic]?
        - Who Needs/Qualifies for [Topic]?
        - How Does [Topic] Work?
        - Requirements/Eligibility
        - Application Process (Step-by-step)
        - Common Mistakes to Avoid
        - Costs and Processing Times
        - [Topic] vs [Related Topic]
        - Real-life Examples and Case Studies
        
        **FAQ Section** (8-10 questions)
        - Target PAA questions
        - Concise, direct answers
        
        **CTA Section**
        - Natural transition
        - Contact details
        - Booking link
        
        **Conclusion** (100-150 words)
        - Recap key takeaways
        - Encourage action
        """
        
        st.text_area("Planned Structure:", value=article_structure, height=300)
        
        if st.button("Generate Content Outline"):
            st.markdown('<div class="subsection-header">Content Writing Template</div>', unsafe_allow_html=True)
            
            # Generate template content
            template = f"""
# Complete Guide to {topic} in the UK 2025

## Introduction

[Start with relatable scenario - 150-200 words]
Have you found yourself wondering about your next steps as your current visa approaches its expiry date? Many people in your situation feel the same uncertainty about what comes next. This guide will walk you through everything you need to know about {topic.lower()}, from eligibility requirements to the application process and beyond.

## What Is {topic}?

[Clear definition and explanation - 150-200 words]
{titlecase(topic)} is... [Provide clear definition in plain English]

## Who Needs {topic}?

[Target audience description - 150-200 words]
You might need {topic.lower()} if... [Describe specific situations]

## How Does {topic} Work?

[Process explanation - 200-250 words]
The process involves... [Step-by-step explanation]

## Eligibility Requirements

[Detailed requirements - 200-250 words]
To qualify for {topic.lower()}, you must meet these criteria...

## Application Process Step by Step

[Detailed steps - 250-300 words]
1. Gather your documents
2. Complete the application form
3. Submit your application
4. Attend biometric appointment
5. Wait for decision

## Common Mistakes to Avoid

[Practical advice - 200-250 words]
Many applicants make these errors... [List common mistakes]

## Costs and Processing Times 2025

[Current information - 150-200 words]
The current fee is... Processing typically takes...

## Real-Life Case Studies

[Practical examples - 200-250 words]
Case Study 1: [Real example]
Case Study 2: [Real example]

## Frequently Asked Questions

### What are the main requirements for {topic.lower()}?
[Concise 50-100 word answer]

### How long does the application take?
[Concise 50-100 word answer]

[6-8 more PAA questions]

## Get Professional Help with Your Application

If you are feeling unsure about any part of the process, our team of immigration solicitors in Manchester is here to help. We understand how important this application is for you and your family, and we are committed to making the process as smooth as possible.

**Contact us today:**
📞 Phone: 0161 464 4140  
📅 Book a consultation: [https://solicitorsinmanchester.co.uk/book-an-appointment/](https://solicitorsinmanchester.co.uk/book-an-appointment/)

## Conclusion

[100-150 word summary and encouragement]
Applying for {topic.lower()} can seem complex, but with the right guidance and preparation, you can navigate the process successfully. Remember to double-check all requirements and consider seeking professional advice if you have any doubts about your application.
            """
            
            st.text_area("Content Template:", value=template, height=600)
            
            st.markdown("""
            <div class="success">
            <strong>Next Steps:</strong><br>
            1. Review the template structure<br>
            2. Fill in specific details for each section<br>
            3. Ensure all mandatory internal links are included<br>
            4. Check against quality checklist before publishing<br>
            5. Maintain conversational tone throughout
            </div>
            """, unsafe_allow_html=True)
    
    # Step 3: SEO Metadata
    else:
        st.markdown('<div class="section-header">🔍 SEO Metadata Generator</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            focus_keyword = st.text_input("Main Focus Keyword:", placeholder="e.g., spouse visa extension")
            location = st.text_input("Location Context:", value="Manchester", disabled=True)
            current_year = st.text_input("Year:", value="2025", disabled=True)
        
        with col2:
            secondary_keywords = st.text_area(
                "Secondary Keywords (one per line):",
                placeholder="visa extension requirements\nspouse visa uk\nimmigration solicitor",
                height=150
            )
        
        if st.button("Generate SEO Metadata"):
            if focus_keyword:
                # Generate metadata options
                meta_titles = [
                    f"{focus_keyword.title()} UK Requirements {current_year} | {location} Solicitors",
                    f"Complete Guide to {focus_keyword.title()} {current_year} | Legal Advice {location}",
                    f"{focus_keyword.title()} Application Process & Costs {current_year}"
                ]
                
                meta_descriptions = [
                    f"Get expert help with your {focus_keyword.lower()} application. Learn about requirements, costs and processing times {current_year}. Contact our {location} solicitors today.",
                    f"Complete {current_year} guide to {focus_keyword.lower()} in the UK. Understand eligibility, application process and avoid common mistakes with our legal support.",
                    f"Need help with {focus_keyword.lower()}? Our {location} immigration solicitors provide clear guidance and professional support for your application."
                ]
                
                slug_url = f"/{focus_keyword.lower().replace(' ', '-')}-guide-{current_year}/"
                
                # Display results
                st.markdown('<div class="subsection-header">Recommended SEO Metadata</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Primary Meta Title:**")
                    st.info(meta_titles[0])
                    st.write(f"Character count: {len(meta_titles[0])}")
                    
                    st.write("**Primary Meta Description:**")
                    st.info(meta_descriptions[0])
                    st.write(f"Character count: {len(meta_descriptions[0])}")
                
                with col2:
                    st.write("**Alternative Meta Titles:**")
                    for i, title in enumerate(meta_titles[1:], 1):
                        st.write(f"{i}. {title} ({len(title)} chars)")
                    
                    st.write("**Alternative Meta Descriptions:**")
                    for i, desc in enumerate(meta_descriptions[1:], 1):
                        st.write(f"{i}. {desc} ({len(desc)} chars)")
                
                st.write("**Slug URL:**")
                st.code(slug_url)
                
                # Schema markup recommendations
                st.markdown('<div class="subsection-header">Schema Markup Recommendations</div>', unsafe_allow_html=True)
                schema_types = [
                    "Article Schema (for the content)",
                    "FAQ Schema (for questions section)",
                    "LocalBusiness Schema (for Manchester location)",
                    "Breadcrumb Schema (for navigation)",
                    "HowTo Schema (if process-oriented)"
                ]
                
                for schema in schema_types:
                    st.write(f"• {schema}")
                
                # Image alt text suggestions
                st.markdown('<div class="subsection-header">Image Alt Text Suggestions</div>', unsafe_allow_html=True)
                alt_texts = [
                    f"Immigration solicitor advising client about {focus_keyword.lower()}",
                    f"Document checklist for {focus_keyword.lower()} application",
                    f"Timeline visualisation for {focus_keyword.lower()} processing",
                    f"Manchester city skyline with immigration law context",
                    f"Family successfully navigating {focus_keyword.lower()} process",
                    f"Step-by-step guide infographic for {focus_keyword.lower()}"
                ]
                
                for alt in alt_texts:
                    st.write(f"• {alt}")
                
                # Content performance indicators
                st.markdown('<div class="subsection-header">Content Performance Indicators</div>', unsafe_allow_html=True)
                indicators = {
                    "Target Word Count": "1,500+ words",
                    "Readability Target": "Grade 8-10 level",
                    "Keyword Density": "1-1.5% for main keyword",
                    "Internal Links": "15-20 relevant links",
                    "External Authority Links": "5-7 government/authority links",
                    "Featured Snippet Targets": "3-5 questions addressed",
                    "Image Optimization": "4-6 images with alt text"
                }
                
                for indicator, target in indicators.items():
                    st.write(f"**{indicator}:** {target}")

def titlecase(s):
    """Convert string to title case excluding small words"""
    small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'with', 'in', 'of'}
    words = s.split()
    title_words = []
    for i, word in enumerate(words):
        if i == 0 or i == len(words) - 1 or word.lower() not in small_words:
            title_words.append(word.capitalize())
        else:
            title_words.append(word.lower())
    return ' '.join(title_words)

if __name__ == "__main__":
    main()
