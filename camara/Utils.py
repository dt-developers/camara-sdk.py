def set_ue_id(payload, from_ipv4, from_ipv6, from_number, ipv4key='ipv4addr', ipv6key='ipv6addr', msisdnkey='msisdn'):
    payload['ueId'] = {}

    if from_ipv4 is not None:
        payload['ueId']['ipv4addr'] = from_ipv4

    if from_ipv6 is not None:
        payload['ueId']['ipv6addr'] = from_ipv6

    if from_number is not None:
        payload['ueId']['msisdn'] = from_number


def remove_empty(d):
    if isinstance(d, dict):
        return {k: remove_empty(v) for k, v in d.items() if v is not None}
    else:
        return d


def hsv(h, s, v):
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
    r, g, b = rgb
    return 16 + int(r * 5) * 36 + int(g * 5) * 6 + int(b * 5)