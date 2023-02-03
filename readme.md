CAMARA CLI - in python
======================

Call Camara APIs (currently only [Quality on Demand](https://github.com/camaraproject/QualityOnDemand/) is supported) through an easy to use CLI (command line interface).

CLI
---

This CLI is written in python and makes it easy to create authorization tokens, and keeping track of the length of said tokens. It automatically renews a token, 
once it expires. Additonally this CLI keeps track of the last session created, and informs when this session needs to be extended.

Functionalities
---------------

- [x] Create and renew authentication tokens
- [x] Create, delete quaality on demand sessions
- [x] Separation of SDK and CLI: Use [camara.py](camara.py) as your interface to the APIs
- [ ] Compeling graphical output of time remaining

Requirements
------------

This library / cli only relies on the requests library. To install it call

```
pip install requests
```

on your favorite venv / python installation.

Usage
-----

To run the cli, use `python3 cli.py` or directly execute the script like `./cli.py`. Once the cli is started typing `help` will show the list of available _verbs_. Entering those will change configuration or actually call the apis.

Please set `CAMARA_CLIENT_ID` and `CAMARA_CLIENT_SECRET` environment variables to authenticate towards the Telekom Camara API gateway. Otherwise you'll get asked at startup of the _cli_.

Using the `qod e` _verb_ will call the qod session creation operation with the priority of `e`. When no token is created this verb will also request a token. Once the token is expired, also it will get renewed.

Using the _info_ verb will present the times left on the last session and the token.

Contact
-------

In case of any questions please contact developers@telekom.de. For issues with the camara qod specification, please file an issue [here](https://github.com/camaraproject/QualityOnDemand/issues/new).
