#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Three files have very similar code pieces. They are:
#   * gcer
#   * gcer.py
#   * geocacher/app.py
# The reason for this is different environments with different needs.
# gcer is the main shell script to run for UNIX-type settings
# gcer.py is required for py2app (OSX Bundle Maker) to work
# geocacher/app.py is the main debug file in Wingware IDE, so that
#    breakpoints work properly (psyco stops the breakpoints from
#    working in Wingware IDE)
# As such, all three of these need to be kept in sync. Fortunately,
# there is extremely little logic in here. It's mostly a startup
# shell, so this bit of code can be mostly ignored. This note is
# just to explain why these pieces are here, and why all of them must
# be updated if one of them is.

try:
    import psyco
    psyco.full()
except ImportError:
    pass

import geocacher

if __name__ == "__main__":
    app = geocacher.GeocacherApp(redirect=False, useBestVisual=True)
    app.MainLoop()