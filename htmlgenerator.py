# app.py
import streamlit as st
import html

st.set_page_config(page_title="🌐 Premium Blue HTML Formatter", layout="wide")

st.title("🌐 Universal Text → HTML Formatter — Blue Premium Edition")
st.markdown("""
This tool converts your ready-made text into a **beautiful blue-themed HTML page**.  
It doesn’t change your content — it only wraps it in a premium, visually distinct layout.
""")

# === INPUT ===
st.subheader("1️⃣ Paste Your Content")
text_input = st.text_area(
    "✏️ Paste your content here:",
    height=400,
    placeholder="Paste your lessons, bilingual lines, or any formatted text..."
)

# === SIDEBAR SETTINGS ===
st.sidebar.header("⚙️ Design Customization")
primary_color = st.sidebar.color_picker("Primary Blue Color", "#004aad")
accent_color = st.sidebar.color_picker("Accent Highlight", "#7fb3ff")
background_color = st.sidebar.color_picker("Background Color", "#eaf2ff")
font_family = st.sidebar.selectbox("Font Family", ["Poppins", "Inter", "Roboto", "Open Sans", "Lato"], index=0)
font_size = st.sidebar.slider("Text Size (px)", 18, 28, 20)
enable_download = st.sidebar.checkbox("Enable Download Button", value=True)
show_code = st.sidebar.checkbox("Show Generated HTML Code", value=True)

# === HTML GENERATOR ===
def generate_html(content: str) -> str:
    # Keep content exactly as is but escape HTML special characters
    safe_content = html.escape(content).replace("\n", "<br>\n")

    css = f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;600&display=swap');
      body {{
        background: linear-gradient(135deg, {background_color} 0%, #ffffff 100%);
        font-family: '{font_family}', sans-serif;
        color: #0a1e44;
        line-height: 1.9;
        padding: 60px 20px;
        display: flex;
        justify-content: center;
      }}
      .container {{
        background: #ffffff;
        border-left: 10px solid {primary_color};
        border-radius: 16px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
        padding: 50px 60px;
        max-width: 950px;
        width: 100%;
      }}
      .content {{
        font-size: {font_size}px;
        font-weight: 400;
        color: #0a1e44;
      }}
      .content br {{
        line-height: 1.8;
      }}
      .highlight {{
        color: {primary_color};
        font-weight: 600;
      }}
      @media (max-width: 768px) {{
        .container {{ padding: 30px 25px; }}
        .content {{ font-size: {font_size - 2}px; }}
      }}
    </style>
    """

    html_body = f"""
    <div class="container">
        <div class="content">
            {safe_content}
        </div>
    </div>
    """

    final_html = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n{css}</head>\n<body>\n{html_body}\n</body>\n</html>"
    return final_html

# === BUTTON ACTION ===
st.subheader("2️⃣ Generate Blue-Themed HTML")
if st.button("⚡ Generate HTML"):
    if not text_input.strip():
        st.error("Please paste your content first.")
    else:
        result_html = generate_html(text_input)
        st.success("✅ HTML generated successfully!")

        if show_code:
            st.code(result_html, language="html")

        if enable_download:
            st.download_button(
                "⬇️ Download HTML File",
                data=result_html.encode("utf-8"),
                file_name="blue_theme_formatted.html",
                mime="text/html",
            )

        st.markdown("---")
        st.markdown("### 🔍 Live Preview")
        st.components.v1.html(result_html, height=750, scrolling=True)

st.markdown("---")
st.caption("💡 Designed for Learnages — elegant, responsive, and visually distinct blue theme. Perfect for embedding into Google Sites or GitHub Pages.")
