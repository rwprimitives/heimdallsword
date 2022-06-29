# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Message Module
==============

This module contains the content defined in a message file.
"""


class Message:
    """
    The :py:class:`heimdallsword.models.message.Message` class represents the content
    required when composing an email.
    """

    PLAIN = "plain"
    """ The MIME sub content type that represents `text/plain`. """

    HTML = "html"
    """ The MIME sub content type that represents `text/html`. """


    def __init__(self):
        self.subject = ""
        # self.attachments = []
        self.content_type = ""
        self.body = ""


    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(subject={self.subject!r}, '
                # f'attachments={self.attachments!r}, '
                f'content_type={self.content_type!r}, '
                f'body={self.body!r})'
                )


    def get_body(self):
        """
        Get the body of the email.

        :returns: the body of the email
        :rtype: str
        """
        return self.body


    def get_content_type(self):
        """
        Get the content type.

        :returns: the content type
        :rtype: str
        """
        return self.content_type


    def get_subject(self):
        """
        Get the subject line.

        :returns: the subject line
        :rtype: str
        """
        return self.subject


    def set_body(self, body):
        """
        Set the email body which contains the message.

        :param body: the body of the email
        :type: str
        """
        self.body = body


    def set_content_type(self, content_type):
        """
        Set the content type. The type of content is the MIME sub content type.
        This can only be either "plain" or "html".

        :param content_type: the type of content
        :type: str
        """
        self.content_type = content_type


    def set_subject(self, subject):
        """
        Set the subject line which summarizes the email.

        :param subject: the subject line
        :type: str
        """
        self.subject = subject
