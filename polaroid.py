import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import math

st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator")
st.title("📸 Dev's Polaroid Style Collage Creator")

# Sidebar controls
st.sidebar.header("Settings")
images = st.sidebar.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
border_px = st.sidebar.slider("Border thickness (px)", 10, 200, 40, step=10)
dpi = st.sidebar.slider("DPI (for print resolution)", 100, 1200, 300, step=50)
caption_text = st.sidebar.text_input("Caption (optional)", "")
caption_font_size = st.sidebar.slider("Caption font size", 10, 300, 80)
font_color = st.sidebar.color_picker("Caption font color", "#000000")
font_name = "ReenieBeanie-Regular.ttf"
font_path = os.path.join("fonts", font_name)

# Crop image to square
def crop_center_square(img):
    width, height = img.size
    new_edge = min(width, height)
    left = (width - new_edge) / 2
    top = (height - new_edge) / 2
    right = (width + new_edge) / 2
    bottom = (height + new_edge) / 2
    return img.crop((left, top, right, bottom))

def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    if not images:
        return None

    try:
        pil_images = [Image.open(img).convert("RGB") for img in images]
        n = len(pil_images)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        half_border = border_px // 2
        polaroid_ratio = 1.2
        caption_scale = 0.7  # Reduced to 70% of original

        thumb_size_px = 1000  # base size before DPI scaling
        thumb_size_px = int(thumb_size_px * (dpi / 300))

        polaroid_width = thumb_size_px + border_px
        polaroid_height = int(thumb_size_px + border_px + caption_scale * border_px)

        collage_width = cols * polaroid_width + border_px
        collage_height = rows * polaroid_height + border_px

        collage = Image.new("RGB", (collage_width, collage_height), color="white")
        draw = ImageDraw.Draw(collage)

        try:
            caption_font = ImageFont.truetype(font_path, size=caption_font_size)
        except Exception as e:
            st.error(f"Font file not found: {font_path}")
            return None

        for idx, img in enumerate(pil_images):
            row = idx // cols
            col = idx % cols
            img = crop_center_square(img).resize((thumb_size_px, thumb_size_px))

            x = border_px + col * polaroid_width
            y = border_px + row * polaroid_height

            polaroid = Image.new("RGB", (polaroid_width, polaroid_height), color="white")
            polaroid.paste(img, (half_border, half_border))

            collage.paste(polaroid, (x, y))

        # Add caption at the bottom of the collage
        if caption_text:
            caption_font = ImageFont.truetype(font_path, size=caption_font_size)
            caption_width, caption_height = draw.textsize(caption_text, font=caption_font)
            caption_x = (collage_width - caption_width) // 2
            caption_y = collage_height - int(border_px * 1.5)  # Adjust bottom space for caption

            draw.text((caption_x, caption_y), caption_text, font=caption_font, fill=font_color)

        return collage

    except Exception as e:
        st.error(f"Error generating collage: {e}")
        return None

if images:
    collage = get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size)
    if collage:
        st.image(collage, caption="Generated Polaroid Collage", use_container_width=True)

        # Download
        buf = io.BytesIO()
        collage.save(buf, format="PNG")
        st.download_button(
            label="Download Collage",
            data=buf.getvalue(),
            file_name="polaroid_collage.png",
            mime="image/png"
        )
