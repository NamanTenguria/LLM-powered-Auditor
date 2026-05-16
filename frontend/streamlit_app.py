import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AuditIQ",
    page_icon="🧠",
    layout="wide"
)

st.sidebar.title("AuditIQ")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Upload Documents",
        "Ask AuditIQ",
        "Risk Review",
        "Finding Generator",
        "Dashboard",
        "Export Report",
        "Admin"
    ]
)

st.title("AuditIQ: GenAI Audit Risk Review Assistant")

if page == "Home":
    st.subheader("Welcome to AuditIQ")

    st.write(
        "AuditIQ is a local GenAI-powered audit risk review assistant. "
        "It helps auditors upload evidence, ask questions, extract risk signals, "
        "generate audit findings, view dashboard metrics, and export a summary report."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("LLM", "llama3.2:3b")
    col2.metric("Embeddings", "nomic-embed-text")
    col3.metric("Vector DB", "ChromaDB")

    st.divider()

    st.subheader("Core Workflow")

    st.markdown(
        """
        1. **Upload Documents**  
           Upload audit policies, logs, evidence files, or prior findings.

        2. **Ask AuditIQ**  
           Ask natural language questions using RAG over uploaded documents.

        3. **Risk Review**  
           Automatically extract risks such as missing approvals, delayed access removal, vendor gaps, or documentation issues.

        4. **Finding Generator**  
           Convert selected risks into structured audit findings.

        5. **Dashboard**  
           View risk counts, severity breakdown, recent risks, and generated findings.

        6. **Export Report**  
           Download a Markdown audit summary report.
        """
    )

    st.divider()

    st.subheader("Backend Connection Test")

    if st.button("Check Backend Health"):
        try:
            response = requests.get(f"{BACKEND_URL}/")

            if response.status_code == 200:
                st.success("Backend is connected.")
                st.json(response.json())
            else:
                st.error("Backend responded, but something went wrong.")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to backend. "
                "Make sure FastAPI is running on port 8000."
            )
elif page == "Upload Documents":
    st.subheader("Upload Audit Documents")

    st.write(
        "Upload audit policies, evidence files, logs, or prior findings. "
        "The backend will extract text, create embeddings, and store the document in ChromaDB."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "csv", "pdf", "docx"]
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Policy Document",
            "Control Description",
            "Audit Evidence",
            "Access Log",
            "Vendor Evidence",
            "Prior Finding",
            "Other"
        ]
    )

    if st.button("Process Document"):
        if uploaded_file is None:
            st.error("Please upload a file first.")
        else:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            data = {
                "document_type": document_type
            }

            with st.spinner("Uploading, extracting text, creating embeddings, and storing in ChromaDB..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        data=data,
                        timeout=180
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.success("Document processed successfully.")
                        st.json(result)

                        st.info(
                            "You can now go to Ask AuditIQ and ask questions about this document."
                        )

                    else:
                        st.error("Upload failed.")
                        st.write(response.text)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to FastAPI backend. "
                        "Make sure it is running on port 8000."
                    )

                except requests.exceptions.Timeout:
                    st.error(
                        "Upload timed out. Local embeddings can be slow. "
                        "Try a smaller file first."
                    )

elif page == "Ask AuditIQ":
    st.subheader("Ask AuditIQ")

    st.write(
        "Ask a question about the audit documents already stored in ChromaDB."
    )

    example_questions = [
        "What access control risks are present?",
        "Based on the access control policy and access log, which users violated the 24-hour access removal rule?",
        "Are there any missing approvals?",
        "What vendor risks are present?",
        "Summarize the main audit issues in simple language."
    ]

    selected_example = st.selectbox(
        "Choose an example question, or write your own below",
        example_questions
    )

    question = st.text_area(
        "Question",
        value=selected_example,
        height=120
    )

    if st.button("Ask"):
        if not question.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner("Retrieving evidence and generating answer..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": question},
                        timeout=120
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.success("Answer generated.")

                        st.subheader("Answer")
                        st.write(result["answer"])

                        st.subheader("Sources Used")

                        sources = result.get("sources", [])

                        if sources:
                            for index, source in enumerate(sources, start=1):
                                with st.expander(
                                    f"Source {index}: {source.get('file_name')} | Chunk {source.get('chunk_id')}"
                                ):
                                    st.write(source.get("preview"))
                        else:
                            st.info("No sources returned.")

                    else:
                        st.error("The backend returned an error.")
                        st.write(response.text)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to FastAPI backend. "
                        "Make sure it is running on port 8000."
                    )

                except requests.exceptions.Timeout:
                    st.error(
                        "The request timed out. Local Ollama models can be slow. "
                        "Try again with a shorter question."
                    )


elif page == "Risk Review":
    st.subheader("Risk Review")

    st.write(
        "Run an automated audit risk scan over the documents stored in ChromaDB. "
        "The system will extract risks, assign severity, and save results to SQLite."
    )

    if st.button("Run Risk Review"):
        with st.spinner("Scanning audit evidence and extracting risks..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/extract-risks",
                    timeout=180
                )

                if response.status_code == 200:
                    result = response.json()

                    if "error" in result:
                        st.error(result["error"])
                        st.write(result.get("raw_response"))
                    else:
                        st.success(
                            f"Risk review completed. Risks extracted: {result.get('risk_count', 0)}"
                        )
                        st.json(result)

                else:
                    st.error("Risk extraction failed.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI backend. "
                    "Make sure it is running on port 8000."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "Risk extraction timed out. Local Ollama models can be slow. "
                    "Try again or reduce the number of uploaded documents."
                )

    st.divider()

    st.subheader("Extracted Risks")

    try:
        risks_response = requests.get(
            f"{BACKEND_URL}/risks",
            timeout=60
        )

        if risks_response.status_code == 200:
            risks = risks_response.json().get("risks", [])

            if risks:
                st.dataframe(
                    risks,
                    use_container_width=True
                )
            else:
                st.info("No risks extracted yet. Click Run Risk Review first.")

        else:
            st.error("Could not load risks.")
            st.write(risks_response.text)

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI backend. "
            "Make sure it is running on port 8000."
        )


elif page == "Finding Generator":
    st.subheader("Finding Generator")

    st.write(
        "Select an extracted risk and generate a structured audit finding."
    )

    try:
        risks_response = requests.get(
            f"{BACKEND_URL}/risks",
            timeout=60
        )

        if risks_response.status_code == 200:
            risks = risks_response.json().get("risks", [])

            if not risks:
                st.info("No risks available. Run Risk Review first.")
            else:
                risk_options = {}

                for risk in risks:
                    label = (
                        f"Risk {risk['risk_id']} | "
                        f"{risk['risk_category']} | "
                        f"{risk['severity']}"
                    )
                    risk_options[label] = risk["risk_id"]

                selected_label = st.selectbox(
                    "Select a risk",
                    list(risk_options.keys())
                )

                selected_risk_id = risk_options[selected_label]

                selected_risk = next(
                    risk for risk in risks
                    if risk["risk_id"] == selected_risk_id
                )

                st.subheader("Selected Risk")
                st.json(selected_risk)

                if st.button("Generate Finding"):
                    with st.spinner("Generating audit finding..."):
                        response = requests.post(
                            f"{BACKEND_URL}/generate-finding",
                            json={"risk_id": selected_risk_id},
                            timeout=180
                        )

                        if response.status_code == 200:
                            finding = response.json()

                            if "error" in finding:
                                st.error(finding["error"])
                                st.write(finding.get("raw_response"))
                            else:
                                st.success("Finding generated.")

                                st.subheader(finding.get("title", "Audit Finding"))

                                st.markdown(f"**Condition:** {finding.get('condition')}")
                                st.markdown(f"**Criteria:** {finding.get('criteria_text')}")
                                st.markdown(f"**Cause:** {finding.get('cause')}")
                                st.markdown(f"**Risk / Impact:** {finding.get('impact')}")
                                st.markdown(f"**Recommendation:** {finding.get('recommendation')}")
                                st.markdown(f"**Severity:** {finding.get('severity')}")

                        else:
                            st.error("Finding generation failed.")
                            st.write(response.text)

        else:
            st.error("Could not load risks.")
            st.write(risks_response.text)

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI backend. "
            "Make sure it is running on port 8000."
        )

    st.divider()

    st.subheader("Generated Findings")

    try:
        findings_response = requests.get(
            f"{BACKEND_URL}/findings",
            timeout=60
        )

        if findings_response.status_code == 200:
            findings = findings_response.json().get("findings", [])

            if findings:
                st.dataframe(
                    findings,
                    use_container_width=True
                )
            else:
                st.info("No findings generated yet.")

        else:
            st.error("Could not load findings.")
            st.write(findings_response.text)

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI backend. "
            "Make sure it is running on port 8000."
        )

elif page == "Dashboard":
    st.subheader("Audit Risk Dashboard")

    st.write(
        "This dashboard summarizes uploaded documents, extracted risks, generated findings, "
        "and human-review items from SQLite."
    )

    try:
        response = requests.get(
            f"{BACKEND_URL}/dashboard",
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Documents Reviewed", data.get("documents_reviewed", 0))
            col2.metric("Risks Detected", data.get("risks_detected", 0))
            col3.metric("High Severity Risks", data.get("high_severity_risks", 0))
            col4.metric("Findings Generated", data.get("findings_generated", 0))

            col5, col6, col7, col8 = st.columns(4)

            col5.metric("Medium Severity", data.get("medium_severity_risks", 0))
            col6.metric("Low Severity", data.get("low_severity_risks", 0))
            col7.metric("Human Review Required", data.get("human_review_required", 0))
            col8.metric(
                "Review Rate",
                f"{round((data.get('human_review_required', 0) / data.get('risks_detected', 1)) * 100, 1) if data.get('risks_detected', 0) else 0}%"
            )

            st.divider()

            st.subheader("Risks by Category")

            risks_by_category = data.get("risks_by_category", [])

            if risks_by_category:
                st.bar_chart(
                    {
                        row["risk_category"]: row["count"]
                        for row in risks_by_category
                    }
                )
            else:
                st.info("No risk category data available yet.")

            st.subheader("Risks by Severity")

            risks_by_severity = data.get("risks_by_severity", [])

            if risks_by_severity:
                st.bar_chart(
                    {
                        row["severity"]: row["count"]
                        for row in risks_by_severity
                    }
                )
            else:
                st.info("No severity data available yet.")

            st.divider()

            st.subheader("Recent Risks")

            recent_risks = data.get("recent_risks", [])

            if recent_risks:
                st.dataframe(
                    recent_risks,
                    use_container_width=True
                )
            else:
                st.info("No risks extracted yet.")

            st.subheader("Recent Findings")

            recent_findings = data.get("recent_findings", [])

            if recent_findings:
                st.dataframe(
                    recent_findings,
                    use_container_width=True
                )
            else:
                st.info("No findings generated yet.")

        else:
            st.error("Could not load dashboard.")
            st.write(response.text)

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to FastAPI backend. "
            "Make sure it is running on port 8000."
        )
elif page == "Export Report":
    st.subheader("Export Audit Report")

    st.write(
        "Generate a Markdown audit summary report using uploaded documents, "
        "extracted risks, and generated findings stored in SQLite."
    )

    if st.button("Generate Report"):
        with st.spinner("Generating audit summary report..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/export-report",
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    report_content = data.get("report", "")

                    st.success("Report generated successfully.")

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Documents", data.get("document_count", 0))
                    col2.metric("Risks", data.get("risk_count", 0))
                    col3.metric("Findings", data.get("finding_count", 0))

                    st.divider()

                    st.subheader("Report Preview")

                    st.markdown(report_content)

                    st.download_button(
                        label="Download Markdown Report",
                        data=report_content,
                        file_name="auditiq_audit_summary_report.md",
                        mime="text/markdown"
                    )

                else:
                    st.error("Could not generate report.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI backend. "
                    "Make sure it is running on port 8000."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "Report generation timed out. Try again."
                )
elif page == "Admin":
    st.subheader("Admin Controls")

    st.warning(
        "These actions permanently clear local project data. "
        "Use them only when you want a fresh demo."
    )

    st.divider()

    st.subheader("Reset Options")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear SQLite Records"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/admin/reset-database",
                    timeout=60
                )

                if response.status_code == 200:
                    st.success(response.json().get("message"))
                else:
                    st.error("Failed to clear SQLite records.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")

    with col2:
        if st.button("Clear ChromaDB"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/admin/reset-chroma",
                    timeout=60
                )

                if response.status_code == 200:
                    st.success(response.json().get("message"))
                else:
                    st.error("Failed to clear ChromaDB.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("Clear Uploaded Files"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/admin/reset-uploads",
                    timeout=60
                )

                if response.status_code == 200:
                    st.success(response.json().get("message"))
                else:
                    st.error("Failed to clear uploaded files.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")

    with col4:
        if st.button("Reset Everything"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/admin/reset-all",
                    timeout=60
                )

                if response.status_code == 200:
                    st.success(response.json().get("message"))
                    st.info(
                        "After resetting everything, upload documents again before using Ask AuditIQ or Risk Review."
                    )
                else:
                    st.error("Failed to reset everything.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")

    st.divider()

    st.subheader("Recommended Fresh Demo Order")

    st.markdown(
        """
        1. Click **Reset Everything**
        2. Go to **Upload Documents**
        3. Upload the five sample audit files
        4. Go to **Ask AuditIQ** and ask a question
        5. Go to **Risk Review** and extract risks
        6. Go to **Finding Generator** and generate findings
        7. Go to **Dashboard**
        8. Go to **Export Report**
        """
    )