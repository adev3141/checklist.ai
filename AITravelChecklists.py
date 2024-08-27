import streamlit as st
from gemini_model import GeminiModel  # Placeholder for the actual import
from fpdf import FPDF
import datetime

# Custom CSS for the design system
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Overpass:wght@400;600&display=swap');

    body {
        font-family: 'Overpass', sans-serif;
        background-color: #2B2D42;
        color: #FA3E01;
    }
    .title {
        font-size: 2.5em;
        color: #FA3E01;
        text-align: center;
    }
    .subtitle {
        font-size: 1.5em;
        background: linear-gradient(90deg, #FF490E 0%, #FF7B02 100%);
        -webkit-background-clip: text;
        color: transparent;
        text-align: left;
        margin-bottom: 20px;
    }
    .container {
        padding: 20px;
        border-radius: 10px;
        background-color: #FF7B02;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF490E 0%, #FF7B02 100%);
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #FF490E 0%, #FF7B02 100%);
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .itinerary {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        color: #2B2D42;
    }
    .itinerary h3 {
        color: #FA3E01;
    }
    .itinerary h4 {
        color: #1B435A;
    }
    .itinerary p {
        font-style: italic;
    }
    .question {
        font-size: 1.3em;
        color: #FA3E01;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0F1116;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the logo
st.image("logo/hunza.ai.png", use_column_width=False, width=75)

# Instructions
with st.expander("Instructions"):
    st.write("""
    1. Enter the travel destination.
    2. Provide the starting date.
    3. Provide the number of nights.
    4. Choose the season.
    5. Specify the trip type.
    6. Enter the group size.
    7. Provide any special considerations.
    """)

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state['responses'] = {}
if 'page' not in st.session_state:
    st.session_state['page'] = 0
if 'checklist' not in st.session_state:
    st.session_state['checklist'] = ""

gemini_model = GeminiModel()

# Questions and inputs
questions = [
    ("Where are you planning to travel in Pakistan?", 'destination', 'text'),
    ("When will your trip start?", 'start_date', 'date'),
    ("How many nights will you be staying?", 'nights', 'number'),
    ("Which season are you traveling in?", 'season', 'select', ['Summer', 'Winter', 'Spring', 'Autumn']),
    ("What type of trip are you planning?", 'trip_type', 'select', ['Adventure', 'Leisure', 'Family', 'Business']),
    ("How many people are traveling with you?", 'group_size', 'number'),
    ("Any special considerations?", 'special_considerations', 'text')
]

# Helper function to ask questions
def ask_question(question, key, input_type="text", options=None):
    st.markdown(f'<div class="question">{question}</div>', unsafe_allow_html=True)
    
    if input_type == "date":
        response = st.date_input("", key=key, label_visibility="hidden")
    elif input_type == "number":
        response = st.number_input("", key=key, label_visibility="hidden", min_value=1)
    elif input_type == "select":
        response = st.selectbox("", options, key=key, label_visibility="hidden")
    else:
        response = st.text_input("", key=key, label_visibility="hidden")
    
    if st.button('Next'):
        st.session_state.responses[key] = response
        st.session_state.page += 1
        st.rerun()

# Generate PDF
def generate_pdf(checklist_text, logo_path):
    checklist_text = checklist_text.replace('\u2013', '-').replace('\u2014', '--')
    subtitle = "\n\nNote: This checklist is AI-generated and may be subject to change."
    complete_text = checklist_text + subtitle
    
    class PDF(FPDF):
        def header(self):
            self.image(logo_path, 10, 8, 33)
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, 'Travel Checklist', ln=True, align='C')
            self.ln(20)
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, complete_text.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# Format checklist for display
def format_checklist(checklist):
    sections = checklist.split('##')
    formatted_checklist = ""
    for section in sections:
        if section.strip():
            formatted_checklist += f"<div class='itinerary'>{section.strip()}</div>"
    formatted_checklist += "<div class='itinerary'><p><em>Note: This checklist is AI-generated and may be subject to change.</em></p></div>"
    return formatted_checklist

# Main interaction flow
with st.container():
    if st.session_state.page < len(questions):
        question, key, input_type, *options = questions[st.session_state.page]
        ask_question(question, key, input_type, options[0] if options else None)
    else:
        # Calculate the number of days based on start date and nights
        responses = st.session_state.responses
        start_date = responses['start_date']
        nights = int(responses['nights'])
        end_date = start_date + datetime.timedelta(days=nights)
        num_days = (end_date - start_date).days + 1

        st.write("Generating your customized checklist...")
        prompt = gemini_model.create_prompt(responses, num_days)
        st.session_state.checklist = gemini_model.generate_checklist(prompt)

        formatted_checklist = format_checklist(st.session_state.checklist)
        
        # Display the checklist
        st.markdown(f'<div class="itinerary"><h4>Travel Checklist for {responses["destination"]} ({num_days} days)</h4>{formatted_checklist}</div>', unsafe_allow_html=True)

        # Generate and provide a download link for the PDF
        if st.session_state.checklist:
            logo_path = "logo/logo.png"
            pdf_content = generate_pdf(st.session_state.checklist, logo_path)
            st.download_button(
                label="Download Checklist as PDF",
                data=pdf_content,
                file_name=f"checklist_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

    if st.session_state.page > 0:
        if st.button('Previous'):
            st.session_state.page -= 1
            st.rerun()

# Footer
st.markdown('<div class="footer">All rights reserved | Created by ADev</div>', unsafe_allow_html=True)
