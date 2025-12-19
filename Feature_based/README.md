# Rug Image Feature Matcher

A Streamlit application that uses LoFTR (Loosely-coupled Feature Transform) to match rug images and find the most similar rugs from a datasource collection.

## Features

- Upload a rug image to find similar matches
- Uses state-of-the-art LoFTR feature matching
- RANSAC-based outlier filtering for robust matching
- Visualizes feature matches between images
- Ranks results by number of inlier matches
- Displays top matches with detailed statistics

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:

```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown (typically `http://localhost:8501`)

3. Upload a rug image using the file uploader

4. Wait for the matching process to complete

5. View the ranked results showing the most similar rugs from the datasources folder

## How It Works

1. **Image Preprocessing**: Both the uploaded image and datasource images are resized to 512x512 pixels
2. **Feature Matching**: Uses LoFTR (pretrained "outdoor" model) to find correspondences between images
3. **Outlier Filtering**: RANSAC (Random Sample Consensus) is used to filter out incorrect matches
4. **Ranking**: Images are ranked by the number of inlier matches (geometrically consistent matches)
5. **Visualization**: Top matches are displayed with visual feature correspondences

## Project Structure

```
Image2ImageFeatureMatching/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── datasources/          # Folder containing rug images to match against
    ├── RCT_AKWL-3143-0001.jpg
    ├── RCT_EA-3009(CS-03)-0001.jpg
    └── RCT_EA-3108(CS-02)-0002.jpg
```

## Notes

- The LoFTR model is cached to avoid reloading on each run
- Images are automatically converted to grayscale for matching (LoFTR requirement)
- The matching process may take some time depending on the number of images in the datasources folder
- Results are ranked by the number of inlier matches, which provides a more reliable similarity measure than total matches

