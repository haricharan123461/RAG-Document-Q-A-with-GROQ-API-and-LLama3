deployedlink[https://ai-powered-textsumarizer-sharer.streamlit.app/]



## **Project: AI-Powered Meeting Notes Summarizer & Sharer**

### **Objective**

Build a full-stack application that allows users to:

1. Upload meeting transcripts (text or PDF).
2. Provide custom instructions (e.g., “Summarize in bullet points” or “Highlight action items”).
3. Generate AI-powered summaries.
4. Edit the generated summaries.
5. Share the summaries via email.

---

### **Approach**

1. **Frontend**

   * Built using **Streamlit**, which provides a lightweight, interactive interface.
   * Features:

     * File uploader for transcripts.
     * Text input for custom instructions.
     * Editable summary text area.
     * Buttons for generating summary, clearing input, downloading, and sending email.

2. **Backend / AI Layer**

   * **Groq LLaMA model** via `langchain_groq`.
   * Use **LangChain `LLMChain`** with a `PromptTemplate` to safely format input for the Groq model.
   * Generates structured, accurate summaries based on the user’s instructions.

3. **Editable Summary**

   * After the AI generates a summary, the user can edit it directly in a Streamlit `text_area`.
   * Ensures flexibility and manual corrections before sharing.

4. **Email Sharing**

   * Users can provide sender email, SMTP server details, and recipient emails.
   * Uses Python’s `smtplib` and `email.mime` libraries to send edited summaries.
   * Optional: App passwords are recommended for Gmail accounts with 2FA.

---

### **Process Flow**

1. **User uploads transcript → Upload widget**
2. **User provides instruction → Text input**
3. **AI generates summary → LLMChain passes instruction & transcript → Groq model produces summary**
4. **Summary displayed in editable text area → User can edit**
5. **Download or send summary via email → smtplib sends email**

---

### **Tech Stack**

| Layer             | Technology / Library                    | Purpose                                                 |
| ----------------- | --------------------------------------- | ------------------------------------------------------- |
| Frontend          | Streamlit                               | Lightweight UI for uploading, input, and display        |
| AI / LLM          | Groq LLaMA (`langchain_groq`)           | Generate structured summaries from transcript text      |
| Prompt Handling   | LangChain `LLMChain` + `PromptTemplate` | Format input safely and interact with Groq API          |
| File Handling     | Python `io` / Streamlit Uploader        | Read uploaded `.txt` files                              |
| Email Sending     | Python `smtplib`, `email.mime`          | Send edited summary to recipients                       |
| Deployment        | Streamlit Cloud / Local                 | Deploy the app for users                                |
| Secret Management | Streamlit Secrets                       | Store API keys (Groq) securely without exposing in code |

---

### **Key Considerations**

* **Security**: API keys stored in Streamlit Secrets, not hardcoded.
* **Error Handling**: Handles missing transcripts, empty instructions, and email sending errors.
* **Flexibility**: Users can edit AI summaries and download them before sharing.
* **Scalability**: Supports additional features like PDF transcripts, multiple LLMs, or database storage.

---

### **Deployment**

* The app is deployable on **Streamlit Cloud**.
* Only the deployed link and working summary generation are required for submission.
* API keys are stored securely using **Streamlit Secrets** to prevent exposure.

---

### **Conclusion**

This project demonstrates a **full-stack AI application** integrating:

* AI model integration (Groq LLaMA)
* Interactive frontend (Streamlit)
* Secure handling of secrets
* Editable outputs and sharing functionality

It emphasizes **functionality over design** and ensures **user flexibility, security, and reliability**.

---

If you want, I can also **create a version with diagrams showing the workflow** of how transcript → AI summary → editable text → email works. This is usually helpful for the project submission.

Do you want me to make that diagram?



