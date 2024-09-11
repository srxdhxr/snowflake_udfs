'''
Actual Implementations of Snowflake UDFs are stored here
Import required functions from utils.py
'''
import sys
import os

# Assuming the 'libs' folder is inside the zip, add it to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

from utils import *

@sf_udf
def get_linkedin_uri(value):
    '''
    Get the cleaned linkedin url

    Args:
        value (str): Input for this function is a string which is a linkedin url
    
    Returns:
        cleaned_url (str): Cleans up the url and returns the clean url. Returns None if failed
    '''
    if isnull(value):
        return None
    try:
        cleaned_url = clean_url(value, linkedin=True)
        if isnull(cleaned_url):
            return None
        return cleaned_url.to_uri().to_text(with_password=True)
    except UnicodeDecodeError:
        return None


@sf_udf
def parse_num_connections(value: str) -> Union[int, None]:
    """
    Parse the number of connections from a string.
    
    Args:
        value (str): The input string that may contain a number of connections.
        
    Returns:
        int or None: The number of connections as an integer or None if parsing fails.
    """
    if value is None:
        return None

    # Ensure the value is a string
    if isinstance(value, str):
        if not re.search(r'\d', value):
            return None
        value = value.replace("\u00a0", " ") if "\u00a0" in value else value
        
        # Handle followers scenario
        if 'followers' in value:
            v = value.rsplit(" followers", 1)[0]
            value = v
            match = re.match(r'(\d+)K', value)
            if match:
                return int(match.group(1)) * 1_000
            elif re.match(r'(\d+,\d+)', value):
                value = value.replace(",", "")

    # Match patterns for connection counts
    for pattern in [r'(\d+)\+', r'(\d+) ']:
        match = re.match(pattern, str(value))
        if match:
            return int(match.group(1))

    # Convert to int and handle potential errors
    try:
        n = int(value)
    except ValueError:
        return None

    # Handle overflow scenario for maximum value
    final = 500 if n == 65535 else n
    return final


@sf_udf
def clean_encoding(value: Union[str, None]) -> Union[str, None]:
    """
    Fixes the encoding of a string value using ftfy's fix_encoding.
    
    Args:
    value (str): The input string that may have incorrect encoding.
    
    Returns:
    str or None: The string with fixed encoding, or None if input is null.
    """
    if isnull(value):
        return None
    clean_text = fix_encoding(value)
    return clean_text


@sf_udf
def parse_full_name(full_name: Union[str, None], index: str) -> Union[str, None]:
    """
    Parses a full name and returns a specific part based on the given index.

    Args:
    full_name (str): The input full name to be parsed.
    index (int): The index of the name part to be returned (0=first, 1=middle, 2=last, 3=prefix, 4=suffix).

    Returns:
    str or None: The requested part of the name, or None if input is null or index is out of range.
    """
    index = int(index)

    # Validating the input name
    if isnull(full_name):
        return None

    # Adjust full name to ensure proper spacing around dots
    full_name = full_name.replace(".", ". ")

    # Parse the full name using HumanName
    parsed_name = HumanName(full_name)

    # Extracting different parts of the name
    name_parts = [
        parsed_name.first,   # 0: First Name
        parsed_name.middle,  # 1: Middle Name
        parsed_name.last,    # 2: Last Name
        parsed_name.title,   # 3: Prefix
        parsed_name.suffix   # 4: Suffix
    ]

    # Return the requested part of the name, if it exists
    part = name_parts[index] if 0 <= index < len(name_parts) else None
    return part if not isnull(part) else None


@sf_udf
def parse_scrapetime(value: Union[str, float, None]) -> str:
    """
    Parses a timestamp or datetime string and returns a formatted datetime string.

    Args:
    value (str, float, or None): The timestamp (float) or datetime string to be parsed.

    Returns:
    str: The formatted datetime string in ISO 8601 format, or a default date if the input is null.
    """
    if value is None:
        # Return a default timestamp if input is null
        return dt.datetime.fromtimestamp(0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    try:
        # If the value is a float (timestamp), treat it as such
        if isinstance(value, (float, int)):
            parsed_date = dt.datetime.fromtimestamp(float(value))
        else:
            # If the value is a string, try parsing it as a datetime string
            parsed_date = dt.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        
        # Return the formatted datetime string with microseconds
        return dt.datetime.strftime(parsed_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    except ValueError:
        # If the format of the string or timestamp is wrong, return a fallback
        return dt.datetime.fromtimestamp(0).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
@sf_udf
def clean_company(value: Union[str, None]) -> Union[str, None]:
    """
    Cleans up a company name by removing special characters, punctuation, and extra spaces, 
    and converting the name to lowercase.

    Args:
    value (str or None): The company name to be cleaned.

    Returns:
    str or None: The cleaned company name, or None if the input is null.
    """
    if isnull(value):
        return None

    # Remove all non-word characters and underscores, replace them with a single space, strip spaces, and convert to lowercase
    cleaned_value = re.sub(r"[\W_]+", " ", str(value)).strip().lower()
    return cleaned_value    


@sf_udf
def parse_linkedin_slug(value, other: bool) -> str:
    """
    Parses a LinkedIn company slug or URL.
    """
    def _parse_company_slug(is_inferred, slug):
        if isnull(slug):
            return None
        if is_inferred:
            return None
        return f'linkedin.com/company/{slug}'

    url = _parse_company_slug(value, other)
    if url is None:
        return None
    
    try:
        cleaned_url = clean_url(url, linkedin=True)
        if isnull(cleaned_url):
            return None
        return cleaned_url.to_uri().to_text(with_password=True)
    except UnicodeDecodeError:
        return None
    
@sf_udf
def clean_encoding(value):
    if not isnull(value):
        return fix_encoding(value)
    return None