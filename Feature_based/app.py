import cv2
import kornia as K
import kornia.feature as KF
import matplotlib.pyplot as plt
import numpy as np
import torch
import streamlit as st
from pathlib import Path
from PIL import Image
import io
from kornia.feature import LoFTR
from kornia_moons.viz import draw_LAF_matches

# Set page config
st.set_page_config(
    page_title="Rug Image Matcher",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Rug Image Feature Matcher")
st.markdown("Upload a rug image to find the most similar rugs from the datasources using LoFTR feature matching.")

# Initialize the matcher (cache it to avoid reloading)
@st.cache_resource
def load_matcher():
    """Load the LoFTR matcher model"""
    return LoFTR(pretrained="indoor")

def load_and_preprocess_image(image_path_or_array, is_uploaded=False):
    """Load and preprocess an image for matching"""
    if is_uploaded:
        # Handle uploaded image (PIL Image or numpy array)
        if isinstance(image_path_or_array, Image.Image):
            img_array = np.array(image_path_or_array)
            img_tensor = K.image_to_tensor(img_array, keepdim=False).float() / 255.0
        else:
            img_tensor = K.image_to_tensor(image_path_or_array, keepdim=False).float() / 255.0
    else:
        # Load from file path
        img_tensor = K.io.load_image(str(image_path_or_array), K.io.ImageLoadType.RGB32)[None, ...]
    
    # Resize to 512x512
    img_tensor = K.geometry.resize(img_tensor, (512, 512), antialias=True)
    return img_tensor

def match_images(img1, img2, matcher):
    """Match features between two images using LoFTR"""
    # Convert to grayscale
    input_dict = {
        "image0": K.color.rgb_to_grayscale(img1),
        "image1": K.color.rgb_to_grayscale(img2),
    }
    
    # Perform matching
    with torch.inference_mode():
        correspondences = matcher(input_dict)
    
    # Extract keypoints
    mkpts0 = correspondences["keypoints0"].cpu().numpy()
    mkpts1 = correspondences["keypoints1"].cpu().numpy()
    
    if len(mkpts0) == 0:
        return None, None, 0, 0
    
    # Clean up with RANSAC
    try:
        Fm, inliers = cv2.findFundamentalMat(
            mkpts0, mkpts1, cv2.USAC_MAGSAC, 0.5, 0.999, 100000
        )
        inliers = inliers > 0 if inliers is not None else np.zeros(len(mkpts0), dtype=bool)
    except:
        inliers = np.ones(len(mkpts0), dtype=bool)
    
    num_inliers = np.sum(inliers)
    num_matches = len(mkpts0)
    
    return mkpts0, mkpts1, num_inliers, num_matches, inliers

def create_match_visualization(img1, img2, mkpts0, mkpts1, inliers):
    """Create a visualization of the matches"""
    try:
        fig, ax = draw_LAF_matches(
            KF.laf_from_center_scale_ori(
                torch.from_numpy(mkpts0).view(1, -1, 2),
                torch.ones(mkpts0.shape[0]).view(1, -1, 1, 1),
                torch.ones(mkpts0.shape[0]).view(1, -1, 1),
            ),
            KF.laf_from_center_scale_ori(
                torch.from_numpy(mkpts1).view(1, -1, 2),
                torch.ones(mkpts1.shape[0]).view(1, -1, 1, 1),
                torch.ones(mkpts1.shape[0]).view(1, -1, 1),
            ),
            torch.arange(mkpts0.shape[0]).view(-1, 1).repeat(1, 2),
            K.tensor_to_image(img1),
            K.tensor_to_image(img2),
            inliers,
            draw_dict={
                "inlier_color": (0.1, 1, 0.1, 0.5),
                "tentative_color": None,
                "feature_color": (0.2, 0.2, 1, 0.5),
                "vertical": False,
            },
            return_fig_ax=True,
        )
        return fig
    except Exception as e:
        st.error(f"Error creating visualization: {e}")
        return None

# Load matcher
matcher = load_matcher()

# File uploader
uploaded_file = st.file_uploader(
    "Upload a rug image",
    type=['jpg', 'jpeg', 'png'],
    help="Upload an image of a rug to find similar matches"
)

if uploaded_file is not None:
    # Display uploaded image
    st.subheader("📤 Uploaded Image")
    uploaded_image = Image.open(uploaded_file)
    st.image(uploaded_image, caption="Your uploaded rug image", use_container_width=True)
    
    # Load and preprocess uploaded image
    uploaded_img_tensor = load_and_preprocess_image(uploaded_image, is_uploaded=True)
    
    # Get all images from datasources
    datasources_dir = Path("datasources")
    image_files = list(datasources_dir.glob("*.jpg")) + list(datasources_dir.glob("*.jpeg")) + list(datasources_dir.glob("*.png"))
    
    if len(image_files) == 0:
        st.error("No images found in the datasources folder!")
    else:
        st.subheader("🔍 Matching Results")
        st.info(f"Comparing with {len(image_files)} images from datasources...")
        
        # Store results
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Match with each image
        for idx, img_path in enumerate(image_files):
            status_text.text(f"Processing {img_path.name}... ({idx+1}/{len(image_files)})")
            progress_bar.progress((idx + 1) / len(image_files))
            
            try:
                # Load and preprocess datasource image
                datasource_img_tensor = load_and_preprocess_image(img_path)
                
                # Match images
                mkpts0, mkpts1, num_inliers, num_matches, inliers = match_images(
                    uploaded_img_tensor, datasource_img_tensor, matcher
                )
                
                if mkpts0 is not None:
                    results.append({
                        "path": img_path,
                        "name": img_path.name,
                        "num_inliers": num_inliers,
                        "num_matches": num_matches,
                        "img_tensor": datasource_img_tensor,
                        "mkpts0": mkpts0,
                        "mkpts1": mkpts1,
                        "inliers": inliers
                    })
            except Exception as e:
                st.warning(f"Error processing {img_path.name}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Sort by number of total matches (descending)
        results.sort(key=lambda x: x["num_matches"], reverse=True)
        
        if len(results) == 0:
            st.error("No matches found! Please try a different image.")
        else:
            st.success(f"Found matches with {len(results)} images!")
            
            # Display top matches
            st.subheader("🏆 Top Matches (Ranked by Total Matches)")
            
            # Show top 3 matches in detail
            top_n = min(3, len(results))
            
            for rank, result in enumerate(results[:top_n], 1):
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### 🥇 Rank #{rank}: {result['name']}")
                    st.metric("Total Matches", result["num_matches"])
                    st.metric("Inlier Matches", result["num_inliers"])
                    
                    # Display the matched image
                    matched_img = K.tensor_to_image(result["img_tensor"])
                    st.image(matched_img, caption=result['name'], use_container_width=True)
                
                with col2:
                    st.markdown("### Match Visualization")
                    try:
                        fig = create_match_visualization(
                            uploaded_img_tensor,
                            result["img_tensor"],
                            result["mkpts0"],
                            result["mkpts1"],
                            result["inliers"]
                        )
                        if fig is not None:
                            st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Could not create visualization: {e}")
            
            # Show summary table of all matches
            if len(results) > top_n:
                st.markdown("---")
                st.subheader("📊 All Matches Summary")
                
                summary_data = {
                    "Rank": list(range(1, len(results) + 1)),
                    "Image Name": [r["name"] for r in results],
                    "Total Matches": [r["num_matches"] for r in results],
                    "Inlier Matches": [r["num_inliers"] for r in results]
                }
                
                st.dataframe(summary_data, use_container_width=True, hide_index=True)
                
                # Show remaining matches as thumbnails
                st.subheader("🖼️ Other Matches")
                cols = st.columns(min(3, len(results) - top_n))
                
                for idx, result in enumerate(results[top_n:]):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.image(
                            K.tensor_to_image(result["img_tensor"]),
                            caption=f"#{top_n + idx + 1}: {result['name']}\n({result['num_matches']} matches)",
                            use_container_width=True
                        )
else:
    st.info("👆 Please upload a rug image to get started!")
    
    # Show available datasource images
    datasources_dir = Path("datasources")
    image_files = list(datasources_dir.glob("*.jpg")) + list(datasources_dir.glob("*.jpeg")) + list(datasources_dir.glob("*.png"))
    
    if len(image_files) > 0:
        st.subheader("📁 Available Images in Datasources")
        cols = st.columns(min(3, len(image_files)))
        for idx, img_path in enumerate(image_files):
            with cols[idx % 3]:
                try:
                    img = Image.open(img_path)
                    st.image(img, caption=img_path.name, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not load {img_path.name}")

