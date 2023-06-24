#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from __future__ import annotations
import math
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent

import json

class DraggablePlot:
    def __init__(self, xlim, ylim, update_callback:callable=None):
        """
        Args:
            xlim: tuple[float,float]
            ylim: tuple[float,float]
            update_callback(points): callable, where points are dict of point_name->(x,y)
        """

        self._figure, self._axes, self._line = None, None, None
        self._dragging_point = None
        self._points = {}
        self.xlim = xlim
        self.ylim = ylim
        self.update_callback = update_callback

        self._init_plot()

    @staticmethod
    def show():
        plt.show()

    def _init_plot(self):
        self._figure = plt.figure("draggable plot")
        axes = plt.subplot(1, 1, 1)
        axes.set_xlim(*self.xlim)
        axes.set_ylim(*self.ylim)
        axes.grid(which="both")
        self._axes = axes

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def update_plot(self):
        if not self._points:
            if self._line:
                self._line.set_data([], [])
        else:
            x, y = zip(*list(self._points.values()))
            # Add new plot
            if not self._line:
                self._line, = self._axes.plot(x, y, "b", marker="o", markersize=10, linestyle="")
            # Update current plot
            else:
                self._line.set_data(x, y)
        self._figure.canvas.draw()
        # send link live data
        if self.update_callback:
            self.update_callback(self._points)

    def add_point(self, x, y, name):
        self._points[name]= (x,y)
        return name

    def remove_point(self, name):
        if name in self._points:
            del self._points[name]

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position

        :rtype: ((int, int)|None)
        :return: name if there are any point around mouse else None
        """
        distance_threshold = 3.0
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for name in self._points:
            x,y = self._points[name]
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = name
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, event):
        u""" callback method for mouse click event

        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
            else:
                # self.add_point(event.xdata, event.ydata, f"point({event.xdata},{event.ydata})")
                pass
            self.update_plot()
        # right click
        #elif event.button == 3 and event.inaxes in [self._axes]:
        #    point = self._find_neighbor_point(event)
        #    if point:
        #        self.remove_point(point)
        #        self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event

        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self._dragging_point:
            self._dragging_point = None
            self.update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event

        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self.remove_point(self._dragging_point)
        self._dragging_point = self.add_point(event.xdata, event.ydata, self._dragging_point)
        self.update_plot()

