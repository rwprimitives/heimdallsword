#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 rwprimitives
Author: eldiablo


Main Module

This module is the entry point of the command line part of the
tool.
"""

# standard modules
import argparse
import logging
import os
import sys
import threading

# internal modules
from heimdallsword.data.config import Config
from heimdallsword.data.metrics import Metrics
from heimdallsword.dispatcher.client import EmailClient
from heimdallsword.dispatcher.orchestrator import Orchestrator
from heimdallsword.graphics.renderer import CliRenderer
from heimdallsword.log import cli_log
from heimdallsword.log.handler import LogHandler
from heimdallsword.release import __author__ as AUTHOR
from heimdallsword.release import __copyright__ as COPYRIGHT
from heimdallsword.release import __description__ as DESCRIPTION
from heimdallsword.release import __license__ as LICENSE
from heimdallsword.release import __package__ as PACKAGE
from heimdallsword.release import __version__ as VERSION
from heimdallsword.release import __python_ver_maj__ as PYTHON_VERSION_MAJOR
from heimdallsword.release import __python_ver_min__ as PYTHON_VERSION_MINOR
from heimdallsword.status import ExitCodes as E
from heimdallsword.utils import parser
from heimdallsword.utils import util


class CustomFormatter(argparse.RawTextHelpFormatter):
    """
    A custom formatter class for the purpose of removing the space
    created when a metavar is not provided. This class inherits from
    :py:mod:`argparse.py` and the :pymod:`HelpFormatter._format_action_invocation()`
    is overwritten to simply modify the line that adds the metavar.
    """

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s' % option_string)
                parts[-1] += ' %s' % args_string
            return ', '.join(parts)


def process_dir(logger, config):
    recipients_file = ""
    senders_file = ""
    content_dir = ""

    senders_file = os.path.abspath(os.path.join(config.process_dir, config.DEFAULT_SENDERS_FILE))
    if not os.path.isfile(senders_file):
        logger.error(f"The directory '{config.process_dir}' does not contain a '{senders_file}' file")
        return (None, None)

    recipients_file = os.path.abspath(os.path.join(config.process_dir, config.DEFAULT_RECIPIENTS_FILE))
    if not os.path.isfile(recipients_file):
        logger.error(f"The directory '{config.process_dir}' does not contain a '{recipients_file}' file")
        return (None, None)

    content_dir = os.path.abspath(os.path.join(config.process_dir, config.DEFAULT_CONTENT_DIR))
    if not os.path.isdir(content_dir):
        logger.error(f"The directory '{config.process_dir}' does not contain a '{content_dir}' directory")
        return (None, None)

    config.senders_file = senders_file
    config.recipients_file = recipients_file
    config.content_dir = content_dir

    return process_individual(logger, config)


def process_individual(logger, config):
    senders = None
    recipients = None

    try:
        senders = parser.get_senders(config.senders_file, config.smtp_port, config.pop3_port)
        recipients = parser.get_recipients(config.content_dir, config.recipients_file)

    except Exception as e:
        logger.error(e)
        logger.exception(e)

    return (senders, recipients)


def process_test_senders(logger, config):
    senders = None

    try:
        senders = parser.get_senders(config.senders_file, config.smtp_port, config.pop3_port)

    except Exception as e:
        logger.error(e)
        logger.exception(e)

    return senders


def test_sender_accounts(logger, senders, stop_on_failure=False):
    status = E.SUCCESS

    for sender in senders:
        client = EmailClient(sender)
        if client.test_connection():
            logger.info(f"Sender '{sender.get_email()}' successfully connected")
        else:
            logger.error(f"Sender '{sender.get_email()}' failed to connect")
            status = E.SERVER_CONNECTION_FAILED

            # If flag set, exit immediately with status
            if stop_on_failure:
                return status

    return status


def get_banner():
    """
    https://www.asciiart.eu/weapons/swords
    """

    return(r"""\
                     __ __    _          __     ________                   __
              /\    / // /__ (_)_ _  ___/ /__ _/ / / __/    _____  _______/ /
             / >>  / _  / -_) /  ' \/ _  / _ `/ / /\ \| |/|/ / _ \/ __/ _  /
            /</   /_//_/\__/_/_/_/_/\_,_/\_,_/_/_/___/|__,__/\___/_/  \_,_/
<\         /< \
 |\________){o}|----------------------------------------------------------_
[////////////{*}:::<==============================================-         >
 |/~~~~~~~~){o}|----------------------------------------------------------~
</         \< /
            \<\
             \ >>
              \/
    """)


def get_light_version_info():
    info = get_banner()
    info += "\n"
    info += f"{PACKAGE} v{VERSION} by {AUTHOR}"
    info += "\n"
    return info


def get_version_info():
    info = get_banner()
    info += "\n"
    info += f"{PACKAGE} v{VERSION} \n"
    info += f"{COPYRIGHT} \n"
    info += f"{LICENSE} \n"
    info += f"Written by {AUTHOR}"
    return info


def formatter(prog):
    return CustomFormatter(prog, max_help_position=52)


def gen_arg_parser(config):
    #
    # Needed to find a way to add padding between the arguments and the descriptions.
    # Found a neat solution at the link below thanks to 'Giacomo Alzetta'.
    # REF: https://stackoverflow.com/a/52606755
    #

    arg_parser = argparse.ArgumentParser(formatter_class=formatter,
                                         prog=PACKAGE,
                                         description=DESCRIPTION)

    arg_parser.add_argument("-d", "--delay",
                            help=f"the time in milliseconds between each email sent "
                                 f"(default: {config.DEFAULT_DELAY} ms)",
                            dest="delay",
                            type=int,
                            metavar='',
                            default=config.DEFAULT_DELAY,
                            required=False)

    arg_parser.add_argument("-g", "--enable-graphics",
                            help="enables command line graphical interface",
                            dest="graphics",
                            action="store_true",
                            default=False,
                            required=False)

    arg_parser.add_argument("-lf", "--log-file",
                            help=f"the log file used to store data (default: {config.DEFAULT_LOG_FILE_PATH})",
                            dest="log_file",
                            type=str,
                            metavar='',
                            default=config.DEFAULT_LOG_FILE_PATH,
                            required=False)

    arg_parser.add_argument("-m", "--metrics-delay",
                            help=f"the time in seconds to wait after the last email sent before gathering metrics "
                                 f"(default: {config.DEFAULT_METRICS_DELAY} secs)",
                            dest="metrics_delay",
                            type=int,
                            metavar='',
                            default=config.DEFAULT_METRICS_DELAY,
                            required=False)

    arg_parser.add_argument("-mf", "--metrics-file",
                            help=f"the metrics file used to store data (default: {config.DEFAULT_METRICS_FILE_PATH})",
                            dest="metrics_file",
                            type=str,
                            metavar='',
                            default=config.DEFAULT_METRICS_FILE_PATH,
                            required=False)

    arg_parser.add_argument("-w", "--worker-count",
                            help=f"the number of worker threads to use for sending emails "
                                 f"(default: {config.worker_count})",
                            dest="worker_count",
                            type=int,
                            metavar='',
                            default=config.worker_count,
                            required=False)

    arg_parser.add_argument("-v", "--version",
                            action="version",
                            version=get_version_info())

    individual_group = arg_parser.add_argument_group("individual arguments")
    individual_group.add_argument("-c", "--content-dir",
                                  help="the directory path to the email body templates (i.e., content)",
                                  dest="content_dir",
                                  type=lambda x: util.is_directory_valid(arg_parser, x),
                                  metavar='',
                                  required=False)
    individual_group.add_argument("-r", "--recipients",
                                  help="the recipients file (i.e., recipients.txt)",
                                  dest="recipients_file",
                                  type=lambda x: util.is_file_valid(arg_parser, x),
                                  metavar='',
                                  required=False)
    individual_group.add_argument("-s", "--senders",
                                  help="the senders file (i.e., senders.txt)",
                                  dest="senders_file",
                                  type=lambda x: util.is_file_valid(arg_parser, x),
                                  metavar='',
                                  required=False)

    process_group = arg_parser.add_argument_group("combined arguments")
    process_group.add_argument("-p", "--process-all",
                               help=f"the directory path which contains the {config.DEFAULT_RECIPIENTS_FILE}, "
                                    f"{config.DEFAULT_SENDERS_FILE} and {config.DEFAULT_CONTENT_DIR} directory",
                               dest="process_dir",
                               type=lambda x: util.is_directory_valid(arg_parser, x),
                               metavar='',
                               required=False)

    test_group = arg_parser.add_argument_group("testing arguments")
    test_group.add_argument("-t", "--test-sender-login",
                            help="the sender file to test login authentication (i.e., senders.txt)",
                            dest="test_sender_file",
                            type=lambda x: util.is_file_valid(arg_parser, x),
                            metavar='',
                            required=False)

    return arg_parser


def run():
    senders = None
    recipients = None
    status = E.SUCCESS
    config = Config()
    arg_parser = gen_arg_parser(config)
    args = arg_parser.parse_args()

    # Must validate that mutually exclusive arguments are mixed
    if args.process_dir and args.test_sender_file:
        arg_parser.print_usage()
        print(f"{PACKAGE}: error: -p and -t are mutually exclusive")
        status = E.INVALID_PARAMS

    elif args.process_dir and (args.content_dir or args.recipients_file or args.senders_file):
        arg_parser.print_usage()
        print(f"{PACKAGE}: error: -p and -c|-r|-s are mutually exclusive")
        status = E.INVALID_PARAMS

    elif args.test_sender_file and (args.content_dir or args.recipients_file or args.senders_file):
        arg_parser.print_usage()
        print(f"{PACKAGE}: error: -t and -c|-r|-s are mutually exclusive")
        status = E.INVALID_PARAMS

    elif not args.process_dir and not args.test_sender_file and \
            not (args.content_dir and args.recipients_file and args.senders_file):
        arg_parser.print_help()
        status = E.INVALID_PARAMS

    else:
        # Display banner
        print(get_light_version_info())

        # Set configuration data
        config.delay = args.delay
        config.log_file_path = args.log_file
        config.metrics_delay = args.metrics_delay
        config.metrics_file_path = args.metrics_file
        config.worker_count = args.worker_count

        # Define the log format
        log_format = logging.Formatter('%(asctime)s [%(module)s] [%(levelname)s] %(message)s')

        # Create a handler to output logs on terminal
        cli_log_handler = LogHandler()
        cli_log_handler.set_callback(cli_log.log)
        cli_log_handler.setFormatter(log_format)

        # Create a handler to output logs on a file
        file_log_handler = logging.FileHandler(config.log_file_path, encoding="UTF-8")
        file_log_handler.setFormatter(log_format)

        # Create a "console" logger to output logs on a terminal and to a file
        logger = logging.getLogger("console")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_log_handler)
        logger.addHandler(cli_log_handler)


        # Log all configuration data
        logger.info(f"Starting {PACKAGE} v{VERSION} by {AUTHOR}")
        logger.info("CONFIG:")
        logger.info(f" -Delay               : {config.delay}")
        logger.info(f" -Metrics delay       : {config.metrics_delay}")
        logger.info(f" -Worker count        : {config.worker_count}")
        logger.info(f" -Log file            : {config.log_file_path}")
        logger.info(f" -Metrics file        : {config.metrics_file_path}")


        if not args.test_sender_file:
            if args.process_dir:
                config.process_dir = args.process_dir
                logger.info(f" -Processing directory: '{args.process_dir}'")
                (senders, recipients) = process_dir(logger, config)
            else:
                config.senders_file = args.senders_file
                config.recipients_file = args.recipients_file
                config.content_dir = args.content_dir
                logger.info(f" -Senders file        : '{args.senders_file}'")
                logger.info(f" -Recipients file     : '{args.recipients_file}'")
                logger.info(f" -Content directory   : '{args.content_dir}'")
                (senders, recipients) = process_individual(logger, config)

            if senders is not None and recipients is not None:
                logger.info("Processing of data completed")

                # Test the sender accounts to make sure they can all authenticate with their
                # respective SMTP server
                logger.info("Testing connection of sender accounts")
                if test_sender_accounts(logger, senders, stop_on_failure=True):
                    logger.error("Failed to authenticate all sender accounts")
                    status = E.SERVER_CONNECTION_FAILED
                else:
                    logger.info("Initiating metrics container")
                    metrics = Metrics(config.metrics_file_path)
                    metrics.set_number_of_senders(len(senders))
                    metrics.set_number_of_recipients(len(recipients))

                    logger.info("Initiating Orchestrator")
                    orchestrator = Orchestrator(config, metrics, config.worker_count)
                    orchestrator.set_content(senders, recipients)

                    if args.graphics:
                        logger.info("Starting graphics panel")
                        cli_renderer = CliRenderer(config, metrics)

                        # Create a "renderer" logger to output logs on a log window and to a file
                        cli_renderer_handler = LogHandler()
                        cli_renderer_handler.set_callback(cli_renderer.update_log)
                        logging.getLogger("renderer").setLevel(logging.DEBUG)
                        logging.getLogger("renderer").addHandler(file_log_handler)
                        logging.getLogger("renderer").addHandler(cli_renderer_handler)

                        # Set the default logger and subscribe the renderer to the orchestrator
                        orchestrator.set_logger(logging.getLogger("renderer"))
                        orchestrator.add_subscriber(cli_renderer)

                        # Initialize the renderer graphics
                        try:
                            cli_renderer.init()

                        except Exception as e:
                            logger.exception(e)
                            status = E.GRAPHICAL_PANEL_FAILED

                        else:
                            # Create and start the orchestrator in it's own thread
                            orchestrator_thread = threading.Thread(target=orchestrator.start,
                                                                   daemon=True)
                            orchestrator_thread.start()

                            # Start monitoring for key strokes and terminal resizing in order
                            # to perform any actions specified by the user or update the graphics
                            cli_renderer.run()

                    else:
                        # Start the operation for sending emails. Program will hang here
                        # until all the emails are sent
                        orchestrator.set_logger(logger)
                        orchestrator.start()

                    if status == E.SUCCESS:
                        logger.info(f"Saving metrics to '{config.metrics_file_path}'")
                        metrics.save_metrics()

                    logger.info("Program terminated")
            else:
                logger.error("Failed to process data")
                status = E.INVALID_FORMAT

        else:
            config.senders_file = args.test_sender_file

            logger.info(f"Processing senders file at '{config.senders_file}'")
            senders = process_test_senders(logger, config)

            logger.info(f"Testing SMTP connection of {len(senders)} sender email accounts")
            status = test_sender_accounts(logger, senders)

            if status == E.SUCCESS:
                logger.info("Successfully authenticated all sender accounts")
            else:
                logger.error("Failed to authenticate sender accounts")

    return status


def is_python_version_supported():
    is_supported = True

    major = sys.version_info[0]
    minor = sys.version_info[1]
    if major < PYTHON_VERSION_MAJOR:
        is_supported = False
    else:
        if minor < PYTHON_VERSION_MINOR:
            is_supported = False

    return is_supported


def main():
    status = E.SUCCESS
    major = sys.version_info[0]
    minor = sys.version_info[1]


    # Check Python version
    if not is_python_version_supported():
        print(f"ERROR: The current version of python {major}.{minor} is not supported")
        print(f"To use this script, please install Python {PYTHON_VERSION_MAJOR}.{PYTHON_VERSION_MINOR} \
                or higher as such: apt-get install python3")
        status = E.UNSUPPORTED_PYTHON_VERSION
    else:
        try:
            status = run()
        except KeyboardInterrupt:
            status = E.ERROR_CTRL_C
        finally:
            print()

    return status


if __name__ == '__main__':
    sys.exit(main())
