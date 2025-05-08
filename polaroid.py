import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Set up title
st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator")
st.title("📸 Dev's Polaroid Style Collage Creator")

# Upload images
images = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

# UI settings
border_px = st.slider("Border thickness (px)", 10, 100, 20)
dpi = st.slider("DPI (for resolution)", 72, 1200, 300)
caption_text = st.text_input("Caption text", "")
caption_font_size = st.slider("Caption font size", 10, 300, 50)
font_color = st.color_picker("Caption color", "#000000")

# Font selection
available_fonts = {
    "Reenie Beanie": "ReenieBeanie-Regular.ttf",
    "Permanent Marker": "PermanentMarker-Regular.ttf",
    "Rock Salt": "RockSalt-Regular.ttf"
}
selected_font_name = st.selectbox("Choose caption font", list(available_fonts.keys()))
selected_font_file = available_fonts[selected_font_name]
font_path = os.path.join("fonts", selected_font_file)

# Confirm font path exists
if not os.path.exists(font_path):
    st.error(f"Font file not found: {font_path}")
    st.stop()

# Core collage function
def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    from math import ceil, sqrt

    imgs = [Image.open(img).convert("RGB") for img in images]
    count = len(imgs)
    cols = ceil(sqrt(count))
    rows = ceil(count / cols)

    thumb_size = 300  # base thumbnail size (we’ll upscale later)
    half_border = border_px // 2
    caption_space = border_px * 6

    thumb_with_border = thumb_size + border_px
    collage_width = cols * thumb_with_border + border_px
    collage_height = rows * (thumb_with_border + caption_space) + border_px

    collage = Image.new("RGB", (collage_width, collage_height), color="white")

    try:
        caption_font = ImageFont.truetype(font_path, caption_font_size)
    except Exception as e:
        st.error(f"Error loading font: {e}")
        st.stop()

    for idx, img in enumerate(imgs):
        img = img.resize((thumb_size, thumb_size))
        bordered_img = Image.new("RGB", (thumb_with_border, thumb_with_border + caption_space), "white")
        bordered_img.paste(img, (half_border, half_border))

        draw = ImageDraw.Draw(bordered_img)
        if caption_text:
            text_w, text_h = draw.textsize(caption_text, font=caption_font)
            text_x = (thumb_with_border - text_w) // 2
            text_y = thumb_size + half_border
            draw.text((text_x, text_y), caption_text, font=caption_font, fill=font_color)

        x = (idx % cols) * thumb_with_border + border_px
        y = (idx // cols) * (thumb_with_border + caption_space) + border_px
        collage.paste(bordered_img, (x, y))

    return collage

# Build collage
if images:
    collage = get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size)
    st.image(collage, caption="Your Polaroid Collage", use_container_width=True)
    img_path = "polaroid_collage_output.jpg"
    collage.save(img_path, dpi=(dpi, dpi))
    with open(img_path, "rb") as f:
        st.download_button("Download Collage", f, file_name="polaroid_collage.jpg")
