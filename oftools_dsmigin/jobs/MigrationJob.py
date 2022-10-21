#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Migration Job.

Typical usage example:
  job = MigrationJob(storage_resource)
  job.run()
"""

# Generic/Built-in modules
import time
import sys

# Third-party modules

# Owned modules
from ..Context import Context
from ..enums.CSV import MCol
from ..enums.Message import Color, LogM
from ..handlers.FileHandler import FileHandler
from ..handlers.ShellHandler import ShellHandler
from .Job import Job
from ..Log import Log


class MigrationJob(Job):
    """A class used to run the Migration Job.

    This class contains a run method that executes all the steps of the job. It
    handles all tasks related to dataset migration which mainly depends on the
    dataset organization, the DSORG column of the CSV file.

    Attributes:
        Inherited from Job module.

    Methods:
        _analyze(record) -- Assesses migration eligibility.
        _cobgensch(record) -- Generates the schema file from the COPYBOOK
            parameter specified for the given migration record.
        _migrate_PO(record) -- Executes the migration using dsmigin for a PO
            dataset.
        _migrate_PS(record) -- Executes the migration using dsmigin for a PS
            dataset.
        _migrate_VSAM(record) -- Executes the migration using dsmigin for a
            VSAM dataset.
        _migrate(record) -- Main method for dataset migration from Linux server
            to OpenFrame environment.
        run(record) -- Performs all the steps to migrate datasets using dsmigin
            and updates the CSV file.
    """

    def _analyze(self, record):
        """Assesses migration eligibility.

        This method double check multiple parameters in the migration dataset
        records to make sure that the given dataset migration can be processed
        without error:
            - check missing information
            - check IGNORE, FTPDATE, and DSMIGIN columns status
            - check DSORG column status, and based on the result check the
                requirements for a successful migration
            - check COPYBOOK column status, to make sure that the file
                specified has a .cpy extension

        Arguments:
            record {list} -- Migration record containing dataset info, which
                needs a verification prior migration.

        Returns:
            integer -- Return code of the method.

        Raises:
            TypeError -- Exception is raised if the extension of the given
                copybook is invalid.
        """
        Log().logger.debug(LogM.ELIGIBILITY.value %
                           (self._name, record[MCol.DSN.value]))
        status = 0

        unset_list = ('', ' ')
        skip_message = LogM.SKIP_DATASET.value % (self._name,
                                                  record[MCol.DSN.value])

        if record[MCol.DSMIGIN.value] == 'F':
            Log().logger.debug(LogM.COL_F.value % (self._name, 'DSMIGIN'))
            status = 0

        else:
            if record[MCol.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + LogM.COL_Y.value % 'IGNORE')
                status = 1
            elif record[MCol.FTPDATE.value] == '':
                Log().logger.info('[migration] ' +
                                  LogM.COL_NOT_SET.value % 'FTPDATE')
                status = 0
            elif record[MCol.DSMIGIN.value] == 'N':
                Log().logger.debug(skip_message + LogM.COL_N.value % 'DSMIGIN')
                status = 1
            elif record[MCol.DSMIGIN.value] in ('', 'Y'):
                Log().logger.debug('[migration] DSMIGIN set to "' +
                                   record[MCol.DSMIGIN.value] + '"')
                status = 0

            # Dataset organization considerations - missing information for
            # successful migration
            if status == 0:
                if record[MCol.DSORG.value] in ('PO', 'PS'):
                    if record[MCol.RECFM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'RECFM')
                        status = 1
                    if record[MCol.LRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'LRECL')
                        status = 1
                    if record[MCol.BLKSIZE.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'BLKSIZE')
                        status = 1

                elif record[MCol.DSORG.value] == 'VSAM':
                    if record[MCol.RECFM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'RECFM')
                        status = 1
                    if record[MCol.VSAM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'VSAM')
                        status = 1
                    if record[MCol.KEYOFF.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'KEYOFF')
                        status = 1
                    if record[MCol.KEYLEN.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'KEYLEN')
                        status = 1
                    if record[MCol.MAXLRECL.value] in unset_list:
                        Log().logger.warning(skip_message + 'MAXLRECL')
                        status = 1
                    if record[MCol.AVGLRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             LogM.COL_EMPTY.value % 'AVGLRECL')
                        status = 1

                elif record[MCol.DSORG.value] == 'GDG':
                    Log().logger.info(skip_message +
                                      LogM.DSORG_GDG.value % self._name)
                    record[MCol.DSMIGINDATE.value] = Context().time_stamp
                    record[MCol.DSMIGINDURATION.value] = '0'
                    record[MCol.DSMIGIN.value] = 'N'
                    status = 1

                elif record[MCol.DSORG.value] in unset_list:
                    Log().logger.warning(skip_message +
                                         LogM.COL_EMPTY.value % 'DSORG')
                    status = 1

                else:
                    Log().logger.error(skip_message + LogM.COL_INVALID.value %
                                       record[MCol.DSORG.value])
                    status = 1

        if status == 0:
            Log().logger.debug(LogM.ELIGIBLE.value %
                               (self._name, record[MCol.DSN.value]))

        return status

    def _cobgensch(self, record):
        """Generates the schema file from the COPYBOOK parameter specified for
        the given migration record.

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
            result = FileHandler().check_extension(copybook_path, 'cpy')
            if result is False:
                status = 1
                return status

        cobgensch = 'cobgensch ' + copybook_path

        Log().logger.info(LogM.COMMAND.value % (self._name, cobgensch))
        _, _, status = ShellHandler().execute_command(cobgensch, 'migration')

        # Copy the copybook to TSAM copybook directory
        if status == 0:
            tsam_path = '${OPENFRAME_HOME}/tsam/copybook/'
            status = FileHandler().copy_file(copybook_path, tsam_path)

        return status

    def _is_in_openframe(self, dsn):
        """Checks if the dataset already exist in OpenFrame.

        Arguments:
            dsn {string} -- Dataset name.

        Returns:
            integer -- Return code of the method.
        """
        status = 0

        if Context().force == '':

            is_in_openframe = False
            openframe_listcat = 'listcat ' + dsn

            Log().logger.debug(LogM.COMMAND.value %
                               (self._name, openframe_listcat))
            stdout, _, status = ShellHandler().execute_command(
                openframe_listcat)

            if status == 0:
                lines = stdout.splitlines()
                if len(lines) > 1:
                    fields = lines[-2].split()
                    try:
                        if int(fields[2]) > 0:
                            is_in_openframe = True
                    except ValueError:
                        Log().logger.critical(
                            LogM.OF_LISTCAT_NOT_WORKING.value % self._name)
                        sys.exit(-1)
                else:
                    Log().logger.debug(LogM.OF_LISTCAT_NOT_ENOUGH.value %
                                       self._name)
                    Log().logger.debug(lines)
            else:
                Log().logger.critical(LogM.OF_LISTCAT_NOT_WORKING.value %
                                      self._name)
                sys.exit(-1)

            if is_in_openframe is True:
                Log().logger.info(LogM.SKIP_MIGRATION.value % self._name)
                status = 1

        return status

    def _migrate_po(self, record):
        """Executes the migration using dsmigin for a PO dataset.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        status = 0

        if Context().conversion == '':
            status = self._is_in_openframe(record[MCol.DSN.value])
            if status != 0:
                return status

        else:
            # Creating directory for dataset conversion
            po_conversion_dir = Context().conversion_directory + '/' + record[
                MCol.DSN.value]
            FileHandler().create_directory(po_conversion_dir, 'po')

        po_dir = Context().datasets_directory + '/' + record[MCol.DSN.value]

        for member in FileHandler.get_files(po_dir):
            src = po_dir + '/' + member

            if Context().conversion == ' -C ':
                dst = po_conversion_dir + '/' + member
            else:
                dst = record[MCol.DSN.value]

                _, _, status = ShellHandler().dsdelete(record)
                if status != 0:
                    break

                _, _, status = ShellHandler().dscreate(record)
                if status != 0:
                    break

            _, _, status = ShellHandler().dsmigin(record, Context(), src, dst,
                                                  member)
            if status != 0:
                break

        return status

    def _migrate_ps(self, record):
        """Executes the migration using dsmigin for a PS dataset.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        status = 0

        if Context().conversion == '':
            status = self._is_in_openframe(record)
            if status != 0:
                return status

            _, _, status = ShellHandler().dsdelete(record)
            if status != 0:
                return status

        _, _, status = ShellHandler().dsmigin(record, Context())

        return status

    def _migrate_vsam(self, record):
        """Executes the migration using idcams and dsmigin for a VSAM dataset.

        Arguments:
            record {list} -- Migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        if Context().conversion == '':
            status = self._is_in_openframe(record)
            if status != 0:
                return status

            _, _, status = ShellHandler().idcams_delete(record)
            if status != 0:
                return status

            _, _, status = ShellHandler().idcams_define(record, Context())
            if status != 0:
                return status

        _, _, status = ShellHandler().dsmigin(record, Context())

        return status

    def _migrate(self, record):
        """Main method for dataset migration from Linux server to OpenFrame
        environment.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the method.
        """
        status = 0
        start_time = time.time()

        if record[MCol.DSORG.value] == 'PO':
            status = self._migrate_po(record)
        elif record[MCol.DSORG.value] == 'PS':
            status = self._migrate_ps(record)
        elif record[MCol.DSORG.value] == 'VSAM':
            status = self._migrate_vsam(record)

        elapsed_time = time.time() - start_time

        # Processing the result of the migration
        if status == 0:
            record[MCol.DSMIGINDATE.value] = Context().time_stamp
            record[MCol.DSMIGINDURATION.value] = str(round(elapsed_time, 4))
            if record[MCol.DSMIGIN.value] != 'F':
                record[MCol.DSMIGIN.value] = 'N'

            result = 'SUCCESS'
            color = Color.GREEN.value
        else:
            result = 'FAILED'
            color = Color.RED.value

        Log().logger.info(color + LogM.MIGRATION_STATUS.value %
                          (result, round(elapsed_time, 4)))

        return status

    def run(self, record, _):
        """Performs all the steps to migrate datasets using dsmigin and updates
        the CSV file.

        It first run the analyze method to check if the given dataset is
        eligible for migration. Then, it executes the dsmigin command to
        download it and updates the DSMIGIN status (success or fail) at the
        same time. Finally, it writes the changes to the CSV file.

        Arguments:
            record {list} -- The given migration record containing dataset info.

        Returns:
            integer -- Return code of the job.
        """
        Log().logger.debug(LogM.START_JOB.value % self._name)
        status = 0

        # Skipping dataset migration under specific conditions
        status = self._analyze(record)
        if status != 0:
            return status

        # Generating schema file from copybook
        status = self._cobgensch(record)
        if status != 0:
            return status

        # Migrating dataset using dsmigin utility
        status = self._migrate(record)

        if Context().test:
            FileHandler().empty_directory(Context().conversion_directory)

        Log().logger.debug(LogM.END_JOB.value % self._name)

        return status
