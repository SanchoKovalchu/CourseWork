# ------------------- IMPORTS -------------------

# PDF Report Libraries
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

# Custom files
from query_data import query_rag
from chroma_db import update_chroma, clear_database
from db import add_report

# Other imports
from datetime import datetime
import re
import io
import os
from nicegui import ui
import PyPDF2

# Function to parse risks from a text using a specific pattern
def parse_risks(text):
    risks = []
    risk_pattern = re.compile(
        r'Risk \d+:\s*- Risk Name: (.*?)\s*- Risk Description: (.*?)\s*- Probability: (.*?)\s*- Context Explanation: (.*?)\s*- Risk Mitigation Way: (.*?)\s*(?=Risk \d+:|$)',
        re.DOTALL)
    matches = risk_pattern.findall(text)

    for match in matches:
        risk = {
            "Risk Name": match[0].strip(),
            "Risk Description": match[1].strip(),
            "Probability": match[2].strip(),
            "Context Explanation": match[3].strip(),
            "Risk Mitigation Way": match[4].strip()
        }
        risks.append(risk)

    return risks

# Function to create a risk report PDF
def create_risk_report(risks, current_date):
    # Create an in-memory file object
    buffer = io.BytesIO()
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    style_subheading = styles['Heading2']

    # Define a custom style for the risk section
    style_risk = ParagraphStyle(
        'RiskStyle',
        parent=style_normal,
        spaceBefore=12,
        spaceAfter=12,
        leftIndent=12,
        rightIndent=12,
        bulletIndent=12,
        leading=15
    )

    elements = []

    # Add a title
    elements.append(Paragraph("Risk Management Report", style_heading))
    elements.append(Paragraph(f"Date: {current_date}", style_subheading))
    elements.append(Spacer(1, 0.4 * inch))

    # Add risks to the document
    for idx, risk in enumerate(risks, start=1):
        elements.append(Paragraph(f"Risk {idx}:", style_subheading))
        elements.append(Paragraph(f"<b>Risk Name:</b> {risk['Risk Name']}", style_risk))
        elements.append(Paragraph(f"<b>Risk Description:</b> {risk['Risk Description']}", style_risk))
        elements.append(Paragraph(f"<b>Probability:</b> {risk['Probability']}", style_risk))
        elements.append(Paragraph(f"<b>Context Explanation:</b> {risk['Context Explanation']}", style_risk))
        elements.append(Paragraph(f"<b>Risk Mitigation Way:</b> {risk['Risk Mitigation Way']}", style_risk))
        elements.append(Spacer(1, 0.2 * inch))

    # Build the PDF
    doc.build(elements)
    # Move to the beginning of the StringIO buffer
    buffer.seek(0)

    # Get the PDF data from the buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    print("PDF has been generated successfully!")
    return pdf_data

# Function to update the Chroma database and generate a risk report
def generate_report(project_id) -> None:
    clear_database()  # Clear the existing Chroma database
    update_chroma(project_id)  # Update the Chroma database with new project data
    generate_risk_report(project_id)  # Generate the risk report for the project

# Function to get the current date in a specific format
def get_current_date():
    current_date = datetime.now()
    current_date_str = current_date.strftime("%d %B %Y")
    return current_date_str

# Function to extract text from PDF files in a given directory
def extract_text_from_pdf(data_path):
    text = ""

    data_dir = os.listdir(data_path)
    for file in data_dir:
        text += "\n ------------------------------------------- " + file + " ------------------------------------------- \n"
        with open(data_path + "/" + file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for page_number in range(num_pages):
                page = reader.pages[page_number]
                text += page.extract_text()
    return text

# Function to generate a risk report PDF and add it to the database
def generate_risk_report(project_id):
    current_date = get_current_date()  # Get the current date
    report_name = "Risk Report " + current_date + ".pdf"  # Create the report name
    risk_attributes = " with following risk attributes (Risk Name, Risk Description (impact from this risk), Probability in %(0-100), Context explanation (why are you write this risk), Risk mitigation way) "
    risks_format = """
    Please provide a list of project risks in the following format: 
    Risk [number]: 
    - Risk Name: [text] 
    - Risk Description: [text] 
    - Probability: [percent] 
    - Context Explanation: [text] 
    - Risk Mitigation Way: [text] 
    Ensure that each risk is numbered sequentially and includes all the specified details. 
    Example: 
    Risk 1: 
    - Risk Name: Model Accuracy
    - Risk Description: Inaccurate estimation of Functional Points (FPA) and Configuration Points (CPA) due to inadequacies or errors in the LLM model. 
    - Probability: 20% 
    - Context Explanation: The success of this project heavily relies on the accuracy of the developed NLP model for FPA and CPA estimation. 
    - Risk Mitigation Way: Implement rigorous testing methodologies, including cross-validation techniques, to ensure model accuracy. 
    """

    general_risks = enter_question('Please write a list of risks' + risk_attributes + 'based on given context ONLY from project charter, NOT from meeting minutes' + risks_format)
    risks = parse_risks(general_risks)  # Parse the general risks into a structured format
    print(risks)
    pdf_data = create_risk_report(risks, current_date)  # Create the risk report PDF using the list of risk details
    add_report(report_name, pdf_data, project_id)  # Add the generated PDF report to the database
    clear_database()  # Clear the Chroma database
    ui.navigate.reload()  # Reload the UI

# Function to enter a question and get a response from the RAG model
def enter_question(question):
    response = query_rag(question)
    return response
