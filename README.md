# Digital Archives as Aesthetic Machines
# A Metacuration Methodology for Recovering Narrative from Digital Cultural Collections

Digital archives increasingly organize visibility through metadata rather than cultural context, flattening meaning into searchable units. This open-source methodology bridges automation and human interpretation to recuperate narrative from systems that fragment meaning.
A hybrid approach that combines algorithmic data collection with subjective curation, using visual clustering to reveal new taxonomies beyond textual metadata.

# Quick Start
# Clone the repository
git clone https://github.com/yourusername/digital-archives-metacuration.git
cd digital-archives-metacuration

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/api_keys.json.template config/api_keys.json
# Add your API keys to config/api_keys.json

# Run a collection
python scripts/collect_images.py --keyword "cloud" --institutions met rijksmuseum --limit 50

# Generate visualization
python scripts/pixplot_integration.py --images-dir data/automated

# Table of Contents
Methodology : Complete theoretical framework and process documentation → Read Methodology
Installation : Setup guides, dependencies, and configuration → Setup Guide 
Usage : Step-by-step tutorials and examples → Usage Guide
Data Sources : API integrations and institutional partnerships → Data Sources 
Tools & Dependencies : Technical specifications and software requirements

# The Four-Phase Methodology
1. Automated Data Collection

API integration with major cultural institutions
Keyword-based searches across multiple databases
Metadata extraction and standardization

2. Subjective Archive Mixing

Manual curation of "cloud-like" images beyond literal representation
Introduction of interpretive criteria and intuitive selection

3.  Visual Clustering

Machine learning analysis using PixPlot
Spatial organization based on visual similarity
Form, color, texture, and composition analysis

4. Editorial Workflow

Transformation of clusters into narrative sequences
Layout planning and publication preparation
Hybrid human-machine curatorial decision making

# Featured Case Study: The Cloud Atlas 
When we search for "cloud" across different institutional databases, we encounter not merely different collections but entirely different epistemological frameworks. This divergence is mediated through APIs (Application Programming Interfaces), which act as structured gateways to institutional data. APIs define what data is accessible, how it can be queried, and in what format it is returned. They are not neutral tools but reflect the priorities, taxonomies, and assumptions of the institutions that design them. For example, the Met's API returns images tagged with controlled vocabularies that emphasize art historical categories: "landscape," "religious imagery," "atmospheric effects." Getty Images prioritizes commercial utility:"weather," "technology," "business concepts." Scientific repositories foreground empirical classification: "cumulus," "stratocumulus," "meteorological phenomena." Each system's parameters encode specific ways of knowing, creating what could be termed "epistemic filters" that shape not just what we see but how we understand what we see.

# Supported Institutions
InstitutionAPI StatusPublic DomainRate LimitMetropolitan Museum✅ No key required✅ Yes80 req/minRijksmuseum🔑 API key required✅ Yes10,000/dayEuropeana🔑 API key required✅ Yes10,000/daySmithsonian🔑 API key required✅ Yes5,000/dayGetty🔑 API key required⚠️ Mixed licensing1,000/day

# Technical Requirements

Python 3.8+
PixPlot for visual clustering
Institutional API access (some require registration)
Basic machine learning libraries (included in requirements.txt)
