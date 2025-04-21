from core import time_converter
from core.output_results import OutputResults
from core.output_results import BaccinoResults
from core.output_results import HenssgeBrainResults
from core.output_results import HenssgeRectalResults
from core.output_results import PostMortemIntervalResults


def format_results_output(results: OutputResults) -> str:
    """
    Formats the OutputResults object into a display string, using the
    time_converter module for date/time formatting.
    """
    if not results:
        return "No results calculated."

    output_lines = []

    # --- Henssge Rectal ---
    if results.henssge_rectal:
        if results.henssge_rectal.error_message:
            output_lines.append(f"**Henssge Rectal:** {results.henssge_rectal.error_message}")
        else:
            pmi_min = results.henssge_rectal.pmi_min()
            pmi_max = results.henssge_rectal.pmi_max()
            pmi_center = results.henssge_rectal.post_mortem_interval
            line = time_converter.format_pmi_range_string(pmi_min, pmi_max, pmi_center, prefix="**Henssge Rectal:**  \nEstimated time of death:")
            if results.henssge_rectal.confidence_interval is not None:
                line += f"  \nConfidence Interval: {results.henssge_rectal.confidence_interval:.2f} hours"
            if results.henssge_rectal.thermal_quotient is not None:
                line += f"  \nThermal Quotient Q: {results.henssge_rectal.thermal_quotient:.2f}"
            if results.henssge_rectal.corrective_factor is not None:
                line += f"  \nCf: {results.henssge_rectal.corrective_factor:.2f}"
            output_lines.append(line)

    # --- Henssge Brain ---
    if results.henssge_brain:
         if results.henssge_brain.error_message:
            output_lines.append(f"**Henssge Brain:** {results.henssge_brain.error_message}")
         else:
            pmi_min = results.henssge_brain.pmi_min()
            pmi_max = results.henssge_brain.pmi_max()
            pmi_center = results.henssge_brain.post_mortem_interval
            line = time_converter.format_pmi_range_string(pmi_min, pmi_max, pmi_center, prefix="**Henssge Brain:**  \nEstimated time of death:")
            if results.henssge_brain.confidence_interval is not None:
                if time_converter.get_reference_datetime() is not None:
                    line += f"  \nConfidence Interval: {results.henssge_brain.confidence_interval:.2f} hours"
            output_lines.append(line)


    # --- Baccino --- 
    if results.baccino:
        if results.baccino.error_message:
            output_lines.append(f"**Baccino:** {results.baccino.error_message}")
        else:
            prefix_baccino = "**Baccino:** Estimated time of death:  \n"
            lines_baccino = [prefix_baccino]

            # Interval Method
            if results.baccino.post_mortem_interval_interval is not None and results.baccino.confidence_interval_interval is not None:
                center_int = results.baccino.post_mortem_interval_interval
                ci_int = results.baccino.confidence_interval_interval
                min_int = max(0.0, center_int - ci_int)
                max_int = center_int + ci_int
                lines_baccino.append(time_converter.format_pmi_range_string(min_int, max_int, center_int, prefix="- Interval Method:"))

            # Global Method
            if results.baccino.post_mortem_interval_global is not None and results.baccino.confidence_interval_global is not None:
                center_glob = results.baccino.post_mortem_interval_global
                ci_glob = results.baccino.confidence_interval_global
                min_glob = max(0.0, center_glob - ci_glob)
                max_glob = center_glob + ci_glob
                lines_baccino.append(time_converter.format_pmi_range_string(min_glob, max_glob, center_glob, prefix="- Global Method:"))

            output_lines.append("\n".join(lines_baccino)) 

    # --- Thanatological Signs (using PostMortemIntervalResults) ---
    sign_results = [
        results.idiomuscular_reaction,
        results.rigor,
        results.lividity,
        results.lividity_disappearance,
        results.lividity_mobility
    ]
    for sign_res in sign_results:
        if sign_res:
            section_lines = [f"**{sign_res.name}:**"]
            if sign_res.error_message:
                section_lines.append(sign_res.error_message)
            elif sign_res.min is not None or sign_res.max is not None: 
                pmi_string = time_converter.format_pmi_range_string(sign_res.min, sign_res.max, prefix=f"")
                if time_converter.get_reference_datetime() is None and 'between' in pmi_string:
                     parts = pmi_string.split('between ')
                     if len(parts) == 2:
                        interval_parts = parts[1].split(' and ')
                        if len(interval_parts) == 2:
                            pmi_string = f"[{interval_parts[0]} / {interval_parts[1]}]"
                section_lines.append(f"{pmi_string.strip()}")
            else:
                 section_lines.append("Not specified")
            output_lines.append("\n".join(section_lines))

    # Join all formatted lines with double newlines
    return "\n\n".join(filter(None, output_lines)) 