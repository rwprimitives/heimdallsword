# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Renderer Module
===============

This module contains a graphics renderer based on :py:mod:curses to
display metrics and logging information on the terminal.
"""

# standard modules
import curses
import logging
import curses.panel

# internal modules
from heimdallsword import release
from heimdallsword.data.metrics import Metrics
from heimdallsword.log import cli_log
from heimdallsword.dispatcher.subscriber import Subscriber


class CliRenderer(Subscriber):
    """
    The :py:class:`heimdallsword.graphics.renderer.CliRenderer` class produces a
    beautifully designed command line graphical interface which provides live metrics
    updates as emails are sent as well as logging information throughout the enterity
    of the operation.

    :param config: a reference to a :py:class:`heimdallsword.data.config.Config` object
                   that contains the configuration which describes the flow of
                   operations for sending emails
    :type: :py:class: `heimdallsword.data.config.Config`

    :param metrics: a reference to a :py:class:`heimdallsword.data.metrics.Metrics` object
                    used to manage data that is tracked for the purpose of generating
                    metrics
    :type: :py:class:`heimdallsword.data.metrics.Metrics`
    """

    def __init__(self, config, metrics):
        self.config = config
        self.metrics = metrics
        self.is_running = True
        self.orchestrator = None
        self.current = 0

        # Create a window object to use as the main screen
        self.screen = curses.initscr()
        # Do not block on getch() to get character key stroke
        self.screen.nodelay(True)
        # Enable function keys (i,e,: F1, F2... Fn) and arrow keys
        self.screen.keypad(True)

        # Turn off echoing of keys
        curses.noecho()
        # Disable line buffering by entering in cbreak mode
        curses.cbreak()
        # Disable the prompt cursor
        curses.curs_set(0)
        # Start color. Harmless if terminal doesn't have color
        if curses.has_colors():
            curses.start_color()
        # Make the background black
        if curses.can_change_color():
            curses.init_color(0, 0, 0, 0)
        # Enable all mouse events to be reported. Enabling this prevents
        # the ability to highlight any text on the screen with the mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        # Get width and height of current window
        self._update_window_sizes()

        # Define color palette
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        self.GREEN_ON_BLACK = curses.color_pair(1)
        self.BLUE_ON_BLACK = curses.color_pair(2)
        self.WHITE_ON_BLACK = curses.color_pair(3)
        self.YELLOW_ON_BLACK = curses.color_pair(4)
        self.RED_ON_BLACK = curses.color_pair(5)


    def init(self):
        """
        Initialize and display the command line graphical interface.

        :raises: IOError - Not enough space available to render graphics panel
        """
        try:
            self._render_border()
            self._render_windows()
            curses.panel.update_panels()
            curses.doupdate()
            self.screen.refresh()
        except Exception:
            self.terminate()
            raise IOError("Not enough space available to render graphics panel")


    def _render_border(self):
        """
        Internal method for drawing the outter border to display the title
        and footer.
        """

        title_bar = f"{release.__package__} v{release.__version__}".encode("utf-8").center(self.max_width - 4)
        bottom_bar = "(s) Save Metrics | (q) Quit".encode("utf-8").center(self.max_width - 4)
        self.screen.erase()
        self.screen.border(0)
        self.screen.addstr(0, 2, title_bar, curses.A_BOLD | curses.A_REVERSE)
        self.screen.addstr(self.max_height - 1, 2, bottom_bar, curses.A_REVERSE)


    def _render_windows(self):
        """
        Internal method for drawing the data, stats and log sections.
        """

        #
        # NOTE:
        # Setting scrollok(True) to windows allows text to overflow and be drawn
        # off screen. This prevents curses from throwing an exception when attemping
        # to draw text off screen.
        #

        self.METRICS_WINDOW_HEIGHT = 19
        self.STATS_DATA_WINDOW_HEIGHT = 16
        self.LOG_WINDOW_HEIGHT = 24

        self.metrics_window = curses.newwin(self.METRICS_WINDOW_HEIGHT, self.max_width - 4, 2, 2)
        self.metrics_window.scrollok(True)
        self.metrics_window_panel = curses.panel.new_panel(self.metrics_window)

        self.data_window = curses.newwin(self.STATS_DATA_WINDOW_HEIGHT, (self.max_width // 2) - 4, 4, 4)
        self.data_window.scrollok(True)
        self.data_window_panel = curses.panel.new_panel(self.data_window)

        self.stats_window = curses.newwin(self.STATS_DATA_WINDOW_HEIGHT, (self.max_width // 2) - 4, 4,
                                          (self.max_width // 2) + 1)
        self.stats_window.scrollok(True)
        self.stats_window_panel = curses.panel.new_panel(self.stats_window)

        self.start_time_window = self._render_stat_window(self.stats_window, 2)
        self.stop_time_window = self._render_stat_window(self.stats_window, 3)
        self.elapsed_time_window = self._render_stat_window(self.stats_window, 4)
        self.delivery_rate_window = self._render_stat_window(self.stats_window, 5)
        self.fail_rate_window = self._render_stat_window(self.stats_window, 6)
        self.emails_delivered_window = self._render_stat_window(self.stats_window, 7)
        self.emails_not_delivered_window = self._render_stat_window(self.stats_window, 8)
        self.emails_failed_delivery_window = self._render_stat_window(self.stats_window, 9)
        self.recipients_rejected_window = self._render_stat_window(self.stats_window, 10)
        self.senders_rejected_window = self._render_stat_window(self.stats_window, 11)
        self.emails_failed_delivery_format_window = self._render_stat_window(self.stats_window, 12)
        self.emails_failed_delivery_disconnect_window = self._render_stat_window(self.stats_window, 13)

        self.log_window = curses.newwin(self.max_height - self.LOG_WINDOW_HEIGHT, self.max_width - 4, 22, 2)
        self.log_window.scrollok(True)
        self.log_window_panel = curses.panel.new_panel(self.log_window)

        self.log_messages_window = self.log_window.derwin(self.max_height - self.LOG_WINDOW_HEIGHT - 2,
                                                          self.max_width - 6, 1, 1)
        self.log_messages_window.scrollok(True)
        self.log_messages_window.idlok(True)
        self.log_messages_window.leaveok(True)
        self._update_windows()


    def _render_stat_window(self, parent_window, nline):
        """
        Internal method for creating derived windows from a given parent window.

        :param parent_window: the parent window to derive a window
        :type: window

        :param nline: the row in which the window will be draw
        :type: int

        :returns: the derived window
        :rtype: window
        """

        win = parent_window.derwin(1, (self.max_width // 2) - 8, nline, 2)
        win.scrollok(True)
        return win


    def _update_window_sizes(self):
        """
        Internal method for caculating the current window size (width and height).
        """

        self.max_height, self.max_width = self.screen.getmaxyx()


    def _update_windows(self):
        """
        Internal method for updating all the windows and texts.
        """

        window_width = self.max_width - 4
        log_window_height = self.max_height - self.LOG_WINDOW_HEIGHT
        side_window_width = (self.max_width // 2) - 4

        #
        # NOTE:
        # When rendering a window, the order of operations matter.
        # Must resize the window before drawing anything on it, i,e,: box()
        # Must set background color before erase() is called in order for it to be applied.
        #

        metrics_window = self.metrics_window_panel.window()
        metrics_window.bkgdset(self.GREEN_ON_BLACK)
        metrics_window.resize(self.METRICS_WINDOW_HEIGHT, window_width)
        metrics_window.erase()
        metrics_window.box()
        metrics_window.addstr(0, 2, " Metrics: ", curses.A_BOLD)

        log_window = self.log_window_panel.window()
        log_window.bkgdset(self.BLUE_ON_BLACK)
        log_window.resize(log_window_height, window_width)
        log_window.erase()
        log_window.box()
        log_window.addstr(0, 2, " Log Window: ", curses.A_BOLD)

        # self.log_messages_window.bkgdset(self.BLUE_ON_BLACK | curses.A_REVERSE)
        self.log_messages_window.resize(log_window_height - 2, window_width - 2)
        # self.log_messages_window.erase()
        self.log_messages_window.refresh()

        data_window = self.data_window_panel.window()
        data_window.bkgdset(self.WHITE_ON_BLACK)
        data_window.resize(self.STATS_DATA_WINDOW_HEIGHT, side_window_width)
        data_window.erase()
        data_window.box()
        data_title_bar = "DATA".encode("utf-8").center((self.max_width // 2) - 6)
        data_window.addstr(0, 1, data_title_bar, curses.A_BOLD | curses.A_REVERSE)
        data_window.addstr(2, 2, "Number of senders:    ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.metrics.get_num_of_senders()}", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(3, 2, "Number of recipients: ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.metrics.get_num_of_recipients()}", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(4, 2, "Delay:                ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.config.delay}ms", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(5, 2, "Metrics delay:        ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.config.metrics_delay}s", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(6, 2, "Worker count:         ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.config.worker_count}", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(7, 2, "Log file:             ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.config.log_file_path}", curses.A_BOLD | self.GREEN_ON_BLACK)
        data_window.addstr(8, 2, "Metrics file:         ", curses.A_BOLD | self.YELLOW_ON_BLACK)
        data_window.addstr(f"{self.config.metrics_file_path}", curses.A_BOLD | self.GREEN_ON_BLACK)

        self.stats_window_panel.move(4, (self.max_width // 2) + 1)
        stats_window = self.stats_window_panel.window()
        stats_window.bkgdset(self.WHITE_ON_BLACK)
        stats_window.resize(self.STATS_DATA_WINDOW_HEIGHT, side_window_width)
        stats_window.erase()
        stats_window.box()
        stats_title_bar = "STATS".encode("utf-8").center((self.max_width // 2) - 6)
        stats_window.addstr(0, 1, stats_title_bar, curses.A_BOLD | curses.A_REVERSE)

        self.update_metrics(self.metrics)


    def update_metrics(self, metrics: Metrics):
        """
        Receive metrics update from Orchestrator and update data on screen.

        :param metrics: a reference to a :py:class:`heimdallsword.data.metrics.Metrics` class
        :type: :py:class:`heimdallsword.data.metrics.Metrics`
        """

        self._update_stat_window(self.start_time_window,
                                 "Start time:                        ", f"{metrics.get_start_time()[1]}")
        self._update_stat_window(self.stop_time_window,
                                 "Stop time:                         ", f"{metrics.get_stop_time()[1]}")
        self._update_stat_window(self.elapsed_time_window,
                                 "Elapsed time:                      ", f"{metrics.get_elapsed_time()}")
        self._update_stat_window(self.delivery_rate_window,
                                 "Delivery rate:                     ", f"{metrics.get_current_delivery_rate()}%")
        self._update_stat_window(self.fail_rate_window,
                                 "Failed rate:                       ", f"{metrics.get_current_fail_rate()}%")
        self._update_stat_window(self.emails_delivered_window,
                                 "Emails delivered:                  ", f"{metrics.get_emails_delivered_count()}")
        self._update_stat_window(self.emails_not_delivered_window,
                                 "Emails not delivered:              ", f"{metrics.get_emails_not_delivered_count()}")
        self._update_stat_window(self.emails_failed_delivery_window,
                                 "Emails failed delivery:            ", f"{metrics.get_emails_failed_delivery_count()}")
        self._update_stat_window(self.recipients_rejected_window,
                                 "Recipients rejected:               ", f"{metrics.get_recipient_rejected_count()}")
        self._update_stat_window(self.senders_rejected_window,
                                 "Senders rejected:                  ", f"{metrics.get_senders_rejected_count()}")
        self._update_stat_window(self.emails_failed_delivery_format_window,
                                 "Emails failed delivery format:     ", f"{metrics.get_failed_delivery_format_count()}")
        self._update_stat_window(self.emails_failed_delivery_disconnect_window,
                                 "Emails failed delivery disconnect: ", f"{metrics.get_disconnected_count()}")


    def _update_stat_window(self, window, label_text, value):
        """
        Internal method used for updating any stat data on the screen.

        :param window: the parent window that contains the data (string)
        :type: window

        :param label_text: the title of the stat
        :type: str

        :param value: the value of the stat
        :type: int, float or str
        """

        window.resize(1, (self.max_width // 2) - 8)
        window.erase()
        window.addstr(label_text, curses.A_BOLD | self.YELLOW_ON_BLACK)
        window.addstr(value, curses.A_BOLD | self.GREEN_ON_BLACK)
        window.refresh()


    def update_log(self, record):
        """
        Display logging information on the log window.

        This method will ignore metric logs generated by the Orchestrator
        since the metrics stats are updated as notifications are received from
        then Orchestrator. Hence no need to display the same result in the log
        window.

        This method is used as a callback in the :py:class:`heimdallsword.log.handler.LogHandler`
        class. That way, whenever a log record is generated, a :py:class:`logging.LogRecord`
        object is passed to this method and it can be displayed in the log window.

        :param record: a :py:class:`logging.LogRecord` instance representing
                       an event logged
        :type: :py:class:`logging.LogRecord`
        """

        if "METRICS" in record.getMessage() or " -" in record.getMessage():
            return

        if record.levelno == logging.ERROR:
            foreground_color = self.RED_ON_BLACK
        elif record.levelno == logging.WARNING:
            foreground_color = self.YELLOW_ON_BLACK
        else:
            foreground_color = self.WHITE_ON_BLACK

        self.log_messages_window.addstr(f"{cli_log.get_log_message(record)}\n", foreground_color)
        self.log_messages_window.refresh()


    def run(self):
        """
        Start monitoring for key strokes and window size changes.
        """

        while self.is_running:
            key_input = self.screen.getch()

            if key_input == curses.KEY_RESIZE:
                self._update_window_sizes()
                self._render_border()
                self._update_windows()

                curses.panel.update_panels()
                curses.doupdate()
                self.screen.refresh()
                continue

            elif key_input == ord("s"):
                self.metrics.save_metrics()
                continue

            elif key_input == ord("q"):
                self.terminate()
                break


    def terminate(self):
        """
        Stop monitoring for key strokes and window size changes. Terminate
        the command line graphical interface and reset the terminal back to
        it's original state.
        """

        self.is_running = False
        self.screen.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)
        curses.endwin()
