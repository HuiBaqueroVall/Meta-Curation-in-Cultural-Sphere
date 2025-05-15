#!/usr/bin/env python3
"""
Metropolitan Museum of Art Collection Scraper

This scraper interfaces with the Metropolitan Museum of Art API to collect cloud-related imagery and metadata.

Usage:
    python met_scraper.py --terms "cloud,sky" --output "met_clouds" --max 200

Variables to configure:
    - SEARCH_TERMS: List of search terms to query
    - MAX_RESULTS: Maximum number of results to retrieve per term
    - OUTPUT_DIR: Directory to save images and metadata
    - EXCLUDED_TERMS: Terms to exclude from search results
"""

import os
import json
import time
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure variables here
SEARCH_TERMS = ["cloud", "sky", "weather", "mist", "fog", "atmosphere"]
EXCLUDED_TERMS = ["saint cloud", "saint-cloud", "st cloud", "st. cloud"]
MAX_RESULTS = 100  # Maximum results per search term
OUTPUT_DIR = "met_data"

# API endpoints
API_BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
SEARCH_ENDPOINT = f"{API_BASE}/search"
OBJECT_ENDPOINT = f"{API_BASE}/objects"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Metropolitan Museum of Art Cloud Image Scraper")
    parser.add_argument("--terms", type=str, help="Comma-separated search terms")
    parser.add_argument("--exclude", type=str, help="Comma-separated terms to exclude")
    parser.add_argument("--max", type=int, help="Maximum results per term")
    parser.add_argument("--output", type=str, help="Output directory")
    args = parser.parse_args()
    
    # Update global variables if arguments provided
    global SEARCH_TERMS, EXCLUDED_TERMS, MAX_RESULTS, OUTPUT_DIR
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

def search_met(term, has_images=True):
    """
    Search the Met collection for a specific term
    
    Args:
        term: Search term
        has_images: Only return results with images
    
    Returns:
        List of object IDs matching the search
    """
    params = {
        "q": term,
        "hasImages": "true" if has_images else "false"
    }
    
    try:
        response = requests.get(SEARCH_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "objectIDs" in data and data["objectIDs"]:
            print(f"Found {len(data['objectIDs'])} results for '{term}'")
            return data["objectIDs"]
        else:
            print(f"No results found for '{term}'")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error searching for '{term}': {e}")
        return []

def get_object_details(object_id):
    """
    Get detailed information about a specific artwork
    
    Args:
        object_id: The object ID for the artwork
    
    Returns:
        JSON response with detailed artwork information
    """
    url = f"{OBJECT_ENDPOINT}/{object_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting details for object {object_id}: {e}")
        return None

def should_exclude(metadata):
    """Check if an object should be excluded based on excluded terms"""
    if not metadata:
        return True
    
    # Convert metadata to string for simple term matching
    metadata_str = json.dumps(metadata).lower()
    
    for term in EXCLUDED_TERMS:
        if term.lower() in metadata_str:
            print(f"Excluding object {metadata.get('objectID')} because it contains '{term}'")
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

def process_object(object_id, images_dir, metadata_dir):
    """Process a single artwork: download images and save metadata"""
    # Check if already downloaded
    metadata_path = os.path.join(metadata_dir, f"{object_id}.json")
    if os.path.exists(metadata_path):
        print(f"Already processed {object_id}, skipping")
        return True
    
    # Get detailed information
    object_details = get_object_details(object_id)
    if not object_details:
        return False
    
    # Check if object contains excluded terms
    if should_exclude(object_details):
        return False
    
    # Extract image URLs
    primary_image = object_details.get("primaryImage")
    additional_images = object_details.get("additionalImages", [])
    
    # Download primary image if available
    if primary_image:
        # Determine file extension
        ext = os.path.splitext(primary_image)[1]
        if not ext:
            ext = ".jpg"  # Default extension
        
        image_path = os.path.join(images_dir, f"{object_id}{ext}")
        success = download_image(primary_image, image_path)
        if not success:
            print(f"Failed to download primary image for {object_id}")
    
    # Download additional images if available (optional)
    for i, img_url in enumerate(additional_images[:5]):  # Limit to first 5 additional images
        if img_url:
            # Determine file extension
            ext = os.path.splitext(img_url)[1]
            if not ext:
                ext = ".jpg"
            
            img_path = os.path.join(images_dir, f"{object_id}_additional_{i+1}{ext}")
            download_image(img_url, img_path)
    
    # Save metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(object_details, f, indent=2)
    
    print(f"Successfully processed {object_id}")
    return True

def search_and_download(term, images_dir, metadata_dir):
    """Search for artworks matching the term and download them"""
    print(f"Searching for term: {term}")
    
    # Search for objects
    object_ids = search_met(term)
    
    # Limit results
    object_ids = object_ids[:MAX_RESULTS]
    
    if not object_ids:
        return 0
    
    print(f"Processing {len(object_ids)} objects for term '{term}'")
    
    # Process each object
    successful = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(
            lambda obj_id: process_object(obj_id, images_dir, metadata_dir),
            object_ids
        ))
        successful = sum(1 for result in results if result)
    
    print(f"Completed search for '{term}'. Successfully processed {successful} objects.")
    return successful

def main():
    """Main function to run the scraper"""
    parse_arguments()
    
    print(f"Metropolitan Museum of Art Cloud Image Scraper")
    print(f"Search Terms: {', '.join(SEARCH_TERMS)}")
    print(f"Excluded Terms: {', '.join(EXCLUDED_TERMS)}")
    print(f"Max Results per Term: {MAX_RESULTS}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    # Setup directories
    images_dir, metadata_dir = setup_directories()
    
    # Process each search term
    total_objects = 0
    for term in SEARCH_TERMS:
        objects_processed = search_and_download(term, images_dir, metadata_dir)
        total_objects += objects_processed
        # Be nice to the API
        time.sleep(1)
    
    print(f"Scraping complete. Total objects processed: {total_objects}")

if __name__ == "__main__":
    main()