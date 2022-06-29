# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 rwprimitives
Author: eldiablo


Status Codes Module

This module contains different status codes based on
the flow of the program.
"""

# standard modules
from enum import IntEnum


class ExitCodes(IntEnum):
    SUCCESS                     = 0

    UNSUPPORTED_PYTHON_VERSION  = 1

    INVALID_PARAMS              = 2

    NETWORK_CONNECTIVITY_ERROR  = 3

    SERVER_CONNECTION_FAILED    = 4

    GRAPHICAL_PANEL_FAILED      = 5

    # Exit codes for data handling
    MISSING_SENDERS_FILE        = 10
    MISSING_RECIPIENTS_FILE     = 11
    MISSING_MESSAGES_DIRECTORY  = 12
    MISSING_MESSAGE_FILE        = 13
    MISSING_DATA                = 14
    INVALID_FORMAT              = 15

    # ref: http://www.tldp.org/LDP/abs/html/exitcodes.html
    # 128+2 SIGINT
    ERROR_CTRL_C                = 130
