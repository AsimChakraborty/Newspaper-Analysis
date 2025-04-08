# Newspaper Analysis App with firewall bypass techniques
# pip install newspaper3k requests beautifulsoup4 streamlit google-generativeai python-dotenv lxml_html_clean requests[socks] fake-useragent selenium webdriver-manager cloudscraper rotating-proxies

import os
import json
import time
import random
import requests
import streamlit as st
from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article, Config
import google.generativeai as genai
from dotenv import load_dotenv
from fake_useragent import UserAgent
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize user agent rotator
ua = UserAgent()

# Configure newspaper
config = Config()
config.browser_user_agent = ua.random
config.request_timeout = 20

# Define newspapers with their URLs
NEWSPAPERS = {
    "Prothom Alo": {
        "base_url": "https://www.prothomalo.com",
        "sections": {
            "latest": "/latest",
            "bangladesh": "/bangladesh",
            "international": "/international",
            "sports": "/sports",
            "entertainment": "/entertainment",
            "business": "/business",
        }
    },
    "The Daily Star": {
        "base_url": "https://www.thedailystar.net",
        "sections": {
            "latest": "/latest-news",
            "bangladesh": "/news/bangladesh",
            "world": "/news/world",
            "sports": "/sports",
            "business": "/business",
        }
    },
    "Kaler Kantho": {
        "base_url": "https://www.kalerkantho.com",
        "sections": {
            "home": "/",
            "national": "/online/national",
            "world": "/online/international",
            "sports": "/online/sports",
            "entertainment": "/online/entertainment",
        }
    }
}

# Gemini prompt template
GEMINI_PROMPT_TEMPLATE = """
Extract the following information from the given news article content:
1. Headline
2. Short summary (2-3 sentences)
3. List of significant locations (country, city, town, province, region, etc.)
4. List of significant names (people, organizations, political parties, etc.)
5. Assign one or multiple relevant categories (e.g., Politics, Sports, Technology, Business, Health, Environment, World, Bangladesh, Crime, Opinion, Editorial, Lifestyle, Entertainment, etc.)

Content:
{content}

Provide the response STRICTLY in JSON format with keys: 'headline', 'summary', 'locations', 'names', 'categories'. 
Ensure the output is ONLY the JSON object, without any surrounding text or markdown formatting.
Make sure 'locations', 'names', and 'categories' are JSON arrays of strings. If no relevant information is found for a list, provide an empty list ([]).
"""

# List of proxy options (add your own proxies if needed)
PROXIES = [
    None,  # No proxy option
    # Add your proxy list here in the format:
    # {"http": "http://user:pass@ip:port", "https": "https://user:pass@ip:port"}
]

def get_random_delay():
    """Generate a random delay to mimic human behavior"""
    return random.uniform(2, 5)

def get_random_proxy():
    """Get a random proxy from the list"""
    return random.choice(PROXIES)

def create_selenium_driver():
    """Create and configure a Selenium WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Add additional arguments to bypass detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # Execute CDP commands to bypass detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        return driver
    except Exception as e:
        st.error(f"Failed to create Selenium driver: {str(e)}")
        return None

def fetch_with_multiple_methods(url, method_index=0):
    """Try different methods to fetch a URL"""
    methods = [
        lambda u: requests_fetch(u),
        lambda u: cloudscraper_fetch(u),
        lambda u: selenium_fetch(u)
    ]
    
    if method_index >= len(methods):
        raise Exception("All fetch methods failed")
    
    try:
        return methods[method_index](url)
    except Exception as e:
        st.warning(f"Method {method_index} failed: {str(e)}. Trying next method...")
        time.sleep(1)
        return fetch_with_multiple_methods(url, method_index + 1)

def requests_fetch(url):
    """Fetch URL using requests library with rotating user-agents and proxies"""
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': '/'.join(url.split('/')[:3]),  # Base domain as referer
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers',
    }
    
    proxy = get_random_proxy()
    response = requests.get(url, headers=headers, proxies=proxy, timeout=20)
    return response.text

def cloudscraper_fetch(url):
    """Fetch URL using cloudscraper to bypass Cloudflare"""
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    response = scraper.get(url)
    return response.text

def selenium_fetch(url):
    """Fetch URL using Selenium for JavaScript rendering"""
    driver = create_selenium_driver()
    if not driver:
        raise Exception("Failed to create Selenium driver")
    
    try:
        driver.get(url)
        # Wait for JavaScript to render
        time.sleep(5)
        # Scroll down to load lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)
        html = driver.page_source
        return html
    finally:
        driver.quit()

def get_article_links(newspaper_name, section, method="auto"):
    """Get article links from a specific section of a newspaper"""
    newspaper_info = NEWSPAPERS[newspaper_name]
    base_url = newspaper_info["base_url"]
    section_url = newspaper_info["sections"][section]
    
    # Handle relative URLs
    if section_url.startswith("/"):
        full_url = base_url + section_url
    else:
        full_url = section_url
    
    st.write(f"Fetching articles from: {full_url}")
    
    try:
        # Add random delay to avoid triggering rate limits
        time.sleep(get_random_delay())
        
        # Choose fetch method based on parameter
        if method == "requests":
            html_content = requests_fetch(full_url)
        elif method == "cloudscraper":
            html_content = cloudscraper_fetch(full_url)
        elif method == "selenium":
            html_content = selenium_fetch(full_url)
        else:  # "auto" - Try all methods
            html_content = fetch_with_multiple_methods(full_url)
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Different newspapers have different HTML structures
        links = []
        
        if newspaper_name == "Prothom Alo":
            # Try multiple possible selectors
            # First try with known container classes
            containers = []
            for class_name in ['customStoryCard', 'news_item', 'palo-article-item', 'article-panel', 'news_content', 'story-card']:
                containers.extend(soup.find_all(['div', 'article'], class_=class_name))
            
            # Debug information
            st.write(f"Found {len(containers)} potential article containers")
            
            # Extract links from containers
            for container in containers:
                anchor = container.find('a')
                if anchor and anchor.get('href'):
                    url = anchor['href']
                    if not url.startswith('http'):
                        url = base_url + url
                    links.append(url)
            
            # If no containers found, look for articles based on URL patterns
            if not links:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    # Look for article-like patterns in URLs
                    if href and ('/news/' in href or '/article/' in href or '/bangladesh/' in href):
                        if not href.startswith('http'):
                            href = base_url + href
                        links.append(href)
        
        elif newspaper_name == "The Daily Star":
            # First try with known container classes
            containers = []
            for class_name in ['card', 'list-item', 'news-item', 'article-panel', 'card-content', 'story-card']:
                containers.extend(soup.find_all(['div', 'article'], class_=class_name))
            
            # Extract links from containers
            for container in containers:
                anchor = container.find('a')
                if anchor and anchor.get('href'):
                    url = anchor['href']
                    if not url.startswith('http'):
                        url = base_url + url
                    links.append(url)
            
            # If no containers found, look for articles based on URL patterns
            if not links:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    # Look for article-like patterns in URLs
                    if href and ('/news/' in href or '/article/' in href):
                        if not href.startswith('http'):
                            href = base_url + href
                        links.append(href)
        
        elif newspaper_name == "Kaler Kantho":
            # First try with known container classes
            containers = []
            for class_name in ['n_row', 'news-item', 'article-panel', 'news-card', 'item-inner']:
                containers.extend(soup.find_all(['div', 'article'], class_=class_name))
            
            # Extract links from containers
            for container in containers:
                anchor = container.find('a')
                if anchor and anchor.get('href'):
                    url = anchor['href']
                    if not url.startswith('http'):
                        url = base_url + url
                    links.append(url)
            
            # If no containers found, look for articles based on URL patterns
            if not links:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href')
                    # Look for article-like patterns in URLs
                    if href and ('/online/' in href or '/article/' in href):
                        if not href.startswith('http'):
                            href = base_url + href
                        links.append(href)
        
        # Remove duplicates and limit to 15 articles
        links = list(set(links))[:15]
        
        # Debug information
        st.write(f"Found {len(links)} article links")
        if links:
            st.write("Sample links:")
            for i, link in enumerate(links[:3]):
                st.write(f"{i+1}. {link}")
        
        return links
    
    except Exception as e:
        st.error(f"Error fetching articles from {newspaper_name}: {str(e)}")
        return []

def extract_article_content(url):
    """Extract article content using newspaper3k with firewall bypass techniques"""
    try:
        # Add random delay to avoid triggering rate limits
        time.sleep(get_random_delay())
        
        try:
            # First try with newspaper3k
            config.browser_user_agent = ua.random  # Rotate user agent
            article = Article(url, config=config)
            article.download()
            article.parse()
            
            content = article.text
            title = article.title
            
            # Check if content is too short (might be blocked)
            if len(content) < 100 or not title:
                raise Exception("Content too short or missing title - might be blocked")
                
        except Exception as e:
            st.warning(f"Newspaper3k extraction failed: {str(e)}. Trying alternative methods...")
            
            # Try alternative methods
            html_content = fetch_with_multiple_methods(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to extract content from common content containers
            content_containers = soup.select('article, .article-body, .story-content, .content-body, .news-content')
            content = ""
            
            if content_containers:
                for container in content_containers:
                    # Remove unwanted elements
                    for unwanted in container.select('script, style, nav, header, footer, .advertisement, .ads'):
                        unwanted.decompose()
                    
                    paragraphs = container.find_all('p')
                    for p in paragraphs:
                        content += p.get_text() + "\n\n"
            
            # Try to extract title
            title_elements = soup.select('h1, .article-title, .headline, .story-title')
            title = title_elements[0].get_text().strip() if title_elements else "Unknown Title"
            
            # Check if content is still too short
            if len(content) < 100:
                raise Exception("Content extraction failed with all methods")
        
        # Debug information
        content_length = len(content)
        st.write(f"Extracted {content_length} characters from article: {title}")
        
        return {
            "title": title,
            "text": content,
            "publish_date": datetime.now(),  # Use current time if actual date not available
            "url": url
        }
    except Exception as e:
        st.error(f"Error extracting content from {url}: {str(e)}")
        return None

def analyze_with_gemini(article_content):
    """Analyze article content using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = GEMINI_PROMPT_TEMPLATE.format(content=article_content["text"])
        response = model.generate_content(prompt)
        
        # Parse JSON response
        json_str = response.text
        try:
            analysis = json.loads(json_str)
            
            # Add original URL and scrape date
            analysis["url"] = article_content["url"]
            analysis["scraped_at"] = datetime.now().isoformat()
            
            return analysis
        except json.JSONDecodeError as e:
            st.error(f"Error parsing Gemini response as JSON: {str(e)}")
            st.write("Raw response:", response.text)
            return None
    except Exception as e:
        st.error(f"Error analyzing content with Gemini: {str(e)}")
        return None

def filter_news(news_items, filters):
    """Filter news based on user input filters"""
    filtered_items = []
    
    for item in news_items:
        matches = True
        
        # Filter by location
        if filters.get("location") and filters["location"]:
            location_match = False
            for loc in item.get("locations", []):
                if filters["location"].lower() in loc.lower():
                    location_match = True
                    break
            if not location_match:
                matches = False
        
        # Filter by name (person, organization)
        if filters.get("name") and filters["name"]:
            name_match = False
            for name in item.get("names", []):
                if filters["name"].lower() in name.lower():
                    name_match = True
                    break
            if not name_match:
                matches = False
        
        # Filter by category
        if filters.get("category") and filters["category"]:
            category_match = False
            for category in item.get("categories", []):
                if filters["category"].lower() in category.lower():
                    category_match = True
                    break
            if not category_match:
                matches = False
        
        if matches:
            filtered_items.append(item)
    
    return filtered_items

def main():
    st.set_page_config(page_title="Bangladeshi News Analyzer", layout="wide")
    
    st.title("Bangladeshi News Analysis App")
    st.write("This app scrapes news from major Bangladeshi newspapers and analyzes them with AI.")
    
    # Initialize session state for storing articles
    if 'news_items' not in st.session_state:
        st.session_state.news_items = []
    
    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["News Scraper", "Manual Input", "Settings"])
    
    with tab1:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Scraping Controls")
            
            # Select newspaper and section
            newspaper = st.selectbox("Select Newspaper", list(NEWSPAPERS.keys()))
            section = st.selectbox("Select Section", list(NEWSPAPERS[newspaper]["sections"].keys()))
            
            # Select scraping method
            scraping_method = st.radio(
                "Scraping Method",
                ["auto", "requests", "cloudscraper", "selenium"],
                help="Auto tries all methods in sequence until one works"
            )
            
            # Scrape button
            if st.button("Scrape Articles"):
                with st.spinner("Scraping and analyzing articles..."):
                    # Get article links
                    links = get_article_links(newspaper, section, method=scraping_method)
                    
                    if not links:
                        st.warning("No article links found. Try another section, newspaper, or scraping method.")
                    else:
                        # Clear previous results if needed
                        if st.checkbox("Clear previous results", value=True):
                            st.session_state.news_items = []
                        
                        # Process each article
                        progress_bar = st.progress(0)
                        success_count = 0
                        
                        for i, link in enumerate(links):
                            st.text(f"Processing article {i+1}/{len(links)}")
                            
                            # Extract article content
                            article_content = extract_article_content(link)
                            if article_content:
                                # Analyze with Gemini
                                analysis = analyze_with_gemini(article_content)
                                if analysis:
                                    st.session_state.news_items.append(analysis)
                                    success_count += 1
                            
                            # Update progress
                            progress_bar.progress((i + 1) / len(links))
                        
                        st.success(f"Successfully scraped and analyzed {success_count} articles!")
            
            # Filters
            st.subheader("Filters")
            location_filter = st.text_input("Filter by Location")
            name_filter = st.text_input("Filter by Person/Organization")
            category_filter = st.text_input("Filter by Category")
            
            filters = {
                "location": location_filter,
                "name": name_filter,
                "category": category_filter
            }
            
            # Apply filters
            if any(filters.values()):
                filtered_items = filter_news(st.session_state.news_items, filters)
                st.write(f"Found {len(filtered_items)} matching articles")
            else:
                filtered_items = st.session_state.news_items
        
        with col2:
            # Display news items
            if not st.session_state.news_items:
                st.info("No articles scraped yet. Use the controls to scrape articles.")
            else:
                st.subheader(f"Articles ({len(filtered_items)})")
                # Display filtered news items
                for item in filtered_items:
                    with st.expander(f"{item.get('headline', 'No headline')}"):
                        st.write(f"**Summary:** {item.get('summary', 'No summary available')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Locations:**")
                            if item.get('locations'):
                                for loc in item['locations']:
                                    st.write(f"- {loc}")
                            else:
                                st.write("No locations found")
                        
                        with col2:
                            st.write("**People/Organizations:**")
                            if item.get('names'):
                                for name in item['names']:
                                    st.write(f"- {name}")
                            else:
                                st.write("No names found")
                        
                        st.write("**Categories:**", ", ".join(item.get('categories', ['Uncategorized'])))
                        st.write(f"**Source:** [Read Original Article]({item.get('url', '#')})")
    
    with tab2:
        st.subheader("Manual Article Input")
        article_url = st.text_input("Enter article URL to analyze")
        
        col1, col2 = st.columns(2)
        with col1:
            scrape_method = st.radio(
                "Extraction Method",
                ["auto", "newspaper3k", "selenium"],
                help="Select the method to extract article content"
            )
        
        with col2:
            if st.button("Analyze Article"):
                if article_url:
                    with st.spinner("Analyzing article..."):
                        # Extract article content
                        article_content = extract_article_content(article_url)
                        if article_content:
                            # Show raw content
                            with st.expander("Raw article content"):
                                st.text(article_content["text"][:500] + "...")
                            
                            # Analyze with Gemini
                            analysis = analyze_with_gemini(article_content)
                            if analysis:
                                st.session_state.news_items.append(analysis)
                                st.success("Article analyzed successfully!")
                                
                                # Show analysis
                                st.subheader("Analysis Result")
                                st.write(f"**Headline:** {analysis.get('headline', 'N/A')}")
                                st.write(f"**Summary:** {analysis.get('summary', 'N/A')}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Locations:**")
                                    if analysis.get('locations'):
                                        for loc in analysis['locations']:
                                            st.write(f"- {loc}")
                                    else:
                                        st.write("No locations found")
                                
                                with col2:
                                    st.write("**People/Organizations:**")
                                    if analysis.get('names'):
                                        for name in analysis['names']:
                                            st.write(f"- {name}")
                                    else:
                                        st.write("No names found")
                                
                                st.write("**Categories:**", ", ".join(analysis.get('categories', ['Uncategorized'])))
                            else:
                                st.error("Failed to analyze article content.")
                        else:
                            st.error("Failed to extract article content.")
                else:
                    st.warning("Please enter a valid URL.")
    
    with tab3:
        st.subheader("Application Settings")
        
        st.write("**Firewall Bypass Settings**")
        
        st.info("""
        This application uses multiple techniques to bypass firewall restrictions:
        
        1. **User-Agent Rotation**: Automatically changes browser identification to avoid detection
        2. **Multiple Extraction Methods**: 
           - Standard requests with headers
           - CloudScraper for Cloudflare-protected sites
           - Selenium for JavaScript-heavy sites
        3. **Request Delays**: Random delays between requests to avoid rate limiting
        """)
        
        if st.button("Clear Data"):
            st.session_state.news_items = []
            st.success("All scraped data cleared!")
        
        st.write("**Test Connection**")
        test_url = st.text_input("Enter URL to test connection", "https://www.prothomalo.com")
        test_method = st.radio("Test Method", ["requests", "cloudscraper", "selenium"])
        
        if st.button("Test"):
            with st.spinner(f"Testing connection to {test_url} using {test_method}..."):
                try:
                    if test_method == "requests":
                        content = requests_fetch(test_url)
                    elif test_method == "cloudscraper":
                        content = cloudscraper_fetch(test_url)
                    else:  # selenium
                        content = selenium_fetch(test_url)
                    
                    content_length = len(content)
                    st.success(f"Connection successful! Retrieved {content_length} characters.")
                    
                    # Parse and check for signs of blocking
                    soup = BeautifulSoup(content, 'html.parser')
                    title = soup.title.text if soup.title else "No title"
                    
                    # Check if likely blocked
                    blocked_keywords = ["access denied", "forbidden", "captcha", "security check", "cloudflare"]
                    is_blocked = any(keyword in content.lower() for keyword in blocked_keywords)
                    
                    if is_blocked:
                        st.warning(f"Connection worked but might be blocked. Page title: {title}")
                    else:
                        st.success(f"Connection appears to be working correctly. Page title: {title}")
                        
                except Exception as e:
                    st.error(f"Connection test failed: {str(e)}")

if __name__ == "__main__":
    main()