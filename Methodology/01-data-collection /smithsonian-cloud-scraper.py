import os
import json
import time
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables from .env file
load_dotenv()

# API configuration
API_KEY = os.getenv('SMITHSONIAN_API_KEY', 'YOUR_API_KEY_HERE')
BASE_URL = 'https://api.si.edu/openaccess/api/v1.0'
SEARCH_ENDPOINT = '/search'

# Create directories for saving data
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'smithsonian_clouds')
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')
METADATA_DIR = os.path.join(OUTPUT_DIR, 'metadata')

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Search parameters
search_params = {
    'q': 'cloud',  # Search for "cloud"
    # Exclude "saint cloud", "saint-cloud", and the National Museum of Natural History
    'fq': '-title:("saint cloud" OR "saint-cloud") AND -unit_code:NMNHBOTANY AND -unit_code:NMNHENTO AND -unit_code:NMNHMIN AND -unit_code:NMNHPALEO AND -unit_code:NMNHHERPS AND -unit_code:NMNHINV AND -unit_code:NMNHMAMMALS AND -unit_code:NMNHMOLLUSKS AND -unit_code:NMNHBIRDS',
    'rows': 100,   # Number of results per page
    'start': 0,    # Starting index for pagination
    'media_type': 'Images'  # Get only images
}

def has_downloadable_image(item):
    """Check if an item has a downloadable image using Smithsonian delivery service."""
    try:
        descriptive = item.get('content', {}).get('descriptiveNonRepeating', {})
        online_media = descriptive.get('online_media', {})
        media_list = online_media.get('media', [])
        
        for media in media_list:
            # Check for delivery service URLs or any URL pattern
            content_url = media.get('content', '')
            if content_url and (
                'deliveryService' in content_url or 
                'ids' in content_url or
                'iiif' in content_url or
                'mq' in content_url):
                return True
        return False
    except Exception as e:
        print(f"Error checking for downloadable image: {e}")
        return False

def is_from_nmnh(item):
    """Check if an item is from the National Museum of Natural History."""
    try:
        unit_code = item.get('unitCode', '')
        return 'NMNH' in unit_code
    except Exception:
        return False

def get_image_url(item):
    """Extract the image URL from an item."""
    try:
        media_list = item['content']['descriptiveNonRepeating']['online_media']['media']
        for media in media_list:
            content_url = media.get('content', '')
            rights = media.get('usage', {}).get('access', 'unknown')
            
            # Check for delivery service URLs or any URL pattern
            if content_url and (
                'deliveryService' in content_url or 
                'ids' in content_url or
                'iiif' in content_url or
                'mq' in content_url):
                
                # Make sure we get the full URL if it's a relative URL
                if content_url.startswith('edu/') or content_url.startswith('/'):
                    content_url = f"https://ids.si.edu/{content_url}"
                    
                # Add max size parameter if not already present
                if 'deliveryService' in content_url and 'max=' not in content_url:
                    content_url += '&max=1000'  # Request larger image
                    
                return content_url, rights
                
        return None, None
    except Exception as e:
        print(f"Error getting image URL: {e}")
        return None, None

def clean_filename(title):
    """Clean a string to make it suitable for a filename."""
    if not title:
        return 'unknown'
    # Replace non-alphanumeric characters with underscores
    clean = ''.join(c if c.isalnum() else '_' for c in title)
    # Ensure it's not too long
    return clean.lower()[:100]

def download_image(url, filename, rights):
    """Download an image from URL to a file."""
    try:
        print(f"Attempting to download: {url} (Rights: {rights})")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Add .jpg extension if not present
        if not filename.lower().endswith('.jpg'):
            filename = f"{filename}.jpg"
        
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Successfully downloaded to: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return False

def search_and_download():
    """Main function to search and download images and metadata."""
    total_processed = 0
    has_more_results = True
    start_index = 0
    eligible_items = 0
    attempted_downloads = 0
    successful_downloads = 0
    nmnh_excluded = 0
    
    print('Starting to search for cloud images (excluding saint cloud/saint-cloud and National Museum of Natural History)...')
    print(f"Using API key: {API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else ''}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    while has_more_results:
        try:
            # Update start index for pagination
            search_params['start'] = start_index
            
            # Construct query URL
            params = {
                'api_key': API_KEY,
                **search_params
            }
            query_string = urlencode(params)
            url = f"{BASE_URL}{SEARCH_ENDPOINT}?{query_string}"
            
            print(f"Fetching results {start_index} to {start_index + search_params['rows']}...")
            
            # Make API request
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('response') or not data['response'].get('rows'):
                print('No results found or unexpected API response format.')
                break
            
            items = data['response']['rows']
            print(f"Received {len(items)} items.")
            
            if not items:
                has_more_results = False
                break
            
            # Process each item
            for item in items:
                # Check if the item is from NMNH (double check as API filter might not catch all)
                if is_from_nmnh(item):
                    nmnh_excluded += 1
                    print(f"Excluding item from NMNH: {item.get('id', 'unknown')}")
                    continue
                    
                if has_downloadable_image(item):
                    eligible_items += 1
                    image_url, rights = get_image_url(item)
                    if not image_url:
                        print(f"Could not extract image URL for item: {item.get('id', 'unknown')}")
                        continue
                    
                    title = item.get('title', 'untitled')
                    item_id = item.get('id', 'unknown_id')
                    filename = clean_filename(f"{item_id}_{title}")
                    
                    # Save metadata to JSON file
                    metadata_path = os.path.join(METADATA_DIR, f"{filename}.json")
                    with open(metadata_path, 'w') as f:
                        json.dump(item, f, indent=2)
                    
                    # Download image
                    image_path = os.path.join(IMAGES_DIR, filename)
                    print(f"Downloading: {title} (ID: {item_id})")
                    attempted_downloads += 1
                    success = download_image(image_url, image_path, rights)
                    if success:
                        successful_downloads += 1
                        total_processed += 1
                else:
                    print(f"Item does not have downloadable image: {item.get('id', 'unknown')}")
            
            # Move to next page
            start_index += len(items)
            
            # Check if we've reached the end of results
            if len(items) < search_params['rows']:
                has_more_results = False
            
            # Optional delay to avoid overwhelming the API
            time.sleep(1)
            
            # Print summary after each batch
            print(f"Summary so far: {eligible_items} eligible items, {attempted_downloads} download attempts, {successful_downloads} successful downloads, {nmnh_excluded} NMNH items excluded")
            
        except Exception as e:
            print(f"Error during API request: {e}")
            break
    
    print(f"Finished processing.")
    print(f"Total stats: {eligible_items} eligible items found")
    print(f"             {attempted_downloads} download attempts")
    print(f"             {successful_downloads} successful downloads")
    print(f"             {nmnh_excluded} NMNH items excluded")

if __name__ == "__main__":
    search_and_download()
