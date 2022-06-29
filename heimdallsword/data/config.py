# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Config Module
=============

This module contains configuration information needed for the
the entire project.
"""

# internal modules
from heimdallsword.utils import util


class Config:
    """
    The Config class contains attributes used to describe the flow of operation
    for sending emails as well as Constants used as default values for most
    attributes.
    """

    DEFAULT_SENDERS_FILE = "senders.txt"
    """ Senders file default name """

    DEFAULT_RECIPIENTS_FILE = "recipients.txt"
    """ Recipients file default name """

    DEFAULT_CONTENT_DIR  = "content"
    """ Content directory default name """

    DEFAULT_DELAY = 100
    """ Default delay value in milliseconds used between each email sent """

    DEFAULT_METRICS_DELAY = 120
    """
    Default metrics delay value in seconds used to wait after sending an email
    before logging into the sender's account and retrieving bounced emails
    """

    DEFAULT_SMTP_PORT = 587
    """ Default SMTP port """

    DEFAULT_POP3_PORT = 995
    """ Default POP3 SSL port """

    DEFAULT_LOG_FILE_PATH = "./heimdallsword.log"
    """ Default log file name and path """

    DEFAULT_METRICS_FILE_PATH = "./metrics.txt"
    """ Default metrics file name and path """


    def __init__(self):
        self.recipient_file = ""
        self.sender_file = ""
        self.content_dir = ""
        self.process_dir = ""
        self.delay = self.DEFAULT_DELAY
        self.metrics_delay = self.DEFAULT_METRICS_DELAY
        self.smtp_port = self.DEFAULT_SMTP_PORT
        self.pop3_port = self.DEFAULT_POP3_PORT
        self.log_file_path = self.DEFAULT_LOG_FILE_PATH
        self.metrics_file_path = self.DEFAULT_METRICS_FILE_PATH
        self.worker_count = util.get_max_thread_count()
