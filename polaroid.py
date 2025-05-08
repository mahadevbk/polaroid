import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import io
import requests
import math
import tempfile

st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator", layout="centered")
st.title("📸 Dev's Polaroid Style Collage Creator")

# --- Font Setup ---
GOOGLE_FONTS = {
    "Covered By Your Grace": "https://github.com/google/fonts/raw/main/ofl/coveredbyyourgrace/CoveredByYourGrace.ttf",
    "Permanent Marker": "https://github.com/google/fonts/raw/main/apache/permanentmarker/PermanentMarker.ttf",
    "Offside": "https://github.com/google/fonts/raw/main/ofl/offside/Offside-Regular.ttf",
    "Rock Salt": "https://github.com/google/fonts/raw/main/apache/rocksalt/RockSalt-Regular.ttf",
    "Nothing You Could Do": "https://github.com/google/fonts/raw/main/ofl/nothingyoucoulddo/NothingYouCouldDo-Regular.ttf",
    "Amatic SC": "https://github.com/google/fonts/raw/main/ofl/amaticsc/AmaticSC-Regular.ttf",
    "Patrick Hand": "https://github.com/google/fonts/raw/main/ofl/patrickhand/PatrickHand-Regular.ttf",
    "Shadows Into Light": "https://github.com/google/fonts/raw/main/ofl/shadowsintolight/ShadowsIntoLight-Regular.ttf",
    "Satisfy": "https://github.com/google/fonts/raw/main/ofl/satisfy/Satisfy-Regular.ttf",
    "Reenie Beanie": "https://github.com/google/fonts/raw/main/ofl/reeniebeanie/ReenieBeanie-Regular.ttf"
}

# --- Sidebar Controls ---
dpi = st.sidebar.slider("📐 DPI of Final Image", 300, 1200, 300, step=100)
border_mm = st.sidebar.slider("📏 Border Size (mm)", 0, 6, 3)
uploaded_files = st.file_uploader("📷 Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
font_name = st.sidebar.radio("✏️ Choose Font (with Preview)", options=list(GOOGLE_FONTS.keys()))
font_color = st.sidebar.color_picker("🎨 Font Color", "#000000")
file_name = st.sidebar.text_input("📝 Output File Name", value="polaroid_collage")
file_path = st.sidebar.text_input("📁 Save To Folder", value=".")
caption_text = st.sidebar.text_input("📝 Caption for Bottom of Collage", value="Your Caption Here")
caption_font_size = st.sidebar.slider("🔠 Caption Font Size", 10, 300, 24)  # Updated range for text size

# --- Helper Functions ---
def download_and_save_font(font_url):
    # Download font to a temporary file
    response = requests.get(font_url)
    font_bytes = io.BytesIO(response.content)
    
    # Create a temporary file to save the font
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf")
    with open(temp_file.name, 'wb') as f:
        f.write(font_bytes.read())
    
    return temp_file.name

def crop_center_square(img):
    width, height = img.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return img.crop((left, top, left + side, top + side))

def create_polaroid(img, border_px):
    side = img.size[0]
    border_total = border_px * 2
    bottom_extra = border_px * 3  # Extra space at the bottom for the caption
    new_img = Image.new("RGB", (side + border_total, side + border_total + bottom_extra), "white")
    new_img.paste(img, (border_px, border_px))
    return new_img

def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    n = math.ceil(math.sqrt(len(images)))
    total_images = n ** 2
    if len(images) < total_images:
        images += images[:total_images - len(images)]

    # Set the internal gap to match the border size
    thumb_size_px = int((2 * dpi))  # Resize to twice the DPI size for better resolution
    thumbnails = []

    for img in images:
        cropped = crop_center_square(img).resize((thumb_size_px, thumb_size_px), Image.Resampling.LANCZOS)
        polaroid = create_polaroid(cropped, border_px)
        thumbnails.append(polaroid)

    polaroid_size = thumbnails[0].size[0]
    
    # Create the collage size, with half of the border around the entire collage
    collage_size = (n * polaroid_size + border_px, n * polaroid_size + border_px + int(border_px * 6))  # Doubled bottom space for caption
    collage = Image.new("RGB", collage_size, "white")

    # Paste the thumbnails with equal internal gap
    for idx, thumb in enumerate(thumbnails):
        row = idx // n
        col = idx % n
        x = col * polaroid_size + border_px // 2  # Add half border space between images
        y = row * polaroid_size + border_px // 2
        collage.paste(thumb, (x, y))

    # Adjust text size based on DPI, ensuring it scales for different DPI values
    adjusted_caption_font_size = max(caption_font_size, int(dpi / 100))  # Adjust caption size for higher DPI

    # Add caption text at the bottom
    if caption_text:
        caption_font = ImageFont.truetype(font_path, size=adjusted_caption_font_size)
        draw = ImageDraw.Draw(collage)
        caption_bbox = draw.textbbox((0, 0), caption_text, font=caption_font)
        caption_width = caption_bbox[2] - caption_bbox[0]
        caption_height = caption_bbox[3] - caption_bbox[1]
        caption_x = (collage_size[0] - caption_width) // 2
        caption_y = collage_size[1] - int(border_px * 2) - caption_height  # Increased bottom margin
        draw.text((caption_x, caption_y), caption_text, fill=font_color, font=caption_font)

    return collage

# --- Main Logic ---
if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded.")
    images = [Image.open(file).convert("RGB") for file in uploaded_files]
    border_px = int((border_mm / 25.4) * dpi)
    
    # Download the selected font and use it
    font_path = download_and_save_font(GOOGLE_FONTS[font_name])
    
    collage = get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size)

    st.image(collage, caption="Polaroid Style Collage", use_container_width=True)

    os.makedirs(file_path, exist_ok=True)
    final_path = os.path.join(file_path, f"{file_name}.jpg")
    collage.save(final_path, dpi=(dpi, dpi))  # Saving with proper DPI
    st.success(f"🎉 Image saved to {final_path}")

    img_buffer = io.BytesIO()
    collage.save(img_buffer, format="JPEG")
    st.download_button("⬇️ Download Image", data=img_buffer.getvalue(), file_name=f"{file_name}.jpg", mime="image/jpeg")
