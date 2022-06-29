# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Client Module
=============

This module is a thread-safe email client.
"""

# standard modules
import poplib
import smtplib
import socket
import threading
import time
from datetime import datetime
from email import parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid

# internal modules
from heimdallsword.data.config import Config
from heimdallsword.models.recipient import DeliveryState


class EmailClient:
    """
    The :py:class:`heimdallsword.dispatcher.client.EmailClient` class serves
    as an email client used to manage an SMTP connection and send emails to
    any given recipients. This is a thread-safe class.

    :param sender: a reference to a :py:class:`heimdallsword.models.sender.Sender` object
                   that contains the email address and password to establish a connection
                   with it's SMTP server which will be used to send emails to any recipient
    :type: :py:obj:`heimdallsword.models.sender.Sender`

    :param metrics_delay: the number of seconds to wait between sending an email and checking
                          the sender inbox for bounced emails
    :type: int
    """

    def __init__(self, sender, metrics_delay=Config.DEFAULT_METRICS_DELAY):
        self._lock = threading.Lock()
        self._connection_state = False
        self._smtp_session = None

        self.sender = sender
        self.metrics_delay = metrics_delay


    def _establish_smtp_connection(self):
        """
        Internal method that attempts to establish a connection between the sender and it's SMTP server,
        and saves the SMTP session for sending emails.

        This method is thread-safe.

        **CAUTION:**
        Several exceptions are thrown when attempting to establish connection with
        an SMTP server.

        The :py:class:`smtplib.SMTP` class throws the following exceptions:

        +---------------------------------+-------------------------------------------------------------+
        | socket.gaierror                 | thrown when there is no network connection                  |
        +---------------------------------+-------------------------------------------------------------+
        | TimeoutError                    | thrown when it took too long to establish a connection      |
        +---------------------------------+-------------------------------------------------------------+
        | ConnectionRefusedError          | thrown when the SMTP server denied connection               |
        +---------------------------------+-------------------------------------------------------------+
        | RuntimeError                    | thrown by starttls().                                       |
        |                                 |                                                             |
        |                                 | *starttls() throws this exception when no SSL support       |
        |                                 |  is included in this Python version                         |
        +---------------------------------+-------------------------------------------------------------+
        | ValueError                      | thrown by starttls().                                       |
        |                                 |                                                             |
        |                                 | *starttls() throws this exception when context and          |
        |                                 |  keyfile arguments are mutually exclusive. Also, when       |
        |                                 |  context and certfile arguments are mutually exclusive      |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPHeloError           | thrown by login() and starttls() when the server didn't     |
        |                                 | reply properly to the helo greeting                         |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPAuthenticationError | thrown by login() when the server didn't accept the         |
        |                                 | username/password combination                               |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPNotSupportedError   | thrown by starttls() and login().                           |
        |                                 |                                                             |
        |                                 | *starttls() thrown this exception when the SMTP server      |
        |                                 |  doesn't support STARTTLS extension                         |
        |                                 | *login() throws this exception when the AUTH command        |
        |                                 |  is not supported by the server                             |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPException           | thrown by login() when no suitable authentication           |
        |                                 | method was found                                            |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPResponseException   | thrown by starttls() due to the following errors RFC 3207:  |
        |                                 |                                                             |
        |                                 | *501: syntax error (no parameters allowed)                  |
        |                                 | *454: TLS not available due to temporary reason             |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPConnectError        | thrown by SMTP constructor when it fails to connect to      |
        |                                 | the SMTP server                                             |
        +---------------------------------+-------------------------------------------------------------+
        | smtplib.SMTPServerDisconnected  | thrown by login() when the connection to the SMTP server    |
        |                                 |is closed unexpectedly                                       |
        +---------------------------------+-------------------------------------------------------------+

        """

        # Terminate any existing connection
        self.terminate_session()

        smtp_session = smtplib.SMTP(host=self.sender.get_smtp_url(), port=self.sender.get_smtp_port())
        smtp_session.set_debuglevel(0)
        smtp_session.ehlo()
        smtp_session.starttls()
        smtp_session.login(self.sender.get_email(), self.sender.get_password())

        self.acquire_lock()
        self._smtp_session = smtp_session
        self._connection_state = True
        self.release_lock()


    def acquire_lock(self):
        """
        Acquires the module-level I/O thread lock.
        """

        if self._lock:
            self._lock.acquire()


    def release_lock(self):
        """
        Releases the module-level I/O thread lock.
        """

        if self._lock:
            self._lock.release()


    def get_lock(self):
        """
        Get a reference to the module-level I/O thread lock.

        :returns: A reference to the lock
        :rtype: :py:obj:`threading.Lock`
        """

        return self._lock


    def test_connection(self):
        """
        Attempts to establish a connection between the sender and it's SMTP server.

        This method is thread-safe.

        :returns: True on successful connection, False otherwise
        :rtype: bool
        """

        try:
            self._establish_smtp_connection()
        except Exception:
            return False
        else:
            self.terminate_session()
            return True


    def terminate_session(self):
        """
        Closes an existing SMTP connection.

        This method is thread-safe.

        **NOTE:**
        This method will catch :py:class:`smtplib.SMTPServerDisconnected` exception
        that is thrown when calling :py:meth:`SMTP.quit()` and it is ignored
        as it has no effect to the process if the session couldn't be
        terminated.
        """

        with self.get_lock():
            if self._smtp_session:
                try:
                    self._connection_state = False
                    self._smtp_session.quit()
                except smtplib.SMTPServerDisconnected:
                    #
                    # NOTE:
                    # It is frown upon to simply pass when catching an exception,
                    # however, if this exception is thrown then there is nothing
                    # more that can be done and we must treat this connection as
                    # dead. This could happen if internet connection dropped, or
                    # the connection timed out. Regardless, a new seesion neets
                    # to be reestalished.
                    #
                    pass
                finally:
                    self._smtp_session = None


    def is_connection_active(self):
        """
        Checks to see if the connection with the SMTP server is still alive by
        sending an SMTP 'noop' command which doesn't do anything.

        This method is thread-safe.

        :returns: True on successful connection, False otherwise
        :rtype: bool
        """

        with self.get_lock():
            status = -1

            if self._smtp_session:
                status = self._smtp_session.noop()[0]

            return True if status == 250 else False


    def send(self, recipient):
        """
        Attempts to send an email to a given `recipient`. This method rethrows
        any exception thrown by the :py:mod:`smtplib.SMTP` module.

        This method is thread-safe.

        When an exception is caught, any error codes generated by the SMTP
        server are stored in the :py:attr:`heimdallsword.models.recipient.Recipient.delivery_error_code` attribute,
        error messages are stored in the :py:attr:`heimdallsword.models.recipient.Recipient.delivery_error_message`
        attribute, and the :py:attr:`heimdallsword.models.recipient.Recipient.delivery_state` attribute is set with
        a constant type from :py:class:`heimdallsword.models.recipient.DeliveryState` class.

        This method returns :py:const:`heimdallsword.models.recipient.DeliveryState.SUCCESSFUL_DELIVERY`, otherwise
        it returns any of the other type of failed constants to describe as much as possible why it failed to send
        the email.

        :param recipient: the recipient object
        :type: :py:obj:`heimdallsword.models.recipient.Recipient`

        :returns: :py:const:`heimdallsword.models.recipient.DeliveryState.SUCCESSFUL_DELIVERY`
                  on successful delivery of an email
        :rtype: :py:obj:`heimdallsword.models.recipient.DeliveryState`
        """

        exception = None
        status = DeliveryState.NOT_DELIVERED
        timestamp = datetime.now().timestamp()

        if not recipient:
            raise IOError("No recipient was provided")

        if not self._connection_state:
            try:
                self._establish_smtp_connection()
            except Exception as e:
                self.release_lock()
                recipient.set_delivery_error_code(0)
                recipient.set_delivery_error_message(str(e))
                recipient.set_delivery_state(DeliveryState.DISCONNECTED)
                recipient.set_sent_timestamp(timestamp)
                raise e

        msg_id = make_msgid(domain=recipient.get_email_domain())
        message = recipient.get_message()

        msg = MIMEMultipart()
        msg["From"] = self.sender.get_email()
        msg["To"] = recipient.get_email()
        msg["Subject"] = message.get_subject()
        msg.add_header("Message-ID", msg_id)
        msg.attach(MIMEText(message.get_body(), message.get_content_type()))

        # Store the message id value generated to track email delivery status if no
        # exception is thrown
        recipient.set_msg_id(msg_id)

        # Update the timestamp again to reflect an accurate time of when the email was sent
        timestamp = datetime.now().timestamp()

        try:
            # Record the epoch time right before the email is sent
            recipient.set_sending_timestamp(timestamp)

            self.acquire_lock()
            failed_recipients = self._smtp_session.send_message(msg)

            # Record the epoch time when the email was sent
            recipient.set_sent_timestamp(timestamp)

            if len(failed_recipients) > 0:
                #
                # NOTE:
                # Since we are only sending one recipient, we should only expect a
                # dictionary of size one which would contain the recipient email address
                # and the error code with message. In the future, if we decide to support
                # multiple recipients, then we need to iterate through the dictionary
                # of failed recipients. For now, this is fine.
                #
                recipient.set_delivery_error_code(failed_recipients[recipient.get_email()][0])
                recipient.set_delivery_error_message(failed_recipients[recipient.get_email()][1])
                recipient.set_delivery_state(DeliveryState.FAILED_DELIVERY)

            else:
                recipient.set_delivery_state(DeliveryState.SUCCESSFUL_DELIVERY)

                # Wait up to whatever time is set for the metrics delay. This is needed
                # in order to give it time for the server to report an email bounced
                time.sleep(self.metrics_delay)

                # Check if there are any emails that bounced by searching for the msg_id
                self._get_bounced_emails(recipient)

                # If the delivery state changed to anything but SUCCESSFUL_DELIVERY, then
                # generate an exception and pass the error message retrieved
                if recipient.get_delivery_state():
                    exception = Exception(recipient.get_delivery_error_message())

        except smtplib.SMTPSenderRefused as e:
            #
            # NOTE:
            # This exception is thrown when the server didn't accept the sender email.
            # This exception inherits from the base class SMTPResponseException
            #
            exception = e
            recipient.set_delivery_error_code(e.smtp_code)
            recipient.set_delivery_error_message(e.smtp_error.decode("utf-8"))
            recipient.set_delivery_state(DeliveryState.SENDER_REJECTED)

        except smtplib.SMTPRecipientsRefused as e:
            #
            # NOTE:
            # This exception is thrown when recipient address rejected; User unknown.
            #
            exception = e
            recipient.set_delivery_error_code(550)
            recipient.set_delivery_error_message(str(e))
            recipient.set_delivery_state(DeliveryState.RECIPIENT_REJECTED)

        except smtplib.SMTPResponseException as e:
            #
            # NOTE:
            # SMTPResponseException is the base class for the following exceptions:
            #   SMTPHeloError
            #   SMTPSenderRefused (shouldn't be captured here as it's captured above)
            #   SMTPDataError
            #
            # Using the base class allows us to catch other exceptions that inherit
            # from the base class making it simpler to just get the SMTP error code
            # and message.
            #
            exception = e
            recipient.set_delivery_error_code(e.smtp_code)
            recipient.set_delivery_error_message(e.smtp_error.decode("utf-8"))
            recipient.set_delivery_state(DeliveryState.FAILED_DELIVERY)

        except smtplib.SMTPNotSupportedError as e:
            #
            # NOTE:
            # This exception is thrown when the mail_options parameter includes 'SMTPUTF8'
            # but the SMTPUTF8 extension is not supported by the server.
            #
            exception = e
            recipient.set_delivery_error_code(0)
            recipient.set_delivery_error_message(str(e))
            recipient.set_delivery_state(DeliveryState.INVALID_FORMAT)

        except ValueError as e:
            #
            # NOTE:
            # This exception is thrown when the message has more than one 'Resent-'
            # header block.
            #
            exception = e
            recipient.set_delivery_error_code(0)
            recipient.set_delivery_error_message(str(e))
            recipient.set_delivery_state(DeliveryState.INVALID_FORMAT)

        except smtplib.SMTPServerDisconnected as e:
            #
            # NOTE:
            # This exception is thrown when the SMTP connection is lost. This could
            # happen for several reasons.
            #
            exception = e
            recipient.set_delivery_error_code(0)
            recipient.set_delivery_error_message(str(e))
            recipient.set_delivery_state(DeliveryState.DISCONNECTED)
            self._connection_state = False

        finally:
            # Release the lock
            self.release_lock()

            # Release message resources
            del msg


        # If an exception is caught above when attempting to send an email, re-throw
        # the except at this point because we needed time to release resources as well as
        # capture information about the exception and so on. This informaiton is stored
        # in the recipient.
        if recipient.get_delivery_state() is not DeliveryState.SUCCESSFUL_DELIVERY and \
           recipient.get_delivery_state() is not DeliveryState.NOT_DELIVERED:
            raise exception

        status = recipient.get_delivery_state()

        return status



    def _close_pop3_connection(self, mailbox):
        """
        Internal method used to close an existing POP3 connection.

        **NOTE:**
        This method will catch any type of exception that may be thrown
        when calling :py:meth:`POP3.quit()` and it is ignored as it has
        no effect to the process if the session couldn't be terminated.

        :param mailbox: a :py:obj:`poplib.POP3_SSL` object with an active
                        session
        """

        if mailbox:
            try:
                mailbox.quit()

            except Exception:
                #
                # NOTE:
                # If there isn't an established connection, quit() will thrown
                # an AttributeError exception because there isn't an active socket
                # connection and hence no `sendall` method is available.
                # Another possible outcome is an `error_proto` exception is called
                # if it fails to get or parse a response.
                #
                pass


    def _establish_pop3_connection(self):
        """
        Internal method used for establishing a POP3 SSL connection.

        **CAUTION:**
        Several exceptions are thrown when attempting to establish a POP3 connection
        with an SMTP server.

        The :py:class:`poplib.POP3_SSL` class throws the following exceptions:

          poplib.error_proto - thrown when it fails to authenticate or when it fails to get
                               a response from the server.
          socket.timeout     - thrown when it took too long to establish a connection.

        :returns: the POP3 mailbox if connection is successful, None otherwise
        :rtype: :py:obj:`poplib.POP3_SSL`
        """

        mailbox = None

        try:
            # Establish a socket connection with the SMTP server to access emails
            mailbox = poplib.POP3_SSL(self.sender.get_smtp_url(), self.sender.get_pop3_port(), timeout=30)
            # Send the user email address. Even if the email is incorrect
            mailbox.user(self.sender.get_email())
            mailbox.pass_(self.sender.get_password())

        except poplib.error_proto:
            #
            # NOTE:
            # This exception is thrown when it failed to authenticate or when it failed to get
            # a response from the server
            #
            self._close_pop3_connection(mailbox)
            mailbox = None

        except socket.timeout:
            #
            # NOTE:
            # The server isn't responding or there is too much latency
            #
            self._close_pop3_connection(mailbox)
            mailbox = None

        return mailbox


    def _get_bounced_emails(self, recipient):
        """
        Internal method used for establishing a POP3 SSL connection and read through
        all the emails looking for any possible email that matches the `msg_id`
        previously assigned to it. If a positive match is found, extract any information
        that contains information regarding the failed delivery attempt and store in
        the given `recipient`.

        :param recipient: the recipient containing the `msg_id` assigned
        :type: :py:obj:`heimdallsword.models.recipient.Recipient`
        """

        if not recipient:
            raise IOError("No recipient was provided to check for bounced emails")

        # It seems that MAXLINE is set too low by default. So we
        # will increase the value to make sure poplib doesn't throw
        # an error_proto("-ERR EOF") exception by _getline() function
        # in poplib.py
        poplib._MAXLINE = 20480

        mailbox = self._establish_pop3_connection()

        if mailbox:
            # Get all the messages from the server
            messages = [mailbox.retr(i) for i in range(1, len(mailbox.list()[1]) + 1)]

            # Concatenate message pieces. All pieces are byte strings
            messages = [b"\n".join(msg[1]) for msg in messages]

            # Parse message into an email object
            messages = [parser.Parser().parsestr(msg.decode(encoding='UTF-8')) for msg in messages]

            for msg in messages:
                if "Undelivered" in msg["subject"]:
                    msg_id = None
                    error_code = 0
                    error_message = "N/A"

                    for part in msg.walk():
                        if part.get_content_type() == "multipart/mixed":
                            if part["Message-ID"] is not None:
                                msg_id = part["Message-ID"]

                        if part.get_content_type() == "text/plain" or \
                           part.get_content_type() == "text/html":
                            if part["Diagnostic-Code"] is not None:
                                error_message = part["Diagnostic-Code"]
                            elif part["Status"] is not None:
                                error_code = part["Status"]


                    # Bail as soon as the bounced email is found and collect info as to why it bounced
                    if recipient.get_msg_id() == msg_id:
                        recipient.set_delivery_error_code(error_code)
                        recipient.set_delivery_error_message(error_message)
                        recipient.set_delivery_state(DeliveryState.FAILED_DELIVERY)
                        break
