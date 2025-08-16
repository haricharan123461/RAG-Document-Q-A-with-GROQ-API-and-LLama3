import streamlit as st
from langchain_groq import ChatGroq
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# Load API key securely from Streamlit Secrets
# -----------------------------
# In Streamlit Secrets:
# GROQ_API_KEY = "your_groq_key_here"
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
groq_api_key = os.environ["GROQ_API_KEY"]

# Initialize Groq LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("AI-Powered Meeting Notes Summarizer & Sharer")

# Step 1: Upload transcript
uploaded_file = st.file_uploader("Upload transcript (txt)", type=["txt"])

# Step 2: Custom instruction/prompt
user_instruction = st.text_input(
    "Enter custom instruction (e.g., 'Summarize in bullet points', 'Highlight action items')"
)

summary_text = ""

if uploaded_file and user_instruction:
    # Read transcript content
    transcript = uploaded_file.read().decode("utf-8")

    # Generate summary using Groq
    prompt_text = f"""
    Summarize the following transcript according to this instruction:
    {user_instruction}

    Transcript:
    {transcript}
    """

    with st.spinner("Generating summary..."):
        response = llm.invoke({"input": prompt_text})
        summary_text = response["output"]

    # Step 3: Editable summary
    editable_summary = st.text_area(
        "Generated Summary (Editable)", value=summary_text, height=300
    )

    # Step 4: Share via email
    st.subheader("Share summary via email")
    recipient_emails = st.text_area(
        "Enter recipient emails (comma separated)", value=""
    )
    sender_email = st.text_input("Your email address")
    sender_password = st.text_input(
        "Your email password (or app password)", type="password"
    )

    if st.button("Send Email") and editable_summary and recipient_emails and sender_email and sender_password:
        try:
            # Prepare email
            recipients = [email.strip() for email in recipient_emails.split(",")]
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = "Meeting Summary"
            msg.attach(MIMEText(editable_summary, "plain"))

            # Send email via SMTP (Gmail example)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
            server.quit()

            st.success("Summary sent successfully!")
        except Exception as e:
            st.error(f"Error sending email: {e}")
