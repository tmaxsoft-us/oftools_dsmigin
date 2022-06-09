#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Migration Job.

Typical usage example:
  job = MigrationJob(storage_resource)
  job.run()
"""

# Generic/Built-in modules
import os
import time

# Third-party modules

# Owned modules
from .Context import Context
from .Job import Job
from .Log import Log
from .enums.MessageEnum import Color, LogM
from .enums.MigrationEnum import MCol
from .handlers.FileHandler import FileHandler
from .handlers.ShellHandler import ShellHandler


class MigrationJob(Job):
    """A class used to run the Migration Job.

    This class contains a run method that executes all the steps of the job. It handles all tasks related to dataset migration which mainly depends on the dataset organization, the DSORG column of the CSV file.

    Attributes:
        Inherited from Job module.

    Methods:
        _analyze(record) -- Assesses migration eligibility.
        _cobgensch(record) -- Generates the schema file from the COPYBOOK parameter specified for the given migration record.
        _migrate_PO(record) -- Executes the migration using dsmigin for a PO dataset.
        _migrate_PS(record) -- Executes the migration using dsmigin for a PS dataset.
        _migrate_VSAM(record) -- Executes the migration using dsmigin for a VSAM dataset.
        _migrate(record) -- Main method for dataset migration from Linux server to OpenFrame environment.
        run(record) -- Performs all the steps to migrate datasets using dsmigin and updates the CSV file.
    """

    def _analyze(self, record):
        """Assesses migration eligibility. 

        This method double check multiple parameters in the migration dataset records to make sure that the given dataset migration can be processed without error:
            - check missing information
            - check IGNORE, FTPDATE, and DSMIGIN columns status
            - check DSORG column status, and based on the result check the requirements for a successful migration
            - check COPYBOOK column status, to make sure that the file specified has a .cpy extension

        Arguments:
            record {list} -- The given migration record containing dataset info, which needs a verification prior migration.

        Returns:
            integer -- Return code of the method.

        Raises:
            TypeError -- Exception is raised if the extension of the given copybook is invalid.
        """
        Log().logger.debug(LogM.ELIGIBILITY.value %
                           (self._name, record[MCol.DSN.value]))
        rc = 0

        unset_list = ('', ' ')
        skip_message = LogM.SKIP.value % (self._name, record[MCol.DSN.value])

        if record[MCol.DSMIGIN.value] == 'F':
            Log().logger.debug(LogM.COL_F.value % (self._name, 'DSMIGIN'))
            rc = 0

        else:
            if record[MCol.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + LogM.COL_Y.value % 'IGNORE')
                rc = 1
            elif record[MCol.FTPDATE.value] == '':
                Log().logger.info('[migration] FTPDATE not set')
                rc = 0
            elif record[MCol.DSMIGIN.value] == 'N':
                Log().logger.debug(skip_message + LogM.COL_N.value % 'DSMIGIN')
                rc = 1
            elif record[MCol.DSMIGIN.value] in ('', 'Y'):
                Log().logger.debug('[migration] DSMIGIN set to "' +
                                   record[MCol.DSMIGIN.value] + '"')
                rc = 0

            # Dataset organization considerations - missing information for successful migration
            if rc == 0:
                if record[MCol.DSORG.value] in ('PO', 'PS'):
                    if record[MCol.COPYBOOK.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'COPYBOOK')
                        rc = 1
                    if record[MCol.RECFM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'RECFM')
                        rc = 1
                    if record[MCol.LRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'LRECL')
                        rc = 1
                    if record[MCol.BLKSIZE.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'BLKSIZE')
                        rc = 1

                elif record[MCol.DSORG.value] == 'VSAM':
                    if record[MCol.RECFM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'RECFM')
                        rc = 1
                    if record[MCol.VSAM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'VSAM')
                        rc = 1
                    if record[MCol.KEYOFF.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'KEYOFF')
                        rc = 1
                    if record[MCol.KEYLEN.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'KEYLEN')
                        rc = 1
                    if record[MCol.MAXLRECL.value] in unset_list:
                        Log().logger.warning(skip_message + 'MAXLRECL')
                        rc = 1
                    if record[MCol.AVGLRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'AVGLRECL')
                        rc = 1

                elif record[MCol.DSORG.value] == 'GDG':
                    Log().logger.warning(skip_message +
                                         LogM.DSORG_GDG.value % self._name)
                    record[MCol.DSMIGINDATE.value] = Context().time_stamp
                    record[MCol.DSMIGINDURATION.value] = '0'
                    record[MCol.DSMIGIN.value] = 'N'
                    rc = 1

                elif record[MCol.DSORG.value] in unset_list:
                    Log().logger.warning(skip_message +
                                         LogM.COL_EMPTY.value % 'DSORG')
                    rc = 1

                else:
                    Log().logger.error(skip_message + LogM.COL_INVALID.value %
                                       record[MCol.DSORG.value])
                    rc = 1

        if rc == 0:
            Log().logger.debug(LogM.ELIGIBLE.value %
                               (self._name, record[MCol.DSN.value]))

        return rc

    def _cobgensch(self, record):
        """Generates the schema file from the COPYBOOK parameter specified for the given migration record.

        Arguments:
            record {list} -- Migration record containing dataset info.
        
        Returns:
            integer -- Return code of the method.
        """
        if record[MCol.COPYBOOK.value] == '':
            copybook_path = Context().copybooks_directory + '/' + record[
                MCol.DSN.value] + '.cpy'
        else:
            copybook_path = Context().copybooks_directory + '/' + record[
                MCol.COPYBOOK.value]
            status = FileHandler().check_extension(copybook_path, 'cpy')
            if status is False:
                rc = 1
                return rc

        cobgensch = 'cobgensch ' + copybook_path

        Log().logger.debug(LogM.COMMAND.value % (self._name, cobgensch))
        _, _, rc = ShellHandler().execute_command(cobgensch, 'migration')

        # Copy the copybook to TSAM copybook directory
        if rc == 0:
            tsam_path = '${OPENFRAME_HOME}/tsam/copybook/'
            rc = FileHandler().copy_file(copybook_path, tsam_path)

        return rc

    def _is_in_openframe(self, dsn):
        """

        Arguments:
            dsn {string} --
            
        Returns:
            boolean --
        """
        is_in_openframe = False
        openframe_listcat = 'listcat ' + dsn

        Log().logger.debug(LogM.COMMAND.value % (self._name, openframe_listcat))
        stdout, _, rc = ShellHandler().execute_command(openframe_listcat)

        if rc == 0:
            lines = stdout.splitlines()
            if len(lines) > 1:
                fields = lines[-2].split()
                #TODO Throw error if the conversion to int is not working
                try:
                    if int(fields[2]) > 0:
                        is_in_openframe = True
                except ValueError:
                    Log().logger.debug(LogM.OF_LISTCAT_NOT_WORKING.value %
                                       self._name)
            else:
                Log().logger.debug(LogM.OF_LISTCAT_NOT_ENOUGH.value %
                                   self._name)
                Log().logger.debug(lines)
        else:
            Log().logger.info(LogM.OF_LISTCAT_NOT_WORKING.value % self._name)

        return is_in_openframe

    def _migrate_PO(self, record):
        """Executes the migration using dsmigin for a PO dataset.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        if Context().conversion == '' and Context().force == '':
            is_in_openframe = self._is_in_openframe(record[MCol.DSN.value])
            if is_in_openframe is True:
                Log().logger.info(LogM.SKIP_MIGRATION.value % self._name)
                rc = 1
                return rc

        po_directory = Context().datasets_directory + '/' + record[
            MCol.DSN.value]

        if Context().conversion == ' -C ':
            # Creating directory for dataset conversion
            dataset_conv_dir = Context().conversion_directory + '/' + record[
                MCol.DSN.value]
            FileHandler().create_directory(dataset_conv_dir)

        for member in FileHandler.get_files(po_directory):
            src = po_directory + '/' + member

            if Context().conversion == ' -C ':
                dst = dataset_conv_dir + '/' + member
            else:
                dst = record[MCol.DSN.value]

                _, _, rc = ShellHandler().dsdelete(record)
                if rc != 0:
                    break

                _, _, rc = ShellHandler().dscreate(record)
                if rc != 0:
                    break

            _, _, rc = ShellHandler().dsmigin(record, Context(), src, dst,
                                              member)
            if rc != 0:
                break

        return rc

    def _migrate_PS(self, record):
        """Executes the migration using dsmigin for a PS dataset.

        Arguments:
            record {list} -- Migration record containing dataset info.
        
        Returns:
            integer -- Return code of the method.
        """
        rc = 0

        if Context().conversion == '':

            if Context().force == '':
                is_in_openframe = self._is_in_openframe(record[MCol.DSN.value])
                if is_in_openframe is True:
                    Log().logger.info(LogM.SKIP_MIGRATION.value % self._name)
                    rc = 1
                    return rc

            _, _, rc = ShellHandler().dsdelete(record)
            if rc != 0:
                return rc

        _, _, rc = ShellHandler().dsmigin(record, Context())

        return rc

    def _migrate_VSAM(self, record):
        """Executes the migration using idcams and dsmigin for a VSAM dataset.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        if Context().conversion == '':

            if Context().force == '':
                is_in_openframe = self._is_in_openframe(record[MCol.DSN.value])
                if is_in_openframe is True:
                    Log().logger.info(LogM.SKIP_MIGRATION.value % self._name)
                    rc = 1
                    return rc

            _, _, rc = ShellHandler().idcams_delete(record)
            if rc != 0:
                return rc

            _, _, rc = ShellHandler().idcams_define(record, Context())
            if rc != 0:
                return rc

        _, _, rc = ShellHandler().dsmigin(record, Context())

        return rc

    def _migrate(self, record):
        """Main method for dataset migration from Linux server to OpenFrame environment.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        start_time = time.time()

        if record[MCol.DSORG.value] == 'PO':
            rc = self._migrate_PO(record)
        elif record[MCol.DSORG.value] == 'PS':
            rc = self._migrate_PS(record)
        elif record[MCol.DSORG.value] == 'VSAM':
            rc = self._migrate_VSAM(record)

        elapsed_time = time.time() - start_time

        # Processing the result of the migration
        if rc == 0:
            record[MCol.DSMIGINDATE.value] = Context().time_stamp
            record[MCol.DSMIGINDURATION.value] = str(round(elapsed_time, 4))
            if record[MCol.DSMIGIN.value] != 'F':
                record[MCol.DSMIGIN.value] = 'N'

            status = 'SUCCESS'
            color = Color.GREEN.value
        else:
            status = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.MIGRATION_STATUS.value %
                          (status, round(elapsed_time, 4)))

        return rc

    def run(self, record, _):
        """Performs all the steps to migrate datasets using dsmigin and updates the CSV file.

        It first run the analyze method to check if the given dataset is eligible for migration. Then, it executes the dsmigin command to download it and updates the DSMIGIN status (success or fail) at the same time. Finally, it writes the changes to the CSV file.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the job.
        """
        Log().logger.debug(LogM.START_JOB.value % self._name)
        rc = 0

        # Skipping dataset migration under specific conditions
        rc = self._analyze(record)
        if rc != 0:
            return rc

        # Generating schema file from copybook
        rc = self._cobgensch(record)
        if rc != 0:
            return rc

        # Migrating dataset using dsmigin utility
        rc = self._migrate(record)

        if Context().test:
            FileHandler().empty_directory(Context().conversion_directory)

        Log().logger.debug(LogM.END_JOB.value % self._name)

        return rc
