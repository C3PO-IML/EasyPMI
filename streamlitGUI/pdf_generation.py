import io
import math
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT

import streamlit as st
from core import time_converter

# --- Custom Paragraph Styles ---
styles = getSampleStyleSheet()

# Input column style 
style_input = ParagraphStyle(
    name='InputStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=11,
    alignment=TA_LEFT,
)
# Style specific for the Input Title 
style_input_title = ParagraphStyle(
    name='InputTitleStyle',
    parent=style_input, 
    fontName='Helvetica-Bold', 
)


# Results column - Normal text
style_results_normal = ParagraphStyle(
    name='ResultNormal',
    parent=styles['BodyText'],
    fontName='Times-Roman',
    fontSize=11,
    leading=13,
    alignment=TA_LEFT,
)

# Results column - Section Title
style_results_title = ParagraphStyle(
    name='ResultTitle',
    parent=style_results_normal,
    fontName='Times-Bold',
)


def generate_pdf() -> bytes:
    """
    Generates a PDF report in memory.
    Inputs on left, Results on right. Updated styling and no graph titles.
    """
    buffer = io.BytesIO()
    width_p, height_p = letter
    c = pdf_canvas.Canvas(buffer, pagesize=letter)

    margin = 0.5*inch
    top_y = height_p - margin

    # --- Calculate Widths and Positions X ---
    total_available_width = width_p - 2 * margin
    space_between_cols = 0.2 * inch
    # Input column (Right, ~1/4)
    input_area_width = total_available_width * 0.25
    # Results column (Left, ~3/4)
    results_area_width = total_available_width - input_area_width - space_between_cols
    # Positions X
    results_area_x = margin # Results at left
    input_area_x = margin + results_area_width + space_between_cols # Inputs at right

    # --- Conditional Main Title ---
    report_title = "Estimation of Post-Mortem Interval"
    if st.session_state.get('use_reference_datetime', False):
        report_title = "Estimation of Time of Death"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, top_y - 0.3*inch, report_title)
    current_y = top_y - 0.7*inch

    # --- Input Parameters Column (Right) ---
    input_col_y_start = current_y 
    grey_background = HexColor("#F0F0F0")

    user_inputs_text = []
    # ADD "User Input:" TITLE TO THE LIST
    user_inputs_text.append("<u><b>User Input:</b></u>")

    if st.session_state.get('use_reference_datetime', False):
        ref_date_str = st.session_state.reference_date.strftime("%d/%m/%Y")
        ref_time_str = st.session_state.reference_time.strftime("%Hh%M")
        user_inputs_text.append(f"<b>Reference Time:</b> {ref_date_str} - {ref_time_str}")
    else:
        user_inputs_text.append("<b>Reference Time:</b> Not Used")
    user_inputs_text.extend([
        f"<b>Tympanic temp.:</b> {st.session_state.input_t_tympanic or 'N/A'} °C",
        f"<b>Rectal temp.:</b> {st.session_state.input_t_rectal or 'N/A'} °C",
        f"<b>Ambient temp.:</b> {st.session_state.input_t_ambient or 'N/A'} °C",
        f"<b>Body weight:</b> {st.session_state.input_M or 'N/A'} kg",
    ])
    cf_mode = st.session_state.get('correction_mode', 'Predefined')
    if cf_mode == "Manual input":
         user_inputs_text.append(f"<b>Corrective factor:</b> {st.session_state.input_Cf or 'N/A'} (Manual)")
    else:
        user_inputs_text.append(f"<b>Corrective factor mode:</b> Predefined")
        user_inputs_text.append(f"<b>Body condition:</b> {st.session_state.body_condition}")
        user_inputs_text.append(f"<b>Environment:</b> {st.session_state.environment}")
        user_inputs_text.append(f"<b>Supporting base:</b> {st.session_state.supporting_base}")
    user_inputs_text.extend([
        f"<b>Idiomuscular reaction:</b> {st.session_state.idiomuscular_reaction}",
        f"<b>Rigor:</b> {st.session_state.rigor}",
        f"<b>Lividity:</b> {st.session_state.lividity}",
        f"<b>Lividity disappearance:</b> {st.session_state.lividity_disappearance}",
        f"<b>Lividity mobility:</b> {st.session_state.lividity_mobility}"
    ])

    # --- Calculate height and draw inputs ---
    input_y_pos = input_col_y_start
    total_input_height_calculated = 0
    input_paragraphs = []
    first_input = True

    for i, text in enumerate(user_inputs_text):
        is_input_title = (i == 0)
        style = style_input_title if is_input_title else style_input
        p = Paragraph(text.replace('\n', '<br/>'), style)
        input_paragraphs.append(p)
        w, h = p.wrapOn(c, input_area_width, height_p)
        spacing = 8 if is_input_title else 2 
        total_input_height_calculated += h + spacing

    # Draw grey background
    bg_padding = 5
    bg_y = input_col_y_start + bg_padding
    bg_height = total_input_height_calculated + bg_padding
    c.setFillColor(grey_background)
    c.rect(input_area_x - bg_padding, bg_y - bg_height,
           input_area_width + 2 * bg_padding, bg_height,
           stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)

    # Draw the input parameters text
    first_input = True
    for p in input_paragraphs:
        is_input_title = first_input
        w, h = p.wrapOn(c, input_area_width, height_p)
        if input_y_pos - h < margin: break
        p.drawOn(c, input_area_x, input_y_pos - h)
        spacing = 8 if is_input_title else 2
        input_y_pos -= (h + spacing)
        first_input = False

    # --- Calculation Results Column (Right) ---
    results_y_start = input_col_y_start 
    results_y_pos = results_y_start

    def draw_results_paragraph(text, x_start, current_y, available_width, is_title=False):
        nonlocal results_y_pos
        clean_text = text.replace('**', '')
        if is_title:
            final_text = f"<u>{clean_text}</u>" 
            style = style_results_title 
        else:
            final_text = clean_text
            style = style_results_normal 

        p = Paragraph(final_text.replace('\n', '<br/>'), style)
        w, h = p.wrapOn(c, available_width, height_p)

        if current_y - h < margin:
            c.showPage()
            current_y = height_p - margin
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin, top_y - 0.3*inch, report_title)
            current_y = top_y - 0.7*inch
            results_y_pos = current_y

        p.drawOn(c, x_start, current_y - h)
        return current_y - (h + 3)

    if hasattr(st.session_state, 'results') and st.session_state.results:
        results_sections = st.session_state.results.split('\n\n')
        for section in results_sections:
            if not section.strip(): continue
            lines = section.split('\n')
            first_line = True
            for line in lines:
                 if not line.strip(): continue
                 is_section_title = first_line and line.startswith("**")
                 results_y_pos = draw_results_paragraph(line, results_area_x, results_y_pos, results_area_width, is_title=is_section_title)
                 first_line = False
            results_y_pos -= 10

    # --- Page 2: Graphs ---
    c.showPage()
    c.setPageSize(landscape(letter))
    width_land, height_land = landscape(letter)

    margin_land = 0.5*inch
    graph_area_top = height_land - margin_land 
    graph_area_bottom = margin_land
    graph_area_height = graph_area_top - graph_area_bottom
    graph_row_height = graph_area_height / 2 - 0.1*inch 

    # Define graph drawing areas
    graph1_x = margin_land
    graph1_width = width_land / 2 - margin_land - 0.1*inch
    graph1_y_bottom = graph_area_top - graph_row_height 

    graph2_x = width_land / 2 + 0.1*inch
    graph2_width = width_land / 2 - margin_land - 0.1*inch
    graph2_y_bottom = graph1_y_bottom 

    graph3_x = margin_land
    graph3_width = width_land - 2 * margin_land
    graph3_y_bottom = graph_area_bottom 

    def draw_image_scaled(img_reader, x, y_bottom, max_w, max_h):
        img_width, img_height = img_reader.getSize()
        if img_width <= 0 or img_height <= 0: return
        scale = min(max_w / img_width, max_h / img_height)
        final_width = img_width * scale
        final_height = img_height * scale
        draw_x = x + (max_w - final_width) / 2
        draw_y = y_bottom + (max_h - final_height) / 2 
        c.drawImage(img_reader, draw_x, draw_y, width=final_width, height=final_height)

    # --- Plot ---
    if hasattr(st.session_state, 'fig_henssge_rectal') and st.session_state.fig_henssge_rectal is not None:
        img_data_1 = io.BytesIO()
        st.session_state.fig_henssge_rectal.savefig(img_data_1, format='png', bbox_inches='tight')
        img_data_1.seek(0)
        img_1 = ImageReader(img_data_1)
        draw_image_scaled(img_1, graph1_x, graph1_y_bottom, graph1_width, graph_row_height) 
        img_data_1.close()

    if hasattr(st.session_state, 'fig_henssge_brain') and st.session_state.fig_henssge_brain is not None:
        img_data_2 = io.BytesIO()
        st.session_state.fig_henssge_brain.savefig(img_data_2, format='png', bbox_inches='tight')
        img_data_2.seek(0)
        img_2 = ImageReader(img_data_2)
        draw_image_scaled(img_2, graph2_x, graph1_y_bottom, graph2_width, graph_row_height) 
        img_data_2.close()

    if hasattr(st.session_state, 'fig_comparison') and st.session_state.fig_comparison is not None:
        img_data_3 = io.BytesIO()
        st.session_state.fig_comparison.savefig(img_data_3, format='png', bbox_inches='tight')
        img_data_3.seek(0)
        img_3 = ImageReader(img_data_3)
        draw_image_scaled(img_3, graph3_x, graph3_y_bottom, graph3_width, graph_row_height)
        img_data_3.close()

    # --- Finalize PDF ---
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes