[![Python Package Build](https://github.com/dt-developers/camara-sdk.py/actions/workflows/main.yml/badge.svg)](https://github.com/dt-developers/camara-sdk.py/actions/workflows/main.yml)

Python CAMARA SDK 
=================

Call Camara APIs (currently only [Quality on Demand](https://github.com/camaraproject/QualityOnDemand/) is supported) through an easy to use CLI (command line interface) and an initial SDK.

Usage
-----

Install the SDK by calling `pip install camara_sdk`. Now you can import it and use it like so:

```
import camara
```

In order to create your first qod session, you need to create a client

```
client = camara.Camara('id', 'secret')
```

specifying the *id* and *secret* given when signing up for a subscription.

Now the `client` can be used for creating a new *qod* session:

```
client.qod.create_session(
  qos = camara.QualityOnDemand.Profile.E,
  from_ip = "127.0.0.1"
)
```

This will trigger a new token creation request (since the sdk notices, that there was no token created before, it does the same when the token expires) and then creates a new quality on demand session for 10 seconds (unless a different value was given with `duration = 100`).

CLI
===

For simple use, a CLI was created, it makes it easy to create authorization tokens, and keeping track of the length of said tokens. It automatically renews a token, once it expires. Additonally this CLI keeps track of the last session created, and informs when this session needs to be extended.

Usage
-----

To run the cli, use `python3 cli.py` or directly execute the script like `./cli.py`. Once the cli is started typing `help` will show the list of available _verbs_. Entering those will change configuration or actually call the apis.

Please set `CAMARA_CLIENT_ID` and `CAMARA_CLIENT_SECRET` environment variables to authenticate towards the Telekom Camara API gateway. Otherwise you'll get asked at startup of the _cli_.

Using the `qod e` _verb_ will call the qod session creation operation with the priority of `e`. When no token is created this verb will also request a token. Once the token is expired, also it will get renewed.

Using the _info_ verb will present the times left on the last session and the token.

Dependencies
============

This library uses python 3.10 (due [union types](https://peps.python.org/pep-0604/)) and otherwise only depends on the *requests* library.


Next Steps
==========

- [ ] Add common files (CONTRIBUTORS, ISSUE_TEMPLATE, ...)
- [ ] Fancyfy this readme (all the colors, all the logos ...)
- [ ] Push package out of testpypi
- [ ] Release more modules (not only QoD)


Contact
=======

In case of any questions please contact developers@telekom.de. For issues with the camara qod specification, please file an issue [here](https://github.com/camaraproject/QualityOnDemand/issues/new).
