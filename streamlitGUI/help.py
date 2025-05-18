# streamlitGUI/help.py

import streamlit as st

def build_help_section():
    """
    Creates a comprehensive help section using expandable containers for the EasyPMI application.
    
    This function builds a detailed help interface organized into multiple tabs within a Streamlit
    expander component. The expander pattern helps keep the UI clean while providing access to
    detailed documentation:
    - Getting Started: basic navigation and usage instructions
    - Cooling Methods: explaining Henssge and Baccino calculation methods
    - Thanatological Signs: information about post-mortem changes
    - Parameters: details about input parameters and corrective factors
       
    Notes:
    ------
    st.expander usage:
        - Creates a collapsible container that can be expanded/collapsed by users
        - Syntax: st.expander(label, expanded=True, icon=None)
        - Parameters:
          * label (str): Header text for the expander (supports Markdown)
          * expanded (bool): If True, initializes as expanded (defaults to True)
          * icon (str, optional): An emoji/icon to display next to the label
    
    Alternative approaches:
        - st.sidebar: Could place help content in sidebar instead of main area
        - st.columns: Could organize help in horizontal columns instead of tabs
        - st.container: Could use simple containers with manual toggles
        - st.popups/modals: Third-party components could create popup help windows
        - External documentation: Could link to external docs instead of in-app help
        
    Implementation note:
        - The current implementation uses an expander with tabs for optimal organization
        - The expander is set to expanded=True by default to ensure visibility
        - Images are included to illustrate corrective factors
        - Warning: Nesting expanders inside other expanders is not supported by Streamlit
    """
    # Picture path
    image_path1 = "Images/Image_1.PNG"
    image_path2 = "Images/Image_2.PNG"
    
    # User Guide
    with st.expander("Help and User Guide", expanded=st.session_state.help_open):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Getting Started", "Cooling Methods", "Thanatological Signs", "Parameters", "Limitations"])

        with tab1: # Getting Started
            st.markdown("""
            ##### Introduction
            Welcome to EasyPMI, the Post-Mortem Interval Calculator.\n
            This application helps estimate the time since death using various methods and parameters.
            
            ##### Quick Tutorial
            1. **Navigation**: Use the sidebar on the left to enter parameters
            2. **Reference Time (Optional)**: enter the **date and time** of measurement.
                - Activating this option will display results as "Estimated times of death" *(Est ToD)* instead of 
                        relative "Post-Mortem Intervals" (e.g., "18/04/2025 - 06h30" instead of "5h30"). 
                - If left deactivated, results remain relative "Post-Mortem Intervals".
            3. **Data Entry**: Enter the measured temperatures, body weight, etc. Use ↹ (*Tab*) to validate a variable and move to the next field.
            4. **Corrective Factor**: Choose your preferred method:
                - **Predefined mode**: Use the dropdown lists for 'Body Condition', 'Environment', and 'Supporting base'.
                - **Manual mode**: Directly enter a specific corrective factor value.
            5. **Thanatological Signs**: Select the observed state for each sign from the dropdown lists.
            6. **Calculate**: Click "Calculate" to get the results.
            7. **Reset**: Click "Reset" to clear all entries.
            8. **Save**: Click "Download PDF" to save your results.
            
            ##### Results Display
            - Results are shown in the main area.
            - If Reference Time is activated, results indicate the estimated **Time of Death (ToD)**.
            - Otherwise, results indicate the estimated **Post-Mortem Interval (PMI)** in hours.
            - Graphs visualize the cooling curves and compare method estimations.
                        
            ##### Error Handling
            If you encounter errors, check that input values are within acceptable ranges.
            The application will guide you with specific error messages.  
            In case of difficulties, you can contact us by sending the error message for correction of any potential bugs.                         
            """)

        with tab2: # Cooling Methods
            st.markdown("""
            ##### Henssge Method
            - Use rectal or brain temperature.
            - Non-linear cooling model.
            - The cerebral temperature is replaced here by the tympanic temperature (measurment with thermal-probe recommended).
                        *Increased risk of error in case of major head trauma or wearing of a cap or beanie.*
            - Body weight is required for rectal equation.
            - Corrective factor is automatically adjusted based on weight.
            
            ##### Baccino Method
            - Uses tympanic temperature.
            - Linear cooling model.
            - Simpler approach, no corrective factor.
            - Body weight is not required.
            - *Increased risk of error in case of major head trauma or wearing of a cap or beanie.*
            """)

        with tab3: # Thanatological Signs
            st.markdown("""
            ##### Idiomuscular Reaction
            - Contraction after direct percussion of the muscle (*biceps brachii, for example*).
            - Zsako phenomenon -  Muscle contraction leading to flexion of the limb.
            - Strong and reversible - Visible contraction band that can be seen with the naked eye.
            - Weak and persistent - Discrete, localized contraction that is not visible but palpable.
    
            ##### Type of Rigor
            - Rigidity Not Established - There is no evidence of rigor mortis having set in.
            - Possible Re-establishment - Early signs of rigor mortis may be present, but it is not fully established.
            - Complete Rigidity - Rigor mortis is fully established, with the body exhibiting maximal stiffness.
            - Persistence - Rigor mortis persists or may be partially resolved.
            - Resolution - Rigor mortis has fully resolved.  
            *Be careful with Rigor: at extreme temperatures, the limits described in the literature are not applicable.
            High temperatures significantly accelerate the onset of rigor mortis, while low temperatures prolong it. 
                        "The corpses of strong persons can stay stiff till 8 - 10 and more days in air of 2.5 to 7.5°C" ; 1856, Kussmaul.*
    
            ##### Type of Lividity
            - Absent - There is no lividity present.
            - Development - Lividity is beginning to develop.
            - Confluence - Lividity is becoming more pronounced and merging.
            - Maximum - Lividity has reached its maximum intensity.
    
            ##### Lividity Mobility
            - Complete - Lividity can be completely displaced when the body is turned.
            - Partial - Lividity can be partially displaced when the body is turned.
            - Only little pallor - Lividity shows only a slight change in color (*or non change*) when the body is turned.
    
            ##### Disappearance of Lividity
            - Complete disappearance - Lividity disappears totaly at light pressure.
            - Incomplete disappearance - Lividity might disappears only with strong pressure (*with forceps*).
            """)

        with tab4: # Parameters
            st.markdown("""
            ##### Temperature 
            - Methods based on body cooling are applicable if thermal conditions are 'stable'
            - Tympanic temperature can vary from one ear to the other *(especially if one is on the floor)*  
            *Increased risk of error in cases of major head trauma, or if wearing warm beanie*
            
            ##### Body Factors
            - **Weight**: The risk of error increases for extreme weights (low or high)
            - **Body Condition, Environment and Supporting base**: The corrective factor is based on the table established by Henssge
            - **Corrective Factor**: Manual adjustment for more precision  
            *The corrective factor is automatically adjusted based on body weight using the equation developed by Henssge*
            
            ##### Corrective Factor Table
            """)
            st.image(image_path1,
                     caption="Empiric corrective factors of the body weight in context of thermally indifferent ground under body and " \
                     "applied to a body weight of 70 kg. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")
            st.image(image_path2, caption="Adaptation of corrective factors to ground under body. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")

        with tab5: # Limitations
            st.markdown("""
            ##### Important Considerations and Limitations

            While this application represents an advancement in integrating multiple PMI estimation methods in an accessible format, 
                        several limitations inherent to the underlying methods must be acknowledged.

            *   **Environmental Factors:** Significance influences on body cooling and decomposition processes include:
                *   Fluctuating ambient temperatures
                *   Humidity levels
                *   Air circulation (wind)
                *   Exposure to sunlight
                *   Surface on which the body is placed (ground, water, etc.)
                These factors can compromise the accuracy of mathematical models based on standardized cooling rates.

            *   **Individual Variables:** Uncertainty is introduced by factors such as:
                *   Subject's age and sex
                *   Body weight (especially at extremes)
                *   Body surface area
                *   Presence and type of clothing or coverings *(Corrective factors are imperfect estimations)*
                *   Underlying pathological conditions (fever, hypothermia before death) and causes of death (burns, blood loss, etc.)
                *   Body composition (fat vs. muscle mass)
                Current algorithms cannot fully account for all these variations.

            *   **Methodological Constraints:** The application's implementations of established equations (Henssge, Baccino, sign-based intervals) 
                        face the same intrinsic limitations as the original methods described in the literature. 
                        The accuracy of PMI estimations remains fundamentally limited by these theoretical constraints.

            *   **Applicability:** Estimations are generally less reliable at very short or very long post-mortem intervals, 
                        or in cases with unusual or rapidly changing environmental conditions. 
                        The limits described for thanatological signs can also be significantly affected by temperature and other factors.

            **Conclusion:**
            These limitations should be seriously considered by forensic practitioners when interpreting the results provided by this application. 
                        The estimations should be viewed as aids within a broader forensic context, not as definitive determinations of the time of death. 
                        Always correlate the application's output with scene findings, witness information, and other forensic evidence.
            """)