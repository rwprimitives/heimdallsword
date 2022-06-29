# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
CLI Log Module
==============

This module provides a simple way of logging output to the terminal.
"""

# standard modules
import logging
from logging import LogRecord
from logging import Formatter


# Terminal color codes
class Colors:
    """
    A class used for ANSI color codes in a POSIX terminal.
    """

    BLUE    = '\033[94m'
    """Blue color."""

    GREEN   = '\033[92m'
    """Green color."""

    RED     = '\033[31m'
    """Red color."""

    YELLOW  = '\033[93m'
    """Yellow color."""

    WHITE   = '\033[37m'
    """White color."""

    ENDC    = '\033[0m'
    """End color tag."""


def get_log_message(record):
    """
    Get a string representation of a log :py:class:`logging.LogRecord`.

    :param record: a :py:class:`logging.LogRecord` instance representing
                   an event logged
    :type: :py:class:`logging.LogRecord`

    :returns: a string repesentation of a log record
    :rtype: str
    """

    f = Formatter()
    ts = f.formatTime(record)

    return ("{} [{}] [{}] {}".format(ts, record.module, record.levelname, record.getMessage()))


def log(record):
    """
    Display a the content of a :py:class:`logging.LogRecord` on a terminal using ANSI color
    codes for the different log levels.

    This method is used as a callback in the :py:class:`heimdallsword.log.handler.LogHandler`
    class. That way, whenever a log record is generated, a :py:class:`logging.LogRecord`
    object is passed to this method and a color is used based on the log level and
    displayed on the terminal window.

    The following colors are assigned to a specific log level:

        INFO = :py:const:`heimdallsword.log.cli_log.Colors.GREEN`

        WARNING = :py:const:`heimdallsword.log.cli_log.Colors.YELLOW`

        ERROR = :py:const:`heimdallsword.log.cli_log.Colors.RED`

    :param record: a :py:class:`logging.LogRecord` instance representing
                   an event logged
    :type: :py:class:`logging.LogRecord`
    """

    if isinstance(record, LogRecord):
        f = Formatter()
        ts = f.formatTime(record)

        if record.levelno == logging.INFO:
            _info(ts, record.module, record.levelname, record.getMessage())
        elif record.levelno == logging.WARNING:
            _warning(ts, record.module, record.levelname, record.getMessage())
        elif record.levelno == logging.ERROR:
            _error(ts, record.module, record.levelname, record.getMessage())


def _info(ts, module, levelname, msg):
    print("{} [{}] {}[{}]{} {}".format(ts, module, Colors.GREEN, levelname, Colors.ENDC, msg))


def _warning(ts, module, levelname, msg):
    print("{} [{}] {}[{}] {} {}".format(ts, module, Colors.YELLOW, levelname, msg, Colors.ENDC))


def _error(ts, module, levelname, msg):
    print("{} [{}] {}[{}] {} {}".format(ts, module, Colors.RED, levelname, msg, Colors.ENDC))
