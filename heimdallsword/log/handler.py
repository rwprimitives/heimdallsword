# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Logging Handler Module
======================

This module inherits from the logging.Handler class and provides
a way to set a callback method to invoke when log records are created.
"""

# standard modules
import logging


class LogHandler(logging.StreamHandler):
    """
    A custom log handler used to invoke a callback method whenever
    a log record is created.
    """

    def set_callback(self, callback):
        """
        Set the callback method to invoke when a log record is created.

        :param callback: callback method
        :type: :py:class:`logging.LogRecord`
        """

        self.callback = callback


    def emit(self, record):
        #
        # NOTE:
        # This function is overwritten and the callback
        # function is called and the :py:class:`logging.LogRecord`
        # object is passed. By not calling the parent function
        # via `super()` we prevent echoing of logs into the
        # console.
        #

        if self.callback:
            self.callback(record)
