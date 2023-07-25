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
