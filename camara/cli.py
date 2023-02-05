#!/usr/bin/env python3
"""
This is the entry point for the CAMARA APIs.

It provides a cli when called as a script, and calls apis specified in [CAMARA](https://github.com/camraproject).
"""
import os
from camara import *

# Set to 'None' to disable color. Otherwise, use an ANSI escape color code
# number from here: https://en.wikipedia.org/wiki/ANSI_escape_code
INFO_COLOR = 32
ERROR_COLOR = 41
COLOR = INFO_COLOR


def colorize(text, color=COLOR):
    """
    Take the text and colorize it with one color.

    This function can be used to colorize a piece of text for console output.

    :param text: which text to colorize
    :param color: which color to be taken.
    :return: a colorized version of the input text.
    """
    if color:
        return f"\033[{color}m{text}\033[m"
    else:
        return text


# Prompt for the user: Whenever this CLI asks the user something, this prompt appears
PROMPT = f"{colorize('CAMARA')}> "

# Client details for authentication. Please ask your CAMARA representative for these values.
CAMARA_CLIENT_SECRET_ENV = 'CAMARA_CLIENT_SECRET'
CAMARA_CLIENT_ID_ENV = 'CAMARA_CLIENT_ID'


def menu(client_id, client_secret):
    """
    Creates a nice menu for the Command Line Interface.

    :param client_id: which id to be used to authenticate
    :param client_secret:  the secret to be used for authentication
    :return: nothing - on return the script ends
    """

    class Config:
        """
        Configuration Abstraction

        Used internally to store the configuration values for the menu. Think of ip addresses and other values needed
        to execute apis.
        """

        def __init__(self):
            self.duration = 10
            self.from_ip = "127.0.0.1"
            self.to_ip = "0.0.0.0/0"

    def user_help():
        """Print help for all verbs."""

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
        """Set to ip address. The ip of the device the connection should start from. Alternative name: ue address."""
        config.to_ip = input(f"ip (currently {config.to_ip})? ")
        return True

    def user_set_from():
        """Set from ip address. The ip the device connects to. Alternative name: as address."""
        config.from_ip = input(f"ip (currently {config.from_ip})? ")
        return True

    def user_set_duration():
        """Set duration of newly created sessions in seconds."""
        try:
            config.duration = int(input(f"duration (currently {config.duration})? "))
        except ValueError:
            print("Not a valid number, please retry.")
        return True

    def user_create_token():
        """Create a new access token. Needs client id and client secret for success."""
        request, response = camara.create_access_token()
        print_request_response(request, response)
        return True

    def create_session(qos: QualityOnDemand.Profile):
        """Create a qos session using one of the defined qos classes. Needs 'from', 'to', and 'duration' values."""
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
        """Close this cli."""
        return False

    def print_request_response(request, response):
        """Helper function for printing the request and response, humanfriendly."""
        print(f"request: {request.body}")
        if 'status' in response:
            status = response['status']
        else:
            status = 'no-status'
        print(f"response: {status} {response}")

    def create_session_creation_function(qod_for_lambda):
        """Create a function that calls the creation of a session. Used for user interaction."""

        def inline():
            return create_session(qod_for_lambda)

        inline.__doc__ = f"Create a qos session of type '{qod_for_lambda}'."

        return inline

    verbs = {
        'help': user_help,
        'exit': user_exit,
        'token': user_create_token,
        'qod to': user_set_to,
        'qod from': user_set_from,
        'qod duration': user_set_duration,
        'qod delete': user_delete_session,
        'qod e': create_session_creation_function(QualityOnDemand.Profile.E),
        'qod s': create_session_creation_function(QualityOnDemand.Profile.S),
        'qod m': create_session_creation_function(QualityOnDemand.Profile.M),
        'qod l': create_session_creation_function(QualityOnDemand.Profile.L),
        'time': user_time,
        'info': user_info,
    }

    camara = Camara(client_id=client_id, client_secret=client_secret)
    qod = camara.qod

    config = Config()

    print()
    print(colorize("Welcome to the CAMARA management command line interface."))
    print()

    # loop till either _exit_ is typed, an uncaught exception is thrown, or one of the _user*_ functions returns false
    go_on = True
    while go_on:
        selection = input(PROMPT)
        if selection in verbs:
            try:
                go_on = verbs[selection]()
            except Exception as exception:
                # be graceful with exceptions: Print them and don't explode the cli.
                print(f"{colorize('Exception caught', ERROR_COLOR)}: {exception}.")
        else:
            print("Unknown verb. Try 'help' to list all the supported _verbs_.")


# Are we in interactive / scripting mode?
if __name__ == "__main__":
    # CLI requested.
    if CAMARA_CLIENT_ID_ENV in os.environ:
        client_id = os.environ[CAMARA_CLIENT_ID_ENV]
    else:
        client_id = input(f"No '{CAMARA_CLIENT_ID_ENV}' environment variable set. Please specify by hand: ")

    if CAMARA_CLIENT_SECRET_ENV in os.environ:
        client_secret = os.environ[CAMARA_CLIENT_SECRET_ENV]
    else:
        client_secret = input(f"No '{CAMARA_CLIENT_SECRET_ENV}' environment variable set. Please specify by hand: ")

    menu(client_id, client_secret)
