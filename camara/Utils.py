import math
import enum
import json

from requests.exceptions import JSONDecodeError


def set_ue_id(payload, from_ipv4, from_ipv6, from_number):
    """
    Set the ue id and delete all others.
    """
    payload['ueId'] = {}

    if from_ipv4 is not None:
        payload['ueId']['ipv4addr'] = from_ipv4

    if from_ipv6 is not None:
        payload['ueId']['ipv6addr'] = from_ipv6

    if from_number is not None:
        payload['ueId']['msisdn'] = from_number


def remove_empty(d):
    """
    Removes all empty slots for a dictionary.
    """
    if isinstance(d, dict):
        return {k: remove_empty(v) for k, v in d.items() if v is not None}
    else:
        return d


def hsv(h, s, v):
    """
    For h (0..360), s (0..1), v(0..1) create a r(0..1) g(0..1) b(0..1) tuple.
    """
    r = 0
    g = 0
    b = 0

    c = v * s
    x = c * (1.0 - abs((((h / 60.0) % 2.0) - 1.0)))
    m = v - c

    if 0 <= h < 60:
        r = c
        g = x
        b = 0
    elif 60 <= h < 120:
        r = x
        g = c
        b = 0
    elif 120 <= h < 180:
        r = 0
        g = c
        b = x
    elif 180 <= h < 240:
        r = 0
        g = x
        b = c
    elif 240 <= h < 300:
        r = x
        g = 0
        b = c
    elif 300 <= h < 360:
        r = c
        g = 0
        b = x

    return r + m, g + m, b + m


def rgb_to_termcolor(rgb):
    """
    Convert the given rgb (given from 0 to 1) to a terminal color from 16 to 216
    """
    r, g, b = rgb
    return 16 + int(r * 5) * 36 + int(g * 5) * 6 + int(b * 5)


def longitude_for_km(latitude, longitude, accuracy):
    """
    return rough approximation of longitude
    """
    return 1 / 110.574 * accuracy


def latitude_for_km(latitude, longitude, accuracy):
    """
    return rough approximation of latitude
    """
    return 1 / (111.320 * math.cos(math.radians(latitude)) * accuracy)


def print_request_response(request, response, verbose):
    """Helper function for printing the request and response, humanfriendly."""

    if not verbose:
        if response.ok:
            status = colorize('Success', TermColor.COLOR_SUCCESS)
        else:
            status = colorize('Failure', TermColor.COLOR_ERROR)

        print(f"{status}: {response.json()}")
    else:
        headers = ""
        for key in request.headers:
            value = ellipsize(request.headers[key]) if key.lower().find('auth') >= 0 else request.headers[key]
            headers += f"  --header \"{key}: {value}\" \\\n"

        curl = f"curl \\\n  --request {request.method} \\\n" \
               f"{headers}"

        if request.body:
            curl += f"  -d '{request.body}' \\\n"

        curl += f"  '{request.url}'"

        print(f"{colorize('request')}\n {curl}")

        headers = ""
        if response.headers:
            for key in response.headers:
                value = ellipsize(response.headers[key]) if key.lower().find('auth') >= 0 else response.headers[key]
                headers += f"  {key}: {value}\n"

        if len(headers) > 0:
            headers = f"\nHeaders\n{headers}"

        status = response.status_code
        try:
            body = response.json()
            body = json.dumps(body, indent=2)
        except JSONDecodeError:
            body = ""

        response_color = TermColor.COLOR_SUCCESS if response.ok else TermColor.COLOR_ERROR
        print(f"\n{colorize('response', response_color)}\n{status}\n{headers}\n{body}")


class TermColor(enum.Enum):
    """
    Enumeration storing all available colors for the colorize function.
    """
    COLOR_INFO = 32
    COLOR_ERROR = 41
    COLOR_SUCCESS = 42
    COLOR_WARN = 43
    COLOR_RAINBOW = 38
    COLOR_EMPHASIZE = 1
    COLOR_RAINBOW_INVERTED = "38;5;0;48"


def colorize(text, color: TermColor = TermColor.COLOR_INFO):
    """
    Take the text and colorize it with one color.

    This function can be used to colorize a piece of text for console output.

    :param text: which text to colorize
    :param color: which color to be taken.
    :return: a colorized version of the input text.
    """
    if color == TermColor.COLOR_RAINBOW or color == TermColor.COLOR_RAINBOW_INVERTED:
        result = ""
        for (index, char) in enumerate(text):
            code = rgb_to_termcolor(hsv(index * 360.0 / len(text), 1.0, 1.0))
            result += f"\033[{color.value};5;{code}m{char}"
        result += f"\033[m"
        return result
    elif color:
        return f"\033[{color.value}m{text}\033[m"
    else:
        return text


def variables(obj):
    """
    Return all variables of the given object.

    Might be incomplete, but good enough for now.
    """
    return list(filter(lambda x: not x.startswith("__") and not callable(x), dir(obj)))


def ellipsize(text: str, max_len: int = 100):
    return (text[:max_len] + '…') if len(text) > max_len else text
