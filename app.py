import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Real Estate Analytics Pro",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class RealEstateAnalyzer:
    def __init__(self):
        self.market_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample real estate data for demonstration"""
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        properties = []
        
        for i in range(1000):
            property_type = np.random.choice(['Single Family', 'Condo', 'Townhouse', 'Multi-Family'])
            bedrooms = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.2, 0.1])
            bathrooms = max(1, bedrooms - np.random.choice([0, 1]))
            sqft = np.random.normal(1500 + bedrooms * 200, 200)
            price = np.random.normal(300000 + bedrooms * 50000, 75000)
            
            properties.append({
                'id': i + 1,
                'address': f"{np.random.randint(100, 9999)} Main St",
                'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'state': np.random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
                'zip_code': np.random.randint(10000, 99999),
                'property_type': property_type,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'square_feet': max(800, sqft),
                'price': max(100000, price),
                'date_listed': np.random.choice(dates),
                'status': np.random.choice(['Active', 'Pending', 'Sold'], p=[0.3, 0.2, 0.5]),
                'days_on_market': np.random.randint(1, 365)
            })
        
        return pd.DataFrame(properties)

    def calculate_metrics(self, df):
        """Calculate key real estate metrics"""
        metrics = {
            'total_listings': len(df),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'avg_days_on_market': df['days_on_market'].mean(),
            'sold_to_list_ratio': len(df[df['status'] == 'Sold']) / len(df) if len(df) > 0 else 0,
            'avg_price_per_sqft': (df['price'] / df['square_feet']).mean()
        }
        return metrics

def main():
    # Header
    st.markdown('<h1 class="main-header">🏠 Real Estate Analytics Pro</h1>', unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = RealEstateAnalyzer()
    
    # Sidebar
    st.sidebar.title("🔍 Filters & Controls")
    
    # Data upload section
    st.sidebar.subheader("📁 Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload your data (CSV)", type=['csv'])
    
    if uploaded_file is not None:
        user_data = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ Data uploaded successfully!")
        current_data = user_data
    else:
        current_data = analyzer.market_data
        st.sidebar.info("💡 Using sample data. Upload your own CSV file for analysis.")
    
    # Filters
    st.sidebar.subheader("🎯 Filters")
    
    selected_cities = st.sidebar.multiselect(
        "Select Cities",
        options=current_data['city'].unique(),
        default=current_data['city'].unique()[:3]
    )
    
    property_types = st.sidebar.multiselect(
        "Property Types",
        options=current_data['property_type'].unique(),
        default=current_data['property_type'].unique()
    )
    
    price_range = st.sidebar.slider(
        "Price Range",
        min_value=int(current_data['price'].min()),
        max_value=int(current_data['price'].max()),
        value=(int(current_data['price'].min()), int(current_data['price'].max()))
    )
    
    bedrooms_filter = st.sidebar.multiselect(
        "Bedrooms",
        options=sorted(current_data['bedrooms'].unique()),
        default=sorted(current_data['bedrooms'].unique())
    )
    
    # Apply filters
    filtered_data = current_data[
        (current_data['city'].isin(selected_cities)) &
        (current_data['property_type'].isin(property_types)) &
        (current_data['price'] >= price_range[0]) &
        (current_data['price'] <= price_range[1]) &
        (current_data['bedrooms'].isin(bedrooms_filter))
    ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = analyzer.calculate_metrics(filtered_data)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Listings", f"{metrics['total_listings']:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average Price", f"${metrics['avg_price']:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Median Price", f"${metrics['median_price']:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Days on Market", f"{metrics['avg_days_on_market']:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts and Visualizations
    st.markdown('<h2 class="section-header">📊 Market Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution by property type
        fig_price_dist = px.box(
            filtered_data, 
            x='property_type', 
            y='price',
            title='Price Distribution by Property Type'
        )
        st.plotly_chart(fig_price_dist, use_container_width=True)
        
        # Days on market analysis
        fig_dom = px.histogram(
            filtered_data,
            x='days_on_market',
            title='Days on Market Distribution',
            nbins=20
        )
        st.plotly_chart(fig_dom, use_container_width=True)
    
    with col2:
        # Price vs Square Feet
        fig_scatter = px.scatter(
            filtered_data,
            x='square_feet',
            y='price',
            color='property_type',
            title='Price vs Square Footage',
            trendline='lowess'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Market status pie chart
        status_counts = filtered_data['status'].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='Listing Status Distribution'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Advanced Analytics Section
    st.markdown('<h2 class="section-header">📈 Advanced Analytics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price trends by city
        city_analysis = filtered_data.groupby('city').agg({
            'price': ['mean', 'median', 'count']
        }).round(0)
        city_analysis.columns = ['Average Price', 'Median Price', 'Listings Count']
        city_analysis = city_analysis.sort_values('Average Price', ascending=False)
        
        st.subheader("🏙️ City-wise Price Analysis")
        st.dataframe(city_analysis, use_container_width=True)
    
    with col2:
        # Bedroom analysis
        bedroom_analysis = filtered_data.groupby('bedrooms').agg({
            'price': ['mean', 'median'],
            'square_feet': 'mean',
            'days_on_market': 'mean'
        }).round(0)
        bedroom_analysis.columns = ['Avg Price', 'Median Price', 'Avg Sq Ft', 'Avg DOM']
        
        st.subheader("🛏️ Bedroom Analysis")
        st.dataframe(bedroom_analysis, use_container_width=True)
    
    # Property Comparison Tool
    st.markdown('<h2 class="section-header">⚖️ Property Comparison Tool</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Property 1")
        prop1_city = st.selectbox("City", options=filtered_data['city'].unique(), key='prop1_city')
        prop1_type = st.selectbox("Type", options=filtered_data['property_type'].unique(), key='prop1_type')
        prop1_bed = st.slider("Bedrooms", 1, 5, 3, key='prop1_bed')
        prop1_bath = st.slider("Bathrooms", 1, 4, 2, key='prop1_bath')
        prop1_sqft = st.slider("Square Feet", 800, 4000, 1500, key='prop1_sqft')
    
    with col2:
        st.subheader("Property 2")
        prop2_city = st.selectbox("City", options=filtered_data['city'].unique(), key='prop2_city')
        prop2_type = st.selectbox("Type", options=filtered_data['property_type'].unique(), key='prop2_type')
        prop2_bed = st.slider("Bedrooms", 1, 5, 3, key='prop2_bed')
        prop2_bath = st.slider("Bathrooms", 1, 4, 2, key='prop2_bath')
        prop2_sqft = st.slider("Square Feet", 800, 4000, 1500, key='prop2_sqft')
    
    with col3:
        st.subheader("Comparison Results")
        
        # Calculate estimated prices (simplified model)
        base_price = 100000
        price_per_sqft = 150
        bed_premium = 25000
        bath_premium = 15000
        city_multipliers = {
            'New York': 1.8, 'Los Angeles': 1.6, 'Chicago': 1.1, 
            'Houston': 0.9, 'Phoenix': 1.0
        }
        
        prop1_est_price = (
            base_price + 
            (prop1_sqft * price_per_sqft) +
            (prop1_bed * bed_premium) +
            (prop1_bath * bath_premium)
        ) * city_multipliers.get(prop1_city, 1.0)
        
        prop2_est_price = (
            base_price + 
            (prop2_sqft * price_per_sqft) +
            (prop2_bed * bed_premium) +
            (prop2_bath * bath_premium)
        ) * city_multipliers.get(prop2_city, 1.0)
        
        st.metric("Property 1 Estimated Value", f"${prop1_est_price:,.0f}")
        st.metric("Property 2 Estimated Value", f"${prop2_est_price:,.0f}")
        st.metric("Price Difference", f"${abs(prop1_est_price - prop2_est_price):,.0f}")
    
    # Data Export Section
    st.markdown('<h2 class="section-header">💾 Export Data</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Filtered Data Preview")
        st.dataframe(filtered_data.head(10), use_container_width=True)
    
    with col2:
        st.subheader("Download Options")
        
        # Convert dataframe to CSV
        csv = filtered_data.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"real_estate_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Generate report
        report_text = f"""
        Real Estate Analysis Report
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Summary Statistics:
        - Total Listings: {metrics['total_listings']}
        - Average Price: ${metrics['avg_price']:,.0f}
        - Median Price: ${metrics['median_price']:,.0f}
        - Average Days on Market: {metrics['avg_days_on_market']:.0f}
        
        Filters Applied:
        - Cities: {', '.join(selected_cities)}
        - Property Types: {', '.join(property_types)}
        - Price Range: ${price_range[0]:,} - ${price_range[1]:,}
        """
        
        st.download_button(
            label="📄 Download Summary Report",
            data=report_text,
            file_name=f"real_estate_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
