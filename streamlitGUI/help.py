import streamlit as st
def build_help_section():

    # Picture path
    image_path1 = "Images/Image_1.PNG"
    image_path2 = "Images/Image_2.PNG"
    
    with st.expander("Help and User Guide", expanded=True):
        tab1, tab2, tab3, tab4 = st.tabs(["Getting Started", "Cooling Methods", "Thanatological Signs", "Parameters"])

        with tab1:
            st.markdown("""
            ##### Introduction
            Welcome to EasyPMI, the Post-Mortem Interval Calculator.\n
            This application helps estimate the time since death using various methods and parameters.
            
            ##### Quick Tutorial
            1. **Navigation**: Use the sidebar on the left to enter parameters
            2. **Data Entry**: Use ↹ (*Tab*) to to validate a variable and automatically move to the next field.  
                a. You can manually determine the corrective factor, it will deactivate dropdnown lists.  
                b. You can use predefined corrective factor : 'Body Condition', 'Environment', 'Supporting base' dropdown lists.*
            3. **Calculate**: Click "Calculate" to get the results
            4. **Reset**: Click "Reset" to clear entries
            5. **Save**: Click "Download PDF" saves your results in PDF format
            
            ##### Error Handling
            If you encounter errors, check that input values are within acceptable ranges.
            The application will guide you with specific error messages.  
            In case of difficulties, you can contact us by sending the error message for correction of any potential bugs. 
            """)

        with tab2:
            st.markdown("""
            ##### Henssge Method
            - Use rectal or brain temperature
            - Non-linear cooling model
            - The cerebral temperature is replaced here by the tympanic temperature.
            - Body weight is required for rectal equation
            - Corrective factor is automatically adjusted based on weight
            
            ##### Baccino Method
            - Uses tympanic temperature
            - Linear cooling model
            - Simpler approach
            - Body weight is not required
            """)

        with tab3:
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
            High temperatures significantly accelerate the onset of rigor mortis, while low temperatures prolong it. "The corpses of strong persons can stay stiff till 8 - 10 and more days in air of 2.5 to 7.5°C" ; 1856, Kussmaul.*
    
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

        with tab4:
            st.markdown("""
            ##### Temperature 
            - Methods based on body cooling are applicable if thermal conditions are 'stable'
            - Tympanic temperature can vary from one ear to the other *(especially if one is on the floor)*  
            *Not applicable in cases of major head trauma, or if wearing warm beanie*
            
            ##### Body Factors
            - **Weight**: The risk of error increases for extreme weights (low or high)
            - **Body Condition, Environment and Supporting base**: The corrective factor is based on the table established by Henssge
            - **Corrective Factor**: Manual adjustment for more precision  
            *The corrective factor is automatically adjusted based on body weight using the equation developed by Henssge*
            
            ##### Corrective Factor Table
            """)
            st.image(image_path1,
                     caption="Empiric corrective factors of the body weight in context of thermally indifferent ground under body and applied to a body weight of 70 kg. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")
            st.image(image_path2, caption="Adaptation of corrective factors to ground under body. Source data : Madea, B. (2023). Estimation of the Time Since Death. CRC Press.")
