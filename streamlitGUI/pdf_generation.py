import io
import math
from datetime import datetime
import re

from core.datetime_utils import format_datetime

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

import streamlit as st

def generate_pdf() -> bytes:
    """
    Generates a PDF in memory and returns the bytes.
    Accurately calculates input box height to prevent overflow.
    """
    buffer = io.BytesIO()
    width, height = letter
    c = pdf_canvas.Canvas(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_normal.fontSize = 10
    # style_bold = styles['Heading6'] # Keep avoiding this for now
    # style_bold.fontSize = 10

    # --- Helper using ReportLab Paragraph ---
    def draw_paragraph(text, x, y, max_width, style):
        # (draw_paragraph function remains the same as before)
        p = Paragraph(text, style)
        try:
            p_width, p_height = p.wrapOn(c, max_width, height)
        except Exception as e:
            print(f"Error wrapping paragraph text: {text}")
            print(f"Error: {e}")
            error_text = f"Error rendering text block: {e}"
            p = Paragraph(error_text, style)
            p_width, p_height = p.wrapOn(c, max_width, height)

        if y - p_height < 30:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Post-Mortem Interval Calculation Results")
            y = height - 80
            # If inputs section needs redrawing on new page, add logic here

        p.drawOn(c, x, y - p_height)
        return y - p_height

    # Page 1: Title and data
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Post-Mortem Interval Calculation Results")

    # --- User Inputs Section ---
    c.setFont("Helvetica-Bold", 11)
    input_section_title_y = height - 70
    c.drawString(width - 250 - 10, input_section_title_y, "User Inputs")

    # --- Generate Input Text Lines ---
    input_texts = []
    # (Keep the logic to populate input_texts as before)
    if st.session_state.get('use_measurement_time', False):
        meas_date = st.session_state.get('measurement_date')
        meas_time = st.session_state.get('measurement_time')
        if meas_date and meas_time:
             dt = datetime.combine(meas_date, meas_time)
             input_texts.append(f"Measurement Time: {format_datetime(dt)}")
        else:
             input_texts.append("Measurement Time: Not fully specified")
    input_texts.extend([
        f"Tympanic temp: {st.session_state.get('input_t_tympanic', 'N/A')} °C",
        f"Rectal temp: {st.session_state.get('input_t_rectal', 'N/A')} °C",
        f"Ambient temp: {st.session_state.get('input_t_ambient', 'N/A')} °C",
        f"Body weight: {st.session_state.get('input_M', 'N/A')} kg",
    ])
    cf_mode = st.session_state.get('correction_mode', 'Predefined')
    input_texts.append(f"CF Mode: {cf_mode}")
    if cf_mode == "Manual input":
         input_texts.append(f"Manual CF: {st.session_state.get('input_Cf', 'N/A')}")
    else:
         input_texts.append(f"Body condition: {str(st.session_state.get('body_condition', 'N/A'))}")
         input_texts.append(f"Environment: {str(st.session_state.get('environment', 'N/A'))}")
         input_texts.append(f"Supporting base: {str(st.session_state.get('supporting_base', 'N/A'))}")
    input_texts.extend([
        f"Idiomuscular reaction: {str(st.session_state.get('idiomuscular_reaction', 'N/A'))}",
        f"Rigor: {str(st.session_state.get('rigor', 'N/A'))}",
        f"Lividity: {str(st.session_state.get('lividity', 'N/A'))}",
        f"Lividity disappearance: {str(st.session_state.get('lividity_disappearance', 'N/A'))}",
        f"Lividity mobility: {str(st.session_state.get('lividity_mobility', 'N/A'))}"
    ])

    # --- Pass 1: Calculate Total Height Needed for Inputs ---
    input_box_width = 250
    input_max_width = input_box_width - 10 # Text width inside box
    input_text_x = width - input_box_width - 10 + 5 # X position of text start
    total_input_height = 0
    line_spacing = 2 # Space between paragraphs
    box_padding = 10 # Top/Bottom padding inside the box

    if input_texts: # Only calculate if there's text
        for line in input_texts:
            p = Paragraph(line, style_normal)
            p_w, p_h = p.wrapOn(c, input_max_width, height) # Wrap to find height
            total_input_height += p_h + line_spacing
        total_input_height -= line_spacing # Remove trailing space
        total_input_height += box_padding # Add padding

    # --- Draw Input Box with Calculated Height ---
    input_box_height = total_input_height
    input_box_x = width - input_box_width - 10
    input_y_start = input_section_title_y - 15 # Y position for top of the box content
    input_box_y = input_y_start - input_box_height # Y position for bottom of the box

    # Ensure box doesn't go off page (adjust if needed)
    if input_box_y < 30 :
        print("Warning: Input section might be too tall for one page.")
        # Potentially add logic here to handle multi-page input section if required
        input_box_y = 30
        input_box_height = input_y_start - input_box_y


    c.setStrokeColorRGB(0, 0, 0.8)
    c.setFillColorRGB(0.9, 0.9, 1)
    # Only draw box if there's content
    if input_texts:
        c.rect(input_box_x, input_box_y, input_box_width, input_box_height, stroke=1, fill=1)
    c.setFillColorRGB(0, 0, 0) # Reset fill color

    # --- Pass 2: Draw Input Text Paragraphs ---
    current_input_y = input_y_start # Start drawing from the top of the content area
    if input_texts:
        for line in input_texts:
            p = Paragraph(line, style_normal)
            # Wrap again to get height for positioning (necessary for drawOn)
            p_w, p_h = p.wrapOn(c, input_max_width, height)
            # Draw the paragraph positioned from the top-left of its bounding box
            p.drawOn(c, input_text_x, current_input_y - p_h)
            current_input_y -= (p_h + line_spacing) # Move y down for next paragraph

    # --- Draw Results ---
    results_text = st.session_state.get('results', '')
    if results_text:
        c.setFont("Helvetica-Bold", 11) # Sub-header
        results_section_title_y = height - 70 # Align with input title
        c.drawString(50, results_section_title_y, "Calculation Results")
        results_y = results_section_title_y - 15 # Start below sub-header
        results_max_width = width - input_box_width - 40 # Available width left of input box

        # Format results text (using regex fix from previous step)
        formatted_results_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', results_text, flags=re.DOTALL)
        formatted_results_text = formatted_results_text.replace('\n', '<br/>')

        # Draw the results paragraph using the helper
        results_y = draw_paragraph(formatted_results_text, 50, results_y, results_max_width, style_normal)

    # --- Page 2: Graphs ---
    # (Graph drawing logic remains the same)
    c.showPage()
    c.setPageSize(landscape(letter))
    width_land, height_land = landscape(letter)
    c.setFont("Helvetica-Bold", 12)
    title_space = 30
    graph_area_height = (height_land / 2) - title_space - 10
    graph_area_width_half = (width_land / 2) - 30
    graph_area_height_bottom = height_land / 2 - title_space - 10
    graph_area_width_full = width_land - 40

    # Graph 1
    c.drawString(30, height_land - title_space, "Graph 1: Henssge Evolution (Rectal)")
    fig1 = st.session_state.get('fig_henssge_rectal')
    if fig1:
        img_data_1 = io.BytesIO()
        fig1.savefig(img_data_1, format='png', bbox_inches='tight')
        img_data_1.seek(0)
        img_1 = ImageReader(img_data_1)
        img_width_1, img_height_1 = img_1.getSize()
        scale_1 = min(graph_area_width_half / img_width_1, graph_area_height / img_height_1)
        final_width_1 = img_width_1 * scale_1
        final_height_1 = img_height_1 * scale_1
        x1 = 30 + (graph_area_width_half - final_width_1) / 2
        y1 = height_land - title_space - 5 - final_height_1
        c.drawImage(img_1, x1, y1, width=final_width_1, height=final_height_1, preserveAspectRatio=True)
        img_data_1.close()

    # Graph 2
    c.drawString(width_land / 2 + 30, height_land - title_space, "Graph 2: Henssge Evolution (Brain)")
    fig2 = st.session_state.get('fig_henssge_brain')
    if fig2:
        img_data_2 = io.BytesIO()
        fig2.savefig(img_data_2, format='png', bbox_inches='tight')
        img_data_2.seek(0)
        img_2 = ImageReader(img_data_2)
        img_width_2, img_height_2 = img_2.getSize()
        scale_2 = min(graph_area_width_half / img_width_2, graph_area_height / img_height_2)
        final_width_2 = img_width_2 * scale_2
        final_height_2 = img_height_2 * scale_2
        x2 = width_land / 2 + 30 + (graph_area_width_half - final_width_2) / 2
        y2 = height_land - title_space - 5 - final_height_2
        c.drawImage(img_2, x2, y2, width=final_width_2, height=final_height_2, preserveAspectRatio=True)
        img_data_2.close()

    # Graph 3
    c.drawString(30, height_land / 2 - title_space + 10, "Graph 3: Methods Comparison")
    fig3 = st.session_state.get('fig_comparison')
    if fig3:
        img_data_3 = io.BytesIO()
        fig3.savefig(img_data_3, format='png', bbox_inches='tight', dpi=300)
        img_data_3.seek(0)
        img_3 = ImageReader(img_data_3)
        img_width_3, img_height_3 = img_3.getSize()
        scale_3 = min(graph_area_width_full / img_width_3, graph_area_height_bottom / img_height_3)
        final_width_3 = img_width_3 * scale_3
        final_height_3 = img_height_3 * scale_3
        x3 = (width_land - final_width_3) / 2
        y3 = max(5, height_land / 2 - title_space - 10 - final_height_3)
        c.drawImage(img_3, x3, y3, width=final_width_3, height=final_height_3, preserveAspectRatio=True)
        img_data_3.close()


    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes