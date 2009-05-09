# -*- coding: utf-8 -*-

import common
import pygtk
pygtk.require('2.0')
import gtk,os,gobject
import sys

def InputBox(parent,label,data,title=_("Geocacher Input")):
    dialog = gtk.Dialog(title, parent, 0,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OK, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)

    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_QUESTION,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)

    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)

    label = gtk.Label(label)
    label.set_use_underline(True)
    table.attach(label, 0, 2, 0, 1)
    local_entry1 = gtk.Entry()
    local_entry1.set_text(data)
    local_entry1.connect("activate", lambda w : dialog.response(gtk.RESPONSE_OK))
    table.attach(local_entry1, 0, 2, 1, 2)
    label.set_mnemonic_widget(local_entry1)


    dialog.show_all()

    response = dialog.run()

    if response == gtk.RESPONSE_OK:
        ret= local_entry1.get_text().decode("utf_8")
    else:
        ret = None
    dialog.destroy()

    return ret

def MessageBox(parent,data,title=_("Geocacher Message")):
    dialog = gtk.Dialog(title, parent, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_OK)
            )
    dialog.set_default_response(gtk.RESPONSE_OK)

    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_INFO,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)

    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)

    label = gtk.Label(data)
    label.set_selectable(True)
    table.attach(label, 0, 2, 0, 1)

    dialog.show_all()

    response = dialog.run()

    dialog.destroy()

def InputQuestion (parent, label, title=_("Geocacher Question"), buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)):
    dialog = gtk.Dialog (title, parent, 0, buttons)
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_has_separator (False)

    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_QUESTION,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)

    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)

    label = gtk.Label(label)
    label.set_use_underline(True)
    table.attach(label, 0, 2, 0, 1)


    dialog.show_all()

    response = dialog.run()

    if response == gtk.RESPONSE_OK:
        ret= True
    else:
        ret = False
    dialog.destroy()

    return ret