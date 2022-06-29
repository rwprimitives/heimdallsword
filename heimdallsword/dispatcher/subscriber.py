# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 rwprimitives
# Author: eldiablo <avsarria@gmail.com>
#

"""
Subscriber Module
=================

This module is an Observer interface which defines update methods.
"""

# standard modules
from __future__ import annotations
from abc import abstractmethod

# internal modules
from heimdallsword.data.metrics import Metrics


class Subscriber():
    """
    The :py:class:`heimdallsword.dispatcher.subscriber.Subscriber` is an **Observer** interface
    used for the purpose of receiving :py:class:`heimdallsword.data.metrics.Metrics` as the
    :py:class:`heimdallsword.dispatcher.orchestrator.Orchestrator` publishes new updates.
    """

    @abstractmethod
    def update_metrics(self, metrics: Metrics) -> None:
        """
        Receive metrics update from Orchestrator.

        :param metrics: a reference to a :py:class:`heimdallsword.data.metrics.Metrics` class
        :type: :py:class:`heimdallsword.data.metrics.Metrics`
        """
        pass
