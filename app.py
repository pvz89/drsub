import streamlit as st
import openai
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import re

# Page configuration
st.set_page_config(
    page_title="UK Immigration SEO Content Generator",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'article_written' not in st.session_state:
    st.session_state.article_written = False

def fetch_sitemap_urls(sitemap_url: str) -> List[str]:
    """Fetch and parse sitemap to get internal linking opportunities"""
    try:
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            urls = []
            # Look for URL elements in the sitemap
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                urls.append(url.text)
            return urls[:15]  # Return first 15 URLs
        return []
    except Exception as e:
        st.warning(f"Could not fetch sitemap: {e}")
        return []

def analyze_competitor_content(api_key: str, competitor_content: str) -> str:
    """Step 1: Analyze competitor content and create SEO brief"""
    
    prompt = f"""
    You are a top-tier UK SEO content strategist and immigration content writer.

    ANALYZE THIS COMPETITOR CONTENT AND CREATE A DETAILED SEO BRIEF:

    Competitor Content:
    {competitor_content}

    TASKS:
    1. Identify the main focus keyword/topic
    2. Build a detailed SEO content brief outline
    3. Optimise for Google Featured Snippets, People Also Ask, and AI Overview
    4. Include headings (H1–H5), FAQs, semantic/LSI/entity keywords, and real-life examples
    5. Add an SEO-optimised CTA for Solicitors in Manchester with phone: 0161 464 4140 and link: https://solicitorsinmanchester.co.uk/book-an-appointment/

    OUTPUT FORMAT:
    Main Focus Keyword: [keyword]

    SEO Content Brief:
    - H1: [heading]
    - H2: [subheadings]
    - H3: [detailed points]
    - FAQs: [questions and brief answers]
    - Semantic Keywords: [list of related terms]
    - Real-life Examples: [UK-specific scenarios]
    - CTA: [compelling call-to-action]

    Focus on UK immigration law and make it locally relevant to Manchester.
    """

    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert UK SEO content strategist specialising in immigration law content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def write_full_article(api_key: str, analysis: str, sitemap_urls: List[str], main_keyword: str) -> str:
    """Step 2: Write full 1500-word article with internal linking"""
    
    # Pre-defined internal links
    predefined_links = {
        "Immigration solicitors in Manchester": "https://solicitorsinmanchester.co.uk/",
        "Home office": "https://www.gov.uk/government/organisations/home-office",
        "UKVI": "https://www.gov.uk/government/organisations/uk-visas-and-immigration",
        "ILR": "https://solicitorsinmanchester.co.uk/indefinite-leave-to-remain/",
        "Life in the UK test": "https://en.wikipedia.org/wiki/Life_in_the_United_Kingdom_test",
        "NHS": "https://www.nhs.uk/",
        "UK Visas & Immigration Services": "https://solicitorsinmanchester.co.uk/uk-visas-immigration-services/"
    }
    
    internal_linking_strategy = "INTERNAL LINKING STRATEGY:\n"
    internal_linking_strategy += "Pre-defined links to use naturally throughout the article:\n"
    for anchor, link in predefined_links.items():
        internal_linking_strategy += f"- '{anchor}': {link}\n"
    
    if sitemap_urls:
        internal_linking_strategy += "\nAdditional internal linking opportunities from sitemap:\n"
        for url in sitemap_urls[:10]:
            # Extract potential anchor text from URL
            anchor_candidate = url.split('/')[-1].replace('-', ' ').title()
            internal_linking_strategy += f"- '{anchor_candidate}': {url}\n"

    prompt = f"""
    WRITE A FULL 1500-WORD ARTICLE BASED ON THIS ANALYSIS:

    SEO Analysis:
    {analysis}

    MAIN FOCUS KEYWORD: {main_keyword}

    WRITING REQUIREMENTS:
    - Write 1500 words in plain UK English
    - Use a human, personable, conversational tone
    - Avoid: em dashes, and words like "expert", "explore", "navigate", "unravel"
    - Optimise for semantic SEO, AI detection bypass, and local SEO
    - Naturally insert the main focus keyword throughout
    - Include real-life UK immigration examples and scenarios

    {internal_linking_strategy}

    Incorporate these internal links naturally where relevant in the content.
    Focus on Manchester-specific immigration issues and solutions.

    Write the full article below:
    """

    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a skilled UK immigration content writer. Write in a natural, conversational tone that sounds human and avoids AI detection."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=3000
    )
    
    return response.choices[0].message.content

def generate_seo_metadata(api_key: str, article: str, main_keyword: str) -> str:
    """Step 3: Generate SEO metadata"""
    
    prompt = f"""
    GENERATE SEO METADATA FOR THIS ARTICLE:

    Article Content:
    {article[:1000]}... [truncated]

    Main Focus Keyword: {main_keyword}

    PROVIDE:
    1. Meta Title (within 60 characters)
    2. Meta Description (within 155 characters, NLP-optimised)
    3. Slug URL (SEO and local intent focused for Manchester)

    Format your response clearly with these headings.
    """

    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SEO specialist focused on UK immigration law."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def extract_main_keyword(analysis: str) -> str:
    """Extract main keyword from analysis"""
    lines = analysis.split('\n')
    for line in lines:
        if 'Main Focus Keyword:' in line:
            return line.split('Main Focus Keyword:')[-1].strip()
    return "UK Immigration"  # fallback

def main():
    st.title("🇬🇧 UK Immigration SEO Content Generator")
    st.markdown("### AI-Powered Content Strategy for Immigration Solicitors")
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password")
        st.markdown("---")
        st.info("""
        **How to use:**
        1. Enter your OpenAI API key
        2. Paste competitor content
        3. Generate SEO analysis
        4. Write full article
        5. Get SEO metadata
        """)
    
    if not api_key:
        st.warning("🔑 Please enter your OpenAI API key to continue")
        return
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Competitor Analysis", "✍️ Article Writing", "🔍 SEO Metadata"])
    
    with tab1:
        st.header("Step 1: Competitor Content Analysis")
        competitor_content = st.text_area(
            "Paste competitor content here:",
            height=200,
            placeholder="Paste the competitor article content you want to analyze and outperform..."
        )
        
        if st.button("Analyze Competitor Content", type="primary"):
            if competitor_content:
                with st.spinner("Analyzing competitor content and creating SEO brief..."):
                    analysis = analyze_competitor_content(api_key, competitor_content)
                    st.session_state.analysis = analysis
                    st.session_state.main_keyword = extract_main_keyword(analysis)
                    st.session_state.analysis_complete = True
                    
                st.success("✅ Analysis Complete!")
                st.subheader("SEO Content Brief")
                st.write(analysis)
            else:
                st.error("Please paste some competitor content to analyze")
    
    with tab2:
        st.header("Step 2: Write Full Article")
        
        if not st.session_state.get('analysis_complete', False):
            st.warning("Please complete Step 1 first to generate the SEO analysis")
        else:
            if st.button("Write 1500-Word Article", type="primary"):
                with st.spinner("Writing comprehensive article with internal linking..."):
                    # Fetch sitemap for internal linking
                    sitemap_urls = fetch_sitemap_urls("https://solicitorsinmanchester.co.uk/page-sitemap.xml")
                    
                    article = write_full_article(
                        api_key, 
                        st.session_state.analysis,
                        sitemap_urls,
                        st.session_state.main_keyword
                    )
                    st.session_state.article = article
                    st.session_state.article_written = True
                
                st.success("✅ Article Written!")
                st.subheader("Full Article")
                st.write(article)
                
                # Word count
                word_count = len(article.split())
                st.metric("Word Count", word_count)
    
    with tab3:
        st.header("Step 3: SEO Metadata")
        
        if not st.session_state.get('article_written', False):
            st.warning("Please complete Step 2 first to generate the article")
        else:
            if st.button("Generate SEO Metadata", type="primary"):
                with st.spinner("Creating optimized SEO metadata..."):
                    metadata = generate_seo_metadata(
                        api_key,
                        st.session_state.article,
                        st.session_state.main_keyword
                    )
                    st.session_state.metadata = metadata
                
                st.success("✅ SEO Metadata Generated!")
                st.subheader("Optimized Metadata")
                st.write(metadata)
            
            # Download section
            if st.session_state.get('article_written', False):
                st.markdown("---")
                st.subheader("Download Content")
                
                # Create downloadable content
                full_content = f"""
SEO ANALYSIS:
{st.session_state.analysis}

{'='*50}

FULL ARTICLE:
{st.session_state.article}

{'='*50}

SEO METADATA:
{st.session_state.get('metadata', 'Generate metadata first')}
"""
                
                st.download_button(
                    label="📥 Download Complete Content",
                    data=full_content,
                    file_name=f"seo_content_{st.session_state.main_keyword.replace(' ', '_')}.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
