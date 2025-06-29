import requests
import os
import json
import time
import random
from datetime import datetime

class CooperHewittScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.collection.cooperhewitt.org/rest/"
        self.output_dir = "cooper_hewitt_clouds"
        
        # Create output directories if they don't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(f"{self.output_dir}/images"):
            os.makedirs(f"{self.output_dir}/images")
        if not os.path.exists(f"{self.output_dir}/metadata"):
            os.makedirs(f"{self.output_dir}/metadata")
            
    def search_objects(self, query, page=1, per_page=100):
        """Search for objects based on query - with broader parameters"""
        params = {
            "method": "cooperhewitt.search.objects",
            "access_token": self.api_key,
            "query": query,
            # Try different parameters to get more results
            "page": page,
            "per_page": per_page,
            # Adding these parameters to get more comprehensive results
            "has_images": "yes",
            "sort": "relevance"
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            print(f"Found {total} total results for query '{query}'")
            return data
        else:
            print(f"Error searching objects: {response.status_code}")
            print(response.text)
            return None
    
    def try_alternate_search(self, query, page=1, per_page=100):
        """Try alternate search methods through the API"""
        methods = [
            # Using facet search might give different results
            {
                "method": "cooperhewitt.search.objects",
                "access_token": self.api_key,
                "query": query,
                "page": page,
                "per_page": per_page
            },
            # Try full text search for different results
            {
                "method": "cooperhewitt.search.collection",
                "access_token": self.api_key,
                "query": query,
                "page": page,
                "per_page": per_page
            },
            # Trying a different method
            {
                "method": "cooperhewitt.exhibitions.getObjects",
                "access_token": self.api_key,
                "query": query,
                "page": page,
                "per_page": per_page
            }
        ]
        
        for params in methods:
            print(f"Trying alternate search method: {params['method']}")
            try:
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "objects" in data and len(data["objects"]) > 0:
                        print(f"Found {len(data['objects'])} objects with method {params['method']}")
                        return data
            except Exception as e:
                print(f"Error with alternate search method: {e}")
                continue
        
        return None
    
    def get_object_details(self, object_id):
        """Get detailed information about a specific object"""
        params = {
            "method": "cooperhewitt.objects.getInfo",
            "access_token": self.api_key,
            "object_id": object_id
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting object details: {response.status_code}")
            return None
    
    def try_get_images(self, object_id):
        """Try multiple methods to get images for an object"""
        methods = [
            # Standard method
            {
                "method": "cooperhewitt.objects.getImages",
                "access_token": self.api_key,
                "object_id": object_id
            },
            # Try with different parameters
            {
                "method": "cooperhewitt.objects.getMedia",
                "access_token": self.api_key,
                "object_id": object_id
            }
        ]
        
        for params in methods:
            try:
                print(f"Trying to get images with method: {params['method']}")
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # Check for images or media
                    if "media" in data and data["media"]:
                        return data["media"]
                    if "images" in data and data["images"]:
                        return data["images"]
            except Exception as e:
                print(f"Error getting images: {e}")
                continue
        
        return None
    
    def construct_object_url(self, object_id):
        """Construct URL for object on Cooper Hewitt website"""
        # Use server-side API to construct URLs for direct linking to objects
        params = {
            "method": "cooperhewitt.objects.getPermalink",
            "access_token": self.api_key,
            "object_id": object_id
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "url" in data:
                    return data["url"]
        except:
            pass
        
        # Fallback to constructed URL
        return f"https://collection.cooperhewitt.org/objects/{object_id}/"
    
    def get_image_from_object(self, obj_data):
        """Try to extract image URL from object data"""
        # Try different patterns where images might be stored
        if "images" in obj_data and obj_data["images"]:
            images = obj_data["images"]
            if isinstance(images, list) and images:
                for img in images:
                    # Try different sizes in order of preference
                    for size in ["b", "z", "n", "d", "l", "o"]:
                        if size in img and "url" in img[size]:
                            return img[size]["url"]
        
        # Try looking for direct image URL
        if "image" in obj_data and "url" in obj_data["image"]:
            return obj_data["image"]["url"]
        
        return None
    
    def get_direct_image_links(self, object_id):
        """Construct direct image links for known patterns"""
        # Try different direct URL patterns
        urls = [
            f"https://images.collection.cooperhewitt.org/images/{object_id}_large.jpg",
            f"https://collection.cooperhewitt.org/iiif/{object_id}/full/full/0/default.jpg",
            f"https://images.collection.cooperhewitt.org/{object_id}_b.jpg"
        ]
        
        for url in urls:
            try:
                print(f"Trying direct image URL: {url}")
                response = requests.head(url)
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if content_type.startswith('image/'):
                        print(f"Found valid image URL: {url}")
                        return url
            except:
                continue
        
        return None
    
    def download_image(self, url, filename):
        """Download image from URL"""
        try:
            print(f"Attempting to download from: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, stream=True)
            
            # Check if it's actually an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"URL is not an image. Content-Type: {content_type}")
                return False
                
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                print(f"Error downloading image {filename}: {response.status_code}")
                return False
        except Exception as e:
            print(f"Exception while downloading {filename}: {e}")
            return False
            
    def save_metadata(self, object_data, filename):
        """Save metadata to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(object_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Exception while saving metadata {filename}: {e}")
            return False
            
    def scrape(self, query="cloud", max_pages=10):
        """Main scraping function"""
        print(f"Starting scrape for query: '{query}'")
        
        total_downloaded = 0
        current_page = 1
        
        while current_page <= max_pages:
            print(f"Processing page {current_page}...")
            
            # Try regular search first
            search_results = self.search_objects(query, page=current_page)
            
            if not search_results or "objects" not in search_results or len(search_results["objects"]) == 0:
                print("No results from standard search, trying alternate methods...")
                search_results = self.try_alternate_search(query, page=current_page)
                
            if not search_results or "objects" not in search_results:
                print("No more results or error in API response")
                break
                
            if len(search_results["objects"]) == 0:
                print("No more objects found")
                break
                
            for i, obj in enumerate(search_results["objects"]):
                object_id = obj["id"]
                print(f"Processing object {i+1}/{len(search_results['objects'])}, ID: {object_id}")
                
                # Get detailed object info
                object_details = self.get_object_details(object_id)
                
                # Save the object data
                obj_data = object_details["object"] if object_details and "object" in object_details else obj
                
                # Try multiple methods to get an image URL
                image_url = None
                
                # Method 1: Try to extract from object data
                if object_details and "object" in object_details:
                    image_url = self.get_image_from_object(object_details["object"])
                
                # Method 2: Try specific API methods for images
                if not image_url:
                    images_data = self.try_get_images(object_id)
                    if images_data and isinstance(images_data, list) and images_data:
                        for img in images_data:
                            for size in ["b", "z", "n", "d", "l", "o"]:
                                if size in img and "url" in img[size]:
                                    image_url = img[size]["url"]
                                    break
                            if image_url:
                                break
                
                # Method 3: Try direct URL patterns
                if not image_url:
                    image_url = self.get_direct_image_links(object_id)
                
                if not image_url:
                    print(f"No image URL found for object ID: {object_id}")
                    
                    # Save metadata even if no image
                    title = obj.get("title", "untitled")
                    safe_title = "".join([c if c.isalnum() else "_" for c in title])
                    safe_title = safe_title[:50]  # Limit length
                    metadata_filename = f"{self.output_dir}/metadata/{object_id}_{safe_title}_noimage.json"
                    self.save_metadata(obj_data, metadata_filename)
                    
                    continue
                    
                # Create sanitized filename from object title
                title = obj.get("title", "untitled")
                safe_title = "".join([c if c.isalnum() else "_" for c in title])
                safe_title = safe_title[:50]  # Limit length
                
                # File paths
                image_filename = f"{self.output_dir}/images/{object_id}_{safe_title}.jpg"
                metadata_filename = f"{self.output_dir}/metadata/{object_id}_{safe_title}.json"
                
                # Download image
                if self.download_image(image_url, image_filename):
                    print(f"Downloaded image: {image_filename}")
                    
                    # Save metadata
                    if self.save_metadata(obj_data, metadata_filename):
                        print(f"Saved metadata: {metadata_filename}")
                        total_downloaded += 1
                
                # Avoid hitting rate limits with randomized delay
                time.sleep(1 + random.random())
                
            current_page += 1
            
        print(f"Scraping completed. Downloaded {total_downloaded} images with metadata.")
        return total_downloaded

if __name__ == "__main__":
    # You'll need to get an API key from Cooper Hewitt
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    
    # Create scraper instance
    scraper = CooperHewittScraper(API_KEY)
    
    # Run the scraper with multiple search strategies
    scraper.scrape(query="cloud", max_pages=10)
    scraper = HarvardArtScraper(API_KEY)
    
    # Run the scraper
    scraper.scrape(query="cloud", max_pages=10)
