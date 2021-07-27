"""Backup Creator Utility

This utility will backup the tree of files that you indicate, into a archive
of your choice.

"""
#  .TemporaryItems
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
__version__ = '1.01'    # Human Readable Version number
version_info = (1,0,1)  # Easier format version data for comparisons
                        # i.e. if version_info > (1,2,5)
                        #
                        #   if __version__ > '1.00' is a little more contrived.

__author__  = 'Benjamin A. Schollnick'
__date__    = '2021-07-26'  # yyyy-mm-dd
__email__   = 'Benjamin@schollnick.net'
__module_name__ = "Archive Backup Tool"
__short_cright__= "Copyright (C) 2009,2010 Benjamin Schollnick. All Rights Reserved."

import os
import os.path
import sys
import time
import zipfile


#######################################################################
class   zip_file_engine:
    """The archive backup tool uses pregenerated classes to allow
    multiple styles of archives to be created.

    This is the wrapper around the Python ZIPFILE module.
    """
    def     __init__       ( self ):
        """
        Inputs  --
                    None

        Outputs --
                    None
        """
        self.Backup_File        = None
        self.Backup_Open        = False
        self.Backup_ReadOnly    = None
        self.Backup_FileName    = None
        self.Max_Size           = 1024*1024*1025*1.5 # (1.5Gb)

    def     close_Backup (self ):
        """This will close the current Archive file, and reset the
        internal structures to a clean state.

        Inputs  --
                    None

        Outputs --
                    None
        """
        if self.Backup_Open <> False:
            self.Backup_File.close ()

        self.Backup_File        = None
        self.Backup_Open        = False
        self.Backup_ReadOnly    = None
        self.Backup_FileName    = None

    def     open_Backup (   self,
                            readonly = False,
                            filename = r"./temp.zip"):
        """This will open a archive file.  Currently appending is not
        formally supported...  The Read Only / Read/Write status is set
        via the readonly flag.

        Inputs  --

            Readonly:
                    True  = Read/Write
                    False = Read Only

            Filename contains the full file/pathname of the zip file.

        Outputs --
                    None
        """
        if self.Backup_Open == True:
            self.close_Backup ()

        self.Backup_Filename = filename

        if readonly == False:
            self.Backup_File        = zipfile.ZipFile ( file=filename, mode="r", compression=zipfile.ZIP_DEFLATED, allowZip64=True )
            self.Backup_Open        = True
            self.Backup_ReadOnly    = True
            self.Backup_FileName    = filename
        else:
            self.Backup_File        = zipfile.ZipFile ( file=filename, mode="w", compression=zipfile.ZIP_DEFLATED,allowZip64=True )
            self.Backup_Open        = True
            self.Backup_ReadOnly    = False
            self.Backup_FileName    = filename

    def     Verify_ZipFile ( self, FileName ):
            """Will create a temporary Zip File object, and verify the Zip file
            at <filename> location.

            Inputs  -
                        FileName - The filename of the ZIP file to verify.

            Outputs -
                        True  - File Intact CRCs match

                        Anything else, File Corrupted.  String Contains the 1st corrupted file.
            """
            temporary_Backup_File = zip_file_engine ( )
            temporary_Backup_File.open_Backup ( False, FileName)
            test_results = temporary_Backup_File.Backup_File.testzip ()
            temporary_Backup_File.close_Backup()
            return test_results

    def     Verify_Backup (self, FileName ):
            """ Generic Wrapper around the Verify_ZipFile object.
            """
            return self.Verify_ZipFile ( FileName )

    def     add_file_to_Backup ( self, filename, archived_filename):
            """Add a file to the writable Zip file.

                inputs -

                    filename = Filename of the file to be added

                    archived_filename = the Filename stored in the archive.


                Outputs -

                    None    - Zip file is in Read Only Mode

                    True    - File has been added to the Zip File.

                      -1    - Or the Zipfile engine is not initialized.
            """
            if self.Backup_ReadOnly:
                #   Archive is read only!
                print "Archive is Read Only!"
                return None
            elif self.Backup_ReadOnly == False:
                #   Archive is Read Write Mode
                if self.Backup_File <> None:
                    #   Zip File Engine is initialized
                    self.Backup_File.write (filename, archived_filename)
                    #print self.size_of_backup ()
                    #   Return Success
                    return True
                else:
                    #   Zip File Engine is *NOT* initialized.
                    return -1

    def     size_of_backup ( self ):
        return os.path.getsize ( self.Backup_FileName )



#########################################################################
No_Archive = 1
ZIP  = 2

class   backup_system:
    """Main Class for the Backup Engine.

    Inputs  -
                default_source  = The pathname for the source files.
                default_target  = The pathname for the archive to be written to.
                default_tag     = the prepended text tag for the archive file.

    Outputs -

            None

    """
    def     __init__ (  self,
                        default_source  = None,
                        default_target  = None,
                        default_exclude = "",
                        default_extensions = "",
                        default_tag     = None,
                        prepend         = False,
                        quiet           = False):
        """The initialization routines for the Backup Engine.

        Inputs  -
                    default_source  = The pathname for the source files.
                    default_target  = The pathname for the archive to be written to.
                    default_exclude =
                    default_tag     = the text tag for the archive file.
                    prepend         = Deterimines the placement of the default tag.

                                        True - The tag is prepended to the filename
                                        False - The Tag is appended to the filename.

                                        The default is to append the default_tag.  (False)

                    quiet           = Forcibly prevent any output from the directory walk.

        Outputs -

                None;  Internal Values are initialized for the core engine.

        """

        self.directory_to_backup        = default_source
        self.backup_storage_location    = default_target
        self.base_filename              = default_tag
        self.archive_filename           = None
        self.force_quiet                = quiet
#        self.exlude_files_dir           = default_exlude

        self.exclude_files_dir           = default_exclude.upper().strip().split(",")
        self.exclude_exts                = default_extensions.upper().strip().split(",")
        print self.exclude_files_dir

        if default_tag == None:
            self.archive_filename_template  = "%m_%d_%Y__%H_%M_%S"
        else:
            if (prepend==True):
                self.archive_filename_template  = self.base_filename + "_%m_%d_%Y__%H_%M_%S"
            elif (prepend==None) or (prepend==False):
                self.archive_filename_template  = "%m_%d_%Y__%H_%M_%S_" + self.base_filename


        self.archive_filename_extension = ".zip"
        self.archive_engine_to_use      = None


    def     create_archive_filename  ( self ):
        """This sets the archive filename in the object.

        This is set, to prevent timing issues internally.

        Inputs -

                None

        Outputs -

                None;  Internally creates the archives filename from the backup_storage_location,
                and the archive_filename_template.
        """
        self.archive_filename = self.backup_storage_location + os.sep + time.strftime (self.archive_filename_template, time.localtime() ) + self.archive_filename_extension


    def     Verify_Backup ( self ):
        """ Wrapper around the archive_engines verify routines.

        This will automatically start the verification process, and
        return the results.

        Inputs -

                    None

        Outputs -

                    True  - File Intact CRCs match

                    Anything else, File Corrupted.  String Contains details from the
                    archiver engine.

        """
        return self.archive_engine_to_use.Verify_Backup ( self.archive_filename )


    def     start_archive_engine ( self, Backup_Type):
        """ Initializae the derived archive_engine, depending on the Backup_Type.

        Inputs -
                Backup_Type
                    1  - None
                    2  - Zip

        Outputs -

                None

        """
        if Backup_Type == 2:
            self.archive_engine_to_use = zip_file_engine ()

        self.create_archive_filename ()
        self.archive_engine_to_use.open_Backup (   readonly = True, filename = self.archive_filename )

    def     close_archive_file ( self ):
        """Stop and Close the Archive File.

        This does terminate the Archive Engine.
        But does not terminate the Backup_Engine.

        Inputs -
                    None

        Outputs -
                    None; Internally resets the archive engine to a closed state.

        """
        self.archive_engine_to_use.close_Backup ()

    def     walk_directory_tree ( self, notify_directory = None, notify_file = None ):
        """Walk the source directory tree, and add each file/directory into the archive file.

        Inputs -

            notify_directory    (Pointer)   - see below
            notify_file         (Pointer)   - see below

        Outputs -

            None


        If you wish to have a console output for the walk function, you can
        have that via the notify_directory and notify_file functions....

        Create two stubs and pass them to the walk routine.  The routines only have
        a single input, either a directory name, or a filename, depending on the
        function.

            def     notify_dir ( directory_name ):
                print
                print "Processing Directory - %s " % directory_name


            def     notify_file ( file_name ):
                print "\t\tFile - %s " % file_name

        Backup_Engine.walk_directory_tree ( notify_directory = notify_dir, notify_file = notify_file )
        """
        selfexclude = os.path.normpath(self.archive_filename)

        if self.force_quiet:
            notify_directory    = None
            notify_file         = None

        for root, dirs, files in os.walk( self.directory_to_backup ):
            if notify_directory <> None:
                notify_directory ( root )
            for fileptr in files:
                if notify_file <> None:
                    notify_file ( fileptr )
                #
                #   Add the file to the backup zip file.

#                if os.path.normpath(file) <> selfexclude:
#                    self.archive_engine_to_use.add_file_to_Backup ( root + os.sep + file, root + os.sep + file)
#                else:
#                     print "Skipping, it is backup file - %s" % file
                exclude_file = False
                if os.path.normpath(fileptr) == selfexclude:
                    exclude_file = True

                if fileptr.strip().upper() in self.exclude_files_dir:
                    exclude_file = True

                if root <> '.' and self.exclude_files_dir <> ['']:
                    root_segment = root.strip().upper().split(os.sep)
                    for x in root_segment:
                        if x in self.exclude_files_dir:
                            exclude_file = True

#self.exclude_exts
                if self.exclude_exts<> ['']:
                    for x in self.exclude_exts:
                    #print "X: ", x.strip(), " - ", os.path.splitext( file )[1].upper().strip()
                    #print  x.strip() == os.path.splitext( file )[1].upper().strip()
                        if x.strip() == os.path.splitext( fileptr )[1].upper().strip():
                            exclude_file = True

                if not exclude_file:
                    self.archive_engine_to_use.add_file_to_Backup ( root + os.sep + fileptr, root + os.sep + fileptr)
                else:
                     print "Skipping - %s" % fileptr

                exclude_file = False

def     notify_dir ( directory_name ):
    print
    print "Processing Directory - %s " % directory_name

def     notify_file ( file_name ):
    print "\t\tFile - %s " % file_name



def     Backup_Directories_App ():
    """Example Application that will backup the Directories as stated in the command line.

    Inputs -
                None

    Outputs -

                None;  FileSystem, Archive file.


    """
    print "Initialization Successful..."
    print

    Backup_Engine = backup_system ( indigo.server.getInstallFolderPath(),
                                    os.path.expanduser ('~/Documents/IndigoBackup'),
                                    "",
                                    "",
                                    'Indigo_Backup',
                                    True,
                                    False)

    Backup_Engine.start_archive_engine ( ZIP )


    print "Backup Source - %s " % Backup_Engine.directory_to_backup
    print "Backup Target - %s " % Backup_Engine.backup_storage_location
    print "Backup Archive - %s " % Backup_Engine.archive_filename

    #Backup_Engine.walk_directory_tree ( notify_directory = notify_dir, notify_file = notify_file )
    Backup_Engine.walk_directory_tree ()
    Backup_Engine.close_archive_file ()

    print "Verifying the Archive File...."
    test = Backup_Engine.Verify_Backup ( )
    if test:
        print
        print "The Backup has failed!"
        print
        print "This file, %s, is bad." % test
    else:
        print
        print "The Backup has been verified!"
        print
        print "Backup is successful."
    print
    print "Backup Application has completed."

if __name__ == "__main__":      #   If run from the Command line
    Backup_Directories_App ()   #   run the unit test.


