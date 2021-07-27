#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2010, Benjamin Schollnick. All rights reserved.
# http://www.schollnick.net/wordpress

################################################################################
# Python imports
import os
import sys
import time
#import backup_indigo
#import common_indigo
################################################################################
# Globals
################################################################################

plugin_id 	= "com.schollnick.indigoplugin.Backup"

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		# Setting debug to True will show you verbose debugging information in the Indigo Event Log
		self.debug = pluginPrefs.get("showDebugInfo", False)
	########################################

	def __del__(self):
		indigo.PluginBase.__del__(self)


	########################################
	# Built-in control methods
	########################################
	def startup(self):
		self.debugLog ("Debug Mode is activated.  (Only use if testing...)")
		#if not os.path.exists ( os.path.expanduser ("~/Documents/IndigoBackup") ):
		#	os.makedirs ( os.path.expanduser ("~/Documents/IndigoBackup"))


	########################################
	def shutdown(self):
		# Nothing to do since deviceStopComm will be called for each of our
		# devices and that's how we'll clean up
		pass

	def	verify_preference ( self, preferencekey, default_value):
		if self.pluginPrefs.has_key ( preferencekey):
			return
		else:
			self.pluginPrefs [ preferencekey ] = default_value


	def	verify_device_properties ( self, dev, propertyname, boolean = False, default_value = "") :
		newProps = dev.pluginProps			#dev.globalProps[plugin_id]
		if newProps.has_key (propertyname):
			return
		else:
			if boolean:
				newProps[propertyname] = True
			else:
				newProps[propertyname] = default_value

			dev.replacePluginPropsOnServer(newProps)

	def	update_device_property ( self, dev, propertyname, new_value = ""):
		newProps = dev.pluginProps
		newProps.update ( {propertyname : new_value} )
		dev.replacePluginPropsOnServer(newProps)
		return None


	def PerformManualBackup (self):
		self.run_Backup ()

	def	PerformTriggeredBackup ( self, action):
		self.run_Backup()

	def	return_indigo_path ( self ):
	#
	#	Next Generation iws path calculation
	#
	#	Uses the Indigo Server version to generate the IWS path
	#
		return indigo.server.getInstallFolderPath()


	def	run_Backup ( self ):
	#
	#	Update requested via Trigger Action
	#
		backup_target_path = self.pluginPrefs["Preferences_BackupLocation"]

#		indigo.server.log ("Starting Backup, saving to ~/Documents/IndigoBackup")
		indigo.server.log ("Starting Backup, saving to %s" % backup_target_path )

# 		Backup_Engine = backup_indigo.backup_system ( self.return_indigo_path ()[0:-1],
#                                     os.path.expanduser ( backup_target_path ),
#         #                            os.path.expanduser ('~/Documents/IndigoBackup'),
#                                     "",
#                                     "",
#                                     'Indigo_Backup',
#                                     True,
#                                     False)
#
# 		Backup_Engine.start_archive_engine ( backup_indigo.ZIP )
# 		Backup_Engine.walk_directory_tree ()
# 		Backup_Engine.close_archive_file ()

		#
		#	The Backup engine has started to generate permissions errors with Indigo v6.03
		#
		#	As a temporary work around, I have switched to using distutils as a shortcut.  I will revisit the
		#	backup engine time permitting.
		#

		import distutils
		import distutils.archive_util
		import zipfile

		archive_filename_template  = "Indigo_Backup_%m_%d_%Y__%H_%M_%S.zip"
		archive_filename = 	os.path.expanduser ( backup_target_path + os.sep + time.strftime ( archive_filename_template, time.localtime() ) )
		indigo.server.log (" archive filename %s" % archive_filename)
		indigo.server.log (" save path %s" % self.return_indigo_path ()[0:-1] )

		try:
			distutils.archive_util.make_zipfile ( archive_filename, os.path.expanduser ( self.return_indigo_path ()[0:-1]) )
		except zipfile.LargeZipFile:
			indigo.server.log ("Zip File Error, Would require 64 bit extensions")
		indigo.server.log ("Backup Finished.")

	def runConcurrentThread(self):
		#
		#
		self.verify_preference ( "Preferences_Timing", 			20160)
		self.verify_preference ( "Preferences_BackupLocation", 	"~/Documents/IndigoBackup")
		self.verify_preference ( "Preferences_BackupSchedule", 	True)

		try:
			while self.stopThread == False:

				if not os.path.exists ( os.path.expanduser ( self.pluginPrefs["Preferences_BackupLocation"] ) ):
					os.makedirs ( os.path.expanduser ( self.pluginPrefs["Preferences_BackupLocation"] ))

				if self.pluginPrefs["Preferences_BackupSchedule"]==True:
					self.run_Backup ( )
					self.sleep ( int(self.pluginPrefs["Preferences_Timing"]) * 60 )
				else:
					self.sleep ( 512 )

		except self.StopThread:
			self.stopThread = True
			indigo.server.log ("Stopping Plugin")
