#!/usr/bin/env python3
import os
from camara import *

COLOR = True


def colorize(text):
    if COLOR:
        return f"\033[32m{text}\033[m"
    else:
        return text


PROMPT = f"{colorize('CAMARA')}> "

CAMARA_CLIENT_SECRET_ENV = 'CAMARA_CLIENT_SECRET'
CAMARA_CLIENT_ID_ENV = 'CAMARA_CLIENT_ID'


def menu(client_id, client_secret):
    class Config:
        def __init__(self):
            self.duration = 10
            self.from_ip = "127.0.0.1"
            self.to_ip = "0.0.0.0/0"

    def user_help():
        """Print help."""

        print(f"Available verbs:")
        for key in verbs.keys():
            documentation = verbs[key].__doc__
            if documentation:
                print(f"{colorize(f'▶ {key}')}: {documentation}")
            else:
                print(colorize(f'▶ {key}'))

        return True

    def user_info():
        """Print information about configuration."""

        try:
            print(f"access_token: {camara.get_access_token()}")
        except Exception:
            print(f"no access_token set")

        print(f"client_id: {camara.client_id}")
        print(f"client_secret: {camara.client_secret}")

        print(f"last session: {qod.last_session}")

        print(f"duration: {config.duration}")
        print(f"from_ip: {config.from_ip}")
        print(f"to_ip: {config.to_ip}")

        user_time()

        return True

    def user_set_to():
        """Set to ip address."""
        config.to_ip = input(f"ip (currently {config.to_ip})? ")
        return True

    def user_set_from():
        """Set from ip address."""
        config.from_ip = input(f"ip (currently {config.from_ip})? ")
        return True

    def user_set_duration():
        """Set duration in seconds."""
        try:
            config.duration = int(input(f"duration (currently {config.duration})? "))
        except ValueError:
            print("Not a valid number, please retry.")
        return True

    def user_create_token():
        """Create a new token."""
        request, response = camara.create_access_token()
        print_request_response(request, response)
        return True

    def create_session(qos):
        """Create a qos session using one of the defined classes, the to and from ip address and a given duration."""
        request, response = qod.create_session(
            qos=qos,
            from_ip=config.from_ip,
            to_ip=config.to_ip,
            duration=config.duration
        )

        print_request_response(request, response)
        return True

    def user_delete_session():
        """Delete last session."""
        if qod.last_session and 'id' in qod.last_session:
            session_id = qod.last_session['id']
            request, response = qod.delete_session(session_id)
            print_request_response(request, response)
        else:
            print("No session.")
        return True

    def user_time():
        """Print seconds left on session and token."""
        if qod.is_session_expired():
            left = qod.session_seconds_remaining()
            print(f"{int(left)}s left in session duration.")
        else:
            print("No session.")

        if camara.is_token_expired():
            print("Token expired.")
        else:
            print(f"{int(camara.token_seconds_remaining())}s left in token duration.")

        return True

    def user_exit():
        """Closes this program."""
        return False

    def print_request_response(request, response):
        print(f"request: {request.body}")
        if 'status' in response:
            status = response['status']
        else:
            status = 'no-status'
        print(f"response: {status} {response}")

    def create_session_creation_function(qod_for_lambda):
        def inline():
            return create_session(qod_for_lambda)

        inline.__doc__ = f"Creates a session of type '{qod_for_lambda}'."

        return inline

    verbs = {
        'help': user_help,
        'exit': user_exit,
        'token': user_create_token,
        'qod to': user_set_to,
        'qod from': user_set_from,
        'qod duration': user_set_duration,
        'qod delete': user_delete_session,
        'qod e': create_session_creation_function("QOS_E"),
        'qod s': create_session_creation_function("QOS_S"),
        'qod m': create_session_creation_function("QOS_M"),
        'qod l': create_session_creation_function("QOS_L"),
        'time': user_time,
        'info': user_info,
    }

    camara = Camara(client_id=client_id, client_secret=client_secret)
    qod = camara.qod

    config = Config()

    print()
    print("Welcome to the CAMARA management command line interface.")
    print()

    go_on = True
    while go_on:
        selection = input(PROMPT)
        if selection in verbs:
            go_on = verbs[selection]()
        else:
            print("Unknown verb. Try 'help'.")


if __name__ == "__main__":
    if CAMARA_CLIENT_ID_ENV in os.environ:
        client_id = os.environ[CAMARA_CLIENT_ID_ENV]
    else:
        client_id = input(f"No '{CAMARA_CLIENT_ID_ENV}' environment variable set. Please specify by hand: ")

    if CAMARA_CLIENT_SECRET_ENV in os.environ:
        client_secret = os.environ[CAMARA_CLIENT_SECRET_ENV]
    else:
        client_secret = input(f"No '{CAMARA_CLIENT_SECRET_ENV}' environment variable set. Please specify by hand: ")

    menu(client_id, client_secret)
else:
    print("Error: Please execute as '__main__'.")
