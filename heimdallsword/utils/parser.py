# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Parser Module
=============

This module provides the necessary means to parse the sender, recipient
and the email templates.
"""

# standard modules
import os
import re
import time
from string import Template

# internal modules
from heimdallsword.utils import util
from heimdallsword.models.recipient import Recipient
from heimdallsword.models.message import Message
from heimdallsword.models.sender import Sender


def _get_body(key, data):
    """
    Internal method for parsing the body content in a message file.

    :param data: the content in a message file
    :type: str

    :returns: the body content
    :rtype: str
    """

    reg_ex_obj = re.compile(key)
    is_body = False
    body = []
    for line in data.splitlines():
        if not is_body:
            if reg_ex_obj.search(line) is not None:
                is_body = True
                line_split = line.split("=")
                if len(line_split) == 2:
                    # Remove the key for the first line
                    line_split = line.split("=")[1]
                    body.append(f"{line_split}\n")
        else:
            body.append(f"{line}\n")

    return ("".join(body))


def get_message(content_dir, recipient):
    """
    Constructs a :py:class:`heimdallsword.models.message.Message` object based
    on a given :py:class:`heimdallsword.models.recipient.Recipient` and the
    path of the message file.

    :param content_dir: the directory path where the message file resides
    :type: str

    :param recipient: the recipient assigned to the message
    :type: :py:class:`heimdallsword.models.recipient.Recipient`

    :returns: a :py:class:`heimdallsword.models.message.Message` object
    :rtype: :py:class:`heimdallsword.models.message.Message`

    :raises: IOError - No recipient was provided
    :raises: FileNotFoundError - Message file '{message_file_path}' was not found
    :raises: ValueError - Failed to parse '{recipient.get_message_filename()}.
                          No subject was provided
    :raises: ValueError - Failed to parse '{recipient.get_message_filename()}'.
                          The content type defined '{content_type}' is invalid.
                          Content type can only be one of the following: {Message.PLAIN}, {Message.HTML}
    :raises: KeyError - Failed to parse '{recipient.get_message_filename()}'.
                        The tag {e} is not defined
    :raises: ValueError - Failed to parse '{recipient.get_message_filename()}'.
                          {e}. Use $$ to add the $ symbol
    """

    subject = ""
    content_type = ""
    # attachments = []
    body = ""
    tag_dict = {}
    message = Message()
    counter = 0


    if not recipient:
        raise IOError("No recipient was provided")

    message_file_path = os.path.abspath(os.path.join(content_dir, recipient.get_message_filename()))

    if not os.path.isfile(message_file_path):
        raise FileNotFoundError(f"Message file '{message_file_path}' was not found")

    f = open(message_file_path, "r", encoding="UTF-8")

    try:
        file_content = f.read()
    except UnicodeDecodeError as e:
        e.reason += f". Failed to parse '{recipient.get_message_filename()}'"
        raise
    finally:
        f.close()

    subject = util.get_value_from_key("subject=", file_content)
    content_type = util.get_value_from_key("content_type=", file_content)
    # attachments = util.get_value_from_key("attachments=", file_content)
    raw_body = _get_body("body=", file_content)

    # Make sure a subject is provided
    if not len(subject):
        raise ValueError(f"Failed to parse '{recipient.get_message_filename()}. No subject was provided")

    # Make sure content type is valid
    if content_type != Message.PLAIN and content_type != Message.HTML:
        raise ValueError(f"Failed to parse '{recipient.get_message_filename()}'. "
                         f"The content type defined '{content_type}' is invalid. "
                         f"Content type can only be one of the following: {Message.PLAIN}, {Message.HTML}")

    # Create a dictionary of supported tags if the template references them
    tag_dict["EMAIL"] = recipient.get_email()
    tag_dict["EMAIL_USERNAME"] = recipient.get_email_username()
    tag_dict["EMAIL_DOMAIN"] = recipient.get_email_domain()

    # Find supported tags with custom definitions
    local_date_tags = re.findall(r"\$\{LOCAL_DATE.*?\}", raw_body, re.MULTILINE)
    local_time_tags = re.findall(r"\$\{LOCAL_TIME.*?\}", raw_body, re.MULTILINE)
    utc_date_tags = re.findall(r"\$\{UTC_DATE.*?\}", raw_body, re.MULTILINE)
    utc_time_tags = re.findall(r"\$\{UTC_TIME.*?\}", raw_body, re.MULTILINE)

    timestamp = time.time()

    # Add current date tags into dictionary
    counter = 1
    for local_date in local_date_tags:
        # Remove unwanted characters
        local_date = f"{local_date}".strip("$").strip("{").strip("}")
        tag_split = local_date.split("=")
        if len(tag_split) == 2:
            key = f"LOCAL_DATE{counter}"
            tag_dict[key] = time.strftime(tag_split[1], time.localtime(timestamp))
            raw_body = raw_body.replace(f"{local_date}", key)
            counter += 1
        else:
            tag_dict[local_date] = time.strftime("%m/%d/%Y", time.localtime(timestamp))

    # Add current time tags into dictionary
    counter = 1
    for local_time in local_time_tags:
        # Remove unwanted characters
        local_time = f"{local_time}".strip("$").strip("{").strip("}")
        tag_split = local_time.split("=")
        if len(tag_split) == 2:
            key = f"LOCAL_TIME{counter}"
            tag_dict[key] = time.strftime(tag_split[1], time.localtime(timestamp))
            raw_body = raw_body.replace(f"{local_time}", key)
            counter += 1
        else:
            tag_dict[local_time] = time.strftime("%I:%M %p", time.localtime(timestamp))

    # Add utc date tags into dictionary
    counter = 1
    for utc_date in utc_date_tags:
        # Remove unwanted characters
        utc_date = f"{utc_date}".strip("$").strip("{").strip("}")
        tag_split = utc_date.split("=")
        if len(tag_split) == 2:
            key = f"UTC_DATE{counter}"
            tag_dict[key] = time.strftime(tag_split[1], time.gmtime(timestamp))
            raw_body = raw_body.replace(f"{utc_date}", key)
            counter += 1
        else:
            tag_dict[utc_date] = time.strftime("%m/%d/%Y", time.gmtime(timestamp))

    # Add utc time tags into dictionary
    counter = 1
    for utc_time in utc_time_tags:
        # Remove unwanted characters
        utc_time = f"{utc_time}".strip("$").strip("{").strip("}")
        tag_split = utc_time.split("=")
        if len(tag_split) == 2:
            key = f"UTC_TIME{counter}"
            tag_dict[key] = time.strftime(tag_split[1], time.gmtime(timestamp))
            raw_body = raw_body.replace(f"{utc_time}", key)
            counter += 1
        else:
            tag_dict[utc_time] = time.strftime("%I:%M %p", time.gmtime(timestamp))

    # Add all custom tags
    for key in recipient.get_all_custom_tags():
        tag_dict[key] = recipient.get_custom_tag(key)

    # Create a string Template and substitute any tags if they are defined
    # in the message file
    # REF: https://docs.python.org/3/library/string.html
    try:
        template = Template(raw_body)
        body = template.substitute(tag_dict)

    except KeyError as e:
        # To trigger a KeyError, add a tag to the body that it isn't in the tag_dict
        raise KeyError(f"Failed to parse '{recipient.get_message_filename()}'. The tag {e} is not defined")

    except ValueError as e:
        # To trigger a ValueError, add a dollar currency number (e.g., $1500)
        raise ValueError(f"Failed to parse '{recipient.get_message_filename()}'. {e}. Use $$ to add the $ symbol")


    else:
        message.set_subject(subject)
        # message.set_attachments(attachments)
        message.set_content_type(content_type)
        message.set_body(body)

    return message


def get_recipients(content_dir, recipients_file):
    """
    Create a list of :py:class:`heimdallsword.models.recipient.Recipient` objects
    based on the a given recipient file and parses the message file associated
    with each recipient.

    Each line should be constructed in the following format:

        email address, message text file

    For example:

        recipient1@example.com, msg1.txt

        recipient2@example.com, msg2.txt

    Key-values pairs can be appended after the message file and must be comma separated.
    Any key-value pairs appended requires that the key be in the message template,
    otherwise it will be ignored.

    For example:

        recipient1@example.com, msg1.txt, fname=John, lname=Smith

        recipient2@example.com, msg2.txt, date=04/25/2022, transaction-id=ID10T

    Using the first example, the key **fname** must be in the body of the message
    template file as such: ${fname}.

    :param content_dir: the directory path where the message file resides
    :type: str

    :param recipients_file: the file containing the recipients
    :type: str

    :returns: a list of :py:class:`heimdallsword.models.recipient.Recipient` objects
    :rtype: :py:class:`heimdallsword.models.recipient.Recipient`

    :raises: NotADirectoryError - The content directory '{content_dir}' was not found
    :raises: FileNotFoundError - Recipients file '{recipients_file}' was not found
    :raises: ValueError - Failed to parse '{recipients_file}'.
                          The '{recipients_file}' is empty
    :raises: ValueError - Failed to parse '{recipients_file}'.
                          Line #{line_counter} contains an invalid email address
    :raises: FileNotFoundError - Failed to parse '{recipients_file}'.
                                 Line #{line_counter} does not contain a valid message file '{message_file}'
    :raises: ValueError - Failed to parse '{recipients_file}'.
                          Line #{line_counter} has an invalid key-value pair '{kv_pair.strip()}'
    :raises: ValueError - Failed to parse '{recipients_file}'.
                          Line #{line_counter} is not in the correct format
    :raises: ValueError - Failed to parse '{recipients_file}'.
                          No emails were found
    """

    recipients = []
    line_counter = 1

    if not os.path.isdir(content_dir):
        raise NotADirectoryError(f"The content directory '{content_dir}' was not found")

    if not os.path.isfile(recipients_file):
        raise FileNotFoundError(f"Recipients file '{recipients_file}' was not found")

    with open(recipients_file, "r", encoding="UTF-8") as f:
        lines = f.readlines()

        if len(lines) <= 0:
            raise ValueError(f"Failed to parse '{recipients_file}'. The '{recipients_file}' is empty")

        for line in lines:
            # Clean up the line first
            line = line.replace("\n", "").replace("\r", "").strip()

            # Ignore lines that begin with a hash character to treat it
            # as a "commented line"
            if line.startswith("#") or line == "":
                continue

            split = line.split(",")
            if len(split) >= 2:
                email = split[0].strip()
                message_file = split[1].strip()
                message_file_path = os.path.abspath(os.path.join(content_dir, message_file))

                if not util.is_email_valid(email):
                    raise ValueError(f"Failed to parse '{recipients_file}'. Line #{line_counter} "
                                     "contains an invalid email address")

                if not os.path.isfile(message_file_path):
                    raise FileNotFoundError(f"Failed to parse '{recipients_file}'. Line #{line_counter} "
                                            "does not contain a valid message file")

                recipient = Recipient()
                recipient.set_email(email)
                recipient.set_message_filename(message_file)

                # parse any key-value pairs parameters
                if len(split) > 2:
                    for kv_pair in split[2:]:
                        # split and check each key-value pair
                        kv_pair_split = kv_pair.split("=")
                        if len(kv_pair_split) == 2:
                            key = kv_pair_split[0].strip()
                            value = kv_pair_split[1].strip()
                            recipient.add_custom_tag(key, value)
                        else:
                            raise ValueError(f"Failed to parse '{recipients_file}'. Line #{line_counter} "
                                             f"has an invalid key-value pair '{kv_pair.strip()}'")

                # parse the message file
                recipient.set_message(get_message(content_dir, recipient))
                recipients.append(recipient)
            else:
                raise ValueError(f"Failed to parse '{recipients_file}'. Line #{line_counter} "
                                 "is not in the correct format")

            line_counter += 1

    if not len(recipients):
        raise ValueError(f"Failed to parse '{recipients_file}'. No emails were found")

    return recipients


def get_senders(senders_file, default_smtp_port, default_pop3_port):
    """
    Create a list of :py:class:`heimdallsword.models.sender.Sender` objects
    based on the a given sender file.

    Default ports for SMTP and POP3 must be provided which will be applied
    to all senders, unless each sender provides it's own SMTP port and POP3 port.

    Each line should be constructed in the following format:

        email address, password, smtp_url=, smtp_port=, pop3_url, pop3_port=

    For example:

        sender1@example.com, secretpassword!

        sender2@example.com, P@$$w0rd, smtp_url=smtp.example.com, pop3_url=pop.example.com

        sender3@example.com, hackyhackhack, smtp_url=smtp.example.com, smtp_port=587,
        pop3_url=pop.example.com, pop3_port=995

    :param senders_file: the file containing one or multiple sender accounts
    :type: str

    :param default_smtp_port: the SMTP port to use for authentication
    :type: int

    :param default_pop3_port: the POP3 port to authenticate and read emails
    :type: int

    :raises: FileNotFoundError - Senders file '{senders_file}' was not found
    :raises: ValueError - Failed to parse '{senders_file}'. The '{senders_file}' is empty
    :raises: ValueError - Failed to parse '{senders_file}'.
                          Line #{line_counter} contains an invalid email address
    :raises: ValueError - Failed to parse '{senders_file}'.
                          Line #{line_counter} has an invalid key-value pair '{kv_pair.strip()}'
    :raises: ValueError - Failed to parse '{senders_file}'.
                          Line #{line_counter} has an invalid SMTP port number
    :raises: ValueError - Failed to parse '{senders_file}'.
                          Line #{line_counter} has an invalid POP3 port number
    :raises: ValueError - Failed to parse '{senders_file}'.
                          Line #{line_counter} is not in the correct format
    :raises: ValueError - Failed to parse '{senders_file}'. No emails were found
    """

    senders = []
    line_counter = 1

    if not os.path.isfile(senders_file):
        raise FileNotFoundError(f"Senders file '{senders_file}' was not found")

    with open(senders_file, "r", encoding="UTF-8") as f:
        lines = f.readlines()

        if len(lines) <= 0:
            raise ValueError(f"Failed to parse '{senders_file}'. The '{senders_file}' is empty")

        for line in lines:
            # Clean up the line first
            line = line.replace("\n", "").replace("\r", "").strip()

            # Ignore lines that begin with a hash character to treat it
            # as a "commented line"
            if line.startswith("#") or line == "":
                continue

            split = line.split(",")
            if len(split) >= 2:
                # Reset these values
                smtp_port = default_smtp_port
                pop3_port = default_pop3_port
                smtp_url = None
                pop3_url = None
                other_options = {}

                email = split[0].strip()
                password = split[1].strip()

                if not util.is_email_valid(email):
                    raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} "
                                     "contains an invalid email address")

                if len(password) == 0:
                    raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} "
                                     "does not contain a valid password")

                # parse any additional options. These should be defined as key-value pairs
                if len(split) > 2:
                    for kv_pair in split[2:]:
                        # split and check each key-value pair
                        kv_pair_split = kv_pair.split("=")
                        if len(kv_pair_split) == 2:
                            key = kv_pair_split[0].strip()
                            value = kv_pair_split[1].strip()
                            other_options[key] = value
                        else:
                            raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} "
                                             f"has an invalid key-value pair '{kv_pair.strip()}'")

                    if "smtp_url" in other_options:
                        smtp_url = other_options["smtp_url"]

                    if "smtp_port" in other_options:
                        smtp_port = other_options["smtp_port"]
                        if not util.is_int(smtp_port):
                            raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} "
                                             "has an invalid SMTP port number")

                    if "pop3_url" in other_options:
                        pop3_url = other_options["pop3_url"]

                    if "pop3_port" in other_options:
                        pop3_port = other_options["pop3_port"]
                        if not util.is_int(pop3_port):
                            raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} "
                                             "has an invalid POP3 port number")

                sender = Sender()
                sender.set_email(email)
                sender.set_password(password)
                sender.set_smtp_port(smtp_port)
                sender.set_smtp_url(smtp_url)
                sender.set_pop3_port(pop3_port)
                sender.set_pop3_url(pop3_url)

                senders.append(sender)

            else:
                raise ValueError(f"Failed to parse '{senders_file}'. Line #{line_counter} is not in the correct format")

            line_counter += 1

    if not len(senders):
        raise ValueError(f"Failed to parse '{senders_file}'. No emails were found")

    return senders
