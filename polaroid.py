import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="📸 Dev's Polaroid Style Collage Creator", layout="wide")

# Font directory and available fonts
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONT_OPTIONS = {
    "Permanent Marker": os.path.join(FONT_DIR, "PermanentMarker-Regular.ttf"),
    "Patrick Hand": os.path.join(FONT_DIR, "PatrickHand-Regular.ttf"),
    "Reenie Beanie": os.path.join(FONT_DIR, "ReenieBeanie-Regular.ttf"),
    # Add more fonts here as needed
}

def crop_center_square(image):
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    return image.crop((left, top, left + min_dim, top + min_dim))

def get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size):
    num_images = len(images)
    grid_size = int(num_images ** 0.5) + (0 if (num_images ** 0.5).is_integer() else 1)

    # Half border for each image; remaining for outer + polaroid bottom
    half_border = border_px // 2
    polaroid_extra = 6 * half_border

    polaroid_size = dpi // 2  # Size of each polaroid square image
    caption_font = ImageFont.truetype(font_path, size=caption_font_size)

    collage_width = grid_size * polaroid_size + (grid_size + 1) * half_border
    collage_height = grid_size * (polaroid_size + polaroid_extra) + (grid_size + 1) * half_border

    collage = Image.new("RGB", (collage_width, collage_height), "white")

    for idx, img in enumerate(images):
        cropped = crop_center_square(img).resize((polaroid_size, polaroid_size), Image.Resampling.LANCZOS)
        row, col = divmod(idx, grid_size)

        x = half_border + col * (polaroid_size + half_border)
        y = half_border + row * (polaroid_size + polaroid_extra + half_border)

        # Create a white polaroid background with extra space at bottom
        polaroid_img = Image.new("RGB", (polaroid_size, polaroid_size + polaroid_extra), "white")
        polaroid_img.paste(cropped, (0, 0))

        if caption_text:
            draw = ImageDraw.Draw(polaroid_img)
            text_width, text_height = draw.textsize(caption_text, font=caption_font)
            text_x = (polaroid_size - text_width) // 2
            text_y = polaroid_size + ((polaroid_extra - text_height) // 2)
            draw.text((text_x, text_y), caption_text, fill=font_color, font=caption_font)

        collage.paste(polaroid_img, (x, y))

    return collage

st.title("📸 Dev's Polaroid Style Collage Creator")

uploaded_images = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

border_px = st.sidebar.slider("Border size (px)", 10, 200, 40)
dpi = st.sidebar.slider("DPI", 300, 2400, 600)
font_color = st.sidebar.color_picker("Text color", "#000000")
caption_text = st.sidebar.text_input("Caption text", "")
caption_font_size = st.sidebar.slider("Caption font size", 10, 300, 48)
selected_font = st.sidebar.selectbox("Choose a font", list(FONT_OPTIONS.keys()))
font_path = FONT_OPTIONS[selected_font]

if uploaded_images:
    images = [Image.open(img).convert("RGB") for img in uploaded_images]
    collage = get_collage(images, border_px, dpi, font_path, font_color, caption_text, caption_font_size)

    buf = io.BytesIO()
    collage.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.image(collage, caption="Polaroid Collage", use_container_width=True)
    st.download_button("Download Collage", data=byte_im, file_name="collage.png", mime="image/png")
