import streamlit as st
from datetime import date, time, datetime
from core.datetime_utils import combine_date_time
from core import compute
from core.constants import IdiomuscularReactionType, SupportingBase, EnvironmentType, BodyCondition, RigorType, LividityType, LividityMobilityType, LividityDisappearanceType
from core.input_parameters import InputParameters
from streamlitGUI import plot
from streamlitGUI.help import build_help_section
from streamlitGUI.pdf_generation import generate_pdf
from streamlitGUI.tools import convert_decimal_separator


def _build_input_parameters() -> InputParameters:
    """
    Constructs an InputParameters object from the current Streamlit session state.
    
    This function extracts all user inputs from the Streamlit session state and converts
    them to appropriate types needed for the calculation engine. Text inputs are 
    converted from string to float values where appropriate.
    
    Returns:
    --------
    InputParameters
        An object containing all parameters needed for PMI calculations
    
    Notes:
    ------
    - Numeric inputs are processed through convert_decimal_separator() to handle
      different decimal formats (comma vs point)
    - Empty string inputs are converted to None to indicate missing data
    - Enumeration values are passed directly from the session state
    """
    measurement_dt = None
    if st.session_state.use_measurement_time:
        measurement_dt = combine_date_time(
            st.session_state.measurement_date,
            st.session_state.measurement_time
        )
        if measurement_dt is None:
             st.warning("Please provide both date and time for measurement reference.", icon="⚠️")

    # --- Determine User Corrective Factor --- ADDED Logic to pass user_corrective_factor if mode is Manual
    user_cf = None
    if st.session_state.correction_mode == "Manual input" and st.session_state.input_Cf:
        try:
            user_cf = convert_decimal_separator(st.session_state.input_Cf)
        except ValueError:
             st.error(f"Invalid format for manual Corrective factor: {st.session_state.input_Cf}")
             user_cf = None # Reset or keep as None if invalid

    return InputParameters(
        tympanic_temperature=convert_decimal_separator(st.session_state.input_t_tympanic) if st.session_state.input_t_tympanic else None,
        rectal_temperature=convert_decimal_separator(st.session_state.input_t_rectal) if st.session_state.input_t_rectal else None,
        ambient_temperature=convert_decimal_separator(st.session_state.input_t_ambient) if st.session_state.input_t_ambient else None,
        body_mass=convert_decimal_separator(st.session_state.input_M) if st.session_state.input_M else None,
        body_condition=st.session_state.body_condition,
        environment=st.session_state.environment,
        supporting_base=st.session_state.supporting_base,
        idiomuscular_reaction=st.session_state.idiomuscular_reaction,
        user_corrective_factor=user_cf,
        rigor_type=st.session_state.rigor,
        lividity=st.session_state.lividity,
        lividity_disappearance=st.session_state.lividity_disappearance,
        lividity_mobility=st.session_state.lividity_mobility,
        measurement_datetime=measurement_dt
        )

def _init_state() -> None:
    """
    Initializes the Streamlit session state with default values.
    
    This function checks for the existence of each required session state variable
    and initializes it with an appropriate default value if not already present.
    It ensures that all necessary variables exist before the application renders.
    
    The initialization includes:
    - Temperature input fields (empty strings)
    - Body parameters (empty strings or default enumerations)
    - Thanatological signs (default to NOT_SPECIFIED)
    - Result storage variables (empty string or None for figures)
    Returns:
        None
    """
    if 'input_t_tympanic' not in st.session_state:
        st.session_state.input_t_tympanic = ""
    if 'input_t_rectal' not in st.session_state:
        st.session_state.input_t_rectal = ""
    if 'input_t_ambient' not in st.session_state:
        st.session_state.input_t_ambient = ""
    if 'input_M' not in st.session_state:
        st.session_state.input_M = ""
    if 'correction_mode' not in st.session_state:
        st.session_state.correction_mode = "Predefined (using dropdown lists)"
    if 'input_Cf' not in st.session_state:
        st.session_state.input_Cf = ""
    if 'body_condition' not in st.session_state:
        st.session_state.body_condition = BodyCondition.NOT_SPECIFIED
    if 'environment' not in st.session_state:
        st.session_state.environment = EnvironmentType.NOT_SPECIFIED
    if 'supporting_base' not in st.session_state:
        st.session_state.supporting_base = SupportingBase.NOT_SPECIFIED
    if 'idiomuscular_reaction' not in st.session_state:
        st.session_state.idiomuscular_reaction = IdiomuscularReactionType.NOT_SPECIFIED
    if 'rigor' not in st.session_state:
        st.session_state.rigor = RigorType.NOT_SPECIFIED
    if 'lividity' not in st.session_state:
        st.session_state.lividity = LividityType.NOT_SPECIFIED
    if 'lividity_disappearance' not in st.session_state:
        st.session_state.lividity_disappearance = LividityDisappearanceType.NOT_SPECIFIED
    if 'lividity_mobility' not in st.session_state:
        st.session_state.lividity_mobility = LividityMobilityType.NOT_SPECIFIED
    if 'results' not in st.session_state:
        st.session_state.results = ""
    if 'fig_henssge_rectal' not in st.session_state:
        st.session_state.fig_henssge_rectal = None
    if 'fig_henssge_brain' not in st.session_state:
        st.session_state.fig_henssge_brain = None
    if 'fig_comparison' not in st.session_state:
        st.session_state.fig_comparison = None
    if 'use_measurement_time' not in st.session_state:
        st.session_state.use_measurement_time = False
    if 'measurement_date' not in st.session_state:
        st.session_state.measurement_date = date.today()
    if 'measurement_time' not in st.session_state:
        st.session_state.measurement_time = time(12, 0)

def _reset() -> None:
    """
    Resets all fields in the user interface to their default state.
    
    This function:
    1. Clears all session state variables to remove user inputs
    2. Explicitly resets figure objects to None
    3. Displays a success message to confirm the reset
    4. Forces a page rerun to refresh all UI components
    
    This provides users with a clean slate for entering new data.
    
    Returns:
    --------
    None
        The function has side effects on the session state but returns no value
    """
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reset figures
    st.session_state.fig_henssge_rectal = None
    st.session_state.fig_henssge_brain = None
    st.session_state.fig_comparison = None
    st.success("The application has been successfully reset.")

    # Force page rerun to reset all widgets
    st.rerun()

def format_results_output(results: compute.OutputResults, inputs: InputParameters) -> str:
    """ Formats the computation results into a display string, using absolute time if available. """
    from core.datetime_utils import format_pmi_absolute # Local import

    output_lines = []

    # Henssge Rectal
    if results.henssge_rectal:
        if results.henssge_rectal.error_message:
            output_lines.append(f"**Henssge Rectal:**\n{results.henssge_rectal.error_message}")
        else:
            pmi_str = format_pmi_absolute(inputs.measurement_datetime,
                                          results.henssge_rectal.pmi_min(),
                                          results.henssge_rectal.pmi_max(),
                                          results.henssge_rectal.post_mortem_interval)
            output_lines.append(f"**Henssge Rectal:**\n{pmi_str}\n"
                                f"Confidence Interval (CI): ±{results.henssge_rectal.confidence_interval:.2f}h\n"
                                f"Thermal Quotient (Q): {results.henssge_rectal.thermal_quotient:.2f}\n"
                                f"Corrective factor (Cf): {results.henssge_rectal.corrective_factor:.2f}")

    # Henssge Brain
    if results.henssge_brain:
        if results.henssge_brain.error_message:
            output_lines.append(f"**Henssge Brain:**\n{results.henssge_brain.error_message}")
        else:
             pmi_str = format_pmi_absolute(inputs.measurement_datetime,
                                           results.henssge_brain.pmi_min(),
                                           results.henssge_brain.pmi_max(),
                                           results.henssge_brain.post_mortem_interval)
             output_lines.append(f"**Henssge Brain:**\n{pmi_str}\n"
                                 f"Confidence Interval (CI): ±{results.henssge_brain.confidence_interval:.2f}h")

    # Baccino
    if results.baccino:
        if results.baccino.error_message:
            output_lines.append(f"**Baccino:**\n{results.baccino.error_message}") # Corrected title
        else:
            pmi_interval_str = format_pmi_absolute(inputs.measurement_datetime,
                                                   results.baccino.post_mortem_interval_interval - results.baccino.confidence_interval_interval,
                                                   results.baccino.post_mortem_interval_interval + results.baccino.confidence_interval_interval,
                                                   results.baccino.post_mortem_interval_interval)
            pmi_global_str = format_pmi_absolute(inputs.measurement_datetime,
                                                 results.baccino.post_mortem_interval_global - results.baccino.confidence_interval_global,
                                                 results.baccino.post_mortem_interval_global + results.baccino.confidence_interval_global,
                                                 results.baccino.post_mortem_interval_global)

            output_lines.append(f"**Baccino:**\n"
                                f"Interval Method: {pmi_interval_str}\n"
                                f"Global Method: {pmi_global_str}")

    # Thanatological Signs
    signs = [
        results.idiomuscular_reaction,
        results.rigor,
        results.lividity,
        results.lividity_disappearance,
        results.lividity_mobility
    ]
    for sign_result in signs:
        if sign_result:
            if sign_result.error_message:
                 output_lines.append(f"**{sign_result.name}:** {sign_result.error_message}")
            else:
                 pmi_str = format_pmi_absolute(inputs.measurement_datetime,
                                               sign_result.min,
                                               sign_result.max)
                 output_lines.append(f"**{sign_result.name}:** {pmi_str}")


    return "\n\n".join(output_lines)

def _on_calculate():
    """
    Processes user inputs and generates results when the Calculate button is clicked.
    
    This function:
    1. Closes the help section if it is open
    2. Builds an InputParameters object from the current session state
    3. Runs the computation engine to calculate PMI estimates
    4. Stores the textual results in the session state
    5. Generates three visualization plots:
       - Henssge rectal temperature model
       - Henssge brain/tympanic temperature model
       - Comparative visualization of all calculation methods
    
    The results and visualizations are stored in the session state for display
    in the main application area.
    
    Returns:
    --------
    None
        The function updates the session state but returns no value
    """
    # Close help section if open
    st.session_state.help_open = False
    input_parameters = _build_input_parameters()

    # Check if manual CF was invalid
    if st.session_state.correction_mode == "Manual input" and not input_parameters.user_corrective_factor and st.session_state.input_Cf:
         st.error("Calculation aborted due to invalid manual Corrective Factor.")
         # Clear previous results if any
         st.session_state.results = ""
         st.session_state.fig_henssge_rectal = None
         st.session_state.fig_henssge_brain = None
         st.session_state.fig_comparison = None
         return # Stop calculation

    results = compute.run(input_parameters)
    # <-- MODIFIED: Use the new formatting function -->
    st.session_state.results = format_results_output(results, input_parameters)

    # Pass input_parameters to plotting functions
    st.session_state.fig_henssge_rectal = plot.plot_temperature_henssge_rectal(input_parameters, results.henssge_rectal)
    st.session_state.fig_henssge_brain = plot.plot_temperature_henssge_brain(input_parameters, results.henssge_brain)
    st.session_state.fig_comparison = plot.plot_comparative_pmi_results(input_parameters, results)

if __name__ == '__main__':
    # User interface
    st.title("EasyPMI")

    # Help section
    if 'help_open' not in st.session_state:
        st.session_state.help_open = True
    build_help_section()

    # Initialize session variables
    _init_state()

    # Measurement time reference
    use_measurement_time = st.sidebar.checkbox("Use Measurement Time Reference", key="use_measurement_time")
    if use_measurement_time:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.date_input("Measurement Date", key="measurement_date")
        with col2:
            st.time_input("Measurement Time", key="measurement_time")
    

    # User inputs
    st.sidebar.header("Parameters")

    # Text inputs with session_state keys
    st.sidebar.text_input(
        "Tympanic temperature (°C) : ",
        key="input_t_tympanic"
    )

    st.sidebar.text_input(
        "Rectal temperature (°C) : ",
        key="input_t_rectal"
    )

    st.sidebar.text_input(
        "Ambient temperature (°C) : ",
        key="input_t_ambient"
    )

    st.sidebar.text_input(
        "Body weight (kg) : ",
        key="input_M"
    )

    # Radio selector for choosing between manual and predefined corrective factor
    correction_mode = st.sidebar.radio(
        "Corrective factor mode:",
        options=["Predefined (using dropdown lists)", "Manual input"],
        key="correction_mode"
    )

    # Display different inputs based on the selected mode
    if st.session_state.correction_mode == "Manual input":
        # Show only manual input field
        st.sidebar.text_input(
            "Corrective factor (Cf) : ",
            key="input_Cf"
        )
    else:
        # Show predefined options with dropdown lists
        # Reset manual input if switching from manual to predefined
        if 'input_Cf' in st.session_state and st.session_state.input_Cf != "":
            st.session_state.input_Cf = ""
            
        body_condition_selectbox = st.sidebar.selectbox(
            "Body condition :",
            options=BodyCondition,
            key="body_condition",
            format_func=lambda x: str(x)
        )

        environment_selectbox = st.sidebar.selectbox(
            "Environment :",
            options=EnvironmentType,
            key="environment",
            format_func=lambda x: str(x)
        )

        supporting_base_selectbox = st.sidebar.selectbox(
            "Supporting base :",
            options=SupportingBase,
            key="supporting_base",
            format_func=lambda x: str(x)
        )

    # Thanatological signs
    st.sidebar.header("Thanatological Signs")
    idiomuscular_reaction_selectbox = st.sidebar.selectbox(
        "Idiomuscular Reaction :",
        options=IdiomuscularReactionType,
        key="idiomuscular_reaction",
        format_func=lambda x: str(x)
    )

    rigor_selectbox = st.sidebar.selectbox(
        "Type of Rigor :",
        options=RigorType,
        key="rigor",
        format_func=lambda x: str(x)
    )

    lividity_selectbox = st.sidebar.selectbox(
        "Type of Lividity :",
        options=LividityType,
        key="lividity",
        format_func=lambda x: str(x)
    )

    lividity_mobility_selectbox = st.sidebar.selectbox(
        "Lividity Mobility :",
        options=LividityMobilityType,
        key="lividity_mobility",
        format_func=lambda x: str(x)
    )

    st.sidebar.selectbox(
        "Disappearance of Lividity :",
        options=LividityDisappearanceType,
        key="lividity_disappearance",
        format_func=lambda x: str(x)
    )

    # Action buttons

    st.sidebar.button("Calculate", on_click=_on_calculate)
        
    if st.sidebar.button("Reset"):
        _reset()

    pdf_download = st.sidebar.download_button(
        label="Download PDF",
        data=generate_pdf() if 'clicked' not in st.session_state else None,
        file_name="results.pdf",
        mime="application/pdf",
        key='pdf_button'
    )

    if pdf_download:
        st.success("PDF downloaded successfully")

    # Display results
    st.header("Results")
    st.write(st.session_state.results)

    # Display graphs
    if st.session_state.fig_comparison:
        st.pyplot(st.session_state.fig_comparison)
    if st.session_state.fig_henssge_rectal:
        st.pyplot(st.session_state.fig_henssge_rectal)
    if st.session_state.fig_henssge_brain:
        st.pyplot(st.session_state.fig_henssge_brain)
