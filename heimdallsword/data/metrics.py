# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Metrics Module
==============

This module contains metrics generated when sending emails.
"""

# standard modules
import json
import threading
from datetime import datetime

# internal modules
from heimdallsword.utils import util


class Metrics:
    """
    The :py:class:`heimdallsword.data.metrics.Metrics` class is used to
    track various values when sending emails. These values are used to
    perform several calculations to assess, compare and track performance
    of the entirety email sending operation.

    The following values are tracked in order to determine the accuracy
    of emails sent:

      +---------------------------------------+------------------------------------------------------+
      | start_time                            | the timestamp before the operation starts            |
      +---------------------------------------+------------------------------------------------------+
      | stop_time                             | the timestamp after the operation ended              |
      +---------------------------------------+------------------------------------------------------+
      | num_of_senders                        | the number of sender accounts                        |
      +---------------------------------------+------------------------------------------------------+
      | num_of_recipients                     | the number of recipient accounts                     |
      +---------------------------------------+------------------------------------------------------+
      | num_of_emails_not_delivered           | the number of emails not delivered                   |
      +---------------------------------------+------------------------------------------------------+
      | num_of_emails_delivered               | the number of emails successfully delivered          |
      +---------------------------------------+------------------------------------------------------+
      | num_of_emails_failed_delivery         | the number of emails that failed to be delivered     |
      +---------------------------------------+------------------------------------------------------+
      | num_of_recipients_rejected            | the number of recipients rejected by the recipient's |
      |                                       | SMTP server due to an invalid recipient              |
      +---------------------------------------+------------------------------------------------------+
      | num_of_senders_rejected               | the number of senders rejected by the recipient's    |
      +---------------------------------------+------------------------------------------------------+
      |                                       | SMTP server                                          |
      | num_of_emails_failed_delivery_format  | the number of emails failed to deliver due to an     |
      |                                       | invalid format                                       |
      +---------------------------------------+------------------------------------------------------+
      | num_of_emails_disconnected            | the number of emails that weren't delivered due      |
      |                                       | to a failed connection with the sender's SMTP server |
      +---------------------------------------+------------------------------------------------------+

    :param metrics_file: a file path including a file name for the metrics file
    :type: str
    """

    def __init__(self, metrics_file=None):
        self._lock = threading.Lock()

        self.start_time = 0.0
        self.stop_time = 0.0
        self.num_of_senders = 0
        self.num_of_recipients = 0
        self.num_of_emails_not_delivered = 0
        self.num_of_emails_delivered = 0
        self.num_of_emails_failed_delivery = 0
        self.num_of_recipients_rejected = 0
        self.num_of_senders_rejected = 0
        self.num_of_emails_failed_delivery_format = 0
        self.num_of_emails_disconnected = 0

        self.metrics_file = metrics_file


    def set_metrics_file(self, metrics_file):
        """
        Set the file path and file name to store the metrics data.

        This method will throw an `IOError` if nothing is passed.

        :param metrics_file: a file path including a file name for the metrics file
        :type: str
        """

        if not metrics_file:
            raise IOError("No metrics file path was provided")

        self.metrics_file = metrics_file


    def activate_start_time(self):
        """
        Set the `start_time` to a timestamp generated from :py:meth:`datetime.datetime.now()`.
        """

        self.start_time = datetime.now()


    def activate_stop_time(self):
        """
        Set the `stop_time` to a timestamp generated from :py:meth:`datetime.datetime.now()`.
        """

        self.stop_time = datetime.now()


    def get_elapsed_time(self):
        """
        Calculate the time difference between the `start_time` and `stop_time`.

        :returns: a string representation of the time difference
        :rtype: str
        """

        elapsed_time = "N/A"

        if self.stop_time:
            elapsed_time = util.calculate_elapsed_time(self.start_time, self.stop_time)

        return elapsed_time


    def get_current_delivery_rate(self):
        """
        Get the current delivery rate. This is calculated based on the total number
        of emails delivered and the total number of recipients.

        :returns: the delivery rate
        :rtype: float
        """

        rate = -1

        with self._lock:
            if self.num_of_recipients:
                rate = round((self.num_of_emails_delivered / self.num_of_recipients) * 100, 1)
            return rate


    def get_current_fail_rate(self):
        """
        Get the current fail rate. This is calculated based on the following values:

        * num_of_emails_failed_delivery
        * num_of_recipients_rejected
        * num_of_senders_rejected
        * num_of_emails_disconnected
        * num_of_emails_failed_delivery_format
        * num_of_recipients

        :returns: the failure rate
        :rtype: float
        """

        rate = -1

        with self._lock:
            if self.num_of_recipients:
                rate = round(((self.num_of_emails_failed_delivery            # noqa: W503
                               + self.num_of_recipients_rejected             # noqa: W503
                               + self.num_of_senders_rejected                # noqa: W503
                               + self.num_of_emails_disconnected             # noqa: W503
                               + self.num_of_emails_failed_delivery_format)  # noqa: W503
                              / self.num_of_recipients) * 100, 1)            # noqa: W503
            return rate


    def get_num_of_recipients(self):
        """
        Get the number of recipients.

        :returns: the number of recipients
        :rtype: int
        """

        with self._lock:
            return self.num_of_recipients


    def get_num_of_senders(self):
        """
        Get the number of senders.

        :returns: the number of senders
        :rtype: int
        """

        with self._lock:
            return self.num_of_senders


    def get_start_time(self, dt_format="%m/%d/%Y %H:%M:%S.%f"):
        """
        Get the start time.

        :param dt_format: a string containing format codes for date and time
        :type: str

        :returns: a tuple containg the start time as a timestamp and
                  a formatted string. Zero and N/A may be returned if
                  `start_time` is zero
        :rtype: tuple
        """

        formatted_time = "N/A"

        if self.start_time:
            if dt_format:
                formatted_time = self.start_time.strftime(dt_format)

        return (self.start_time, formatted_time)


    def get_stop_time(self, dt_format="%m/%d/%Y %H:%M:%S.%f"):
        """
        Get the stop time.

        :param dt_format: a string containing format codes for date and time
        :type: str

        :returns: a tuple containg the stop time as a timestamp and
                  a formatted string. Zero and N/A may be returned if
                  `stop_time` is zero
        :rtype: tuple
        """

        formatted_time = "N/A"

        if self.stop_time:
            if dt_format:
                formatted_time = self.stop_time.strftime(dt_format)

        return (self.stop_time, formatted_time)


    def get_emails_delivered_count(self):
        """
        Get the number of emails delivered.

        This method is thread-safe.

        :returns: the number of emails delivered
        :rtype: int
        """

        with self._lock:
            return self.num_of_emails_delivered


    def get_emails_not_delivered_count(self):
        """
        Get the number of emails not delivered.

        This method is thread-safe.

        :returns: the number of emails not delivered
        :rtype: int
        """

        with self._lock:
            return self.num_of_emails_not_delivered


    def get_emails_failed_delivery_count(self):
        """
        Get the number of emails that failed to be delivered.

        This method is thread-safe.

        :returns: the number of emails that failed to be delivered
        :rtype: int
        """

        with self._lock:
            return self.num_of_emails_failed_delivery


    def get_recipient_rejected_count(self):
        """
        Get the number of recipients rejected by the recipient's
        SMTP server due to an invalid recipient.

        This method is thread-safe.

        :returns: the number of rejected recipients
        :rtype: int
        """

        with self._lock:
            return self.num_of_recipients_rejected


    def get_senders_rejected_count(self):
        """
        Get the number of senders rejected by the recipient's
        SMTP server.

        This method is thread-safe.

        :returns: the number of rejected senders
        :rtype: int
        """

        with self._lock:
            return self.num_of_senders_rejected


    def get_failed_delivery_format_count(self):
        """
        Get the number of emails failed to deliver due to an
        invalid format.

        This method is thread-safe.

        :returns: the number of emails failed to delivery due to invalid format
        :rtype: int
        """

        with self._lock:
            return self.num_of_emails_failed_delivery_format


    def get_disconnected_count(self):
        """
        Get the number of emails that weren't delivered due
        to a failed connection with the sender's SMTP server.

        This method is thread-safe.

        :returns: the number of emails failed to send due to sender's
                  connection failure with SMTP server
        :rtype: int
        """

        with self._lock:
            return self.num_of_emails_disconnected


    def increment_emails_delivered_count(self):
        """
        Increment the number of emails delivered counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_emails_delivered += 1


    def increment_emails_not_delivered_count(self):
        """
        Increment the number of emails not delivered counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_emails_not_delivered += 1


    def increment_emails_failed_delivery_count(self):
        """
        Increment the number of emails that failed to e delivered
        counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_emails_failed_delivery += 1


    def increment_recipient_rejected_count(self):
        """
        Increment the number of recipients rejected counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_recipients_rejected += 1


    def increment_senders_rejected_count(self):
        """
        Increment the number of senders rejected counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_senders_rejected += 1


    def increment_failed_delivery_format_count(self):
        """
        Increment the number of emails failed to deliver due to
        invalid format counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_emails_failed_delivery_format += 1


    def increment_disconnected_count(self):
        """
        Increment the number of emails that weren't delivered due
        to a failed connection with the sender's SMTP server
        counter by one.

        This method is thread-safe.
        """

        with self._lock:
            self.num_of_emails_disconnected += 1


    def set_number_of_senders(self, num_of_senders):
        """
        Set the number of senders.

        :param num_of_senders: the number of senders
        :type: int
        """

        self.num_of_senders = num_of_senders


    def set_number_of_recipients(self, num_of_recipients):
        """
        Set the number of recipients.

        :param num_of_recipients: the number of recipients
        :type: int
        """

        self.num_of_recipients = num_of_recipients


    def save_metrics(self, is_json=False, is_json_prettyprint=True):
        """
        Save the metrics data to file defined by `metrics_file`.
        The metrics data by default is saved as key-value pairs,
        however `is_json` can be set to True to save the data
        in JSON format.

        :param is_json: True to write the metrics in JSON format,
                        False to write the metrics as key-value
                        pairs. Default value is False
        :type: bool

        :param is_json_prettyprint: True to enable pretty print JSON
                                    data if `is_json` is enabled
        :type: bool
        """

        if not self.metrics_file:
            raise IOError("No metrics file path was provided")

        items = {}
        items["Total senders"] = self.get_num_of_senders()
        items["Total recipients"] = self.get_num_of_recipients()
        items["Start time"] = self.get_start_time()[1]
        items["Stop time"] = self.get_stop_time()[1]
        items["Elapsed time"] = self.get_elapsed_time()
        items["Delivery rate"] = self.get_current_delivery_rate()
        items["Fail rate"] = self.get_current_fail_rate()
        items["Emails delivered"] = self.get_emails_delivered_count()
        items["Emails not delivered"] = self.get_emails_not_delivered_count()
        items["Emails failed delivery"] = self.get_emails_failed_delivery_count()
        items["Recipients rejected"] = self.get_recipient_rejected_count()
        items["Senders rejected"] = self.get_senders_rejected_count()
        items["Emails failed delivery format"] = self.get_failed_delivery_format_count()
        items["Emails failed delivery disconnect"] = self.get_disconnected_count()

        with self._lock:
            with open(self.metrics_file, "w") as f:
                if is_json:
                    if is_json_prettyprint:
                        f.write(json.dumps(items, indent=4))
                    else:
                        f.write(json.dumps(items))
                    f.write("\n")
                else:
                    for i in items:
                        f.write(f"{i} = {items[i]}\n")
