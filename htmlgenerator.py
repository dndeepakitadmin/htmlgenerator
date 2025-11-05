# app.py
import streamlit as st
from bs4 import BeautifulSoup
import re
import html
import io
import os

# Optional AI integration (OpenAI)
USE_OPENAI = False
try:
    import openai
    USE_OPENAI = True
except Exception:
    USE_OPENAI = False

st.set_page_config(page_title="Universal Text & HTML Customizer", layout="wide")

st.title("🔧 Universal Text & HTML Customizer — Cloud")
st.markdown(
    "Paste text or upload HTML/text files, give an instruction (e.g. `Add top navigation linking each lesson`, "
    "`Apply Learnages blue theme`, `Convert to bilingual HTML table`), then click **Generate**. "
    "Optional: connect an OpenAI API key in Streamlit secrets for advanced natural-language edits."
)

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    st.markdown(
        "- The app auto-detects HTML vs plain text.\n"
        "- If you want advanced rewriting using OpenAI, add `OPENAI_API_KEY` to Streamlit secrets.\n"
        "- Toggle automatic heading-to-nav detection below."
    )
    auto_nav = st.checkbox("Auto-generate nav from headings (h1-h3)", value=True)
    show_pretty = st.checkbox("Prettify (format) output HTML", value=True)
    use_ai_if_available = st.checkbox("Use AI when API key is set (optional)", value=True)

# Input area
st.subheader("1) Input (paste or upload)")
col1, col2 = st.columns([3,1])
with col1:
    data_input = st.text_area("Paste text or HTML here", height=300, placeholder="Paste HTML or plain text...")
with col2:
    uploaded = st.file_uploader("Or upload file (.html, .txt)", type=["html", "htm", "txt"])
    if uploaded:
        raw = uploaded.read()
        try:
            data_input = raw.decode("utf-8")
        except:
            data_input = raw.decode("latin-1")
        st.success("File loaded into input box.")

st.subheader("2) Instruction / Prompt")
prompt = st.text_input("Describe what you want done", value="Add a top navigation linking to lessons and apply a blue theme", max_chars=1000)

# Utility functions
def is_html(text: str) -> bool:
    # simple heuristic
    if "<html" in text.lower() or "<body" in text.lower() or re.search(r"<[a-zA-Z]+\s*[^>]*>", text):
        return True
    return False

def generate_nav_from_headings(soup):
    headings = []
    for h in soup.find_all(re.compile('^h[1-3]$', re.I)):
        text = h.get_text(strip=True)
        if not text:
            continue
        # generate id if not exists
        if not h.has_attr("id"):
            safe_id = re.sub(r'\s+', '-', text.lower())
            safe_id = re.sub(r'[^a-z0-9\-]', '', safe_id)
            h['id'] = safe_id
        headings.append((h['id'], text))
    if not headings:
        return None
    nav = soup.new_tag("nav")
    nav['style'] = "background:#0466c8;color:white;padding:12px;border-radius:6px;margin-bottom:12px;"
    container = soup.new_tag("div")
    for i,(hid,txt) in enumerate(headings):
        a = soup.new_tag("a", href=f"#{hid}")
        a.string = txt
        a['style'] = "color:white;text-decoration:none;padding:6px;margin-right:8px;font-weight:600;"
        container.append(a)
        if i != len(headings)-1:
            sep = soup.new_tag("span")
            sep.string = " | "
            sep['style'] = "color:rgba(255,255,255,0.8);margin-right:8px;"
            container.append(sep)
    nav.append(container)
    return nav

def apply_blue_theme(soup):
    style_tag = soup.new_tag("style")
    css = """
    body { background:#f2f8ff; font-family: 'Poppins', Arial, sans-serif; color:#0b2545; padding:20px; }
    h1,h2,h3 { color:#023e8a; }
    table { border-collapse: collapse; width:100%; margin-top:10px; }
    table, th, td { border: 1px solid #cddff6; padding:8px; text-align:left; }
    a { color:#023e8a; }
    """
    style_tag.string = css
    # ensure head exists
    if soup.head is None:
        head = soup.new_tag("head")
        soup.insert(0, head)
    soup.head.append(style_tag)

def convert_plain_text_to_table(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # assume bilingual lines like "Kannada - Hindi - English" or comma separated
    rows = []
    for ln in lines:
        # try split by dash or tab or | or comma
        parts = [p.strip() for p in re.split(r'\s*[-\|,\/\t]\s*', ln) if p.strip()]
        if len(parts) == 1:
            # try whitespace split into 3 parts
            parts = ln.split(maxsplit=2)
        rows.append(parts)
    # build html table
    table_html = "<table>\n<thead>\n<tr>\n"
    # pick header based on max columns
    maxcols = max(len(r) for r in rows) if rows else 1
    headers = ["Col " + str(i+1) for i in range(maxcols)]
    for h in headers:
        table_html += f"<th>{html.escape(h)}</th>\n"
    table_html += "</tr>\n</thead>\n<tbody>\n"
    for r in rows:
        table_html += "<tr>\n"
        for i in range(maxcols):
            v = html.escape(r[i]) if i < len(r) else ""
            table_html += f"<td>{v}</td>\n"
        table_html += "</tr>\n"
    table_html += "</tbody>\n</table>\n"
    return table_html

def apply_request_rule_based(input_text, instruction, treat_as_html=True):
    """
    A set of rule-based operations to satisfy common instructions without AI.
    """
    inst = instruction.lower()
    if treat_as_html:
        soup = BeautifulSoup(input_text, "html.parser")
        # Add nav from headings
        if ("navigation" in inst or "nav" in inst or "menu" in inst) and auto_nav:
            nav = generate_nav_from_headings(soup)
            if nav:
                # put nav after body start
                if soup.body:
                    soup.body.insert(0, nav)
                else:
                    soup.insert(0, nav)
        # Apply blue theme
        if "blue" in inst or "theme" in inst or "learnages" in inst:
            apply_blue_theme(soup)
        # If asked to "minify" or "prettify" handled outside
        return str(soup)
    else:
        # plain text transformations
        out = input_text
        # Convert to HTML table if asked
        if any(k in inst for k in ["table", "convert to html table", "bilingual table"]):
            return convert_plain_text_to_table(input_text)
        # Wrap in <p> tags if asked
        if "wrap" in inst and "<p" in inst:
            paras = [f"<p>{html.escape(p)}</p>" for p in input_text.splitlines() if p.strip()]
            return "\n".join(paras)
        # default: return original text
        return out

# AI helper
def run_openai_transform(prompt, input_text):
    if not USE_OPENAI:
        return None
    # check for API key in Streamlit secrets
    key = None
    try:
        key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    openai.api_key = key
    # Build a system + user prompt to instruct the model to output ONLY the final HTML or text
    system = "You are a helpful assistant that only outputs valid HTML or plain text as requested. Do NOT add explanation. If the user asks to modify HTML, return only the modified HTML. If it's text->HTML conversion return only the HTML. Keep the output raw."
    user = f"INSTRUCTION:\n{prompt}\n\nINPUT:\n{input_text}\n\nRespond only with the final result (no commentary)."
    try:
        # ChatCompletion or newer API can be used; this uses ChatCompletion for compatibility.
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini", # if unavailable the user will need to configure model; you may change in secrets
            messages=[
                {"role":"system","content":system},
                {"role":"user","content":user}
            ],
            max_tokens=3000,
            temperature=0.2
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.warning(f"OpenAI call failed: {e}")
        return None

# PROCESSING
st.subheader("3) Generate")
if st.button("Generate"):
    if not data_input or not prompt:
        st.error("Please provide input and an instruction.")
    else:
        with st.spinner("Processing..."):
            treat_html = is_html(data_input)
            result = None

            # Try AI if allowed and available
            if use_ai_if_available and USE_OPENAI:
                ai_out = run_openai_transform(prompt, data_input)
                if ai_out:
                    result = ai_out

            # If AI not used or failed, use rule-based
            if not result:
                result = apply_request_rule_based(data_input, prompt, treat_as_html=treat_html)

            # Prettify HTML if requested and result seems like HTML
            if show_pretty and ("<html" in result.lower() or "<body" in result.lower() or re.search(r"<[a-zA-Z]+[^>]*>", result)):
                try:
                    pretty = BeautifulSoup(result, "html.parser").prettify()
                    result = pretty
                except Exception:
                    pass

            st.success("Done. Preview below.")
            st.code(result, language="html" if ("<" in result and ">" in result) else "text")

            # Download button
            bname = "output.html" if "<" in result and ">" in result else "output.txt"
            st.download_button("Download Output", data=result.encode("utf-8"), file_name=bname, mime="text/html" if bname.endswith(".html") else "text/plain")

            # Quick copy
            st.markdown("**Copy output** (select and copy from the preview above).")

st.markdown("---")
st.caption("Built for Learnages — you can deploy this file directly to Streamlit Cloud. For advanced AI edits configure OPENAI_API_KEY in Streamlit Secrets. Rule-based ops work offline.")
