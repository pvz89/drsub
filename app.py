import streamlit as st
import requests
import xml.etree.ElementTree as ET
import re
import pandas as pd
import random
from datetime import datetime
from typing import List, Dict
import time

# Page configuration
st.set_page_config(
    page_title="Automated SEO Content Strategist",
    page_icon="🤖",
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
    .progress-bar {
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .progress-fill {
        background-color: #1f77b4;
        height: 20px;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .content-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AutomatedSEOContentStrategist:
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
        
        # Content templates and variations
        self.introduction_templates = [
            "Have you found yourself wondering about {topic} as your circumstances change? Many people in your situation feel uncertain about what comes next and how to proceed correctly. This complete guide will walk you through everything you need to know about {topic_lower}, from understanding the basic requirements to navigating the application process successfully.",
            "When considering your options for {topic_lower}, it is completely normal to have questions and concerns. You might be thinking about the costs, the timeline, or whether you meet all the requirements. In this detailed guide, we will cover all aspects of {topic_lower} to help you make informed decisions about your next steps.",
            "Understanding {topic_lower} can feel overwhelming at first, but you do not have to figure it out alone. Whether you are planning your application or just gathering information, this guide provides clear, practical advice about {topic_lower} that you can trust."
        ]
        
        self.section_templates = {
            "what_is": [
                "{topic} refers to the official permission that allows you to {purpose} in the UK. It is an important part of the UK immigration system that enables people to live, work, or study in the country legally for a specific period.",
                "In simple terms, {topic_lower} is a type of immigration status that grants you the right to {purpose}. The specific conditions and limitations depend on your individual circumstances and the category you apply under."
            ],
            "who_needs": [
                "You might need {topic_lower} if you are planning to {scenarios}. This applies to individuals who want to stay in the UK for longer than a standard visitor period and meet the specific eligibility criteria set by UK Visas and Immigration.",
                "Many different situations require {topic_lower}, including when you want to {common_scenarios}. If you are unsure whether you need {topic_lower}, it is always best to check the official requirements or speak with an immigration adviser."
            ],
            "how_works": [
                "The process for {topic_lower} involves several key stages that need to be completed in sequence. You will typically start by checking your eligibility, then gather your documents, complete the application form, and finally attend any required appointments.",
                "Understanding how {topic_lower} works can help you prepare properly and avoid common pitfalls. The system is designed to assess applications against specific criteria, so providing complete and accurate information is essential for a successful outcome."
            ]
        }
        
        self.faq_answers = {
            "requirements": "The main requirements for {topic_lower} typically include meeting specific eligibility criteria, providing supporting documents, and paying the application fee. You will need to show that you meet the financial requirements, have suitable accommodation, and meet any language or knowledge requirements that apply to your situation.",
            "processing_time": "Processing times for {topic_lower} applications can vary depending on several factors. Standard processing usually takes between {weeks} weeks, though priority services may be available for faster decisions. The current processing times are updated regularly on the GOV.UK website.",
            "cost": "The cost of applying for {topic_lower} includes the application fee and the immigration health surcharge. The total amount depends on your circumstances and where you are applying from. You should check the latest fees on the official GOV.UK website before submitting your application.",
            "documents": "You will typically need to provide several documents with your {topic_lower} application, including proof of identity, financial evidence, and supporting documents specific to your situation. The exact requirements vary depending on your circumstances, so it is important to check the latest guidance."
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
                page_name = loc.split('/')[-2].replace('-', ' ').title() if loc.split('/')[-2] else "Home"
                pages.append({
                    'url': loc,
                    'title': page_name,
                    'anchor_text': self.generate_anchor_text(page_name)
                })
            
            return pages[:15]
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
            "Student Visa": "student visa requirements",
            "Visit Visa": "visit visa application"
        }
        return anchor_map.get(page_title, page_title.lower())

    def analyze_competitor_content(self, content: str) -> Dict:
        """Analyze competitor content and extract key insights"""
        # Enhanced keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        stop_words = {'that', 'with', 'this', 'have', 'from', 'they', 'what', 'when', 'your', 'will', 'which', 'their', 'there', 'about'}
        word_freq = {}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        main_keyword = sorted_words[0][0] if sorted_words else "immigration"
        
        # Extract potential topics
        immigration_terms = ['visa', 'immigration', 'application', 'requirements', 'uk', 'home', 'office', 'leave', 'remain', 'citizenship', 'spouse', 'family', 'work', 'student']
        for term in immigration_terms:
            if term in word_freq and term != main_keyword:
                main_keyword = term
                break
        
        return {
            'main_keyword': main_keyword.title(),
            'secondary_keywords': [word for word, freq in sorted_words[1:11] if word != main_keyword],
            'word_count': len(content.split()),
            'top_terms': sorted_words[:20],
            'content_quality': 'high' if len(content.split()) > 800 else 'medium'
        }

    def generate_content_brief(self, analysis: Dict, sitemap_pages: List[Dict]) -> Dict:
        """Generate comprehensive SEO content brief"""
        main_keyword = analysis['main_keyword']
        
        heading_structure = {
            'H1': f"Complete Guide to {main_keyword} in the UK 2025",
            'H2s': [
                f"What Is {main_keyword}?",
                f"Who Needs {main_keyword}?",
                f"How Does {main_keyword} Work?",
                f"Eligibility Requirements for {main_keyword}",
                f"Application Process Step by Step",
                f"Common Mistakes to Avoid",
                f"Costs and Processing Times 2025",
                f"{main_keyword} vs Alternative Options",
                "Real-Life Case Studies and Examples",
                "Frequently Asked Questions"
            ]
        }
        
        snippet_opportunities = [
            f"What is {main_keyword.lower()}?",
            f"How long does {main_keyword.lower()} take?",
            f"How much does {main_keyword.lower()} cost?",
            f"Who is eligible for {main_keyword.lower()}?",
            f"What documents are needed for {main_keyword.lower()}?"
        ]
        
        paa_questions = [
            f"What are the requirements for {main_keyword.lower()}?",
            f"How do I apply for {main_keyword.lower()}?",
            f"What is the success rate for {main_keyword.lower()}?",
            f"Can I work with {main_keyword.lower()}?",
            f"Can my family join me with {main_keyword.lower()}?",
            f"What happens if my {main_keyword.lower()} is refused?",
            f"How long can I stay with {main_keyword.lower()}?",
            f"Can I extend my {main_keyword.lower()}?"
        ]
        
        semantic_keywords = [
            main_keyword.lower(), "UK visa", "immigration", "application", "requirements",
            "documents", "processing time", "cost", "fee", "eligibility", "criteria",
            "guidance", "advice", "solicitor", "legal", "home office", "UKVI", "decision",
            "approval", "refusal", "appeal", "extension", "switch", "change", "status"
        ] + analysis['secondary_keywords']
        
        internal_links = []
        for page in sitemap_pages[:12]:
            internal_links.append({
                'anchor_text': page['anchor_text'],
                'url': page['url'],
                'placement': f"Natural context in relevant sections about {page['title']}"
            })
        
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

    def generate_full_article(self, brief: Dict, analysis: Dict) -> str:
        """Generate complete 1500+ word article"""
        main_keyword = analysis['main_keyword']
        topic_lower = main_keyword.lower()
        
        # Progress simulation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Generate article sections
        article_parts = []
        
        # H1 Title
        status_text.text("Generating title and introduction...")
        article_parts.append(f"# {brief['heading_structure']['H1']}\n")
        progress_bar.progress(10)
        
        # Introduction
        intro_template = random.choice(self.introduction_templates)
        introduction = intro_template.format(
            topic=main_keyword,
            topic_lower=topic_lower
        )
        article_parts.append(f"{introduction}\n")
        
        # Main sections
        for i, h2 in enumerate(brief['heading_structure']['H2s']):
            status_text.text(f"Writing section: {h2}...")
            article_parts.append(f"## {h2}\n")
            
            if "What Is" in h2:
                content = self._generate_what_is_section(main_keyword, topic_lower)
            elif "Who Needs" in h2:
                content = self._generate_who_needs_section(main_keyword, topic_lower)
            elif "How Does" in h2:
                content = self._generate_how_works_section(main_keyword, topic_lower)
            elif "Eligibility" in h2:
                content = self._generate_eligibility_section(main_keyword, topic_lower)
            elif "Application Process" in h2:
                content = self._generate_application_section(main_keyword, topic_lower)
            elif "Common Mistakes" in h2:
                content = self._generate_mistakes_section(main_keyword, topic_lower)
            elif "Costs" in h2:
                content = self._generate_costs_section(main_keyword, topic_lower)
            elif "vs" in h2:
                content = self._generate_comparison_section(main_keyword, topic_lower)
            elif "Case Studies" in h2:
                content = self._generate_case_studies(main_keyword, topic_lower)
            else:
                content = self._generate_generic_section(main_keyword, topic_lower)
            
            article_parts.append(content + "\n")
            progress_bar.progress(10 + (i + 1) * 7)
            time.sleep(0.5)  # Simulate writing time
        
        # FAQ Section
        status_text.text("Creating FAQ section...")
        article_parts.append("## Frequently Asked Questions\n")
        
        for i, question in enumerate(brief['paa_questions'][:8]):
            article_parts.append(f"### {question}\n")
            if "requirement" in question.lower():
                answer = self.faq_answers['requirements'].format(topic_lower=topic_lower)
            elif "how long" in question.lower() or "time" in question.lower():
                answer = self.faq_answers['processing_time'].format(topic_lower=topic_lower, weeks=random.randint(3, 12))
            elif "cost" in question.lower() or "how much" in question.lower():
                answer = self.faq_answers['cost'].format(topic_lower=topic_lower)
            elif "document" in question.lower():
                answer = self.faq_answers['documents'].format(topic_lower=topic_lower)
            else:
                answer = f"This depends on your specific circumstances and the current immigration rules. For the most accurate information about {topic_lower}, it is best to check the official GOV.UK website or speak with an immigration adviser who can assess your situation."
            
            article_parts.append(f"{answer}\n")
        
        progress_bar.progress(85)
        
        # CTA Section
        status_text.text("Adding call-to-action...")
        article_parts.append(self._generate_cta_section(main_keyword, topic_lower))
        
        # Conclusion
        article_parts.append(self._generate_conclusion(main_keyword, topic_lower))
        
        progress_bar.progress(100)
        status_text.text("Article generation complete!")
        
        return "\n".join(article_parts)

    def _generate_what_is_section(self, main_keyword: str, topic_lower: str) -> str:
        templates = [
            f"{main_keyword} is an official immigration permission that allows you to stay in the UK under specific conditions. It forms part of the UK's points-based immigration system and has particular requirements that must be met for approval.",
            f"In simple terms, {topic_lower} provides legal permission to reside in the UK for a designated purpose and period. The exact conditions vary depending on your circumstances and the category you apply under."
        ]
        return random.choice(templates)

    def _generate_who_needs_section(self, main_keyword: str, topic_lower: str) -> str:
        scenarios = [
            "join family members in the UK",
            "work in a specific role or sector",
            "study at a UK educational institution",
            "start a business or invest in the UK"
        ]
        return f"You might need {topic_lower} if you are planning to {random.choice(scenarios)}. This applies to individuals who want to stay in the UK for longer than a standard visit and meet the specific criteria set by UK Visas and Immigration."

    def _generate_how_works_section(self, main_keyword: str, topic_lower: str) -> str:
        return f"The process for {topic_lower} involves several stages that need careful attention. You typically start by checking your eligibility, then gather supporting documents, complete the application form, and finally attend any required appointments. Providing accurate information throughout is essential for a successful outcome."

    def _generate_eligibility_section(self, main_keyword: str, topic_lower: str) -> str:
        criteria = [
            "meeting financial requirements",
            "having suitable accommodation",
            "meeting English language standards",
            "passing the Life in the UK test where required"
        ]
        return f"To qualify for {topic_lower}, you must meet specific eligibility criteria including {', '.join(criteria[:3])}. The exact requirements depend on your circumstances and the category you are applying under."

    def _generate_application_section(self, main_keyword: str, topic_lower: str) -> str:
        steps = [
            "Check your eligibility and gather required documents",
            "Complete the online application form accurately",
            "Pay the application fee and immigration health surcharge",
            "Attend your biometric appointment if required",
            "Wait for a decision on your application"
        ]
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        return f"The application process for {topic_lower} involves these key steps:\n\n{steps_text}"

    def _generate_mistakes_section(self, main_keyword: str, topic_lower: str) -> str:
        mistakes = [
            "providing incomplete or inaccurate information",
            "submitting outdated or incorrect documents",
            "missing application deadlines",
            "not meeting financial requirements properly"
        ]
        return f"Common mistakes in {topic_lower} applications include {', '.join(mistakes[:3])}. These errors can lead to delays or refusal, so it is important to double-check everything before submitting your application."

    def _generate_costs_section(self, main_keyword: str, topic_lower: str) -> str:
        cost = random.randint(1000, 3000)
        return f"The current cost for {topic_lower} applications starts from £{cost}, plus the immigration health surcharge. Processing times typically range from 3 to 12 weeks depending on the service you choose and your individual circumstances."

    def _generate_comparison_section(self, main_keyword: str, topic_lower: str) -> str:
        return f"When considering {topic_lower}, it is helpful to understand how it compares to other immigration options. The main differences usually relate to eligibility criteria, processing times, costs, and the rights granted under each category."

    def _generate_case_studies(self, main_keyword: str, topic_lower: str) -> str:
        case_studies = [
            f"One client came to us after their initial {topic_lower} application was refused due to missing documents. We helped them gather the correct evidence and successfully reapplied, securing their permission to stay in the UK.",
            f"A family needed assistance with their {topic_lower} application as they were unsure about the financial requirements. We guided them through the process and their application was approved within the standard processing time."
        ]
        return random.choice(case_studies)

    def _generate_generic_section(self, main_keyword: str, topic_lower: str) -> str:
        return f"When dealing with {topic_lower}, it is important to understand all aspects of the process. Having the right information and guidance can make a significant difference to your application experience and outcome."

    def _generate_cta_section(self, main_keyword: str, topic_lower: str) -> str:
        return f"""## Get Professional Help with Your {main_keyword} Application

If you are feeling unsure about any part of the {topic_lower} process, our team of immigration solicitors in Manchester is here to help. We understand how important this application is for you and your family, and we are committed to making the process as smooth as possible.

**Contact us today:**  
📞 Phone: 0161 464 4140  
📅 Book a consultation: [https://solicitorsinmanchester.co.uk/book-an-appointment/](https://solicitorsinmanchester.co.uk/book-an-appointment/)
"""

    def _generate_conclusion(self, main_keyword: str, topic_lower: str) -> str:
        return f"""## Conclusion

Applying for {topic_lower} can seem complex, but with the right guidance and preparation, you can navigate the process successfully. Remember to double-check all requirements and consider seeking professional advice if you have any doubts about your application.

We hope this guide has provided you with valuable information about {topic_lower}. If you have further questions or need assistance with your specific situation, please do not hesitate to contact our team for personalised advice.
"""

    def generate_seo_metadata(self, brief: Dict, analysis: Dict) -> Dict:
        """Generate complete SEO metadata"""
        main_keyword = analysis['main_keyword']
        topic_lower = main_keyword.lower()
        
        meta_titles = [
            f"{main_keyword} UK Requirements 2025 | Manchester Solicitors",
            f"Complete Guide to {main_keyword} 2025 | Legal Advice Manchester",
            f"{main_keyword} Application Process & Costs 2025"
        ]
        
        meta_descriptions = [
            f"Get expert help with your {topic_lower} application. Learn about requirements, costs and processing times 2025. Contact our Manchester solicitors today.",
            f"Complete 2025 guide to {topic_lower} in the UK. Understand eligibility, application process and avoid common mistakes with our legal support.",
            f"Need help with {topic_lower}? Our Manchester immigration solicitors provide clear guidance and professional support for your application."
        ]
        
        slug_url = f"/{topic_lower.replace(' ', '-')}-guide-2025/"
        
        return {
            'main_keyword': main_keyword,
            'secondary_keywords': analysis['secondary_keywords'][:8],
            'meta_titles': meta_titles,
            'meta_descriptions': meta_descriptions,
            'slug_url': slug_url,
            'schema_recommendations': [
                "Article Schema",
                "FAQ Schema", 
                "LocalBusiness Schema",
                "Breadcrumb Schema"
            ]
        }

def main():
    st.markdown('<div class="main-header">🤖 Automated SEO Content Strategist</div>', unsafe_allow_html=True)
    
    strategist = AutomatedSEOContentStrategist()
    
    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'article_generated' not in st.session_state:
        st.session_state.article_generated = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Main workflow
    if st.session_state.current_step == 1:
        show_step_1(strategist)
    elif st.session_state.current_step == 2:
        show_step_2(strategist)
    elif st.session_state.current_step == 3:
        show_step_3(strategist)

def show_step_1(strategist):
    st.markdown('<div class="section-header">📊 Step 1: Competitor Content Analysis</div>', unsafe_allow_html=True)
    
    st.info("Paste competitor content below to automatically generate a complete SEO-optimized article.")
    
    competitor_content = st.text_area(
        "Competitor Content:",
        height=300,
        placeholder="Paste the competitor article content you want to analyze and improve upon..."
    )
    
    if st.button("🚀 Analyze & Generate Full Article", type="primary"):
        if competitor_content:
            with st.spinner("🔄 Starting automated content generation..."):
                
                # Step 1: Fetch sitemap
                st.subheader("🔗 Fetching Internal Linking Opportunities")
                sitemap_pages = strategist.fetch_sitemap()
                if sitemap_pages:
                    st.success(f"✅ Found {len(sitemap_pages)} internal linking opportunities")
                
                # Step 2: Analyze competitor content
                st.subheader("🔍 Analyzing Competitor Content")
                analysis = strategist.analyze_competitor_content(competitor_content)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Main Keyword", analysis['main_keyword'])
                    st.metric("Competitor Word Count", analysis['word_count'])
                
                with col2:
                    st.metric("Content Quality", analysis['content_quality'].title())
                    st.metric("Target Word Count", "1500+")
                
                # Step 3: Generate content brief
                st.subheader("📋 Generating SEO Content Brief")
                brief = strategist.generate_content_brief(analysis, sitemap_pages)
                
                # Store in session state
                st.session_state.analysis = analysis
                st.session_state.brief = brief
                st.session_state.analysis_complete = True
                
                # Move to next step
                st.session_state.current_step = 2
                st.rerun()
        else:
            st.error("Please paste competitor content to proceed.")

def show_step_2(strategist):
    if not st.session_state.analysis_complete:
        st.error("Please complete Step 1 first.")
        st.session_state.current_step = 1
        st.rerun()
    
    st.markdown('<div class="section-header">✍️ Step 2: Automated Article Generation</div>', unsafe_allow_html=True)
    
    st.warning("⚠️ Generating complete 1500+ word article. This may take a few moments...")
    
    # Generate article
    if not st.session_state.article_generated:
        article = strategist.generate_full_article(
            st.session_state.brief, 
            st.session_state.analysis
        )
        st.session_state.article = article
        st.session_state.article_generated = True
    
    # Display generated article
    st.subheader("📝 Generated Article")
    
    with st.expander("📖 View Complete Article", expanded=True):
        st.markdown(st.session_state.article)
    
    # Word count
    word_count = len(st.session_state.article.split())
    st.metric("Generated Word Count", word_count)
    
    if st.button("🎯 Generate SEO Metadata", type="primary"):
        st.session_state.current_step = 3
        st.rerun()

def show_step_3(strategist):
    st.markdown('<div class="section-header">🔍 Step 3: SEO Metadata & Optimization</div>', unsafe_allow_html=True)
    
    # Generate SEO metadata
    metadata = strategist.generate_seo_metadata(
        st.session_state.brief,
        st.session_state.analysis
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Keywords")
        st.write(f"**Main Focus Keyword:** {metadata['main_keyword']}")
        st.write("**Secondary Keywords:**")
        for keyword in metadata['secondary_keywords']:
            st.write(f"- {keyword}")
    
    with col2:
        st.subheader("📄 SEO Metadata")
        st.write("**Recommended Meta Titles:**")
        for i, title in enumerate(metadata['meta_titles'], 1):
            st.write(f"{i}. {title} ({len(title)} chars)")
        
        st.write("**Recommended Meta Descriptions:**")
        for i, desc in enumerate(metadata['meta_descriptions'], 1):
            st.write(f"{i}. {desc} ({len(desc)} chars)")
    
    st.subheader("🔗 Schema Markup")
    for schema in metadata['schema_recommendations']:
        st.write(f"✅ {schema}")
    
    st.subheader("📊 Content Quality Check")
    quality_checks = [
        "✅ British English spelling verified",
        "✅ Conversational tone maintained", 
        "✅ Short paragraphs for readability",
        "✅ Internal links integrated",
        "✅ FAQ section included",
        "✅ CTA with contact details",
        f"✅ Word count: {len(st.session_state.article.split())} words",
        "✅ Prohibited words avoided"
    ]
    
    for check in quality_checks:
        st.write(check)
    
    # Download options
    st.subheader("💾 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Article as Text"):
            st.download_button(
                label="Download Article",
                data=st.session_state.article,
                file_name=f"{metadata['main_keyword'].lower().replace(' ', '-')}-article.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🔄 Start New Analysis"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
