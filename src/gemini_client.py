import os
import logging
from typing import List

from google import genai
from google.genai import types
import requests

logger = logging.getLogger(__name__)


class GeminiError(RuntimeError):
    pass


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def _fetch_image_bytes(url: str) -> bytes:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.content


def generate_description(image_urls: List[str], name: str, keywords: List[str]) -> str:
    """
    Uses Gemini to draft a product description based on images, name, and keywords.
    Processes each image individually, then collates all descriptions into one.
    """
    client = _get_client()
    
    # Individual image description prompt - focused on visual/aesthetic details
    individual_prompt = (
        "You are a visual description specialist for a premium rug/carpet retailer. "
        "Your goal is to describe this rug image in rich visual detail so someone who cannot see it can vividly imagine its appearance. "
        "Write a detailed visual description (60-100 words) that captures EVERYTHING visible in this image. "
        "Focus intensely on:\n"
        "- COLORS: Exact color names, shades, tones, gradients, and how colors interact (e.g., 'deep navy blue with ivory cream accents', 'warm terracotta fading to soft beige')\n"
        "- PATTERNS & MOTIFS: Detailed pattern descriptions (geometric shapes, floral designs, medallions, borders, repeating motifs, symmetry/asymmetry)\n"
        "- TEXTURE & SURFACE: Visual texture appearance (smooth, plush, flat-weave, high-pile, low-pile, shaggy, nubby, silky sheen, matte finish)\n"
        "- VISUAL DETAILS: Border designs, fringe details, edge treatments, any decorative elements visible\n"
        "- LAYOUT & COMPOSITION: How the design is arranged (centered medallion, all-over pattern, directional, etc.)\n"
        "- MATERIAL APPEARANCE: How the materials look visually (wool's matte texture, silk's luster, synthetic's uniform appearance)\n"
        "- SIZE & PROPORTION: Visual cues about dimensions and scale from the image\n"
        "Be extremely specific about visual elements. Describe colors with precision, patterns with detail, and textures as they appear. "
        "Write as if painting a picture with words for someone who cannot see."
        f"\nProduct name: {name}\nKeywords: {', '.join(keywords)}"
    )
    
    # Process each image individually
    individual_descriptions = []
    for idx, url in enumerate(image_urls, 1):
        logger.info(f"[Image {idx}/{len(image_urls)}] Processing image: {url}")
        
        try:
            img_bytes = _fetch_image_bytes(url)
            image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            
            logger.info(f"[Image {idx}/{len(image_urls)}] Input - URL: {url}")
            logger.info(f"[Image {idx}/{len(image_urls)}] Input - Prompt: {individual_prompt}")
            
            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[individual_prompt, image_part],
            )
            
            if not result or not result.text:
                raise GeminiError(f"No description returned by Gemini for image {idx}.")
            
            description = result.text.strip()
            individual_descriptions.append(description)
            
            logger.info(f"[Image {idx}/{len(image_urls)}] Output - Description: {description}")
            
        except Exception as e:
            logger.error(f"[Image {idx}/{len(image_urls)}] Error processing {url}: {e}")
            raise
    
    # Collate all descriptions into one
    logger.info(f"[Collation] Starting collation of {len(individual_descriptions)} descriptions")
    
    collation_prompt = (
        "You are a visual description specialist for a premium rug/carpet retailer. "
        "Your goal is to create a comprehensive visual description that helps someone who cannot see the rug vividly imagine its complete appearance. "
        "Given multiple detailed visual descriptions of the same rug from different angles/views, "
        "synthesize them into a single, rich, comprehensive visual description (80-150 words). "
        "\n\nCRITICAL: The final description must be extremely detailed about VISUAL and AESTHETIC elements:\n"
        "- Combine all color information from all views into a complete color palette description\n"
        "- Merge pattern details from different angles to describe the full pattern layout\n"
        "- Integrate texture and surface appearance details from all views\n"
        "- Include all visible decorative elements, borders, fringes, and design features\n"
        "- Describe the overall aesthetic and visual style (e.g., 'traditional Persian elegance', 'modern minimalist geometric', 'rustic bohemian')\n"
        "- Mention construction method only if it affects visual appearance (e.g., 'hand-knotted texture creates subtle depth')\n"
        "- Include material appearance (how wool/silk/synthetic looks visually, not just what it is)\n"
        "- Describe size and proportion based on visual cues from all images\n"
        "\nWrite in a way that paints a complete visual picture. Be specific about colors, patterns, textures, and aesthetic details. "
        "The description should be so detailed that a blind person can form a clear mental image of exactly how this rug looks. "
        "Prioritize visual and aesthetic information over technical specifications. "
        "Remove redundancies but preserve all unique visual details from each view. Ensure the description is cohesive and flows naturally."
        f"\nProduct name: {name}\nKeywords: {', '.join(keywords)}"
        f"\n\nIndividual descriptions from different views:\n" + "\n\n---\n\n".join(
            f"View {i+1}:\n{desc}" for i, desc in enumerate(individual_descriptions)
        )
    )
    
    logger.info(f"[Collation] Input - Prompt: {collation_prompt}")
    
    collation_result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[collation_prompt],
    )
    
    if not collation_result or not collation_result.text:
        raise GeminiError("No collated description returned by Gemini.")
    
    final_description = collation_result.text.strip()
    logger.info(f"[Collation] Output - Final Description: {final_description}")
    
    return final_description

