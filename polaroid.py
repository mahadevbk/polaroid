import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import math

st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator")

st.title("📸 Dev's Polaroid Style Collage Creator")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    border_px = st.slider("Border Size (px)", 10, 200, 40)
    dpi = st.slider("Output DPI", 72, 1200, 300)
    caption_font_size = st.slider("Caption Font Size", 10, 300, 40)
    font_color = st.color_picker("Font Color", "#000000")
    caption_text = st.text_input("Bottom Caption", "My Collage")
    font_file = st.selectbox("Choose Font", sorted(os.listdir("fonts")))

uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def crop_center_square(img):
    width, height = img.size
    min_dim = min(width, height)
    return img.crop((
        (width - min_dim) // 2,
        (height - min_dim) // 2,
        (width + min_dim) // 2,
        (height + min_dim) // 2
    ))

def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    # Calculate scale
    inch_size = 8  # base collage width in inches
    base_collage_px = inch_size * dpi

    # Half border logic
    half_border = border_px // 2

    n = len(images)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    thumb_size = (base_collage_px - (cols + 1) * half_border * 2) // cols

    processed_images = []
    for img in images:
        cropped = crop_center_square(img).resize((thumb_size, thumb_size))
        bordered = Image.new("RGB", (thumb_size + half_border * 2, thumb_size + half_border * 2), "white")
        bordered.paste(cropped, (half_border, half_border))
        processed_images.append(bordered)

    cell_size = thumb_size + half_border * 2
    collage_width = cols * cell_size
    collage_height = rows * cell_size

    # Add bottom padding for caption (6x half_border)
    full_width = collage_width + half_border * 2
    full_height = collage_height + half_border * 2 + 6 * half_border

    collage = Image.new("RGB", (full_width, full_height), "white")

    for index, img in enumerate(processed_images):
        x = (index % cols) * cell_size + half_border
        y = (index // cols) * cell_size + half_border
        collage.paste(img, (x, y))

    # Caption
    draw = ImageDraw.Draw(collage)
    font = ImageFont.truetype(font_path, size=caption_font_size)

    bbox = draw.textbbox((0, 0), caption_text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    caption_x = (collage.width - text_w) // 2
    caption_y = collage_height + half_border * 2

    draw.text((caption_x, caption_y), caption_text, font=font, fill=font_color)

    return collage

if uploaded_files:
    images = [Image.open(file).convert("RGB") for file in uploaded_files]

    font_path = os.path.join("fonts", font_file)
    if not os.path.exists(font_path):
        st.error(f"Font file not found: {font_path}")
    else:
        collage = get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size)

        st.image(collage, caption="Preview", use_column_width=True)

        buffer = io.BytesIO()
        collage.save(buffer, format="JPEG", dpi=(dpi, dpi))
        st.download_button(
            label="Download Collage",
            data=buffer.getvalue(),
            file_name="polaroid_collage.jpg",
            mime="image/jpeg"
        )
