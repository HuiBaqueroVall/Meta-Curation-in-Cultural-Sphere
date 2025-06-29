# Step 3: Visual Clustering - Organizing Images Beyond Tags

The next stage shifts from textual tagging to **visual similarity**. Instead of relying on semantic metadata, images are clustered using a software tool called **PixPlot**—an open-source, WebGL-powered visualization engine developed by **Douglas Duhaime at the Yale Digital Humanities Lab**. PixPlot uses machine learning to analyze and position images within a two-dimensional space based on features such as **form, color, texture,** and **composition**.

## Overview

Once the combined folder (including both automated and manually selected images) is uploaded, PixPlot visualizes the archive as a **spatial map** of visual clusters. This spatial overview makes it easier to observe recurring forms and patterns, revealing new thematic groupings. After this automated clustering, the images are **manually recurated**, emphasizing how visual language can shape taxonomies that transcend textual classification systems.

## PixPlot Integration

### What is PixPlot?
PixPlot is a visualization tool that:
- Uses deep learning models to analyze visual features
- Creates 2D spatial layouts based on visual similarity
- Generates interactive web-based visualizations
- Allows exploration of large image collections
- Reveals unexpected visual connections

### Technical Requirements
- Python 3.6+
- TensorFlow/Keras for feature extraction
- WebGL-compatible browser for visualization
- Sufficient RAM for processing large collections (8GB+ recommended)

## File Structure

```
03-visual-clustering/
├── pixplot_setup/
│   ├── installation_guide.md    # Step-by-step setup
│   ├── config_files/           # PixPlot configurations
│   └── custom_settings.json    # Project-specific settings
├── clustering_results/
│   ├── cluster_maps/           # Generated visualizations
│   ├── similarity_matrices/    # Feature analysis data
│   └── visual_analysis/        # Cluster interpretation
├── recuration_tools/
│   ├── cluster_reviewer.py     # Manual cluster adjustment
│   └── manual_adjustment_tracker.py # Document changes
└── scripts/
    ├── run_pixplot.py          # Execute clustering
    ├── export_clusters.py      # Extract cluster data
    └── analyze_clusters.py     # Generate reports
```

## Installation and Setup

### 1. Install PixPlot
```bash
# Clone PixPlot repository
git clone https://github.com/YaleDHLab/pix-plot
cd pix-plot

# Install dependencies
pip install -r requirements.txt

# Install additional requirements for this project
pip install matplotlib seaborn pandas
```

### 2. Prepare Image Collection
```bash
# Copy combined collection from Step 2
cp -r ../02-mixing-archive/shared_folder/merged_collection/ input_images/

# Ensure consistent image format and size
python scripts/prepare_images.py --input input_images/ --output processed_images/
```

### 3. Configure PixPlot Settings
Edit `pixplot_setup/custom_settings.json`:
```json
{
  "images_dir": "processed_images/",
  "output_dir": "clustering_results/cluster_maps/",
  "model": "vgg16",
  "max_images": 5000,
  "plot_width": 2400,
  "plot_height": 2400,
  "point_size": 4,
  "image_size": 64,
  "n_neighbors": 6,
  "min_distance": 0.1,
  "metric": "cosine"
}
```

## Running the Clustering Process

### 1. Generate Feature Vectors
```bash
# Extract visual features from all images
python scripts/run_pixplot.py --stage features --config pixplot_setup/custom_settings.json
```

### 2. Create Spatial Layout
```bash
# Generate 2D clustering layout
python scripts/run_pixplot.py --stage layout --config pixplot_setup/custom_settings.json
```

### 3. Build Visualization
```bash
# Create interactive web visualization
python scripts/run_pixplot.py --stage visualization --config pixplot_setup/custom_settings.json
```

## Analyzing Cluster Results

### Visual Cluster Exploration
1. **Open the generated HTML visualization**
2. **Navigate the spatial map** to identify cluster regions
3. **Zoom into specific areas** to examine groupings
4. **Take screenshots** of interesting cluster formations
5. **Document recurring visual patterns**

### Cluster Interpretation Guidelines

#### What to Look For:
- **Color-based clusters**: Images grouped by dominant colors
- **Texture clusters**: Similar surface qualities (smooth, rough, soft)
- **Compositional clusters**: Similar layouts or arrangements
- **Form clusters**: Recurring shapes or structures
- **Style clusters**: Similar artistic techniques or periods

#### Documentation Process:
For each significant cluster, record:
```markdown
## Cluster Analysis: Region A-1
- **Location**: Upper left quadrant of visualization
- **Dominant Features**: Blue-gray tones, horizontal compositions
- **Visual Characteristics**: Atmospheric, minimal contrast
- **Example Images**: [list 3-5 representative images]
- **Interpretation**: Sky studies and seascapes grouped by tonal similarity
- **Unexpected Connections**: Modern abstract paintings clustered with 19th-century cloud studies
```

## Manual Recuration Process

### 1. Identify Problematic Groupings
- Images that seem misplaced in their clusters
- Clusters that are too large or heterogeneous
- Interesting outliers that deserve their own groups

### 2. Manual Adjustment Tools
```bash
# Review cluster assignments
python recuration_tools/cluster_reviewer.py --visualization clustering_results/cluster_maps/

# Create custom groupings
python recuration_tools/manual_adjustment_tracker.py --create-group "atmospheric-studies"
```

### 3. Document Recuration Decisions
Track all manual adjustments:
- Which images were moved and why
- New clusters created through manual intervention
- Rationale for overriding algorithmic groupings
- Impact on overall collection organization

## Advanced Analysis

### Statistical Overview
```bash
# Generate cluster statistics
python scripts/analyze_clusters.py --stats

# Output includes:
# - Number of clusters identified
# - Cluster size distribution
# - Feature similarity scores
# - Outlier detection
```

### Cross-Reference with Metadata
Compare visual clusters with original metadata:
- Do visually similar images share textual tags?
- Are there chronological patterns in visual clusters?
- How do different institutional sources distribute across clusters?

### Export Cluster Data
```bash
# Export cluster assignments for Step 4
python scripts/export_clusters.py --format excel --output ../04-editorial-workflow/cluster_data.xlsx

# Create cluster-based folder structure
python scripts/export_clusters.py --format folders --output clustered_images/
```

## Quality Assessment

### Validation Criteria
1. **Visual Coherence**: Do cluster members share meaningful visual characteristics?
2. **Appropriate Granularity**: Are clusters neither too broad nor too specific?
3. **Meaningful Outliers**: Do isolated images offer interesting contrasts?
4. **Narrative Potential**: Can clusters tell visual stories?

### Iteration Process
- Run multiple clustering attempts with different parameters
- Compare results from different machine learning models
- Incorporate manual feedback into algorithmic parameters
- Balance automation with human interpretation

## Integration with Publication Goals

### Preparing for Editorial Layout
The clustering results inform the editorial workflow by:
- Providing visual groupings for page layouts
- Suggesting narrative sequences through cluster relationships
- Identifying key representative images for each theme
- Creating bridges between disparate visual concepts

### Documentation for Step 4
Generate comprehensive cluster documentation:
- Visual cluster maps with annotations
- Statistical analysis of groupings
- List of representative images per cluster
- Rationale for manual adjustments
- Recommendations for editorial organization

## Reflection on Process

### Key Questions
- How do machine-generated clusters compare to your subjective groupings?
- What unexpected visual connections did the algorithm reveal?
- Where did human interpretation add value to computational analysis?
- How might different clustering parameters change the narrative?

### Theoretical Implications
This step demonstrates:
- The power of visual similarity over textual categorization
- How algorithms can reveal hidden patterns in cultural collections
- The necessity of human interpretation in computational processes
- The hybrid nature of contemporary digital humanities methods

## Next Steps

After completing visual clustering:
1. Review and finalize cluster organization
2. Proceed to [Step 4: Editorial Workflow](../04-editorial-workflow/)
3. Begin translation from visual clusters to publication layout

---

*"This spatial overview makes it easier to observe recurring forms and patterns, revealing new thematic groupings that transcend textual classification systems."*
