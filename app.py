def google_custom_search(keyword, api_key, search_engine_id, num_results=5):
    """Use Google Custom Search API for reliable results"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': keyword,
            'num': num_results
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        urls = []
        if 'items' in data:
            for item in data['items']:
                if not is_gov_url(item['link']):
                    urls.append(item['link'])
        
        return urls
    except Exception as e:
        st.error(f"Google Custom Search error: {str(e)}")
        return []
