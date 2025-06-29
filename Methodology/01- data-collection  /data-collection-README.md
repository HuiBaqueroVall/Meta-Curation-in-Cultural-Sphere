# Step 1: Data Collection - Automating Access via APIs and Web Scraping

This first phase integrates automated data collection using **APIs** and **web scraping techniques**, aiming to accumulate a large corpus of image files available under open-access licenses. The scraper automates keyword-based searches and downloads content according to a predefined term: in this case, **"cloud."**

## Overview

The primary data sources for this project include a variety of museums, art institutions, and catalog platforms, each providing access to collections through APIs. The institutions selected are the ones that currently within the cultural sphere have the most granularity offering digital access to both public domain materials and metadata.

**Granularity in data** refers to the level of detail or precision of the data. For example, data that has a high level of granularity would have a large number of individual pieces of information.

## Data Collection Targets

The scraper collects:
- **Thumbnail and full-resolution images** (where available)
- **Metadata**: title, creator, date, medium, institutional source
- **API response data**: tags, subject headings, collection name, object ID and URL links to original image entries for traceability

## Supported Data Sources

### Museum APIs
- **Metropolitan Museum of Art** - Open Access API
- **Smithsonian Institution** - Multiple collection APIs
- **Digital Public Library of America** - Multiple collection APIs
- **Europeana** - European cultural heritage
- **Rijksmuseum** - Dutch national collection
- **Chicago Art Institute** - Open Access API
- **Cooper Hewitt** - Open Access API

### Configuration Files

#### `data_sources/api_endpoints.json`
Contains all API endpoint configurations, rate limits, and authentication requirements.

#### `config/api_config.yaml`
Store your API keys and personal configurations here (not tracked in git).

## File Structure

```
01-data-collection/
├── scrapers/
│   ├── base_scraper.py          # Base class for all scrapers
│   ├── museum_apis/             # API-specific scrapers
│   └── web_scrapers/            # General web scraping tools
├── data_sources/
│   ├── api_endpoints.json       # API configurations
│   └── institution_list.md      # Detailed source documentation
├── output/
│   ├── raw_images/              # Downloaded images
│   ├── metadata/                # JSON metadata files
│   └── logs/                    # Collection logs and reports
└── scripts/
    ├── run_collection.py        # Main collection script
    ├── validate_downloads.py    # Quality control
    └── generate_metadata_report.py
```

## Usage

### 1. Setup Configuration
```bash
# Copy example config
cp ../config/api_config.yaml.example ../config/api_config.yaml

# Edit with your API keys
nano ../config/api_config.yaml
```

### 2. Run Collection
```bash
# Collect from all sources
python scripts/run_collection.py --keyword "cloud" --max-items 1000

# Collect from specific source
python scripts/run_collection.py --source "met_museum" --keyword "cloud"

# Resume interrupted collection
python scripts/run_collection.py --resume --log-file output/logs/collection_2025.log
```

### 3. Validate Results
```bash
# Check download integrity
python scripts/validate_downloads.py

# Generate collection report
python scripts/generate_metadata_report.py
```

## Output Format

### Image Files
- Stored in `output/raw_images/[source]/[object_id].[extension]`
- Original filename preserved when possible
- Multiple resolutions saved when available

### Metadata Files
- JSON format: `output/metadata/[source]/[object_id].json`
- Standardized schema across all sources
- Includes original API response data

### Example Metadata Structure
```json
{
  "object_id": "12345",
  "source": "met_museum",
  "title": "Cloud Study",
  "creator": "John Constable",
  "date": "1821",
  "medium": "Oil on paper",
  "tags": ["landscape", "sky", "cloud", "nature"],
  "collection": "European Paintings",
  "api_url": "https://collectionapi.metmuseum.org/public/collection/v1/objects/12345",
  "image_urls": {
    "thumbnail": "https://images.metmuseum.org/CRDImages/ep/web-large/12345.jpg",
    "primary": "https://images.metmuseum.org/CRDImages/ep/original/12345.jpg"
  },
  "downloaded_at": "2025-06-29T10:30:00Z",
  "file_paths": {
    "thumbnail": "output/raw_images/met_museum/12345_thumb.jpg",
    "primary": "output/raw_images/met_museum/12345.jpg"
  }
}
```

## Rate Limiting and Ethics

- Respects API rate limits (typically 1-5 requests/second)
- Only downloads open-access/public domain materials
- Includes proper attribution and source links
- Logs all requests for transparency
- Implements retry logic for failed requests

## Troubleshooting

### Common Issues
1. **API Key Issues** - Check configuration file format
2. **Rate Limiting** - Adjust delay settings in scraper config
3. **Network Timeouts** - Enable resume functionality
4. **Storage Space** - Monitor disk usage, implement cleanup scripts

### Log Files
All operations are logged in `output/logs/` with timestamps and error details.

## Next Steps

After collection completion:
1. Review collection statistics in generated reports
2. Proceed to [Step 2: Mixing the Archive]
3. Begin manual curation and subjective selection process


Happy cloud hunting!
