#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This modules runs the Migration Job.

    Typical usage example:

  job = MigrationJob()
  job.run()
    Module that contains all functions required for successful dataset migration to OpenFrame.

    Typical usage example:
      dsmigin = DSMIGINHandler()
      dsmigin.run(records)
"""

# Generic/Built-in modules
import os
import time

# Third-party modules

# Owned modules
from .Context import Context
from .Job import Job
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class MigrationJob(Job):
    """A class used to run the migration job.

        This class contains a run method that executes all the steps of the job.

        Methods:
            run(): Perform all the steps to migrate datasets in OpenFrame using dsmigin and update the CSV file.

        A class used to perform all task regarding dataset migration depending mainly on the dataset organization, the DSORG column of the CSV file.

        Attributes:
            _migration_type: A string, either 'C' or 'G' for generation or conversion only migration type.
            _encoding_code: A string, specifies to what ASCII characters the EBCDIC two-byte data should be converted.
            _today_date: A string, the date of today respecting a certain format.
            _dataset_directory: A string, located under the working directory, this directory contains all downloaded datasets.
            _conversion_directory: A string, located under the working directory, this directory contains all converted datasets 
                that are cleared after each migration (useless files).
            _copybook_directory: A string, the location of the copybook directory tracked with git.
            _records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Methods:
            _cobgensch(record): Generate the schema file from the COPYBOOK specified in the CSV file for the given dataset.
            _migrate_PO(record): Execute migration with the tool dsmigin for a PO dataset.
            _migrate_PS(record): Execute migration with the tool dsmigin for a PS dataset.
            _migrate_VSAM(record): Execute migration with the tool dsmigin for a VSAM dataset.
            _formatting_command(shell_command): Prevent bugs in dsmigin execution by escaping some special characters.
            _clear_conversion_directory(self): Delete all files in the conversion direcotry at the end of the migration.
            _analyze(record): Assess migration eligibility.
            run(records): Main method for dataset migration from Linux environment to OpenFrame volume."""

    def _analyze(self, record):
        """Assess migration eligibility. 

            This method double check multiple parameters in the CSV file to make sure that dataset migration can process without error:
                - check missing information
                - check DSMIGIN and IGNORE columns status

            Args:
                record: A list, the dataset data to perform the migration.

            Returns:
                An integer, the return code of the method."""
        Log().logger.debug('[migration] Assessing dataset eligibility: ' +
                           record[Col.DSN.value])
        rc = 0

        unset_list = ('', ' ')
        skip_message = '[migration] Skipping dataset: ' + record[
            Col.DSN.value] + ': '

        if record[Col.DSMIGIN.value] == 'F':
            Log().logger.debug('[migration] DSMIGIN set to "F"')
            rc = 0

        else:
            if record[Col.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + 'IGNORE set to "Y"')
                rc = 1
            elif record[Col.FTPDATE.value] == '':
                Log().logger.debug(skip_message + 'FTPDATE not set')
                rc = 1
            elif record[Col.DSMIGIN.value] == 'N':
                Log().logger.debug(skip_message + 'DSMIGIN set to "N"')
                rc = 1
            elif record[Col.DSMIGIN.value] in ('', 'Y'):
                Log().logger.debug('[migration] DSMIGIN set to "' +
                                   record[Col.DSMIGIN.value] + '"')
                rc = 0

            # Dataset organization considerations - missing information for successful migration
            if rc == 0:
                if record[Col.DSORG.value] in ('PO', 'PS'):
                    if record[Col.COPYBOOK.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing COPYBOOK parameter: It needs to be manually entered'
                        )
                        rc = 1
                    if record[Col.RECFM.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing record format RECFM parameter')
                        rc = 1
                    if record[Col.LRECL.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing record length LRECL parameter')
                        rc = 1
                    if record[Col.BLKSIZE.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing block size BLKSIZE parameter')
                        rc = 1

                elif record[Col.DSORG.value] == 'VSAM':
                    if record[Col.COPYBOOK.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing COPYBOOK parameter: It needs to be manually entered'
                        )
                        rc = 1
                    if record[Col.RECFM.value] in unset_list:
                        Log().logger.warning(
                            skip_message +
                            'Missing record format RECFM parameter')
                        rc = 1
                    if record[Col.VSAM.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             'Missing VSAM parameter')
                        rc = 1
                    if record[Col.KEYOFF.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             'Missing KEYOFF parameter')
                        rc = 1
                    if record[Col.KEYLEN.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             'Missing KEYLEN parameter')
                        rc = 1
                    if record[Col.MAXLRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             'Missing MAXLRECL parameter')
                        rc = 1
                    if record[Col.AVGLRECL.value] in unset_list:
                        Log().logger.warning(skip_message +
                                             'Missing AVGLRECL parameter')
                        rc = 1

                elif record[Col.DSORG.value] in unset_list:
                    Log().logger.warning(skip_message +
                                         'Missing DSORG parameter')
                    rc = 1

                else:
                    Log().logger.error(skip_message + 'Invalid DSORG parameter')
                    rc = 1

            # Copybook considerations - evaluating copybook extension
            if rc == 0:
                try:
                    status = Utils().check_file_extension(
                        record[Col.COPYBOOK.value], 'cpy')
                    if status is True:
                        rc = 0
                    else:
                        raise TypeError()
                except TypeError:
                    Log().logger.warning(
                        skip_message +
                        'Invalid COPYBOOK parameter: Expected .cpy extension')
                    rc = 1

        if rc == 0:
            Log().logger.debug('[migration] Proceeding, dataset eligible: ' +
                               record[Col.DSN.value])

        return rc

    def _cobgensch(self, record):
        """Generate the schema file from the COPYBOOK specified in the storage resource for the given dataset.

            Args:
                record: A list, the dataset data where to retrieve COPYBOOK location.
            
            Returns:
                An integer, the return code of the method."""
        rc = 0

        cobgensch_command = 'cobgensch ' + Context().copybooks_directory
        cobgensch_command += '/' + record[Col.COPYBOOK.value]
        cobgensch_command = Utils().format_command(cobgensch_command)
        _, _, rc = Utils().execute_shell_command(cobgensch_command)

        return rc

    def _migrate_PO(self, record):
        """Execute migration with the tool dsmigin for a PO dataset.

            Args:
                record: A list, the dataset data to perform the migration.

            Returns:
                An integer, the return code of the method."""
        po_directory = Context().datasets_directory + '/' + record[
            Col.DSN.value]
        os.chdir(po_directory)
        rc = 0

        #TODO Complete review of this method needed
        if Context().conversion == ' -C ':
            # Creating directory for dataset conversion
            try:
                dataset_conv_dir = Context().conversion_directory + record[
                    Col.DSN.value]
                if not os.path.exists(dataset_conv_dir):
                    os.mkdir(dataset_conv_dir)
                else:
                    print('This directory already exist... skipping mkdir')
            except OSError as e:
                dataset_conv_dir = ''
                print(
                    'Dataset conversion directory creation failed. Permission denied.'
                    + str(e))

            for member in os.listdir(po_directory):
                # dsmigin command
                src_file = po_directory + '/' + member
                dst_file = dataset_conv_dir + '/' + member
                options = ' -e ' + Context().encoding_code
                options += ' -s ' + record[Col.COPYBOOK.value].rsplit(
                    '.', 1)[0] + '.conv'
                options += ' -l ' + record[Col.LRECL.value]
                options += ' -o PS'
                options += ' -b ' + record[Col.BLKSIZE.value]
                options += ' -f L'
                options += ' -sosi 6'
                options += Context().conversion
                # Forced migration
                options += ' -F'

                dsmigin_command = 'dsmigin ' + src_file + ' ' + dst_file + options
                dsmigin_command = Utils().format_command(dsmigin_command)
                _, _, rc = Utils().execute_shell_command(dsmigin_command)
                if rc != 0:
                    break
        else:
            #? Useless since we force migration by default?
            # dsdelete command
            dsdelete_command = 'dsdelete ' + record[Col.DSN.value]
            dsdelete_command = Utils().format_command(dsdelete_command)
            _, _, rc = Utils().execute_shell_command(dsdelete_command)

            # dscreate command
            options = '-o ' + record[Col.DSORG.value]
            options += ' -b ' + record[Col.BLKSIZE.value]
            options += ' -l ' + record[Col.LRECL.value]

            if 'F' in record[Col.RECFM.value] and record[
                    Col.LRECL.value] == '80' and record[
                        Col.COPYBOOK.value] == 'L_80.convcpy':
                options += ' -f L '
            else:
                options += ' -f ' + record[Col.RECFM.value]

            dscreate_command = 'dscreate ' + options + ' ' + record[
                Col.DSN.value]
            dscreate_command = Utils().format_command(dscreate_command)
            _, _, rc = Utils().execute_shell_command(dscreate_command)

            for member in os.listdir(po_directory):
                # dsmigin command
                src_file = po_directory + '/' + member
                dst_file = record[Col.DSN.value]
                options = ' -m ' + member
                options += ' -e ' + Context().encoding_code
                options += ' -s ' + record[Col.COPYBOOK.value].rsplit(
                    '.', 1)[0] + '.conv'
                options += ' -l ' + record[Col.LRECL.value]
                options += ' -o ' + record[Col.DSORG.value]
                options += ' -b ' + record[Col.BLKSIZE.value]
                if 'F' in record[Col.RECFM.value] and record[
                        Col.LRECL.value] == '80' and record[
                            Col.COPYBOOK.value] == 'L_80.convcpy':
                    options += ' -f L '
                else:
                    options += ' -f ' + record[Col.RECFM.value]
                options += ' -sosi 6'
                options += ' -F'  # Forced migration

                dsmigin_command = 'dsmigin ' + src_file + ' ' + dst_file + options
                dsmigin_command = Utils().format_command(dsmigin_command)
                _, _, rc = Utils().execute_shell_command(dsmigin_command)
                if rc != 0:
                    break

        os.chdir(Context().datasets_directory)

        return rc

    def _migrate_PS(self, record):
        """Execute migration with the tool dsmigin for a PS dataset.

            Args:
                record: A list, the dataset data to perform the migration.
            
            Returns:
                An integer, the return code of the method."""
        rc = 0

        # dsdelete command
        src_file = record[Col.DSN.value]
        dsdelete_command = 'dsdelete ' + src_file

        dsdelete_command = Utils().format_command(dsdelete_command)
        _, _, rc = Utils().execute_shell_command(dsdelete_command)

        # dsmigin command
        src_file = Context().datasets_directory + '/' + record[Col.DSN.value]
        if Context().conversion == ' -C ':
            dst_file = Context().conversion_directory + '/' + record[
                Col.DSN.value]
        else:
            dst_file = record[Col.DSN.value]

        options = ' -e ' + Context().encoding_code
        options += ' -s ' + record[Col.COPYBOOK.value].rsplit('.',
                                                              1)[0] + '.conv'
        options += ' -f ' + record[Col.RECFM.value]
        options += ' -l ' + record[Col.LRECL.value]
        options += ' -b ' + record[Col.BLKSIZE.value]
        options += ' -o ' + record[Col.DSORG.value]
        options += ' -sosi 6'
        options += Context().conversion
        options += ' -F'  # Forced migration

        dsmigin_command = 'dsmigin ' + src_file + ' ' + dst_file + options
        dsmigin_command = Utils().format_command(dsmigin_command)
        _, _, rc = Utils().execute_shell_command(dsmigin_command)

        return rc

    def _migrate_VSAM(self, record):
        """Execute migration with the tool dsmigin for a VSAM dataset.

            Args:
                record:

            Returns:
                An integer, the return code of the method."""
        rc = 0

        # dsmigin command
        src_file = record[Col.DSN.value]
        if Context().conversion == ' -C ':
            dst_file = Context().conversion_directory + '/' + src_file
        else:
            dst_file = 'OFTOOLS.DSMIGIN.TEMP'

        options = ' -e ' + Context().encoding_code
        options += ' -s ' + record[Col.COPYBOOK.value].rsplit('.',
                                                              1)[0] + '.conv'
        options += ' -f ' + record[Col.RECFM.value]
        options += ' -R'
        options += ' -sosi 6'
        options += Context().conversion
        options += ' -F'  # Forced migration

        dsmigin_command = 'dsmigin ' + src_file + ' ' + dst_file + options
        dsmigin_command = Utils().format_command(dsmigin_command)
        _, _, rc = Utils().execute_shell_command(dsmigin_command)

        if Context().conversion != ' -C ':
            # idcams delete command
            src_file = record[Col.DSN.value]
            options = ' -t CL'

            idcams_delete_command = 'idcams delete' + ' -n ' + src_file + options
            idcams_delete_command = Utils().format_command(
                idcams_delete_command)
            _, _, rc = Utils().execute_shell_command(idcams_delete_command)

            # idcams define command
            src_file = record[Col.DSN.value]
            options = ' -o ' + record[Col.VSAM.value]
            options += ' -l ' + record[Col.AVGLRECL.value]
            options += ',' + record[Col.MAXLRECL.value]
            options += ' -k ' + record[Col.KEYLEN.value]
            options += ',' + record[Col.KEYOFF.value]
            options += ' -t CL'
            
            if 'CATALOG' in Context().enable_column_list:
                options += ' -c ' + record[Col.CATALOG.value]
            else:
                options += ' -c SYS1.MASTER.ICFCAT'
            if 'VOLSER' in Context().enable_column_list:
                options += ' -v ' + record[Col.VOLSER.value]
            else:
                options += ' -v DEFVOL'

            idcams_define_command = 'idcams define' + ' -n ' + src_file + options
            idcams_define_command = Utils().format_command(
                idcams_define_command)
            _, _, rc = Utils().execute_shell_command(idcams_define_command)

            # idcams repro command
            src_file = 'OFTOOLS.DSMIGIN.TEMP'
            dst_file = record[Col.DSN.value]

            idcams_repro_command = 'idcams repro' + ' -i ' + src_file + ' -o ' + dst_file
            idcams_repro_command = Utils().format_command(idcams_repro_command)
            _, _, rc = Utils().execute_shell_command(idcams_repro_command)

            # dsdelete command on the Non-VSAM dataset
            dsdelete_command = 'dsdelete OFTOOLS.DSMIGIN.TEMP'
            dsdelete_command = Utils().format_command(dsdelete_command)
            _, _, rc = Utils().execute_shell_command(dsdelete_command)

        return rc

    def _migrate(self, record):
        """
        """
        start_time = time.time()

        if record[Col.DSORG.value] == 'PO':
            rc = self._migrate_PO(record)
        elif record[Col.DSORG.value] == 'PS':
            rc = self._migrate_PS(record)
        elif record[Col.DSORG.value] == 'VSAM':
            rc = self._migrate_VSAM(record)

        elapsed_time = time.time() - start_time

        # Processing the result of the migration
        if rc == 0:
            status = 'SUCCESS'
            record[Col.DSMIGINDATE.value] = Context().timestamp
            record[Col.DSMIGINDURATION.value] = str(round(elapsed_time, 4))
            if record[Col.DSMIGIN.value] != 'F':
                record[Col.DSMIGIN.value] = 'N'
        else:
            status = 'FAILED'

        Log().logger.info('MIGRATION ' + status + ' (' +
                          str(round(elapsed_time, 4)) + ' s)')

        return rc

    def _clear_conversion_directory(self):
        """Delete all files in the conversion directory at the end of the migration.

            In the situation of a migration with conversion only, some files are created in this folder but they are completely useless and take some space, that is why it needs to be cleared after each migration with conversion only.

            Returns:
                An integer, the return code of the method."""
        rc = 0
        os.chdir(Context().conversion_directory)

        for file_name in os.listdir(Context().conversion_directory):
            try:
                os.remove(file_name)
            except Exception as e:
                rc = -1
                Log().logger.error('Failed to delete' + file_name +
                                   '. Reason: ' + e)

        return rc

    def run(self, record):
        """Main method for dataset migration from Linux environment to OpenFrame volume.

            Args:
                records: A 2D-list, the elements of the CSV file containing all the dataset data.

            Returns:
                A 2D-list, dataset data after all the changes applied in the migration execution."""
        Log().logger.debug('[migration] Starting Job')
        os.chdir(Context().datasets_directory)
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
        if rc == 0:
            self._storage_resource.write()

        # self._clear_conversion_directory()
        Log().logger.debug('[migration] Ending Job')

        return rc