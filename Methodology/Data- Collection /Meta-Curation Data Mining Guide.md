# Meta-Curation Data Collection Guide

This guide explains how to use our collection of web scrapers to gather imagery and metadata (in this case cloud, but can be altered) from various digital archives and museum collections. Even if you've never used a command-line tool before, this step-by-step guide will help you get started.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setting Up Your Environment](#setting-up-your-environment)
3. [Getting API Keys](#getting-api-keys)
4. [Running the Scrapers](#running-the-scrapers)
5. [Customizing Your Searches](#customizing-your-searches)
6. [Understanding the Output](#understanding-the-output)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, you'll need:

- **Python 3.7 or higher** installed on your computer
- **Command line/terminal** access
- **Internet connection**
- **API keys** for the collections you want to access (instructions below)
- At least **1GB of free disk space** (more is better as image collections can grow large)

If you don't have Python installed, visit [python.org](https://www.python.org/downloads/) to download and install it for your operating system.

## Setting Up Your Environment

1. **Clone or download this repository**:
   ```bash
   git clone https://github.com/yourusername/meta-curation-atlas.git
   cd meta-curation-atlas/scrapers
   ```

2. **Create a virtual environment** (recommended but optional):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Getting API Keys

Each institution requires its own API key. Here's how to get them:

### Rijksmuseum
1. Visit [Rijksmuseum API](https://www.rijksmuseum.nl/en/api)
2. Create a free account
3. Request an API key through your account dashboard

### Harvard Art Museums
1. Visit [Harvard Art Museums API](https://harvardartmuseums.org/collections/api)
2. Fill out the request form with your information
3. You'll receive an API key via email

### Digital Public Library of America (DPLA)
1. Visit [DPLA API](https://pro.dp.la/developers)
2. Click on "Get a Key"
3. Fill out the form
4. You'll receive an API key via email

### Metropolitan Museum of Art
The Met API doesn't require a key, so you can use that scraper without additional steps.

## Running the Scrapers

Each scraper can be run independently from the command line. Here are examples for each:

### Rijksmuseum Scraper

```bash
python rijksmuseum_scraper.py --key YOUR_API_KEY --terms "cloud,sky,mist" --max 50 --output "rijks_clouds"
```

### Metropolitan Museum of Art Scraper

```bash
python met_scraper.py --terms "cloud,sky,atmosphere" --max 100 --output "met_clouds"
```

### Harvard Art Museums Scraper

```bash
python harvard_scraper.py --key YOUR_API_KEY --terms "cloud,sky" --max 75 --output "harvard_clouds"
```

### DPLA Scraper

```bash
python dpla_scraper.py --key YOUR_API_KEY --terms "cloud,sky,weather" --max 200 --output "dpla_clouds"
```

## Customizing Your Searches

### Using a Configuration File

Create a `config.json` file in the scrapers directory to store your API keys and preferences:

```json
{
  "api_keys": {
    "rijksmuseum": "YOUR_RIJKSMUSEUM_KEY",
    "harvard": "YOUR_HARVARD_KEY",
    "dpla": "YOUR_DPLA_KEY"
  },
  "search_terms": [
    "cloud",
    "sky",
    "weather",
    "mist",
    "fog",
    "atmosphere"
  ],
  "excluded_terms": [
    "saint cloud",
    "saint-cloud",
    "st cloud",
    "st. cloud"
  ],
  "max_results": 100,
  "output_dir": "cloud_data"
}
```

### Customizing Search Terms

You can customize the search terms for more specific clouds:

```bash
python rijksmuseum_scraper.py --key YOUR_KEY --terms "storm,thunder,lightning,cumulus,nimbus" --output "storm_clouds"
```

### Excluding Terms

To exclude certain terms from your results:

```bash
python met_scraper.py --terms "cloud" --exclude "saint-cloud,computing,computer" --output "met_natural_clouds"
```

## Understanding the Output

Each scraper creates a structured output directory containing:

```
output_dir/
├── images/              # Full-resolution images 
├── thumbnails/          # Thumbnail images (when available)
├── metadata/            # JSON files with complete metadata
└── log.txt              # Processing log with timestamps
```

### Metadata Structure

The metadata JSON files contain rich information from each institution, including:

- Title, creator, and date
- Medium and materials
- Dimensions
- Geographic information
- Subjects and classification
- Rights information
- Links to the original source

## Troubleshooting

### API Rate Limits

If you encounter errors about rate limits:

1. Decrease the `--max` parameter
2. Add longer pauses between requests by editing the scraper
3. Run the scrapers at different times

### Connection Errors

If you experience connection issues:

1. Check your internet connection
2. Verify that your API key is valid and entered correctly
3. Some institutions may have scheduled maintenance - try again later

### Image Download Failures

If images fail to download:

1. Check if the institution allows programmatic downloading
2. Some high-resolution images may require special permissions
3. Try running with just a few results to troubleshoot

### Permission Denied Errors

If you get "permission denied" when saving files:

1. Ensure you have write permissions to the output directory
2. Close any open files in the output directory
3. Try a different output location

## Next Steps

After collecting your cloud imagery dataset, you can proceed to:

1. **Data Organization**: Cluster the images based on visual similarity
2. **Data Curation**: Create meaningful sequences and typologies

For more information, see the [Data Organization Guide]
## Need Help?

If you encounter issues not covered here: Contact the project maintainer directly

Happy cloud hunting!
