# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import threading

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog


import logging
from sgtk.log import LogManager

handler = logging.FileHandler("/tmp/toolkit.log")
LogManager().initialize_custom_handler(handler)

logger = sgtk.LogManager.get_logger(__name__)

# import the shotgun_menus module from the framework
playback_label = sgtk.platform.import_framework("tk-framework-qtwidgets", "playback_label")
sg_data = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_data")

def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("My App...", app_instance, AppDialog)

    logger.info("tk-start, dialog: show_diaglog")
    


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)
        
        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)
        
        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()
        
        # via the self._app handle we can for example access:
        # - The engine, via self._app.engine
        # - A Shotgun API instance, via self._app.shotgun
        # - A tk API instance, via self._app.tk 
        
        # lastly, set up our very basic UI
        self.ui.context.setText("Current Context: %s" % self._app.context)

        logger.info("tk-start, AppDiaglog: init")

        # get Version data from Shotgun. Make sure to include relevant fields.
        # For a Version, this includes:
        #  - image: so you can pass its URL to the thumbnail downloader
        #  - sg_uploaded_movie: which ShotgunPlayBackLabel uses to determine if 
        #    the entity is playable
        fields = ['id', 'code', 'image', 'sg_uploaded_movie']
        #filters = [['image','is_not', None]]
        filters = [['id','is', 6747]]
        version_data = self._app.shotgun.find_one('Version', filters, fields)
	
        logger.info(version_data)

        # download the thumbnail for the version
        # TODO: this should be done asynchronously, ShotgunDataRetriever supports this.
        self.__sg_data = sg_data.ShotgunDataRetriever(self)
        self.__sg_data.start()
        thumbnail_path = self.__sg_data.download_thumbnail(version_data['image'], self._app)
	
	logger.info(thumbnail_path)
