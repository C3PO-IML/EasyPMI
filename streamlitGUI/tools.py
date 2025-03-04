def convert_decimal_separator(value: str) -> float:
    """
    Convert a numeric string with a comma as a decimal separator to a float.
    The function handles various input formats including spaces, multiple commas,
    and different whitespace characters.

    Parameters
    ----------
    value : str
        Input string that may contain a comma as a decimal separator.
    Returns
    -------
    float
        Converted number.
    Raises
    ------
    ValueError
        If the input string is empty or cannot be converted to a float.
    """
    if not value:
        raise ValueError("Input value is empty")

    # Clean the input
    value = (
        value
        .strip()  # Remove leading/trailing whitespace
        .replace('\xa0', ' ')  # Replace non-breaking spaces
        .replace('\t', ' ')  # Replace tabs with spaces
        .replace(' ', '')  # Remove all spaces
    )

    # Check for multiple commas
    if value.count(',') > 1:
        raise ValueError(f"Multiple commas found in input: {value}")

    # Replace comma with dot
    value = value.replace(',', '.')

    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number format: {value}")
