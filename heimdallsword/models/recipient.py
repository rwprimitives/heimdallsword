# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Recipient Module
================

This module contains information about the recipient
as well as delivery status information.
"""


class DeliveryState:
    """
    The :py:class:`DeliveryState` class provides constants that define the delivery status of a recipient.
    """


    SUCCESSFUL_DELIVERY = 0
    """ Message was successfully delivered to recipient """

    NOT_DELIVERED = 1
    """ Message has not been sent to recipient """

    FAILED_DELIVERY = 2
    """ Message failed to reach recipient
        This state follows the exception SMTPHeloError, SMTPDataError, SMTPResponseException
    """

    DISCONNECTED = 3
    """ Message was not delivered due to loss of connectivity with SMTP server.
        This state follows the exception SMTPServerDisconnected
    """

    INVALID_FORMAT = 4
    """ Mail parameters provided are not supported, i,e., SMTPUTF8
        This state follows the exception SMTPNotSupportedError, ValueError
    """

    RECIPIENT_REJECTED = 5
    """ Mail server rejected recipient
        This state follows the exception SMTPRecipientsRefused
    """

    SENDER_REJECTED = 6
    """ Mail server rejected sender email
        This state follows the exception SMTPSenderRefused
    """


class Recipient:
    """
    The :py:class:`Recipient` class represents a recipient.
    """


    def __init__(self):
        self._email_domain = ""
        self._email_username = ""

        self.email = ""
        self.message_filename = ""
        self.custom_tags = {}
        self.message = None

        self.msg_id = ""
        self.sending_timestamp = 0
        self.sent_timestamp = 0
        self.delivery_state = DeliveryState.NOT_DELIVERED
        self.delivery_error_code = 0
        self.delivery_error_message = ""


    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(email={self.email!r}, '
                f'message_filename={self.message_filename!r}, '
                f'custom_tags={self.custom_tags!r}, '
                f'message={self.message!r})'
                )


    def add_custom_tag(self, key, value):
        """
        Add a custom tag given a key-value pair.

        :param key: the key
        :type: str

        :param value: the value
        :type: str
        """
        self.custom_tags[key] = value


    def get_email(self):
        """
        Get the email address of the recipient.

        :returns: the recipient's email address
        :rtype: str
        """

        return self.email


    def get_message_filename(self):
        """
        Get the filename of the message file.

        :returns: the filename of the message
        :rtype: str
        """

        return self.message_filename


    def get_all_custom_tags(self):
        """
        Get the :py:obj:`Dictionary` that contains a list of
        custom tags associated with a message template file.

        :returns: a list of custom tags
        :rtype: :py:obj:`Dictionary`
        """

        return self.custom_tags


    def get_custom_tag(self, key):
        """
        Get the value of a custom tag given a key.

        :param key: the key of the tag
        :type: str

        :returns: the value
        :rtype: str
        """

        return self.custom_tags[key]


    def get_message(self):
        """
        Get the :py:obj:`Message` object associated with this recipient.

        :returns: the :py:obj:`Message`
        :rtype: :py:obj:`Message`
        """

        return self.message


    def get_msg_id(self):
        """
        Get the RFC 2822-compliant Message-ID header string assigned to
        the recipient.

        :returns: RFC 2822-compliant Message-ID header string
        :rtype: str
        """

        return self.msg_id


    def get_sending_timestamp(self):
        """
        Get the timestamp before the email is sent.

        :returns: the sending timestamp
        :rtype: str
        """

        return self.sending_timestamp


    def get_sent_timestamp(self):
        """
        Get the timestamp after the email was successfully sent.

        :returns: the sent timestamp
        :rtype: str
        """

        return self.sent_timestamp


    def get_delivery_state(self):
        """
        Get the state of the delivery of the email to the recipient.

        :returns: the state of delivery
        :rtype: :py:class:`heimdallsword.models.recipient.DeliveryState`
        """

        return self.delivery_state


    def get_delivery_error_code(self):
        """
        Get the SMTP error code provided by the SMTP server.

        :returns: the SMTP error code
        :rtype: int
        """

        return self.delivery_error_code


    def get_delivery_error_message(self):
        """
        Get the SMTP error message provided by the SMTP server.

        :returns: the SMTP error message
        :rtype: str
        """

        return self.delivery_error_message


    def get_email_username(self):
        """
        Get the email username.

        :returns: the email username
        :rtype: str
        """

        return self._email_username


    def get_email_domain(self):
        """
        Get the email domain URL.

        :returns: the domain URL of the email address
        :rtype: str
        """

        return self._email_domain


    def set_email(self, email):
        """
        Set the email address of the recipient.

        :param email: the recipient's email address
        :type: str

        :raises: IOError - Invalid recipient email
        """

        if len(email.split("@")) == 2:
            self.email = email
            self._email_username = email.split("@")[0]
            self._email_domain = email.split("@")[1]
        else:
            raise IOError("Invalid recipient email")


    def set_message_filename(self, message_filename):
        """
        Set the filename which contains the message to send to the recipient.

        :param message_filename: the filename of the message file
        :type: str
        """

        self.message_filename = message_filename


    def set_custom_tags(self, tags):
        """
        Set a :py:obj:`Dictionary` object which contains a list of key-value
        pairs defined in the message content.

        :param tags: the custom tags
        :type: dict

        :raises: IOError - tags must be of dictionary type
        """

        if not isinstance(tags, dict):
            raise IOError("tags must be of dictionary type")

        self.custom_tags = tags


    def set_message(self, message):
        """
        Set a :py:obj:`Message` object based on the content in the
        message file (:py:attr:`Recipient.message_filename`).

        :param message: the :py:obj:`Message`
        :type: :py:obj:`Message`
        """

        self.message = message


    def set_msg_id(self, msg_id):
        """
        Set the RFC 2822-compliant Message-ID header string used
        for tracking an email sent.

        :param msg_id: the message ID assigned
        :type: str
        """

        self.msg_id = msg_id


    def set_sending_timestamp(self, sending_timestamp):
        """
        Set the timestamp before the email is sent.

        :param sending_timestamp: the timestamp before the email is sent
        :type: str
        """

        self.sending_timestamp = sending_timestamp


    def set_sent_timestamp(self, sent_timestamp):
        """
        Set the timestamp after the email was successfully sent.

        :param sent_timestamp: the timestamp after the email was successfully sent
        :type: str
        """

        self.sent_timestamp = sent_timestamp


    def set_delivery_state(self, delivery_state):
        """
        Set the state of the delivery of the email to the recipient.

        :param delivery_state: the delivery state
        :type: :py:class:`heimdallsword.models.recipient.DeliveryState`
        """

        self.delivery_state = delivery_state


    def set_delivery_error_code(self, delivery_error_code):
        """
        Set the SMTP error code provided by the SMTP server.

        :param delivery_error_code: the SMTP error code
        :type: int
        """

        self.delivery_error_code = delivery_error_code


    def set_delivery_error_message(self, delivery_error_message):
        """
        Set the SMTP error message provided by the SMTP server.

        :param delivery_error_message: the SMTP error message
        :type: str
        """

        self.delivery_error_message = delivery_error_message
