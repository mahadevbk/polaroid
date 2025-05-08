import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import io
import requests
import math

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

# Optional preview images (can be hosted yourself)
FONT_PREVIEWS = {
    name: f"https://your-username.github.io/polaroid-font-previews/previews/{name.replace(' ', '_')}.png"
    for name in GOOGLE_FONTS
}

# --- Sidebar Controls ---
dpi = st.sidebar.slider("📐 DPI of Final Image", 300, 1200, 300, step=100)
border_mm = st.sidebar.slider("📏 Border Size (mm)", 0, 6, 3)
uploaded_files = st.file_uploader("📷 Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
font_name = st.sidebar.radio("✏️ Choose Font (with Preview)", options=list(GOOGLE_FONTS.keys()))
if font_name in FONT_PREVIEWS:
    st.sidebar.image(FONT_PREVIEWS[font_name], caption=font_name, use_container_width=True)
font_color = st.sidebar.color_picker("🎨 Font Color", "#000000")
file_name = st.sidebar.text_input("📝 Output File Name", value="polaroid_collage")
file_path = st.sidebar.text_input("📁 Save To Folder", value=".")

# --- Helper Functions ---
def get_google_font(font_url):
    response = requests.get(font_url)
    font_bytes = io.BytesIO(response.content)
    return font_bytes

def crop_center_square(img):
    width, height = img.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return img.crop((left, top, left + side, top + side))

def create_polaroid(img, border_px):
    side = img.size[0]
    border_total = border_px * 2
    bottom_extra = border_px * 3  # Extra for text at the bottom
    new_img = Image.new("RGB", (side + border_total, side + border_total + bottom_extra), "white")
    new_img.paste(img, (border_px, border_px))
    return new_img

def get_collage(images, border_px, dpi, font_bytes, font_color):
    n = math.ceil(math.sqrt(len(images)))
    total_images = n ** 2
    if len(images) < total_images:
        images += images[:total_images - len(images)]

    thumb_size_px = int((25.4 / dpi) * dpi)  # 1 inch square thumbnails
    thumbnails = []

    for img in images:
        cropped = crop_center_square(img).resize((thumb_size_px, thumb_size_px))
        polaroid = create_polaroid(cropped, border_px)
        thumbnails.append(polaroid)

    polaroid_size = thumbnails[0].size[0]
    collage_size = (n * polaroid_size, n * polaroid_size)
    collage = Image.new("RGB", collage_size, "white")

    font = ImageFont.truetype(font_bytes, size=polaroid_size // 10)

    for idx, thumb in enumerate(thumbnails):
        row = idx // n
        col = idx % n
        x = col * polaroid_size
        y = row * polaroid_size
        collage.paste(thumb, (x, y))

        draw = ImageDraw.Draw(collage)
        text = f"Photo {idx + 1}"

        # Fix for deprecated textsize() method
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = x + (polaroid_size - text_width) // 2
        text_y = y + polaroid_size - int(border_px * 0.5) - text_height
        draw.text((text_x, text_y), text, fill=font_color, font=font)

    return collage

# --- Main Logic ---
if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded.")
    images = [Image.open(file).convert("RGB") for file in uploaded_files]
    border_px = int((border_mm / 25.4) * dpi)
    font_bytes = get_google_font(GOOGLE_FONTS[font_name])
    collage = get_collage(images, border_px, dpi, font_bytes, font_color)

    st.image(collage, caption="Polaroid Style Collage", use_container_width=True)

    os.makedirs(file_path, exist_ok=True)
    final_path = os.path.join(file_path, f"{file_name}.jpg")
    collage.save(final_path, dpi=(dpi, dpi))
    st.success(f"🎉 Image saved to {final_path}")

    img_buffer = io.BytesIO()
    collage.save(img_buffer, format="JPEG")
    st.download_button("⬇️ Download Image", data=img_buffer.getvalue(), file_name=f"{file_name}.jpg", mime="image/jpeg")
