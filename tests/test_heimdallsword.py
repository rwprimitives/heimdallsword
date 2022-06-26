# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Unit Test for HeimdallSword
===========================

This is a unit test script for HeimdallSword to ensure that any changes made in the main
code do not break the functionality of the tool.
"""

# standard modules
import logging
import re
import sys
import os
import unittest

# add the parent directory path to PYTHONPATH so that the HeimdallSword modules
# can be imported for testing
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# internal modules
from heimdallsword.utils import parser
from heimdallsword.data.config import Config
from heimdallsword.data.metrics import Metrics
from heimdallsword.models.recipient import Recipient
from heimdallsword.models.message import Message
from heimdallsword.release import __package__ as PACKAGE
from heimdallsword.release import __version__ as VERSION


class HeimdallSwordTests(unittest.TestCase):

    def test_recipient_content_bad_currency(self):
        content_dir = "./sample_data/recipient_test/content"

        recipient = Recipient()
        recipient.set_email("recip1@gmail.com")
        recipient.set_message_filename("msg_bad_currency.txt")

        with self.assertRaises(ValueError) as exception_context:
            parser.get_message(content_dir, recipient)

        e_rx = re.compile(f"Failed to parse '{recipient.get_message_filename()}'\.([^\.]*)\. Use \$\$ to add the \$ symbol")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_content_bad_key(self):
        content_dir = "./sample_data/recipient_test/content"

        recipient = Recipient()
        recipient.set_email("recip1@gmail.com")
        recipient.set_message_filename("msg_bad_key.txt")

        with self.assertRaises(KeyError) as exception_context:
            parser.get_message(content_dir, recipient)

        e_rx = re.compile(f'"Failed to parse \'{recipient.get_message_filename()}\'. The tag \'([^\']*)\' is not defined"')
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)



    def test_recipient_content_bad_subject(self):
        content_dir = "./sample_data/recipient_test/content"

        recipient = Recipient()
        recipient.set_email("recip1@gmail.com")
        recipient.set_message_filename("msg_bad_content_subject.txt")

        with self.assertRaises(ValueError) as exception_context:
            parser.get_message(content_dir, recipient)

        self.assertEqual(str(exception_context.exception),
                         f"Failed to parse '{recipient.get_message_filename()}. No subject was provided")


    def test_recipient_content_bad_type(self):
        content_dir = "./sample_data/recipient_test/content"

        recipient = Recipient()
        recipient.set_email("recip1@gmail.com")
        recipient.set_message_filename("msg_bad_content_type.txt")

        with self.assertRaises(ValueError) as exception_context:
            parser.get_message(content_dir, recipient)

        e_rx = re.compile(f"Failed to parse '{recipient.get_message_filename()}'. The content type defined '([^']*)' is invalid. Content type can only be one of the following: {Message.PLAIN}, {Message.HTML}")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_content_no_message_file(self):
        content_dir = "./sample_data/recipient_test/content"

        recipient = Recipient()
        recipient.set_email("recip1@gmail.com")
        recipient.set_message_filename("asdf")

        with self.assertRaises(FileNotFoundError) as exception_context:
            parser.get_message(content_dir, recipient)

        e_rx = re.compile("Message file '([^']*)' was not found")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_bad_email(self):
        recipient_file = "./sample_data/recipient_test/recipient_bad_email.txt"
        content_dir = "./sample_data/recipient_test/content"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_recipients(content_dir, recipient_file)

        e_rx = re.compile(f"Failed to parse '{recipient_file}'. Line #[0-9]+ contains an invalid email address")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_bad_format(self):
        recipient_file = "./sample_data/recipient_test/recipient_bad_format.txt"
        content_dir = "./sample_data/recipient_test/content"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_recipients(content_dir, recipient_file)

        e_rx = re.compile(f"Failed to parse '{recipient_file}'. Line #[0-9]+ is not in the correct format")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_bad_key_value(self):
        recipient_file = "./sample_data/recipient_test/recipient_bad_key-value.txt"
        content_dir = "./sample_data/recipient_test/content"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_recipients(content_dir, recipient_file)

        e_rx = re.compile(f"Failed to parse '{recipient_file}'. Line #[0-9]+ has an invalid key-value pair '[a-zA-Z0-1]+'")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_bad_message_file(self):
        recipient_file = "./sample_data/recipient_test/recipient_no_message_file.txt"
        content_dir = "./sample_data/recipient_test/content"

        with self.assertRaises(FileNotFoundError) as exception_context:
            parser.get_recipients(content_dir, recipient_file)

        e_rx = re.compile(f"Failed to parse '{recipient_file}'. Line #[0-9]+ does not contain a valid message file")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_recipient_good_file(self):
        recipient_file = "./sample_data/recipient_test/recipient_good.txt"
        content_dir = "./sample_data/recipient_test/content"

        try:
            parser.get_recipients(content_dir, recipient_file)

        except Exception as e:
            self.fail(e)


    def test_recipient_no_emails(self):
        recipient_file = "./sample_data/recipient_test/recipient_no_emails.txt"
        content_dir = "./sample_data/recipient_test/content"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_recipients(content_dir, recipient_file)

        self.assertEqual(str(exception_context.exception),
                         f"Failed to parse '{recipient_file}'. No emails were found")


    def test_sender_bad_email(self):
        sender_file = "./sample_data/sender_test/sender_bad_email.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_SMTP_PORT)

        e_rx = re.compile(f"Failed to parse '{sender_file}'. Line #[0-9]+ contains an invalid email address")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_sender_bad_password(self):
        sender_file = "./sample_data/sender_test/sender_bad_password.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_SMTP_PORT)

        e_rx = re.compile(f"Failed to parse '{sender_file}'. Line #[0-9]+ does not contain a valid password")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_sender_bad_key_value(self):
        sender_file = "./sample_data/sender_test/sender_bad_key-value.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_SMTP_PORT)

        e_rx = re.compile(f"Failed to parse '{sender_file}'. Line #[0-9]+ has an invalid key-value pair '[a-zA-Z0-1]+'")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_sender_bad_pop3_port(self):
        sender_file = "./sample_data/sender_test/sender_bad_pop3_port.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_SMTP_PORT)

        e_rx = re.compile(f"Failed to parse '{sender_file}'. Line #[0-9]+ has an invalid POP3 port number")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_sender_bad_smtp_port(self):
        sender_file = "./sample_data/sender_test/sender_bad_smtp_port.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_SMTP_PORT)

        e_rx = re.compile(f"Failed to parse '{sender_file}'. Line #[0-9]+ has an invalid SMTP port number")
        self.assertNotEqual(e_rx.fullmatch(str(exception_context.exception)), None)


    def test_sender_good_file(self):
        sender_file = "./sample_data/sender_test/sender_good.txt"
        try:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_POP3_PORT)

        except Exception as e:
            self.fail(e)


    def test_sender_no_emails(self):
        sender_file = "./sample_data/sender_test/sender_no_emails.txt"

        with self.assertRaises(ValueError) as exception_context:
            parser.get_senders(sender_file, Config.DEFAULT_SMTP_PORT, Config.DEFAULT_POP3_PORT)

        self.assertEqual(str(exception_context.exception),
                         f"Failed to parse '{sender_file}'. No emails were found")



    # def test_process_all(self):
    #     self.config = Config()
    #     self.config.sender_file = "./sample_data/good_sample/senders.txt"
    #     self.config.recipient_file = "./sample_data/good_sample/recipient.txt"
    #     self.config.content_dir = "./sample_data/good_sample/content"
    #     self.config.process_dir = "./sample_data/good_sample"

    #     self.metrics = Metrics(self.config.metrics_file_path)

if __name__ == '__main__':
    unittest.main()
