import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# App Title
st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator")
st.title("📸 Dev's Polaroid Style Collage Creator")

# Sidebar Controls
st.sidebar.header("Configuration")
border_px = st.sidebar.slider("Border (pixels)", 10, 200, 50, step=5)
dpi = st.sidebar.slider("DPI (Resolution)", 100, 2400, 300, step=100)
caption_font_size = st.sidebar.slider("Caption Font Size", 10, 300, 60)
font_color = st.sidebar.color_picker("Font Color", "#000000")
caption_text = st.sidebar.text_input("Caption Text (optional)", "")
font_file = st.sidebar.selectbox("Font", os.listdir("fonts") if os.path.exists("fonts") else [])

# Upload Images
uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

def crop_center_square(img):
    width, height = img.size
    new_edge = min(width, height)
    left = (width - new_edge) // 2
    top = (height - new_edge) // 2
    return img.crop((left, top, left + new_edge, top + new_edge))

def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    try:
        imgs = [Image.open(img).convert("RGB") for img in images]
        if not imgs:
            return None

        # Determine thumbnail size
        thumb_size_in = 2
        thumb_size_px = int(thumb_size_in * dpi)
        half_border = border_px // 2

        thumbs = []
        for img in imgs:
            cropped = crop_center_square(img).resize((thumb_size_px, thumb_size_px), Image.LANCZOS)
            new_img = Image.new("RGB", (thumb_size_px + border_px, thumb_size_px + border_px), (255, 255, 255))
            new_img.paste(cropped, (half_border, half_border))
            thumbs.append(new_img)

        cols = int(len(thumbs) ** 0.5)
        rows = (len(thumbs) + cols - 1) // cols

        img_w, img_h = thumbs[0].size
        canvas_w = cols * img_w + border_px
        canvas_h = rows * img_h + border_px + (6 * border_px if caption_text else 0)

        collage = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))

        for index, img in enumerate(thumbs):
            row = index // cols
            col = index % cols
            x = col * img_w + half_border
            y = row * img_h + half_border
            collage.paste(img, (x, y))

        if caption_text:
            draw = ImageDraw.Draw(collage)
            caption_font = ImageFont.truetype(font_path, size=caption_font_size)
            bbox = draw.textbbox((0, 0), caption_text, font=caption_font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            caption_x = (canvas_w - text_w) // 2
            caption_y = canvas_h - (6 * border_px // 2) - text_h // 2
            draw.text((caption_x, caption_y), caption_text, font=caption_font, fill=font_color)

        return collage
    except Exception as e:
        st.error(f"Error generating collage: {e}")
        return None

if uploaded_files and font_file:
    font_path = os.path.join("fonts", font_file)
    collage = get_collage(uploaded_files, border_px, dpi, font_path, font_color, caption_text, caption_font_size)

    if collage:
        st.image(collage, caption="Polaroid Collage", use_container_width=True)

        buf = io.BytesIO()
        collage.save(buf, format="JPEG", dpi=(dpi, dpi))
        st.download_button("Download Collage", buf.getvalue(), file_name="polaroid_collage.jpg", mime="image/jpeg")
