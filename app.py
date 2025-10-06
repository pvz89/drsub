import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
from urllib.parse import urlparse
import time

# Page configuration
st.set_page_config(
    page_title="SEO Content Optimizer",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'competitor_content' not in st.session_state:
    st.session_state.competitor_content = []
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""

def is_gov_url(url):
    """Check if URL is a .gov domain"""
    parsed_url = urlparse(url)
    return parsed_url.netloc.endswith('.gov')

def extract_content_from_url(url):
    """Extract main content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '[role="main"]',
            'div#content',
            'div.content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        # If no specific content area found, use body
        if not content:
            content = soup.find('body')
        
        if content:
            # Get text and clean it
            text = content.get_text()
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:4000]  # Limit content length
        return None
        
    except Exception as e:
        st.error(f"Error extracting content from {url}: {str(e)}")
        return None

def get_serp_results(keyword, num_results=10):
    """Get top SERP results for a keyword"""
    try:
        urls = []
        for url in search(keyword, num_results=num_results, advanced=True):
            if not is_gov_url(url.url):
                urls.append(url.url)
            if len(urls) >= 5:  # Get top 5 non-gov results
                break
        return urls
    except Exception as e:
        st.error(f"Error getting SERP results: {str(e)}")
        return []

def analyze_competitor_content(content_list, keyword):
    """Analyze competitor content using OpenAI"""
    try:
        analysis_prompt = f"""
        Analyze the following competitor content for the keyword "{keyword}". Provide insights on:
        
        1. Content structure and formatting
        2. Key topics covered
        3. Content depth and quality
        4. Missing opportunities
        5. SEO elements used
        
        Competitor Content:
        {content_list}
        
        Provide a comprehensive analysis that will help create better content.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO content analyst."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def generate_seo_content(competitor_analysis, keyword, competitor_content):
    """Generate optimized SEO content"""
    try:
        content_prompt = f"""
        Based on the competitor analysis and the top-ranking content, create a comprehensive, SEO-optimized article for the keyword "{keyword}".
        
        Competitor Analysis:
        {competitor_analysis}
        
        Top Competitor Content Samples:
        {competitor_content}
        
        Requirements:
        1. Create content that is BETTER than all competitors
        2. Make it more comprehensive, engaging, and valuable
        3. Use proper SEO formatting (H1, H2, H3, bullet points, etc.)
        4. Ensure it's human-friendly and easy to read
        5. Include practical examples and actionable advice
        6. Make it 30-50% more detailed than competitors
        7. Use natural language and avoid keyword stuffing
        
        Structure:
        - Compelling introduction
        - Comprehensive main sections
        - Practical examples
        - Actionable tips
        - Conclusion
        
        Generate the complete article:
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer who creates content that ranks #1 on Google."},
                {"role": "user", "content": content_prompt}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"

def generate_meta_elements(content, keyword):
    """Generate meta title, description, and slug"""
    try:
        meta_prompt = f"""
        Based on the following content and main keyword "{keyword}", generate:
        
        1. A compelling meta title (50-60 characters)
        2. An engaging meta description (150-160 characters)
        3. A SEO-friendly URL slug
        4. 3-5 secondary keywords
        
        Content:
        {content[:1000]}
        
        Provide the output in this exact format:
        META_TITLE: [title here]
        META_DESCRIPTION: [description here]
        SLUG: [slug here]
        SECONDARY_KEYWORDS: [comma separated keywords here]
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO specialist."},
                {"role": "user", "content": meta_prompt}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating meta elements: {str(e)}"

def main():
    st.title("🚀 SEO Content Optimizer")
    st.markdown("Create content that ranks better than your competitors!")
    
    # Sidebar for API key
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        if api_key:
            openai.api_key = api_key
        
        st.markdown("---")
        st.info("""
        **How to use:**
        1. Enter your OpenAI API key
        2. Input your target keyword
        3. Click 'Analyze & Generate'
        4. Get optimized content + SEO elements
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword = st.text_input("🎯 Target Keyword:", placeholder="e.g., best coffee makers 2024")
        
        if st.button("🚀 Analyze & Generate SEO Content", type="primary"):
            if not api_key:
                st.error("⚠️ Please enter your OpenAI API key")
                return
            if not keyword:
                st.error("⚠️ Please enter a target keyword")
                return
            
            with st.spinner("🕵️‍♂️ Analyzing competitors and generating content..."):
                # Progress tracking
                progress_bar = st.progress(0)
                
                # Step 1: Get SERP results
                st.info("🔍 Searching Google for top ranking pages...")
                serp_urls = get_serp_results(keyword)
                progress_bar.progress(25)
                
                if not serp_urls:
                    st.error("No suitable competitor URLs found. Try a different keyword.")
                    return
                
                # Step 2: Extract content from URLs
                st.info("📄 Extracting content from competitor pages...")
                competitor_contents = []
                for i, url in enumerate(serp_urls):
                    content = extract_content_from_url(url)
                    if content:
                        competitor_contents.append({
                            'url': url,
                            'content': content[:1000]  # First 1000 chars for analysis
                        })
                    time.sleep(1)  # Be respectful to servers
                
                progress_bar.progress(50)
                
                if not competitor_contents:
                    st.error("Could not extract content from competitor pages.")
                    return
                
                # Step 3: Analyze competitor content
                st.info("📊 Analyzing competitor content...")
                content_for_analysis = "\n\n".join([f"URL: {item['url']}\nContent: {item['content']}" 
                                                  for item in competitor_contents])
                competitor_analysis = analyze_competitor_content(content_for_analysis, keyword)
                progress_bar.progress(75)
                
                # Step 4: Generate optimized content
                st.info("✍️ Generating optimized SEO content...")
                full_competitor_content = "\n\n".join([item['content'] for item in competitor_contents])
                generated_content = generate_seo_content(competitor_analysis, keyword, full_competitor_content)
                
                # Step 5: Generate meta elements
                st.info("🏷️ Generating SEO elements...")
                meta_elements = generate_meta_elements(generated_content, keyword)
                progress_bar.progress(100)
                
                # Store results in session state
                st.session_state.competitor_content = competitor_contents
                st.session_state.generated_content = generated_content
                st.session_state.meta_elements = meta_elements
                st.session_state.analysis_complete = True
                st.session_state.competitor_analysis = competitor_analysis
    
    # Display results
    if st.session_state.analysis_complete:
        st.markdown("---")
        st.success("✅ Analysis Complete!")
        
        # Display competitor analysis
        with st.expander("📊 Competitor Analysis", expanded=False):
            st.write(st.session_state.competitor_analysis)
        
        # Display competitor URLs
        with st.expander("🔗 Top Competitor URLs", expanded=False):
            for item in st.session_state.competitor_content:
                st.write(f"• {item['url']}")
        
        # Display generated content
        st.subheader("✨ Generated SEO Content")
        st.text_area("Optimized Content", st.session_state.generated_content, height=400)
        
        # Display meta elements
        st.subheader("🏷️ SEO Elements")
        
        # Parse meta elements
        meta_text = st.session_state.meta_elements
        meta_lines = meta_text.split('\n')
        
        meta_data = {}
        for line in meta_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                meta_data[key.strip()] = value.strip()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Meta Title", 
                         value=meta_data.get('META_TITLE', ''), 
                         key="meta_title_display")
            st.text_input("URL Slug", 
                         value=meta_data.get('SLUG', ''), 
                         key="slug_display")
        
        with col2:
            st.text_area("Meta Description", 
                        value=meta_data.get('META_DESCRIPTION', ''), 
                        height=100,
                        key="meta_desc_display")
            st.text_input("Secondary Keywords", 
                         value=meta_data.get('SECONDARY_KEYWORDS', ''), 
                         key="secondary_kw_display")
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copy Content"):
                st.code(st.session_state.generated_content)
                st.success("Content copied to clipboard!")
        
        with col2:
            st.download_button(
                label="📥 Download Content",
                data=st.session_state.generated_content,
                file_name=f"seo_content_{keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with col3:
            st.download_button(
                label="📊 Download Analysis",
                data=f"Keyword: {keyword}\n\nCompetitor Analysis:\n{st.session_state.competitor_analysis}\n\nGenerated Content:\n{st.session_state.generated_content}",
                file_name=f"seo_analysis_{keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Built with ❤️ using Streamlit & OpenAI</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
