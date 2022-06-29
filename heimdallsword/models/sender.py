# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Sender Module
=============

This module contains information about the sender account.
"""


class Sender:
    """
    The :py:class:`Sender` class represents a sender.


    :param email: the email address of the sender
    :type: str

    :param password: the password of the sender email account to authenticate with the SMTP server
    :type: str

    :param smtp_port: the port number used to establish an SMTP session. Default port is 587
    :type: int

    :param smtp_url: the sender's SMTP URL to authenticate. Default is the domain of the
                     sender's email
    :type: str

    :param pop3_port: the port number used to establish a POP3 session. Default port is 995
    :type: int

    :param pop3_url: the sender's POP3 URL to authenticate. Default is the domain of the
                     sender's email
    :type: str
    """

    def __init__(self):
        self._email_domain = ""

        self.email = ""
        self.password = ""
        self.smtp_port = ""
        self.pop3_port = ""
        self.smtp_url = ""
        self.pop3_url = ""


    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(email={self.email!r}, '
                f'password={self.password!r}, '
                f'smtp_port={self.smtp_port!r}, '
                f'smtp_url={self.smtp_url!r}), '
                f'pop3_port={self.pop3_port!r}, '
                f'pop3_url={self.pop3_url!r})'
                )

    def get_email(self):
        """
        Get the email address of the sender.

        :returns: the sender's email
        :rtype: str
        """

        return self.email


    def get_password(self):
        """
        Get the password of the sender email account to authenticate with
        the SMTP server.

        :returns: the sender's password
        :rtype: str
        """

        return self.password


    def get_smtp_port(self):
        """
        Get the port number used to establish an SMTP session.

        :returns: the SMTP port
        :rtype: int
        """

        return self.smtp_port


    def get_smtp_url(self):
        """
        Get the sender's SMTP URL to authenticate. If no SMTP URL was
        specified, then the domain of the sender's email is returned.

        :returns: the SMTP URL
        :rtype: str
        """

        if self.smtp_url:
            return self.smtp_url
        else:
            return self._email_domain


    def get_pop3_port(self):
        """
        Get the port number used to establish a POP3 session.

        :returns: the port number used to establish a POP3 session.
        :rtype: int
        """

        return self.pop3_port


    def get_pop3_url(self):
        """
        Get the sender's POP3 URL to authenticate. If no POP3 URL was
        specified, then the domain of the sender's email is returned.

        :returns: the POP3 URL
        :rtype: str
        """

        if self.pop3_url:
            return self.pop3_url
        else:
            return self._email_domain


    def set_email(self, email):
        """
        Set the email address of the sender.

        :param email: the sender's email
        :type: str

        :raises: IOError - Invalid sender email
        """

        if len(email.split("@")) == 2:
            self.email = email
            self._email_domain = email.split("@")[1]
        else:
            raise IOError("Invalid sender email")


    def set_password(self, password):
        """
        Set the password of the sender email account to authenticate
        with the SMTP server.

        :param password: the sender's email password
        :type: str
        """

        self.password = password


    def set_smtp_port(self, smtp_port):
        """
        Set the port number used to establish an SMTP session.

        :param smtp_port: the SMTP port
        :type: int
        """

        self.smtp_port = smtp_port


    def set_smtp_url(self, smtp_url):
        """
        Set the sender's SMTP URL to authenticate.

        :param smtp_url: the SMTP URL
        :type: str
        """

        self.smtp_url = smtp_url


    def set_pop3_port(self, pop3_port):
        """
        Set the port number used to establish a POP3 session.

        :param pop3_port: the POP3 port
        :type: int
        """

        self.pop3_port = pop3_port


    def set_pop3_url(self, pop3_url):
        """
        Set the sender's POP3 URL to authenticate.

        :param pop3_url: the POP3 URL
        :type: str
        """

        self.pop3_url = pop3_url
