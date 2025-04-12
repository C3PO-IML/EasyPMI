import io
import math

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

import streamlit as st


def generate_pdf() -> bytes:
    """
    Generates a PDF in memory and returns the bytes.
    """
    buffer = io.BytesIO()
    width, height = letter
    c = pdf_canvas.Canvas(buffer, pagesize=letter)

    def draw_formatted_text(text, x, y, is_bold=False):
        """Helper function to draw text with proper formatting"""
        if is_bold:
            c.setFont("Helvetica-Bold", 12)
        else:
            c.setFont("Helvetica", 12)
        c.drawString(x, y, text.strip('*'))  # Remove any remaining * characters

    # Page 1: Title and data
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Post-Mortem Interval Calculation Results")

    # Calculate text width and height for user inputs
    c.setFont("Helvetica", 10)
    user_inputs = [
        f"Tympanic temperature : {st.session_state.input_t_tympanic or 'Not specified'} °C",
        f"Rectal temperature : {st.session_state.input_t_rectal or 'Not specified'} °C",
        f"Ambient temperature : {st.session_state.input_t_ambient or 'Not specified'} °C",
        f"Body weight : {st.session_state.input_M or 'Not specified'} kg",
        f"Corrective factor : {st.session_state.input_Cf or 'Not specified'}",
        f"Body condition : {st.session_state.body_condition or 'Not specified'}",
        f"Environment : {st.session_state.environment or 'Not specified'}",
        f"Supporting base : {st.session_state.supporting_base or 'Not specified'}",
        f"Idiomuscular reaction : {st.session_state.idiomuscular_reaction or 'Not specified'}",
        f"Rigor : {st.session_state.rigor or 'Not specified'}",
        f"Lividity : {st.session_state.lividity or 'Not specified'}",
        f"Lividity disappearance : {st.session_state.lividity_disappearance or 'Not specified'}",
        f"Lividity mobility : {st.session_state.lividity_mobility or 'Not specified'}"
    ]

    rect_width = 200
    line_height = 15
    margin = 10
    x_start = width - rect_width - margin

    # Calculate required height for text
    total_height = margin * 2
    for text in user_inputs:
        text_width = c.stringWidth(text, "Helvetica", 10)
        lines_needed = max(1, math.ceil(text_width / (rect_width - 2 * margin)))
        total_height += line_height * lines_needed

    # Draw blue rectangle with calculated height
    rect_height = total_height
    c.setStrokeColorRGB(0, 0, 1)  # Blue color
    c.setFillColorRGB(0.9, 0.9, 1)  # Light blue fill color
    c.rect(x_start, height - 50 - rect_height, rect_width, rect_height, stroke=1, fill=1)

    # Reset text color to black
    c.setFillColorRGB(0, 0, 0)

    # Draw user inputs with word wrapping
    y_position = (height - 55 - rect_height) + rect_height - margin
    for text in user_inputs:
        words = text.split()
        line = []
        for word in words:
            line.append(word)
            test_line = ' '.join(line)
            text_width = c.stringWidth(test_line, "Helvetica", 10)

            if text_width > rect_width - 2 * margin:
                # Draw the line without the last word
                line.pop()
                c.drawString(x_start + margin, y_position, ' '.join(line))
                line = [word]
                y_position -= line_height

        # Draw remaining words
        if line:
            c.drawString(x_start + margin, y_position, ' '.join(line))
            y_position -= line_height

    # Draw results starting right under title
    if hasattr(st.session_state, 'results') and st.session_state.results:
        y_position = height - 80  # Start under title
        text_lines = st.session_state.results.split('\n')

        for line in text_lines:
            if y_position < 50:
                c.showPage()
                y_position = height - 50

            if not line.strip():  # Skip empty lines but maintain spacing
                y_position -= 15
                continue

            if line.startswith('**') and line.endswith('**'):
                # Entirely bold line
                draw_formatted_text(line, 50, y_position, is_bold=True)
            elif '**' in line:
                # Line contains bold sections
                parts = line.split('**')
                x_position = 50
                for i, part in enumerate(parts):
                    if not part:  # Skip empty parts
                        continue
                    is_bold = (i % 2 == 1)  # Alternate between normal and bold
                    draw_formatted_text(part, x_position, y_position, is_bold=is_bold)
                    # Calculate next x position based on text width
                    font = "Helvetica-Bold" if is_bold else "Helvetica"
                    x_position += c.stringWidth(part, font, 12)
            else:
                # Normal text
                draw_formatted_text(line, 50, y_position, is_bold=False)

            y_position -= 15

    # Page 2: Graphs
    c.showPage()
    c.setPageSize(landscape(letter))
    width, height = landscape(letter)

    # Graph area
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 30, "Graph 1 : Henssge Evolution (Rectal)")
    c.drawString(width / 2 + 50, height - 30, "Graph 2 : Henssge Evolution (Brain)")
    c.drawString(50, height / 2, "Graph 3 : Methods Comparison")

    # Add graphs if they exist
    if hasattr(st.session_state, 'fig_henssge_rectal') and st.session_state.fig_henssge_rectal is not None:
        img_data_1 = io.BytesIO()
        st.session_state.fig_henssge_rectal.savefig(img_data_1, format='png')
        img_data_1.seek(0)
        img_1 = ImageReader(img_data_1)
        img_width_1, img_height_1 = img_1.getSize()
        scale_1 = min((width / 2 - 30) / img_width_1, (height / 2 - 30) / img_height_1)
        final_width_1 = img_width_1 * scale_1
        final_height_1 = img_height_1 * scale_1
        c.drawImage(img_1, 20, height - 36 - final_height_1, width=final_width_1, height=final_height_1)
        img_data_1.close()

    if hasattr(st.session_state, 'fig_henssge_brain') and st.session_state.fig_henssge_brain is not None:
        img_data_2 = io.BytesIO()
        st.session_state.fig_henssge_brain.savefig(img_data_2, format='png')
        img_data_2.seek(0)
        img_2 = ImageReader(img_data_2)
        img_width_2, img_height_2 = img_2.getSize()
        scale_2 = min((width / 2 - 30) / img_width_2, (height / 2 - 30) / img_height_2)
        final_width_2 = img_width_2 * scale_2
        final_height_2 = img_height_2 * scale_2
        c.drawImage(img_2, width / 2 + 20, height - 36 - final_height_2, width=final_width_2, height=final_height_2)
        img_data_2.close()

    if hasattr(st.session_state, 'fig_comparison') and st.session_state.fig_comparison is not None:
        img_data_3 = io.BytesIO()
        st.session_state.fig_comparison.savefig(img_data_3, format='png')
        img_data_3.seek(0)
        img_3 = ImageReader(img_data_3)
        img_width_3, img_height_3 = img_3.getSize()
        scale_3 = min((width - 20) / img_width_3, (height / 2 - 20) / img_height_3)
        final_width_3 = img_width_3 * scale_3
        final_height_3 = img_height_3 * scale_3
        c.drawImage(img_3, 00, 00, width=final_width_3, height=final_height_3)
        img_data_3.close()

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
