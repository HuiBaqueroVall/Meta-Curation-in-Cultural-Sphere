#!/usr/bin/env python3
"""
Harvard Art Museums Collection Scraper

This scraper interfaces with the Harvard Art Museums API to collect cloud-related imagery and metadata.

Usage:
    python harvard_scraper.py --key YOUR_API_KEY --terms "cloud,sky" --output "harvard_clouds"

Variables to configure:
    - API_KEY: Your Harvard Art Museums API key
    - SEARCH_TERMS: List of search terms to query
    - MAX_RESULTS: Maximum number of results to retrieve per term
    - OUTPUT_DIR: Directory to save images and metadata
"""

import os
import json
import time
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure variables here
API_KEY = "YOUR_API_KEY"  # Replace with your Harvard Art Museums API key
SEARCH_TERMS = ["cloud", "sky", "weather", "mist", "fog", "atmosphere"]
EXCLUDED_TERMS = ["saint cloud", "saint-cloud", "st cloud", "st. cloud"]
MAX_RESULTS = 100  # Maximum results per search term
OUTPUT_DIR = "harvard_data"

# API endpoints
API_BASE = "https://api.harvardartmuseums.org"
OBJECT_ENDPOINT = f"{API_BASE}/object"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Harvard Art Museums Cloud Image Scraper")
    parser.add_argument("--key", type=str, help="Harvard Art Museums API key")
    parser.add_argument("--terms", type=str, help="Comma-separated search terms")
    parser.add_argument("--exclude", type=str, help="Comma-separated terms to exclude")
    parser.add_argument("--max", type=int, help="Maximum results per term")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args()
    
    # Update global variables if arguments provided
    global API_KEY, SEARCH_TERMS, EXCLUDED_TERMS, MAX_RESULTS, OUTPUT_DIR
    if args.key:
        API_KEY = args.key
    if args.terms:
        SEARCH_TERMS = args.terms.split(",")
    if args.exclude:
        EXCLUDED_TERMS = args.exclude.split(",")
    if args.max:
        MAX_RESULTS = args.max
    if args.output:
        OUTPUT_DIR = args.output

def setup_directories():
    """Create necessary directories for storing data"""
    # Main output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    
    # Images directory
    images_dir = os.path.join(OUTPUT_DIR, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Created directory: {images_dir}")
    
    # Metadata directory
    metadata_dir = os.path.join(OUTPUT_DIR, "metadata")
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
        print(f"Created directory: {metadata_dir}")
    
    return images_dir, metadata_dir

def search_harvard(term, page=1, has_image=True):
    """
    Search the Harvard Art Museums collection for a specific term
    
    Args:
        term: Search term
        page: Page number for pagination
        has_image: Only return results with images
    
    Returns:
        JSON response from the API
    """
    params = {
        "apikey": API_KEY,
        "q": term,
        "hasimage": 1 if has_image else 0,
        "page": page,
        "size": 100,  # Maximum per page
        "fields": "id,title,description,primaryimageurl,imagepermissionlevel,images,people,culture,dated"
    }
    
    try:
        response = requests.get(OBJECT_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching for '{term}': {e}")
        return None

def should_exclude(metadata):
    """Check if an object should be excluded based on excluded terms"""
    if not metadata:
        return True
    
    # Convert metadata to string for simple term matching
    metadata_str = json.dumps(metadata).lower()
    
    for term in EXCLUDED_TERMS:
        if term.lower() in metadata_str:
            print(f"Excluding object {metadata.get('id')} because it contains '{term}'")
            return True
    
    return False

def download_image(url, filepath):
    """Download an image from a URL and save it to a file"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def process_object(art_object, images_dir, metadata_dir):
    """Process a single artwork: download images and save metadata"""
    # Extract basic information
    object_id = art_object.get("id")
    if not object_id:
        return False
    
    # Check if already downloaded
    metadata_path = os.path.join(metadata_dir, f"{object_id}.json")
    if os.path.exists(metadata_path):
        print(f"Already processed {object_id}, skipping")
        return True
    
    # Check if object contains excluded terms
    if should_exclude(art_object):
        return False
    
    # Extract image URL
    primary_image_url = art_object.get("primaryimageurl")
    
    # Download primary image if available
    if primary_image_url:
        # Determine file extension
        ext = os.path.splitext(primary_image_url)[1]
        if not ext:
            ext = ".jpg"  # Default extension
        
        image_path = os.path.join(images_dir, f"{object_id}{ext}")
        success = download_image(primary_image_url, image_path)
        if not success:
            print(f"Failed to download image for {object_id}")
    else:
        print(f"No image available for {object_id}")
        return False
    
    # Process additional images
    if "images" in art_object and art_object["images"]:
        for i, img in enumerate(art_object["images"][:5]):  # Limit to 5 additional images
            if "baseimageurl" in img:
                img_url = img["baseimageurl"]
                img_ext = os.path.splitext(img_url)[1] or ".jpg"
                img_path = os.path.join(images_dir, f"{object_id}_additional_{i+1}{img_ext}")
                download_image(img_url, img_path)
    
    # Save metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(art_object, f, indent=2)
    
    print(f"Successfully processed {object_id}")
    return True

def search_and_download(term, images_dir, metadata_dir):
    """Search for artworks matching the term and download them"""
    print(f"Searching for term: {term}")
    
    processed_count = 0
    page = 1
    
    while processed_count < MAX_RESULTS:
        # Search for objects
        search_results = search_harvard(term, page=page)
        
        if not search_results or "records" not in search_results or not search_results["records"]:
            print(f"No more results for '{term}' or error in API response")
            break
        
        objects = search_results["records"]
        if not objects:
            break
        
        print(f"Found {len(objects)} results for '{term}' on page {page}")
        
        # Process each object
        successful = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(
                lambda obj: process_object(obj, images_dir, metadata_dir),
                objects
            ))
            successful = sum(1 for result in results if result)
        
        processed_count += successful
        page += 1
        
        # Check if we've reached the last page or max results
        if len(objects) < 100 or processed_count >= MAX_RESULTS:
            break
        
        # Be nice to the API
        time.sleep(1)
    
    print(f"Completed search for '{term}'. Successfully processed {processed_count} objects.")
    return processed_count

def main():
    """Main function to run the scraper"""
    parse_arguments()
    
    print(f"Harvard Art Museums Cloud Image Scraper")
    print(f"API Key: {API_KEY[:5]}[...]")
    print(f"Search Terms: {', '.join(SEARCH_TERMS)}")
    print(f"Excluded Terms: {', '.join(EXCLUDED_TERMS)}")
    print(f"Max Results per Term: {MAX_RESULTS}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    if API_KEY == "YOUR_API_KEY":
        print("Please provide a valid API key with --key or by editing the script.")
        return
    
    # Setup directories
    images_dir, metadata_dir = setup_directories()
    
    # Process each search term
    total_objects = 0
    for term in SEARCH_TERMS:
        objects_processed = search_and_download(term, images_dir, metadata_dir)
        total_objects += objects_processed
        # Be nice to the API
        time.sleep(2)
