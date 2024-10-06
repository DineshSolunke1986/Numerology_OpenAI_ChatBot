import streamlit as st
import datetime
import openai
import matplotlib.pyplot as plt # type: ignore
from fpdf import FPDF # type: ignore
import unicodedata
import os

# Set OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

# Helper functions for numerology calculations
def reduce_number(num):
    """Reduce a number to a single digit, unless it's a master number (11, 22, 33)."""
    while num > 9 and num not in [11, 22, 33]:
        num = sum([int(i) for i in str(num)])
    return num

def calculate_life_path_number(birthdate):
    """Calculate the Life Path Number from a birthdate."""
    total = birthdate.year + birthdate.month + birthdate.day
    return reduce_number(total)

def letter_to_number(letter):
    """Convert a letter to a corresponding number."""
    return ord(letter.lower()) - 96

def calculate_expression_number(full_name):
    """Calculate the Expression Number from the full name."""
    total = sum([letter_to_number(c) for c in full_name if c.isalpha()])
    return reduce_number(total)

def calculate_soul_urge_number(full_name):
    """Calculate the Soul Urge Number using vowels from the full name."""
    vowels = "aeiou"
    total = sum([letter_to_number(c) for c in full_name if c.lower() in vowels])
    return reduce_number(total)

def calculate_personality_number(full_name):
    """Calculate the Personality Number using consonants from the full name."""
    vowels = "aeiou"
    total = sum([letter_to_number(c) for c in full_name if c.isalpha() and c.lower() not in vowels])
    return reduce_number(total)

# Functions to generate AI responses using OpenAI
def get_career_advice(life_path_number):
    prompt = f"Based on numerology, the Life Path Number is {life_path_number}. Provide detailed career advice for this person. Keep description precise, points and small"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

def get_relationship_advice(soul_urge_number):
    prompt = f"Based on numerology, the Soul Urge Number is {soul_urge_number}. Provide relationship advice for this person.Keep description precise, points and small"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

def get_action_steps(expression_number):
    prompt = f"Based on numerology, the Expression Number is {expression_number}. Provide actionable steps for achieving life goals. Keep description precise, points and small"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

# Visualize numerology numbers
def plot_numerology_numbers(life_path, expression, soul_urge, personality):
    labels = ['Life Path', 'Expression', 'Soul Urge', 'Personality']
    numbers = [life_path, expression, soul_urge, personality]
    fig, ax = plt.subplots()
    ax.bar(labels, numbers)
    ax.set_ylabel("Numerology Values")
    ax.set_title("Numerology Insights")
    st.pyplot(fig)


# Helper function to strip non-ASCII characters
# Helper function to strip non-ASCII characters
def remove_non_ascii(text):
    """Normalize the text to remove or replace non-ASCII characters."""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# Generate a downloadable PDF report
def generate_pdf_report(life_path, expression, soul_urge, personality, career_advice, relationship_advice, action_steps):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Report title
    pdf.cell(200, 10, txt="Numerology Report", ln=True, align="C")
    pdf.ln(10)

    # Add numerology numbers
    pdf.cell(200, 10, txt=f"Life Path: {life_path}", ln=True)
    pdf.cell(200, 10, txt=f"Expression: {expression}", ln=True)
    pdf.cell(200, 10, txt=f"Soul Urge: {soul_urge}", ln=True)
    pdf.cell(200, 10, txt=f"Personality: {personality}", ln=True)
    pdf.ln(10)

    # Add AI-generated advice (cleaning up non-ASCII characters)
    pdf.cell(200, 10, txt="Career Advice:", ln=True)
    pdf.multi_cell(0, 10, remove_non_ascii(career_advice))
    
    pdf.cell(200, 10, txt="Relationship Advice:", ln=True)
    pdf.multi_cell(0, 10, remove_non_ascii(relationship_advice))

    pdf.cell(200, 10, txt="Action Steps:", ln=True)
    pdf.multi_cell(0, 10, remove_non_ascii(action_steps))

    # Save the PDF file
    pdf_file = "numerology_report.pdf"
    pdf.output(pdf_file)

    return pdf_file


# Streamlit application
st.title("Numerology-Based Chatbot")

# Sidebar for user input
with st.sidebar:
    st.header("User Input")
    full_name = st.text_input("Enter your full name (as on your birth certificate):")
    birthdate = st.date_input("Enter your birthdate (YYYY-MM-DD):", 
                              value=datetime.date(2000, 1, 1),  # Default value
                              min_value=datetime.date(1970, 1, 1),  # Start from 1980
                              max_value=datetime.date.today())  # Present day
    submit_button = st.button("Get Insights")

# Create two columns for layout: left for user input, right for results
col1, col2 = st.columns([1, 2])  # Col1 is 1/3 width, Col2 is 2/3

if submit_button:
    if full_name and birthdate:
        # Show a spinner while generating insights
        with st.spinner("Generating insights, please wait..."):
            # Perform numerology calculations
            life_path = calculate_life_path_number(birthdate)
            expression_number = calculate_expression_number(full_name)
            soul_urge_number = calculate_soul_urge_number(full_name)
            personality_number = calculate_personality_number(full_name)

            # Get AI-generated insights
            career_advice = get_career_advice(life_path)
            relationship_advice = get_relationship_advice(soul_urge_number)
            action_steps = get_action_steps(expression_number)

            # Display results on the right side (col2)
            with col2:
                st.subheader("Numerology Insights")

                # Expandable sections for each numerology number
                with st.expander("Numerology Numbers", expanded=True):
                    st.write(f"**Life Path Number**: {life_path}")
                    st.write(f"**Expression Number**: {expression_number}")
                    st.write(f"**Soul Urge Number**: {soul_urge_number}")
                    st.write(f"**Personality Number**: {personality_number}")

                # Show AI-generated insights in expandable sections with limited width
                st.subheader("AI-Generated Advice")

                with st.expander("Career Advice", expanded=True):
                    st.write(f"<div style='max-width: 800px;'>{career_advice}</div>", unsafe_allow_html=True)

                with st.expander("Relationship Advice", expanded=True):
                    st.write(f"<div style='max-width: 800px;'>{relationship_advice}</div>", unsafe_allow_html=True)

                with st.expander("Action Steps", expanded=True):
                    st.write(f"<div style='max-width: 800px;'>{action_steps}</div>", unsafe_allow_html=True)

                # Plot numerology numbers
                plot_numerology_numbers(life_path, expression_number, soul_urge_number, personality_number)
                
                # Option to download the results as PDF (same as before)
                pdf_file = generate_pdf_report(life_path, expression_number, soul_urge_number, personality_number, career_advice, relationship_advice, action_steps)
                with open(pdf_file, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name=pdf_file)

    else:
        st.error("Please enter both your full name and birthdate.")
