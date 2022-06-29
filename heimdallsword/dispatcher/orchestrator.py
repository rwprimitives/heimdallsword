# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Orchestrator Module
===================

This module serves as an Email client which establishes and maintains
a connection with the SMTP server in order to send emails and check
the status of the emails sent in a multi-threaded fashion
"""

# standard modules
import queue
import threading
import time

# internal modules
from heimdallsword.dispatcher.client import EmailClient
from heimdallsword.models.recipient import DeliveryState
from heimdallsword.utils import util


class Orchestrator:
    """
    The :py:class:`heimdallsword.dispatcher.orchestrator.Orchestrator` class serves as the
    organizer for the entirity of the email sending operation.

    Emails can be sent concurrently or sequentially based on the number of working
    threads defined in `worker_count`. By default, `worker_count` is set by taking the
    number of processors on the machine and multiplying it by 5. This method of calculation
    is used in the :py:class:`concurrent.futures.ThreadPoolExecutor` module when `max_workers`
    is set to None.

    As emails are sent, metrics are gathered to help calculate success or failure rates.
    The :py:class:`heimdallsword.dispatcher.orchestrator.Orchestrator` class allows for
    subscribers to register and receive notifications when metrics are updated.

    A :py:class:`logging` object can be passed by calling the method `set_logger()` if
    logging information is desired.

    :param config: a reference to a :py:class:`heimdallsword.data.config.Config` object
                   that contains the configuration which describes the flow of
                   operations for sending emails
    :type: :py:obj:`heimdallsword.data.config.Config`

    :param metrics: a reference to a :py:class:`heimdallsword.data.metrics.Metrics` object
                    used to manage data that is tracked for the purpose of generating
                    metrics
    :type: :py:obj:`heimdallsword.data.metrics.Metrics`

    :param worker_count: the numer of worker threads to use for sending emails. Default
                         value varies per machine
    :type: int
    """

    def __init__(self, config, metrics, worker_count=None):
        if not worker_count:
            self.worker_count = util.get_max_thread_count()
        else:
            if type(worker_count) == int:
                if (worker_count > 0) and (worker_count <= util.get_max_thread_count()):
                    self.worker_count = worker_count
                else:
                    raise ValueError(f"worker_count must be greater than 0 and less than {util.get_max_thread_count()}")
            else:
                raise TypeError("worker_count argument must be int")

        self.config = config
        self.metrics = metrics
        self.renderer_stats_callback = None
        self.job_queue = queue.Queue()
        self.metrics_queue = queue.Queue()
        self.worker_threads = {}
        self.subscribers = []
        self.logger = None


    def set_config(self, config):
        """
        Set the configuration.

        This method will return `IOError` exception if config is not provided.

        :param config: a reference to a :py:class:`heimdallsword.data.config.Config` object
                       that contains the configuration which describes the flow of
                       operations for sending emails.
        :type: :py:obj:`heimdallsword.data.config.Config`
        """

        if not config:
            raise IOError("No configuration was provided")

        self.config = config


    def set_content(self, senders, recipients):
        """
        Set the sender and recipient content.

        This method will return `IOError` exception if a sender or recipient is not provided.

        :param senders: a reference to a :py:class:`heimdallsword.models.sender.Sender` class
                       that contains one or more senders
        :type: :py:obj:`heimdallsword.models.sender.Sender`

        :param recipients: a reference to a :py:class:`heimdallsword.models.recipient.Recipient`
                           class that contains one or more recipients
        :type: :py:obj:`heimdallsword.models.sender.Sender`
        """

        if not senders or not len(senders):
            raise IOError("No senders was provided")

        if not recipients or not len(recipients):
            raise IOError("No recipients was provided")

        self.senders = senders
        self.recipients = recipients


    def add_subscriber(self, subscriber):
        """
        Add a subscriber to receive metrics update notifications.

        All subscribers must inherit the base class :py:class:`heimdallsword.dispatcher.subscriber.Subscriber`
        and implement the :py:meth:`heimdallsword.dispatcher.subscriber.Subscriber.update_metrics()` method.

        :param subscriber: a subscriber
        :type: :py:obj:`heimdallsword.dispatcher.subscriber.Subscriber`
        """

        self.subscribers.append(subscriber)


    def remove_subscriber(self, subscriber):
        """
        Remove a subscriber to stop receiving metrics update notifications.

        This method will throw a `ValueError` exception if the suscriber is not in the list.

        :param subscriber: the subscriber to remove
        :type: :py:obj:`heimdallsword.dispatcher.subscriber.Subscriber`
        """

        self.subscribers.remove(subscriber)


    def notify_subscribers(self, metrics):
        """
        Notify subscribers of metrics updates.

        :param metrics: a reference to a :py:class:`heimdallsword.data.metrics.Metrics` object
                        used to manage data that is tracked for the purpose of generating
                        metrics
        :type: :py:obj:`heimdallsword.data.metrics.Metrics`
        """

        for subscriber in self.subscribers:
            subscriber.update_metrics(metrics)


    def set_logger(self, logger):
        """
        Set the logger based :py:obj:`logging.Logger` to use for logging information.

        :param logger: the logger object to call for logging information
        :type: :py:obj:`logging.Logger`
        """

        self.logger = logger


    def _log_info(self, message):
        """
        Internal method used for logging information if a logger is set.

        :param message: the content to log as information only
        :type: str
        """

        if self.logger:
            self.logger.info(message)


    def _log_error(self, message):
        """
        Internal method used for logging errors if a logger is set.

        :param message: the content to log errors
        :type: str
        """

        if self.logger:
            self.logger.error(message, exc_info=True)


    def _log_bad_recipient(self, recipient):
        """
        Internal method used for populating a file of recipients considered to be
        bad either due to the email address being erronous, no longer exists,
        mailbox full, etc. The file is named `bad_recipients.txt`.

        Note, that this method will open any existing `bad_recipients.txt` file
        and append to the end any bad recipient emails.

        :param recipient: the recipient object
        :type: :py:obj:`heimdallsword.models.recipient.Recipient`
        """

        with open("bad_recipients.txt", "a") as f:
            f.write(recipient.get_email())
            f.write("\n")


    def _log_good_recipient(self, recipient):
        """
        Internal method used for populating a file of recipients considered to be
        bad either due to the email address being erronous, no longer exists,
        mailbox full, etc. The file is named `good_recipients.txt`.

        Note, that this method will open any existing `good_recipients.txt` file
        and append to the end any good recipient emails.

        :param recipient: the recipient object
        :type: :py:obj:`heimdallsword.models.recipient.Recipient`
        """

        with open("good_recipients.txt", "a") as f:
            f.write(recipient.get_email())
            f.write("\n")


    def start(self):
        """
        Starts the process of sending emails using `n` number of worker threads.
        Each sender is paired with a recipient and are assigned a worker thread.
        Once a worker thread finishes the operation, it notifies all subscribers
        of updates in the metrics data.

        **NOTE:**
        Worker threads will stay active even after all emails are sent. The worker
        threads will only terminate once the program terminates.
        """

        if not self.config:
            raise IOError("No configuration was set")

        if not self.senders or not len(self.senders):
            raise IOError("No senders was provided")

        if not self.recipients or not len(self.recipients):
            raise IOError("No recipients was provided")

        if not self.metrics:
            raise IOError("No metrics was set")

        self._log_info("Starting orchestrator")

        self.metrics.set_number_of_senders(len(self.senders))
        self.metrics.set_number_of_recipients(len(self.recipients))
        self.metrics.activate_start_time()

        self.notify_subscribers(self.metrics)

        self._log_info(f"Spinning of {self.worker_count} workers...")
        for i in range(self.worker_count):
            worker = threading.Thread(target=self._worker_callack,
                                      args=(self.job_queue, self.metrics, i),
                                      daemon=True)
            worker.start()
            self.worker_threads[i] = worker

        self._log_info("Finished spinning up worker threads")

        self._log_info("Setting up email clients per sender")
        email_clients = []
        for sender in self.senders:
            email_clients.append(EmailClient(sender, self.config.metrics_delay))

        self._log_info("Starting mail delivery process!")

        self._log_info("Adding jobs into the workers' queue")
        ec_index = 0
        for recipient in self.recipients:
            client = email_clients[ec_index]
            self.job_queue.put((client, recipient))

            ec_index += 1
            if ec_index >= len(email_clients):
                ec_index = 0

            time.sleep(self.config.delay / 1000)

        # Wait until all the tasks are complete
        self.job_queue.join()
        self._log_info("Done sending emails")

        self.metrics.activate_stop_time()

        self.notify_subscribers(self.metrics)

        self._log_info("Gathering final metrics...")
        self._print_metrics(self.metrics)

        self._log_info("Closing all client's SMTP sessions..")
        for client in email_clients:
            client.terminate_session()

        self._log_info("Finished closing all client's SMTP sessions")

        # NOTE:
        # No need to terminate the worker threads as they will be terminated
        # once the program ends.


    def _print_metrics(self, metrics, thread_no=None):
        """
        Internal method used for logging metrics after the worker thread completes
        it's operation.

        :param metrics: the metrics object containing up-to-date data
        :type: :py:obj:`heimdallsword.data.metrics.Metrics`

        :param thread_no: the worker thread number assigned
        :type: int
        """

        worker_label = ""
        if thread_no is not None:
            worker_label = f"[worker={thread_no}] "

        self._log_info(f"{worker_label}METRICS:")
        self._log_info(f"{worker_label} -Total senders                    : "
                       f"{metrics.get_num_of_senders()}")
        self._log_info(f"{worker_label} -Total recipients                 : "
                       f"{metrics.get_num_of_recipients()}")
        self._log_info(f"{worker_label} -Start time                       : "
                       f"{metrics.get_start_time()[1]}")
        self._log_info(f"{worker_label} -Stop time                        : "
                       f"{metrics.get_stop_time()[1]}")
        self._log_info(f"{worker_label} -Elapsed time                     : "
                       f"{metrics.get_elapsed_time()}")
        self._log_info(f"{worker_label} -Delivery rate                    : "
                       f"{metrics.get_current_delivery_rate()}%")
        self._log_info(f"{worker_label} -Bounce rate                      : "
                       f"{metrics.get_current_fail_rate()}%")
        self._log_info(f"{worker_label} -Emails delivered                 : "
                       f"{metrics.get_emails_delivered_count()}")
        self._log_info(f"{worker_label} -Emails not delivered             : "
                       f"{metrics.get_emails_not_delivered_count()}")
        self._log_info(f"{worker_label} -Emails failed delivery           : "
                       f"{metrics.get_emails_failed_delivery_count()}")
        self._log_info(f"{worker_label} -Recipients rejected              : "
                       f"{metrics.get_recipient_rejected_count()}")
        self._log_info(f"{worker_label} -Senders rejected                 : "
                       f"{metrics.get_senders_rejected_count()}")
        self._log_info(f"{worker_label} -Emails failed delivery format    : "
                       f"{metrics.get_failed_delivery_format_count()}")
        self._log_info(f"{worker_label} -Emails failed delivery disconnect: "
                       f"{metrics.get_disconnected_count()}")


    def _worker_callack(self, queue, metrics, thread_no):
        """
        Internal method used as the callback method for a worker thread. In this method,
        the sender conducts the operation to send an email to the recipient assigned. Metrics
        are recorded based on the status returned or exceptions thrown by the sender. After metrics
        are updated, subscribers are notified of changes in the metrics.

        :param queue: a synchronized queue containing a sender and recipient
        :type: queue

        :param metrics: the metrics object containing up-to-date data
        :type: :py:obj:`heimdallsword.data.metrics.Metrics`

        :param thread_no: the worker thread number assigned
        :type: int
        """

        while True:
            status = DeliveryState.NOT_DELIVERED
            task = queue.get()

            client = task[0]
            recipient = task[1]

            self._log_info(f"[worker={thread_no}] Sending email. Recipient: '{recipient.get_email()}', "
                           f"sender: '{client.sender.get_email()}', message: '{recipient.get_message_filename()}'")

            try:
                status = client.send(recipient)
                self._log_info(f"[worker={thread_no}] Sent email to '{recipient.get_email()}'")
            except Exception as e:
                #
                # NOTE:
                # Catch any exception thrown by the email client and log it since there is nothing
                # else we can do except for logging it. For more information, read the
                # :py:meth:`heimdallsword.client.EmailClient.send` documentation
                #
                self._log_error(f"[worker={thread_no}] Failed to send Recipient: '{recipient.get_email()}', "
                                f"sender: '{client.sender.get_email()}', message: '{recipient.get_message_filename()}'")
                self._log_error(f"[worker={thread_no}] {type(e).__name__}: {e}")

            finally:
                status = recipient.get_delivery_state()

                if status == DeliveryState.SUCCESSFUL_DELIVERY:
                    metrics.increment_emails_delivered_count()

                elif status == DeliveryState.FAILED_DELIVERY:
                    metrics.increment_emails_failed_delivery_count()

                elif status == DeliveryState.RECIPIENT_REJECTED:
                    metrics.increment_recipient_rejected_count()

                elif status == DeliveryState.SENDER_REJECTED:
                    metrics.increment_senders_rejected_count()

                elif status == DeliveryState.INVALID_FORMAT:
                    metrics.increment_failed_delivery_format_count()

                elif status == DeliveryState.DISCONNECTED:
                    metrics.increment_disconnected_count()

                else:
                    metrics.increment_emails_not_delivered_count()


                # Log good and bad recipients into separate files to help clean up
                # the original recipient list
                if status == DeliveryState.SUCCESSFUL_DELIVERY:
                    self._log_good_recipient(recipient)
                else:
                    self._log_bad_recipient(recipient)

                # Notify all subscribers of metrics updates
                self.notify_subscribers(self.metrics)

                # Log metrics for every email sent in case a hard crash occurs later
                # in the process and at least some metrics can be retrieved from the
                # last attempt
                self._print_metrics(metrics, thread_no)

                queue.task_done()
