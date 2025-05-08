import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io

# --- Configuration ---
FONT_DIR = "fonts"
DEFAULT_FONT = "ReenieBeanie-Regular.ttf"

# --- Helper Functions ---
def crop_center_square(img):
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim))

def load_font(font_filename, size):
    font_path = os.path.join(FONT_DIR, font_filename)
    if not os.path.exists(font_path):
        st.error(f"Font file not found: {font_path}")
        return None
    return ImageFont.truetype(font_path, size=size)

def get_collage(images, border_px, dpi, font_filename, font_color, caption_text, caption_font_size):
    num_images = len(images)
    if num_images == 0:
        return None

    cols = int(num_images ** 0.5)
    rows = (num_images + cols - 1) // cols

    # Sizes
    base_thumb_size = 300
    scale_factor = dpi / 300  # Scale based on DPI
    thumb_size = int(base_thumb_size * scale_factor)

    half_border = border_px // 2
    bottom_polaroid_extra = 6 * half_border

    # Create thumbnail images with inner border
    thumbs = []
    for img in images:
        cropped = crop_center_square(img).resize((thumb_size, thumb_size))
        thumb_with_border = Image.new("RGB", (thumb_size + border_px, thumb_size + border_px + bottom_polaroid_extra), "white")
        thumb_with_border.paste(cropped, (half_border, half_border))
        thumbs.append(thumb_with_border)

    thumb_w, thumb_h = thumbs[0].size

    collage_w = cols * thumb_w + (cols + 1) * half_border
    collage_h = rows * thumb_h + (rows + 1) * half_border

    collage = Image.new("RGB", (collage_w, collage_h), "white")
    draw = ImageDraw.Draw(collage)

    for index, thumb in enumerate(thumbs):
        row, col = divmod(index, cols)
        x = half_border + col * (thumb_w + half_border)
        y = half_border + row * (thumb_h + half_border)
        collage.paste(thumb, (x, y))

    # Draw caption if provided
    if caption_text:
        caption_font = load_font(font_filename, caption_font_size)
        if caption_font:
            text_w, text_h = draw.textsize(caption_text, font=caption_font)
            x = (collage_w - text_w) // 2
            y = collage_h - text_h - half_border
            draw.text((x, y), caption_text, fill=font_color, font=caption_font)

    return collage

# --- Streamlit UI ---
st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator")
st.title("📸 Dev's Polaroid Style Collage Creator")

with st.sidebar:
    st.header("📐 Layout Options")
    border_px = st.slider("Border Thickness (pixels)", min_value=10, max_value=200, value=40, step=5)
    dpi = st.slider("Output DPI", min_value=72, max_value=1200, value=300, step=50)
    caption_text = st.text_input("Caption (optional)", "")
    caption_font_size = st.slider("Caption Font Size", min_value=10, max_value=300, value=40)

    st.header("🎨 Style")
    font_color = st.color_picker("Caption Font Color", "#000000")
    available_fonts = sorted([f for f in os.listdir(FONT_DIR) if f.lower().endswith(".ttf")])
    font_filename = st.selectbox("Font", options=available_fonts, index=available_fonts.index(DEFAULT_FONT) if DEFAULT_FONT in available_fonts else 0)

uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    images = [Image.open(file).convert("RGB") for file in uploaded_files]

    try:
        collage = get_collage(images, border_px, dpi, font_filename, font_color, caption_text, caption_font_size)
        if collage:
            st.image(collage, caption="Preview", use_container_width=True)

            # Save to BytesIO for download
            img_bytes = io.BytesIO()
            collage.save(img_bytes, format="JPEG", dpi=(dpi, dpi))
            st.download_button("Download Collage", data=img_bytes.getvalue(), file_name="polaroid_collage.jpg", mime="image/jpeg")
    except Exception as e:
        st.error(f"Error generating collage: {e}")
else:
    st.info("Please upload one or more images to begin.")
