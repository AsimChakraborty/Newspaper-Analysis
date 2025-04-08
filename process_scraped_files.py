
import os
import json
import time
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re  # For cleaning Gemini's response
import validators  


# --- Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

CRAWL_DOC_FOLDER = "F:/softograph/news_demo/crawl_documents"  # Path to scraped JSON files
OUTPUT_CSV_FILE = "F:/softograph/news_demo/processed_data/analyzed_articles.csv" 
PROCESSING_DELAY_SECONDS = 1  # Delay between Gemini API calls
MAX_CONTENT_LENGTH = 25000  # Limit text sent to Gemini

# --- Initialize APIs ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# --- Gemini Prompt Template ---
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

# --- Helper Functions ---
def extract_text_from_html(html_content):
    """Extract meaningful text content from raw HTML using BeautifulSoup."""
    if not html_content:
        return None
    try:
        soup = BeautifulSoup(html_content, 'lxml')  # Use lxml parser
        # Remove script, style, header, footer, nav tags as they usually don't contain main content
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
            tag.decompose()
        # Try to find common main content containers
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'(content|main|body|article)', re.I))
        text_element = main_content if main_content else soup.body
        if not text_element:
            text_element = soup  # Fallback to whole soup if no body
        # Get text, joining paragraphs/blocks with spaces, and strip extra whitespace
        text = ' '.join(text_element.stripped_strings)
        return text.strip()
    except Exception as e:
        print(f"  Error parsing HTML: {e}")
        return None
     

def clean_gemini_response(response_text):
    """Clean and extract valid JSON from Gemini's response."""
    try:
        # Remove potential newlines and extra spaces
        cleaned_text = re.sub(r'\s+', ' ', response_text.strip())
        # Find the first '{' and the last '}' to extract potential JSON
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = cleaned_text[json_start:json_end + 1]
            return json_str
        else:
            print(f"  Error: Could not find valid JSON structure in Gemini response.")
            print(f"  Raw Response: {cleaned_text[:500]}...")  # Log beginning of raw response
            return None
    except Exception as e:
        print(f"  Error cleaning Gemini response: {e}")
        return None


def extract_data_with_gemini(content, url):
    """Send content to Gemini and parse the structured JSON response."""
    if not content:
        print(f"  Skipping Gemini call for {url} due to empty content.")
        return None

    print(f"  Sending content (length: {len(content)}) to Gemini for extraction...")
    # Truncate content if it's too long
    truncated_content = content[:MAX_CONTENT_LENGTH]
    if len(content) > MAX_CONTENT_LENGTH:
        print(f"  Warning: Content truncated to {MAX_CONTENT_LENGTH} characters for Gemini.")

    prompt = GEMINI_PROMPT_TEMPLATE.format(content=truncated_content)
    try:
        # Configure safety settings to be less restrictive if needed
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)

        # Clean the response
        cleaned_json_str = clean_gemini_response(response.text)
        if not cleaned_json_str:
            print(f"  Failed to clean Gemini response for {url}.")
            return None

        # Attempt to parse the cleaned JSON response
        try:
            extracted_data = json.loads(cleaned_json_str)
            # Basic validation
            expected_keys = ['headline', 'summary', 'locations', 'names', 'categories']
            if all(k in extracted_data for k in expected_keys):
                # Ensure list fields are actually lists
                for key in ['locations', 'names', 'categories']:
                    if not isinstance(extracted_data[key], list):
                        print(f"  Warning: Gemini returned non-list for '{key}'. Setting empty list for {url}.")
                        extracted_data[key] = []
                # Further clean lists: remove empty strings or extraneous items
                for key in ['locations', 'names', 'categories']:
                    extracted_data[key] = [item for item in extracted_data[key] if isinstance(item, str) and item.strip()]
                print(f"  Successfully extracted structured data from Gemini for {url}.")
                return extracted_data
            else:
                missing_keys = [k for k in expected_keys if k not in extracted_data]
                print(f"  Warning: Gemini response missing expected keys: {missing_keys} for {url}. Response: {cleaned_json_str}")
                return None
        except json.JSONDecodeError as json_err:
            print(f"  Error: Gemini did not return valid JSON after cleaning for {url}. {json_err}")
            print(f"  Problematic JSON String: {cleaned_json_str}")
            return None
    except Exception as e:
        print(f"  Error calling Gemini API for {url}: {e}")
        try:
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                print(f"  Gemini Block Reason: {response.prompt_feedback.block_reason}")
        except AttributeError:
            pass  # Ignore if feedback attributes don't exist
        return None


# --- Main Processing Logic ---
all_processed_articles = []
processed_urls = set()  # Keep track of URLs processed to avoid duplicates

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_CSV_FILE), exist_ok=True)
print(f"Starting processing of JSON files in: {CRAWL_DOC_FOLDER}")
json_files = [f for f in os.listdir(CRAWL_DOC_FOLDER) if f.endswith('.json')]
print(f"Found {len(json_files)} JSON files.")

for filename in json_files:
    filepath = os.path.join(CRAWL_DOC_FOLDER, filename)
    print(f"\nProcessing file: {filename}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Expecting a list of objects
            if not isinstance(data, list):
                print(f"  Warning: Expected a list of objects in {filename}, found {type(data)}. Skipping file.")
                continue
            for item in data:
                if not isinstance(item, dict):
                    print(f"  Warning: Expected a dictionary item in {filename}, found {type(item)}. Skipping item.")
                    continue
                html_content = item.get('html')
                metadata = item.get('metadata', {})
                url = metadata.get('url') or metadata.get('sourceURL')  # Get URL from metadata

                # Validate the URL
                if not url or not validators.url(url):
                    print(f"  Warning: Invalid or missing URL for item in file {filename}. Metadata: {metadata}")
                    continue

                if url in processed_urls:
                    print(f"  Skipping already processed URL: {url}")
                    continue

                if not html_content:
                    print(f"  Warning: Skipping item for URL {url}, no HTML content found.")
                    continue

                print(f"Processing URL: {url}")
                text_content = extract_text_from_html(html_content)
                if text_content:
                    structured_data = extract_data_with_gemini(text_content, url)
                    if structured_data:
                        structured_data['url'] = url  # Add the source URL
                        all_processed_articles.append(structured_data)
                        processed_urls.add(url)  # Mark URL as processed
                    else:
                        print(f"  Failed to extract structured data via Gemini for {url}")
                else:
                    print(f"  Skipping Gemini processing for {url} due to failure in text extraction from HTML.")

                # Polite delay between API calls
                print(f"  Waiting for {PROCESSING_DELAY_SECONDS} seconds...")
                time.sleep(PROCESSING_DELAY_SECONDS)
    except json.JSONDecodeError as e:
        print(f"  Error reading JSON file {filename}: {e}")
    except Exception as e:
        print(f"  An unexpected error occurred processing file {filename}: {e}")

# --- Save to CSV ---
if all_processed_articles:
    print(f"\nProcessed {len(all_processed_articles)} articles successfully.")
    df = pd.DataFrame(all_processed_articles)
    # Ensure consistent column order
    column_order = ['headline', 'summary', 'categories', 'locations', 'names', 'url']
    df = df.reindex(columns=column_order)  # Use reindex to handle potential missing columns gracefully
    try:
        df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
        print(f"Successfully saved processed data to {OUTPUT_CSV_FILE}")
    except Exception as e:
        print(f"Error saving data to CSV {OUTPUT_CSV_FILE}: {e}")
else:
    print("\nNo articles were processed successfully or data could be extracted.")
print("Processing finished.")