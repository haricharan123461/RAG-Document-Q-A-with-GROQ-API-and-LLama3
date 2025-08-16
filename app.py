# app.py
import os
import streamlit as st
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# LangChain / Groq imports
from langchain_groq import ChatGroq
from langchain import LLMChain
from langchain.prompts import PromptTemplate

# -------------------------
# Secure keys via Streamlit secrets
# -------------------------
# In Streamlit Cloud: Settings -> Secrets -> add GROQ_API_KEY = "..."
if "GROQ_API_KEY" not in st.secrets:
    st.error("GROQ_API_KEY not found in Streamlit secrets. Add it in app settings.")
    st.stop()

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
groq_api_key = os.environ["GROQ_API_KEY"]

# -------------------------
# Initialize the Groq chat model
# -------------------------
# model_name can be changed based on your Groq plan / available models
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

# -------------------------
# Prompt template and chain (uses LLMChain to avoid low-level invoke issues)
# -------------------------
# Keep template small and explicit. We'll pass 'instruction' and 'transcript'
template = """You are an assistant that follows instructions precisely.
Instruction: {instruction}

Transcript:
{transcript}

Provide a concise, structured summary based on the instruction.
"""
prompt = PromptTemplate(input_variables=["instruction", "transcript"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

# -------------------------
# Streamlit UI
# -------------------------
st.title("Meeting Notes Summarizer & Sharer (Groq)")

st.markdown("Upload a `.txt` transcript, give an instruction (e.g., 'bullet points for execs'), generate a summary, edit it, then download or email it.")

# Upload transcript (text)
uploaded_file = st.file_uploader("Upload transcript (.txt)", type=["txt"])

# Custom instruction
user_instruction = st.text_input("Custom instruction / prompt", value="Summarize in bullet points highlighting action items")

# Buttons & state
if "last_summary" not in st.session_state:
    st.session_state["last_summary"] = ""

col1, col2 = st.columns([1, 1])
with col1:
    generate_btn = st.button("Generate Summary")
with col2:
    clear_btn = st.button("Clear")

if clear_btn:
    st.session_state["last_summary"] = ""
    st.experimental_rerun()

# Generate summary
if generate_btn:
    if not uploaded_file:
        st.error("Please upload a transcript (.txt) file first.")
    elif not user_instruction.strip():
        st.error("Please provide a custom instruction/prompt.")
    else:
        try:
            transcript = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Couldn't read uploaded file: {e}")
            transcript = None

        if transcript:
            with st.spinner("Generating summary..."):
                start = time.time()
                try:
                    # Use the LLMChain to generate a string response
                    summary_text = chain.run({"instruction": user_instruction, "transcript": transcript})
                except Exception as e:
                    st.error(f"Error generating summary from Groq: {e}")
                    st.stop()

                elapsed = time.time() - start
                st.success(f"Summary generated in {elapsed:.2f} s")
                st.session_state["last_summary"] = summary_text

# Show editable summary area (if any)
editable = st.text_area("Generated Summary (editable)", value=st.session_state.get("last_summary", ""), height=300)

# Update stored summary if user edits it
if editable != st.session_state.get("last_summary", ""):
    st.session_state["last_summary"] = editable

# Download button for the edited summary
if st.session_state.get("last_summary", "").strip():
    st.download_button("Download Edited Summary (.txt)", st.session_state["last_summary"], file_name="summary.txt", mime="text/plain")

# Email sharing UI
st.markdown("---")
st.subheader("Share summary via email")
recipient_emails = st.text_input("Recipient emails (comma separated)")
sender_email = st.text_input("Sender email (for SMTP)")
sender_smtp_server = st.text_input("SMTP server (e.g., smtp.gmail.com)")
sender_smtp_port = st.text_input("SMTP port (e.g., 587)", value="587")
sender_password = st.text_input("Sender email password / app password", type="password")

def send_email(sender, password, smtp_server, smtp_port, recipients, subject, body):
    try:
        recipients_list = [r.strip() for r in recipients.split(",") if r.strip()]
        if not recipients_list:
            return False, "No recipient emails provided."

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients_list)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients_list, msg.as_string())
        server.quit()
        return True, "Email sent successfully."
    except Exception as e:
        return False, str(e)

if st.button("Send Email"):
    if not st.session_state.get("last_summary", "").strip():
        st.error("No summary available to send. Generate one first.")
    elif not (recipient_emails and sender_email and sender_smtp_server and sender_password):
        st.error("Provide sender details, SMTP server, and recipient emails.")
    else:
        ok, msg = send_email(
            sender_email,
            sender_password,
            sender_smtp_server,
            sender_smtp_port,
            recipient_emails,
            "Meeting Summary",
            st.session_state["last_summary"]
        )
        if ok:
            st.success(msg)
        else:
            st.error(f"Email failed: {msg}")
