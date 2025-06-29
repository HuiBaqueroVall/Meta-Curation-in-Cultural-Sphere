#!/usr/bin/env python3
"""
Rijksmuseum Collection Scraper

This scraper interfaces with the Rijksmuseum API to collect cloud-related imagery and metadata.

Usage:
    python rijksmuseum_scraper.py --key YOUR_API_KEY --terms "cloud,sky" --output "rijks_clouds"

Variables to configure:
    - API_KEY: Your Rijksmuseum API key
    - SEARCH_TERMS: List of search terms to query
    - MAX_RESULTS: Maximum number of results to retrieve per term
    - OUTPUT_DIR: Directory to save images and metadata
"""

import os
import json
import time
import argparse
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# Configure variables here
API_KEY = "YOUR_API_KEY"  # Replace with your Rijksmuseum API key
SEARCH_TERMS = ["cloud", "sky", "weather", "mist", "fog", "atmosphere"]
MAX_RESULTS = 100  # Maximum results per search term
OUTPUT_DIR = "rijksmuseum_data"

# API endpoints
API_BASE = "https://www.rijksmuseum.nl/api/en"
SEARCH_ENDPOINT = f"{API_BASE}/collection"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Rijksmuseum Cloud Image Scraper")
    parser.add_argument("--key", type=str, help="Rijksmuseum API key")
    parser.add_argument("--terms", type=str, help="Comma-separated search terms")
    parser.add_argument("--max", type=int, help="Maximum results per term")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args()
    
    # Update global variables if arguments provided
    global API_KEY, SEARCH_TERMS, MAX_RESULTS, OUTPUT_DIR
    if args.key:
        API_KEY = args.key
    if args.terms:
        SEARCH_TERMS = args.terms.split(",")
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
    
    # Thumbnails directory
    thumbnails_dir = os.path.join(OUTPUT_DIR, "thumbnails")
    if not os.path.exists(thumbnails_dir):
        os.makedirs(thumbnails_dir)
        print(f"Created directory: {thumbnails_dir}")
    
    return images_dir, metadata_dir, thumbnails_dir

def search_rijksmuseum(term, page=1, images_only=True):
    """
    Search the Rijksmuseum collection for a specific term
    
    Args:
        term: Search term
        page: Page number for pagination
        images_only: Only return results with images
    
    Returns:
        JSON response from the API
    """
    params = {
        "q": term,
        "key": API_KEY,
        "format": "json",
        "imgonly": "True" if images_only else "False",
        "p": page,
        "ps": 100,  # Page size (max 100)
        "culture": "en"
    }
    
    url = f"{SEARCH_ENDPOINT}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching for '{term}': {e}")
        return None

def get_artwork_details(object_number):
    """
    Get detailed information about a specific artwork
    
    Args:
        object_number: The object number identifier for the artwork
    
    Returns:
        JSON response with detailed artwork information
    """
    params = {
        "key": API_KEY,
        "format": "json",
    }
    
    url = f"{API_BASE}/collection/{object_number}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting details for object {object_number}: {e}")
        return None

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

def process_artwork(artwork, images_dir, metadata_dir, thumbnails_dir):
    """Process a single artwork: download images and save metadata"""
    # Extract basic information
    object_number = artwork.get("objectNumber")
    if not object_number:
        return False
    
    # Create safe filename
    safe_id = object_number.replace("/", "_").replace(" ", "_")
    
    # Check if already downloaded
    metadata_path = os.path.join(metadata_dir, f"{safe_id}.json")
    if os.path.exists(metadata_path):
        print(f"Already processed {object_number}, skipping")
        return True
    
    # Get detailed information
    artwork_details = get_artwork_details(object_number)
    if not artwork_details or "artObject" not in artwork_details:
        return False
    
    art_object = artwork_details["artObject"]
    
    # Extract image URLs
    web_image = art_object.get("webImage", {})
    image_url = web_image.get("url") if web_image else None
    
    # Download main image if available
    if image_url:
        # Determine file extension
        ext = os.path.splitext(image_url)[1]
        if not ext:
            ext = ".jpg"  # Default extension
        
        image_path = os.path.join(images_dir, f"{safe_id}{ext}")
        success = download_image(image_url, image_path)
        if not success:
            print(f"Failed to download main image for {object_number}")
    
    # Download thumbnail if available
    thumbnail_url = art_object.get("headerImage", {}).get("url")
    if thumbnail_url:
        thumb_ext = os.path.splitext(thumbnail_url)[1]
        if not thumb_ext:
            thumb_ext = ".jpg"
        
        thumb_path = os.path.join(thumbnails_dir, f"{safe_id}{thumb_ext}")
        download_image(thumbnail_url, thumb_path)
    
    # Save metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(art_object, f, indent=2)
    
    print(f"Successfully processed {object_number}")
    return True

def search_and_download(term, images_dir, metadata_dir, thumbnails_dir):
    """Search for artworks matching the term and download them"""
    print(f"Searching for term: {term}")
    
    total_processed = 0
    page = 1
    
    while total_processed < MAX_RESULTS:
        search_results = search_rijksmuseum(term, page=page)
        
        if not search_results or "artObjects" not in search_results:
            print(f"No more results for '{term}' or error in API response")
            break
        
        art_objects = search_results["artObjects"]
        if not art_objects:
            print(f"No more results for '{term}'")
            break
        
        print(f"Found {len(art_objects)} results for '{term}' on page {page}")
        
        # Process each artwork
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(
                lambda artwork: process_artwork(artwork, images_dir, metadata_dir, thumbnails_dir),
                art_objects
            )
        
        total_processed += len(art_objects)
        page += 1
        
        # Check if we've reached the maximum results or the last page
        if total_processed >= MAX_RESULTS or len(art_objects) < 100:
            break
        
        # Be nice to the API
        time.sleep(1)
    
    print(f"Completed search for '{term}'. Processed approximately {total_processed} artworks.")
    return total_processed

def main():
    """Main function to run the scraper"""
    parse_arguments()
    
    print(f"Rijksmuseum Cloud Image Scraper")
    print(f"API Key: {API_KEY[:5]}[...]")
    print(f"Search Terms: {', '.join(SEARCH_TERMS)}")
    print(f"Max Results per Term: {MAX_RESULTS}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    if API_KEY == "YOUR_API_KEY":
        print("Please provide a valid API key with --key or by editing the script.")
        return
    
    # Setup directories
    images_dir, metadata_dir, thumbnails_dir = setup_directories()
    
    # Process each search term
    total_artworks = 0
    for term in SEARCH_TERMS:
        artworks_processed = search_and_download(term, images_dir, metadata_dir, thumbnails_dir)
        total_artworks += artworks_processed
    
    print(f"Scraping complete. Total artworks processed: {total_artworks}")

if __name__ == "__main__":
    main()
