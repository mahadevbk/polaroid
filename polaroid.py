import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import io
import requests
import math

st.set_page_config(page_title="Polaroid Collage Creator", layout="centered")

st.title("📸 Polaroid Style Collage Creator")

# --- Font Setup ---
GOOGLE_FONTS = {
    "Covered By Your Grace": "https://fonts.gstatic.com/s/coveredbyyourgrace/v15/QGY2z_wNahGAdqQ43Rh_fKDvWNxdMKRbpw.woff2",
    "Permanent Marker": "https://fonts.gstatic.com/s/permanentmarker/v13/Fh4uPib9w3w1AmH8zF4VX3N2LBKcgX8.woff2",
    "Offside": "https://fonts.gstatic.com/s/offside/v18/HI_KiYMWKa9QrAykc5I.woff2",
    "Rock Salt": "https://fonts.gstatic.com/s/rocksalt/v18/MwQ0bhv11fWD6QsAVOZrt0M6.woff2",
    "Nothing You Could Do": "https://fonts.gstatic.com/s/nothingyoucoulddo/v19/oY1B8fbBpaP5OX3DtrRYf_Q2BPB1SnfZWFzFUw.woff2",
    "Amatic SC": "https://fonts.gstatic.com/s/amaticsc/v28/TUZyzwprpvBS1izr_vOEDuSfU5c.woff2",
    "Patrick Hand": "https://fonts.gstatic.com/s/patrickhand/v17/LDI1apSQOAYtSuYWp8ZhfYe8Uc8.woff2",
    "Shadows Into Light": "https://fonts.gstatic.com/s/shadowsintolight/v16/UqyNK9UOIntux_czAvDQx_ZcHqZXBNQzdcD8.woff2",
    "Satisfy": "https://fonts.gstatic.com/s/satisfy/v18/rP2Hp2yn6lkG50LoOZSCHBeHFl0.woff2",
    "Reenie Beanie": "https://fonts.gstatic.com/s/reeniebeanie/v19/z7NSdR76eDkaJKZJFkkjuvWxXPq1rg.woff2"
}

# --- Sidebar options ---
dpi = st.sidebar.slider("📐 DPI of Final Image", 300, 1200, 300, step=100)
border_mm = st.sidebar.slider("📏 Border Size (mm)", 0, 6, 3)

uploaded_files = st.file_uploader("📷 Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

font_name = st.sidebar.selectbox("✏️ Choose Font", GOOGLE_FONTS.keys())
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

def create_polaroid(img, border_px, dpi):
    side = img.size[0]
    border_total = border_px * 2
    bottom_extra = border_px * 3  # More space at bottom like a polaroid

    new_img = Image.new("RGB", (side + border_total, side + border_total + bottom_extra), "white")
    new_img.paste(img, (border_px, border_px))
    return new_img

def get_collage(images, border_px, dpi, font_bytes, font_color):
    n = math.ceil(math.sqrt(len(images)))
    total_images = n ** 2
    if len(images) < total_images:
        images += images[:total_images - len(images)]

    thumb_size_px = int((25.4 / dpi) * dpi)  # 1 inch square
    thumbnails = []

    for img in images:
        cropped = crop_center_square(img).resize((thumb_size_px, thumb_size_px))
        polaroid = create_polaroid(cropped, border_px, dpi)
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
        text = f"Photo {idx+1}"
        text_width, text_height = draw.textsize(text, font=font)
        text_x = x + (polaroid_size - text_width) // 2
        text_y = y + polaroid_size - int(border_px * 0.5) - text_height
        draw.text((text_x, text_y), text, fill=font_color, font=font)

    return collage

# --- Processing ---
if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded.")
    images = [Image.open(file).convert("RGB") for file in uploaded_files]
    border_px = int((border_mm / 25.4) * dpi)
    font_bytes = get_google_font(GOOGLE_FONTS[font_name])
    collage = get_collage(images, border_px, dpi, font_bytes, font_color)

    st.image(collage, caption="Polaroid Style Collage", use_column_width=True)
    
    # Save logic
    os.makedirs(file_path, exist_ok=True)
    final_path = os.path.join(file_path, f"{file_name}.jpg")
    collage.save(final_path, dpi=(dpi, dpi))
    st.success(f"🎉 Image saved to {final_path}")

    # Download
    img_buffer = io.BytesIO()
    collage.save(img_buffer, format="JPEG")
    st.download_button("⬇️ Download Image", data=img_buffer.getvalue(), file_name=f"{file_name}.jpg", mime="image/jpeg")
