#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from __future__ import annotations
import random
from draggable_plot import DraggablePlot
from jsonlivelink import JsonLiveLink

# ======================  test ======================

jll = JsonLiveLink("127.0.0.1", 54321)
subject_name = "mortar"
skeleton =  {
    "root": {
        "base": {},
        "stone_1": "stone_2",
        "stupka": {}
    }
}

jll.set_bones(subject_name, skeleton)

# matplot callback
def on_update_plot(points):
    global jll, subject_name
    scale = 1.0
    transforms = jll.transforms[subject_name]
    for name in points:
        x,y = points[name]
        transform = transforms[name]
        transform[0] = x * scale
        transform[1] = 0 * scale
        transform[2] = y * scale
    jll.update(subject_name)

xlim = (-100, 100)
ylim = xlim
plot = DraggablePlot(xlim, ylim, on_update_plot)
# add bones
for bone in jll.skeleton[subject_name][0]:
    rand_x = random.randint(*xlim)
    rand_y = random.randint(*ylim)
    plot.add_point(rand_x, rand_y, bone)
# manual update to plot newly added bones
plot.update_plot()

plot.show()
