import pycountry


def validate_iso_639_3(input_code: str):
    if len(input_code) != 3:
        return "und"

    match = pycountry.languages.get(alpha_3=input_code.lower())

    if match:
        return match.alpha_3

    return "und"
