# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Util Module
===========

This module contains general purpose functionalities that are
used across the entire project.
"""

# standard modules
import os
import re
from datetime import datetime


def is_directory_valid(arg_parser, dir_path):
    """
    Callback method for validating the existance of a directory provided by the
    user as an argument. If the directory doesn't exist, it provides an error
    message to the :py:class:`argparse.ArgumentParser` object.

    :param arg_parser: the argparser object that is parsing the directory argument
    :type: :py:class:`argparse.ArgumentParser`

    :returns: True if the directory exists, False otherwise
    :rtype: bool
    """
    if not os.path.isdir(dir_path):
        arg_parser.error(f"The directory path provided '{dir_path}' is not valid")
    else:
        return os.path.abspath(dir_path)


def is_file_valid(arg_parser, file):
    """
    Callback method for validating the existance of a file provided by the user as
    an argument. If the file doesn't exist, it provides an error message to the
    :py:class:`argparse.ArgumentParser` object.

    :param arg_parser: the argparser object that is parsing the file argument
    :type: :py:class:`argparse.ArgumentParser`

    :returns: True if the file exists, False otherwise
    :rtype: bool
    """
    if not os.path.isfile(file):
        arg_parser.error(f"The file provided '{file}' is not valid")
    else:
        return os.path.abspath(file)


def get_value_from_key(key, data):
    """
    Retrieves the value of a key-value pair given a key and the data in which
    the pair may exist.

    :param key: the key used to identify the key-value pair
    :type: string

    :param data: the data in which the key-value pair may exist
    :type: string

    :returns: the value of the key-value pair, otherwise an empty string
    :rtype: str
    """
    reg_ex_obj = re.compile(key)
    for line in data.splitlines():
        if reg_ex_obj.search(line) is not None:
            line = line.replace("\n", "")
            kv_pair = line.split("=")
            return kv_pair[1]

    return ""


def is_email_valid(email):
    """
    Checks to see if a given string follows the proper email format by using
    regular expressions.

    The regular expression used in this method was based from:

        - **URL:**    https://stackoverflow.com/a/201378
        - **Author:** bortzmeyer

    However, **bortzmeyer**'s regular expression is a modified version of the
    original one found at http://emailregex.com. It was modified because according
    to **bortzmeyer**:

        | "One RFC 5322 compliant regex can be found at the top of the page
        | at http://emailregex.com/ but uses the IP address pattern that is
        | floating around the internet with a bug that allows 00 for any of
        | the unsigned byte decimal values in a dot-delimited address,
        | which is illegal."

    An additional modification was made to **bortzmeyer**'s modified version
    which validates uppercase letters in emails.

    :param email: the email string to validate
    :type: string

    :returns: True if email is in valid format, False otherwise
    :rtype: bool
    """
    email_rx = re.compile(r"(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*|\""
                          r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b"
                          r"\x0c\x0e-\x7f])*\")@(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]("
                          r"?:[a-zA-Z0-9-]*[a-zA-Z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]"
                          r"?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-zA-Z0-"
                          r"9-]*[a-zA-Z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01"
                          r"-\x09\x0b\x0c\x0e-\x7f])+)\])")

    if not email_rx.match(email):
        return False

    return True


def get_max_thread_count():
    """
    Calculates the number of maximum threads based on the number of
    processors on the machine and multiply by 5. This is the same
    method used in the :py:class:`concurrent.futures.ThreadPoolExecutor` module
    when `max_workers` is set to None.

    :returns: max thread count
    :rtype: int
    """
    return (os.cpu_count() * 5)


def is_int(number):
    """
    Determine if a given object is a whole number.

    :returns: True if is a whole number, False otherwise
    :rtype: bool
    """

    try:
        val = int(number)  # noqa: F841
    except ValueError:
        return False
    else:
        return True


def calculate_elapsed_time(start_time, stop_time, interval="default"):
    """
    Calculates the time elapsed between two timestamps and returns the
    duration based on the type of interval specified.

    The following `interval` types are supported:

        - years
        - days
        - hours
        - minutes
        - seconds

    This method is a modified version of a stackoverflow post by
    **Attaque** found at https://stackoverflow.com/a/47207182

    :param start_time: the start time
    :type: datetime

    :param stop_time: the stop time (this must be greater than the start time)
    :type: datetime

    :returns:
        - str - the total time elapsed between two timestamps
        - int - the value based on the interval given

    :raises:
        - IOError - start_time is not of datetime type
        - IOError - stop_time is not of datetime type
        - IOError - The interval provided is not supported: '{interval}'
    """

    if not isinstance(start_time, datetime):
        raise IOError("start_time is not of datetime type")

    if not isinstance(stop_time, datetime):
        raise IOError("stop_time is not of datetime type")

    elapsed_time = stop_time - start_time
    elapsed_time_secs = elapsed_time.total_seconds()

    def years():
        # Seconds in a year is: 365 days * 24 hours * 60 minutes * 60 seconds
        return divmod(elapsed_time_secs, 365 * 24 * 60 * 60)

    def days(seconds=None):
        # Seconds in a day is: 24 hours * 60 minutes * 60 seconds
        return divmod(seconds if seconds is not None else elapsed_time_secs, 24 * 60 * 60)

    def hours(seconds=None):
        # Seconds in an hour is: 60 minutes * 60 seconds
        return divmod(seconds if seconds is not None else elapsed_time_secs, 60 * 60)

    def minutes(seconds=None):
        # Seconds in a minute is: 60 seconds
        return divmod(seconds if seconds is not None else elapsed_time_secs, 60)

    def seconds(seconds=None):
        return divmod(seconds, 1) if seconds is not None else elapsed_time_secs

    def total_time_elapsed():
        # Use remainder of previous calculation to calculate the next value.
        # We get the remainder because divmod returns a tuple that contains
        # quotient and remainder of the division.
        y = years()
        d = days(y[1])
        h = hours(d[1])
        m = minutes(h[1])
        s = seconds(m[1])

        time_list = []

        if y[0]:
            time_list.append(f"{int(y[0])} years, ")

        if d[0]:
            time_list.append(f"{int(d[0])} days, ")

        if h[0]:
            time_list.append(f"{int(h[0])} hours, ")

        if m[0]:
            time_list.append(f"{int(m[0])} minutes, ")

        if s[0]:
            time_list.append(f"{int(s[0])} seconds")

        return "".join(time_list)

    t = {}
    t["years"] = int(years()[0])
    t["days"] = int(days()[0])
    t["hours"] = int(hours()[0])
    t["minutes"] = int(minutes()[0])
    t["seconds"] = int(seconds())
    t["default"] = total_time_elapsed()

    if interval not in t:
        raise IOError(f"The interval provided is not supported: '{interval}'")

    return t[interval]
