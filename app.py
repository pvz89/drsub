import streamlit as st
import openai
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple
import re
import time
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="UK Immigration SEO Content Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f3d7a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        color: #1f3d7a;
        border-bottom: 2px solid #1f3d7a;
        padding-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f3d7a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    session_defaults = {
        'analysis_complete': False,
        'article_written': False,
        'metadata_generated': False,
        'analysis': '',
        'article': '',
        'metadata': '',
        'main_keyword': '',
        'sitemap_urls': [],
        'word_count': 0,
        'current_step': 1
    }
    
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_sitemap_urls(sitemap_url: str) -> List[str]:
    """Fetch and parse sitemap to get internal linking opportunities"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            urls = []
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            for url in root.findall('.//ns:loc', namespace):
                urls.append(url.text)
            return urls[:15]
        return []
    except Exception as e:
        st.error(f"Error fetching sitemap: {str(e)}")
        return []

def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key"""
    if not api_key.startswith('sk-'):
        return False
    return True

def extract_main_keyword(analysis: str) -> str:
    """Extract main keyword from analysis using multiple patterns"""
    patterns = [
        r'Main Focus Keyword:\s*(.+)',
        r'Keyword:\s*(.+)',
        r'Focus Keyword:\s*(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, analysis, re.IGNORECASE)
        if match:
            keyword = match.group(1).strip()
            if keyword and len(keyword) > 3:
                return keyword
    
    # Fallback: find the most common phrase
    words = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', analysis)
    if words:
        return max(set(words), key=words.count)
    
    return "UK Immigration"

def create_analysis_prompt(competitor_content: str) -> str:
    """Create optimized prompt for competitor analysis"""
    return f"""
You are a top-tier UK SEO content strategist specialising in immigration law.

ANALYZE THIS COMPETITOR CONTENT AND CREATE A DETAILED SEO BRIEF:

COMPETITOR CONTENT:
{competitor_content[:3000]}  # Limit content to avoid token issues

TASKS:
1. Identify the SINGLE main focus keyword/topic (most important)
2. Create comprehensive SEO content brief
3. Optimise for Featured Snippets, People Also Ask, and AI Overview
4. Structure with H1-H5 headings
5. Include 5-7 relevant FAQs
6. List semantic/LSI keywords (10-15)
7. Provide 2-3 real-life UK immigration examples
8. Create compelling CTA for Manchester solicitors

OUTPUT FORMAT:
Main Focus Keyword: [exact keyword phrase]

SEO Content Brief:
H1: [Main heading]
H2: [Subheading 1]
H2: [Subheading 2]
H3: [Detailed points under subheading 2]
H2: [Subheading 3]
FAQs:
- Q: [Question 1]
  A: [Brief answer]
- Q: [Question 2]
  A: [Brief answer]
Semantic Keywords: [keyword1, keyword2, keyword3]
Real-life Examples: [Example 1, Example 2]
CTA: [Call-to-action with phone 0161 464 4140 and booking link]

Keep it concise and actionable. Focus on UK immigration law and Manchester locality.
"""

def create_article_prompt(analysis: str, main_keyword: str, internal_links: str) -> str:
    """Create optimized prompt for article writing"""
    return f"""
WRITE A COMPREHENSIVE 1500-WORD IMMIGRATION ARTICLE:

SEO BRIEF:
{analysis}

MAIN KEYWORD: {main_keyword}

WRITING REQUIREMENTS:
- 1500 words in plain UK English
- Conversational, personable tone
- Avoid: "expert", "explore", "navigate", "unravel", em dashes
- Natural keyword integration
- UK-focused examples and scenarios
- Manchester-specific local references

INTERNAL LINKING STRATEGY:
{internal_links}

Incorporate links naturally where relevant. Focus on helping readers understand UK immigration processes.

Write the complete article with proper heading structure:
"""

def create_metadata_prompt(article: str, main_keyword: str) -> str:
    """Create optimized prompt for metadata generation"""
    return f"""
Generate SEO metadata for this immigration article:

MAIN KEYWORD: {main_keyword}

ARTICLE EXCERPT:
{article[:800]}

REQUIREMENTS:
- Meta Title: Under 60 characters, compelling
- Meta Description: Under 155 characters, includes keyword, call-to-action
- Slug URL: SEO-friendly, includes location and keyword

Format exactly:
Meta Title: [title]
Meta Description: [description]
Slug URL: [slug]
"""

def call_openai(api_key: str, prompt: str, system_message: str, max_tokens: int = 2000) -> str:
    """Make OpenAI API call with error handling"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=30
        )
        
        return response.choices[0].message.content.strip()
        
    except openai.APIConnectionError:
        st.error("Network connection error. Please check your internet connection.")
    except openai.RateLimitError:
        st.error("Rate limit exceeded. Please wait a moment and try again.")
    except openai.AuthenticationError:
        st.error("Invalid API key. Please check your OpenAI API key.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    return ""

def process_step_1(api_key: str, competitor_content: str):
    """Process competitor analysis"""
    with st.spinner("🔍 Analyzing competitor content and creating SEO brief..."):
        prompt = create_analysis_prompt(competitor_content)
        system_msg = "You are an expert UK SEO content strategist specialising in immigration law content."
        
        analysis = call_openai(api_key, prompt, system_msg)
        
        if analysis:
            st.session_state.analysis = analysis
            st.session_state.main_keyword = extract_main_keyword(analysis)
            st.session_state.analysis_complete = True
            st.session_state.current_step = 2
            return True
        return False

def process_step_2(api_key: str):
    """Process article writing"""
    with st.spinner("✍️ Writing comprehensive 1500-word article..."):
        # Prepare internal links
        predefined_links = {
            "Immigration solicitors in Manchester": "https://solicitorsinmanchester.co.uk/",
            "Home Office": "https://www.gov.uk/government/organisations/home-office",
            "UKVI": "https://www.gov.uk/government/organisations/uk-visas-and-immigration",
            "ILR": "https://solicitorsinmanchester.co.uk/indefinite-leave-to-remain/",
            "Life in the UK test": "https://en.wikipedia.org/wiki/Life_in_the_United_Kingdom_test",
            "NHS": "https://www.nhs.uk/",
            "UK Visas & Immigration Services": "https://solicitorsinmanchester.co.uk/uk-visas-immigration-services/"
        }
        
        internal_links = "Pre-defined internal links to use naturally:\n"
        for anchor, link in predefined_links.items():
            internal_links += f"- {anchor}: {link}\n"
        
        # Add sitemap links
        sitemap_urls = fetch_sitemap_urls("https://solicitorsinmanchester.co.uk/page-sitemap.xml")
        if sitemap_urls:
            internal_links += "\nAdditional linking opportunities:\n"
            for url in sitemap_urls[:8]:
                anchor = url.split('/')[-1].replace('-', ' ').title()
                internal_links += f"- {anchor}: {url}\n"
        
        prompt = create_article_prompt(
            st.session_state.analysis,
            st.session_state.main_keyword,
            internal_links
        )
        
        system_msg = "You are a skilled UK immigration content writer. Write in a natural, conversational tone that sounds human."
        
        article = call_openai(api_key, prompt, system_msg, max_tokens=3000)
        
        if article:
            st.session_state.article = article
            st.session_state.word_count = len(article.split())
            st.session_state.article_written = True
            st.session_state.current_step = 3
            return True
        return False

def process_step_3(api_key: str):
    """Process metadata generation"""
    with st.spinner("🔍 Generating optimized SEO metadata..."):
        prompt = create_metadata_prompt(
            st.session_state.article,
            st.session_state.main_keyword
        )
        
        system_msg = "You are an SEO specialist focused on UK immigration law and local search optimization."
        
        metadata = call_openai(api_key, prompt, system_msg)
        
        if metadata:
            st.session_state.metadata = metadata
            st.session_state.metadata_generated = True
            return True
        return False

def render_sidebar():
    """Render the sidebar with configuration and progress"""
    with st.sidebar:
        st.markdown("## 🔑 Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key starting with 'sk-'",
            placeholder="sk-..."
        )
        
        st.markdown("---")
        st.markdown("## 📊 Progress")
        
        # Progress indicators
        steps = {
            1: "Competitor Analysis",
            2: "Article Writing", 
            3: "SEO Metadata"
        }
        
        for step_num, step_name in steps.items():
            status = "✅" if (
                (step_num == 1 and st.session_state.analysis_complete) or
                (step_num == 2 and st.session_state.article_written) or
                (step_num == 3 and st.session_state.metadata_generated)
            ) else "◻️"
            
            st.write(f"{status} Step {step_num}: {step_name}")
        
        st.markdown("---")
        st.markdown("## 💡 Tips")
        st.info("""
        - Paste complete competitor articles for best analysis
        - Review each step before proceeding
        - The app caches sitemap data for 1 hour
        - All content is optimized for UK audience
        """)
        
        return api_key

def render_step_1(api_key: str):
    """Render step 1: Competitor analysis"""
    st.markdown('<div class="step-header">Step 1: Competitor Content Analysis</div>', unsafe_allow_html=True)
    
    competitor_content = st.text_area(
        "Paste competitor content here:",
        height=250,
        placeholder="Copy and paste the complete competitor article you want to analyze and outperform...",
        key="competitor_content"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Analyze Content", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please enter your OpenAI API key in the sidebar")
            elif not competitor_content.strip():
                st.error("Please paste some competitor content to analyze")
            elif len(competitor_content.strip()) < 100:
                st.error("Please provide more content for meaningful analysis (min 100 characters)")
            else:
                if process_step_1(api_key, competitor_content.strip()):
                    st.success("Competitor analysis completed successfully!")
    
    if st.session_state.analysis_complete:
        with st.expander("📊 SEO Content Brief", expanded=True):
            st.write(st.session_state.analysis)
            
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Main Keyword", st.session_state.main_keyword)
            st.markdown('</div>', unsafe_allow_html=True)

def render_step_2(api_key: str):
    """Render step 2: Article writing"""
    st.markdown('<div class="step-header">Step 2: Article Writing</div>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.warning("Please complete Step 1 first to generate the SEO analysis")
        return
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Write Article", type="primary", use_container_width=True):
            if process_step_2(api_key):
                st.success("Article written successfully!")
    
    if st.session_state.article_written:
        with st.expander("✍️ Full Article", expanded=True):
            st.write(st.session_state.article)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Word Count", st.session_state.word_count)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Target", "1500")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            percentage = min(100, int((st.session_state.word_count / 1500) * 100))
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Completion", f"{percentage}%")
            st.markdown('</div>', unsafe_allow_html=True)

def render_step_3(api_key: str):
    """Render step 3: SEO metadata"""
    st.markdown('<div class="step-header">Step 3: SEO Metadata</div>', unsafe_allow_html=True)
    
    if not st.session_state.article_written:
        st.warning("Please complete Step 2 first to generate the article")
        return
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Generate Metadata", type="primary", use_container_width=True):
            if process_step_3(api_key):
                st.success("SEO metadata generated successfully!")
    
    if st.session_state.metadata_generated:
        with st.expander("🔍 SEO Metadata", expanded=True):
            st.write(st.session_state.metadata)
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Content")
        
        full_content = f"""
SEO ANALYSIS:
{st.session_state.analysis}

{'='*60}

FULL ARTICLE:
{st.session_state.article}

{'='*60}

SEO METADATA:
{st.session_state.metadata}
"""
        
        filename = f"seo_content_{st.session_state.main_keyword.replace(' ', '_').lower()}.txt"
        
        st.download_button(
            label="Download Complete Package",
            data=full_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

def main():
    """Main application function"""
    st.markdown('<div class="main-header">🇬🇧 UK Immigration SEO Content Generator</div>', unsafe_allow_html=True)
    
    # Get API key from sidebar
    api_key = render_sidebar()
    
    if not api_key:
        st.warning("🔑 Please enter your OpenAI API key in the sidebar to begin")
        return
    
    if not validate_api_key(api_key):
        st.error("❌ Please enter a valid OpenAI API key (should start with 'sk-')")
        return
    
    # Render steps in tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Competitor Analysis", 
        "✍️ Article Writing", 
        "🔍 SEO Metadata"
    ])
    
    with tab1:
        render_step_1(api_key)
    
    with tab2:
        render_step_2(api_key)
    
    with tab3:
        render_step_3(api_key)

if __name__ == "__main__":
    main()
