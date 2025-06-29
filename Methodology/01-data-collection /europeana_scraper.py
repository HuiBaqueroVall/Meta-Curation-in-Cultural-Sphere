#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Europeana Cloud Image Scraper
----------------------------
This script searches for "cloud" images on Europeana and downloads them with metadata,
excluding images related to "saint cloud" or "saint-cloud".
"""

import os
import json
import time
import requests
from urllib.parse import urljoin
from pathlib import Path
import argparse


class EuropeanaCloudScraper:
    """Scraper for downloading cloud images from Europeana."""
    
    def __init__(self, api_key, output_dir="europeana_cloud_images"):
        """Initialize the scraper with API key and output directory."""
        self.api_key = api_key
        self.base_url = "https://api.europeana.eu/record/v2/search.json"
        self.search_term = "cloud"
        self.excluded_terms = ["saint cloud", "saint-cloud", "st cloud", "st. cloud"]
        self.output_dir = Path(output_dir)
        self.metadata_file = self.output_dir / "metadata.json"
        self.rows_per_page = 100  # Maximum allowed by Europeana API
        self.max_images = 1000  # Limit the total number of images to download
        self.metadata = []
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True, parents=True)
        print(f"Output directory: {self.output_dir}")
    
    def should_exclude_item(self, item):
        """Check if an item contains any of the excluded terms."""
        text_fields = [
            item.get('title', [''])[0] if item.get('title') else '',
            item.get('dcDescription', [''])[0] if item.get('dcDescription') else '',
            item.get('dcSubject', [''])[0] if item.get('dcSubject') else '',
            item.get('dcCreator', [''])[0] if item.get('dcCreator') else ''
        ]
        
        combined_text = ' '.join(text_fields).lower()
        return any(term.lower() in combined_text for term in self.excluded_terms)
    
    def search_europeana(self, page=1):
        """Search Europeana API for cloud images."""
        params = {
            'query': self.search_term,
            'media': 'true',
            'thumbnail': 'true',
            'reusability': 'open',
            'rows': self.rows_per_page,
            'start': ((page - 1) * self.rows_per_page) + 1,
            'wskey': self.api_key
        }
        
        print(f"Fetching page {page}...")
        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        return response.json()
    
    async def download_image(self, image_url, item_id, filename=None):
        """Download an image from the given URL."""
        if not image_url:
            print(f"No image URL provided for item {item_id}")
            return None
        
        try:
            if not filename:
                # Generate a filename from the item ID by removing any path traversal characters
                safe_id = item_id.replace('/', '_').replace('\\', '_')
                filename = f"{safe_id}.jpg"
            
            filepath = self.output_dir / filename
            
            # Download the image
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
                return filename
            else:
                print(f"Failed to download image {image_url}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")
            return None
    
    def save_metadata(self):
        """Save metadata to a JSON file."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        print(f"Metadata saved to {self.metadata_file}")
    
    def run(self):
        """Run the scraper to download cloud images from Europeana."""
        print(f"Starting Europeana Cloud Image Scraper")
        print(f"Searching for: {self.search_term}")
        print(f"Excluding: {', '.join(self.excluded_terms)}")
        
        downloaded_count = 0
        page = 1
        
        while downloaded_count < self.max_images:
            data = self.search_europeana(page)
            
            if not data or 'items' not in data or not data['items']:
                print("No more results or API error")
                break
            
            total_results = data.get('totalResults', 0)
            print(f"Found {total_results} total results")
            
            items = data['items']
            print(f"Processing {len(items)} items from page {page}")
            
            for item in items:
                if downloaded_count >= self.max_images:
                    break
                
                if self.should_exclude_item(item):
                    print(f"Skipping item with excluded terms: {item.get('title', ['Unknown'])[0]}")
                    continue
                
                item_id = item.get('id', '')
                title = item.get('title', ['Untitled'])[0]
                image_url = item.get('edmPreview', [''])[0]
                
                if not image_url:
                    print(f"No image URL for item: {title}")
                    continue
                
                # Download image
                safe_id = item_id.replace('/', '_').replace('\\', '_')
                filename = f"{safe_id}.jpg"
                
                try:
                    # Use requests instead of async for simplicity
                    response = requests.get(image_url, stream=True)
                    if response.status_code == 200:
                        filepath = self.output_dir / filename
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        
                        # Store metadata
                        item_metadata = {
                            'id': item_id,
                            'title': title,
                            'url': image_url,
                            'filename': filename,
                            'provider': item.get('dataProvider', ['Unknown'])[0],
                            'source': item.get('guid', ''),
                            'rights': item.get('rights', []),
                            'description': item.get('dcDescription', []),
                            'creator': item.get('dcCreator', []),
                            'date': item.get('year', [])
                        }
                        
                        self.metadata.append(item_metadata)
                        downloaded_count += 1
                        
                        print(f"Downloaded {downloaded_count}/{self.max_images}: {title}")
                        
                        # Respect rate limits
                        time.sleep(0.5)
                    else:
                        print(f"Failed to download image for {title}: {response.status_code}")
                except Exception as e:
                    print(f"Error downloading image for {title}: {e}")
            
            # Save metadata periodically
            if downloaded_count % 20 == 0:
                self.save_metadata()
            
            # Check if there are more pages
            if len(items) < self.rows_per_page:
                print("Reached last page of results")
                break
            
            page += 1
        
        # Final save of metadata
        self.save_metadata()
        print(f"Download complete. Downloaded {downloaded_count} images.")


def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description='Download cloud images from Europeana')
    parser.add_argument('--api-key', required=True, help='Europeana API key')
    parser.add_argument('--output-dir', default='europeana_cloud_images', 
                        help='Directory to save downloaded images')
    parser.add_argument('--max-images', type=int, default=1000,
                        help='Maximum number of images to download')
    
    args = parser.parse_args()
    
    scraper = EuropeanaCloudScraper(args.api_key, args.output_dir)
    scraper.max_images = args.max_images
    scraper.run()


if __name__ == "__main__":
    main()
