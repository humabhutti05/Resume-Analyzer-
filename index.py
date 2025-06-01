import streamlit as st
import os
import heapq
import fitz  # PyMuPDF for PDF reading
from collections import defaultdict

# -------------------- CONFIG -------------------- #
st.set_page_config(page_title="Resume Analyzer", layout="centered", page_icon="📄")

# -------------------- STYLES -------------------- #
dark_mode_css = """
<style>
    /* Background & font */
    body, .main {
        background-color: #0f172a;
        color: #e0e7ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Title style */
    h1, h2, h3 {
        color: #7dd3fc;
    }
    /* Input styling */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: #cbd5e1;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #3b82f6;
        font-weight: 600;
    }
    /* File uploader styling */
    .stFileUploader>div>div>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stFileUploader>div>div>button:hover {
        background-color: #2563eb;
    }
    /* Resume card */
    .resume-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 15px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgb(59 130 246 / 0.3);
        transition: transform 0.3s ease;
    }
    .resume-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgb(59 130 246 / 0.6);
    }
    /* Skill badge */
    .skill-badge {
        background-color: #3b82f6;
        padding: 4px 12px;
        border-radius: 15px;
        color: white;
        margin-right: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 6px;
    }
    /* Progress bar container */
    .progress-container {
        background-color: #334155;
        border-radius: 15px;
        height: 18px;
        margin-top: 8px;
    }
    /* Progress bar fill */
    .progress-fill {
        background-color: #3b82f6;
        height: 100%;
        border-radius: 15px;
        text-align: right;
        padding-right: 8px;
        font-weight: 700;
        font-size: 0.8rem;
        color: white;
        line-height: 18px;
    }
    /* Info box styling */
    .stAlert {
        background-color: #1e293b;
        color: #94a3b8;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 10px;
        font-size: 1rem;
        margin-top: 20px;
    }
</style>
"""

st.markdown(dark_mode_css, unsafe_allow_html=True)

# -------------------- HEADER -------------------- #
st.markdown("<h1 style='text-align:center;'>📄 AI-Powered Resume Analyzer & Ranker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:1.1rem;'>Upload resumes (.txt or .pdf) and see who fits best for the job based on skills!</p>", unsafe_allow_html=True)

# -------------------- INPUT: SKILLS -------------------- #
skills_input = st.text_input("🔍 Enter target job skills (comma-separated)", "Python, Machine Learning, AI, SQL", help="Example: Python, Machine Learning, AI, SQL")
target_skills = [skill.strip().lower() for skill in skills_input.split(",") if skill.strip()]

# -------------------- FILE UPLOAD -------------------- #
uploaded_files = st.file_uploader(
    "📤 Upload resumes (.txt or .pdf) — multiple allowed",
    type=["txt", "pdf"],
    accept_multiple_files=True,
    help="Drag & drop or click to select multiple resume files"
)

# -------------------- PROCESSING -------------------- #
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()

def render_skill_badge(skill):
    return f"<span class='skill-badge'>{skill.title()}</span>"

def render_progress_bar(percentage):
    # percentage between 0 and 100
    return f"""
    <div class='progress-container'>
      <div class='progress-fill' style='width:{percentage}%;'>{percentage:.0f}%</div>
    </div>
    """

if uploaded_files and target_skills:
    st.markdown("### 📊 Resume Ranking Results")

    results = []
    for resume_file in uploaded_files:
        content = ""
        if resume_file.name.endswith(".pdf"):
            try:
                content = extract_text_from_pdf(resume_file)
            except Exception as e:
                st.warning(f"Could not read PDF: {resume_file.name}. Error: {e}")
                continue
        elif resume_file.name.endswith(".txt"):
            content = resume_file.read().decode('utf-8').lower()

        skill_count = defaultdict(int)
        score = 0

        for skill in target_skills:
            count = content.count(skill)
            skill_count[skill] = count
            score += count

        matched_skills = [skill for skill in target_skills if skill_count[skill] > 0]
        results.append((-score, resume_file.name, matched_skills, score, skill_count))

    # Sort by score
    heapq.heapify(results)

    rank = 1
    while results:
        neg_score, filename, matched, score, skill_counts = heapq.heappop(results)
        with st.container():
            st.markdown(f"""
            <div class="resume-card">
                <h3>#{rank} 🧑‍💼 {filename}</h3>
                <p><strong>Score:</strong> {score}</p>
                <p><strong>Matched Skills:</strong></p>
                <p>{''.join([render_skill_badge(skill) for skill in matched]) if matched else "<em>None</em>"}</p>
            """, unsafe_allow_html=True)

            # Display progress bars for each matched skill relative to max count for scaling
            max_count = max(skill_counts.values()) if skill_counts else 1
            for skill in matched:
                count = skill_counts[skill]
                percentage = (count / max_count) * 100 if max_count > 0 else 0
                st.markdown(f"<strong>{skill.title()}:</strong>", unsafe_allow_html=True)
                st.markdown(render_progress_bar(percentage), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        rank += 1

else:
    st.info("ℹ️ Enter skills and upload resumes to begin analysis.")
