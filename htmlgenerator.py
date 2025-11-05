# app.py
import streamlit as st
import html

st.set_page_config(page_title="🌐 Premium Text → HTML Formatter", layout="wide")

st.title("🌐 Universal Text → HTML Formatter — Pro Edition")
st.markdown("""
This tool converts your ready-made text into a **beautifully formatted HTML page**  
with premium design, responsive layout, and your chosen title at the top.  
It never changes your content — only wraps and styles it professionally.
""")

# === INPUT ===
st.subheader("1️⃣ Paste Your Ready Content")
text_input = st.text_area("✏️ Paste your text or lesson content here:", height=400, placeholder="Paste text exactly as you want it shown...")

# === SIDEBAR SETTINGS ===
st.sidebar.header("⚙️ HTML Customization Options")
page_title = st.sidebar.text_input("Page Title / Heading:", "Lesson 1: Greetings")
primary_color = st.sidebar.color_picker("Primary Theme Color", "#004aad")
accent_color = st.sidebar.color_picker("Accent Color", "#7fb3ff")
bg_color = st.sidebar.color_picker("Background Color", "#f9fbff")
font_family = st.sidebar.selectbox("Font Style", ["Poppins", "Inter", "Roboto", "Open Sans", "Lato"], index=0)
include_html_wrapper = st.sidebar.checkbox("Include full HTML <html>/<body> structure", value=True)
download_enabled = st.sidebar.checkbox("Enable Download Button", value=True)
show_code = st.sidebar.checkbox("Show HTML Code", value=True)

# === HTML GENERATION FUNCTION ===
def generate_html(content: str, title: str) -> str:
    # Escape special characters except HTML tags
    safe_content = content.replace("\n", "<br>\n")
    heading = f"<h1>{html.escape(title)}</h1>"

    # Modern CSS with responsive layout
    css = f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;600&display=swap');
      body {{
        background: {bg_color};
        font-family: '{font_family}', sans-serif;
        color: #1b1b1b;
        line-height: 1.8;
        padding: 40px;
        max-width: 900px;
        margin: 0 auto;
      }}
      h1 {{
        text-align: center;
        color: {primary_color};
        font-size: 2em;
        border-bottom: 3px solid {accent_color};
        padding-bottom: 10px;
        margin-bottom: 30px;
      }}
      .content-box {{
        background: white;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        padding: 30px 40px;
        font-size: 1.05rem;
      }}
      .content-box p {{
        margin: 10px 0;
      }}
      .content-box br {{
        line-height: 1.6;
      }}
      footer {{
        text-align: center;
        font-size: 0.85rem;
        color: #555;
        margin-top: 40px;
      }}
    </style>
    """

    body = f"""
    <div class="content-box">
      {safe_content}
    </div>
    <footer>Generated using Learnages Universal HTML Formatter © 2025</footer>
    """

    # Combine all parts
    final_html = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<title>{html.escape(title)}</title>\n{css}</head>\n<body>\n{heading}\n{body}\n</body>\n</html>"
    return final_html

# === GENERATE BUTTON ===
st.subheader("2️⃣ Generate Premium HTML")
if st.button("⚡ Generate HTML"):
    if not text_input.strip():
        st.error("Please paste your content first.")
    else:
        result_html = generate_html(text_input, page_title)
        st.success("✅ Premium HTML generated successfully!")

        if show_code:
            st.code(result_html, language="html")

        if download_enabled:
            st.download_button(
                "⬇️ Download HTML File",
                data=result_html.encode("utf-8"),
                file_name="premium_formatted.html",
                mime="text/html",
            )

        st.markdown("---")
        st.markdown("### 🔍 Live Preview")
        st.components.v1.html(result_html, height=700, scrolling=True)

st.markdown("---")
st.caption("💡 This version is built for professional-quality output — elegant, mobile-friendly, and ready for Google Sites or GitHub Pages embedding.")
