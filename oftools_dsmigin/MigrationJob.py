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
        rc = 0
        unset_list = ('', ' ', None)
        root_skipping_message = '[migration] Skipping dataset: ' + record[
            Col.DSN.value] + ': '

        # # Dataset organization considerations - missing information for successful migration
        if record[Col.DSORG.value] == 'PO' or record[Col.DSORG.value] == 'PS':
            if record[Col.COPYBOOK.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing COPYBOOK information for the given dataset')
                rc = 1
            if record[Col.LRECL.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing record length LRECL information for the given dataset'
                )
                rc = 1
            if record[Col.BLKSIZE.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing block size BLKSIZE information for the given dataset'
                )
                rc = 1
            if record[Col.RECFM.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing record format RECFM information for the given dataset'
                )
                rc = 1

        elif record[Col.DSORG.value] == 'VSAM':
            if Context().prefix == '':
                Log().logger.warning(
                    root_skipping_message +
                    'PrefixError: -p or --prefix option must be specified for VSAM dataset download from mainframe'
                )
                rc = 1
            if record[Col.COPYBOOK.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing COPYBOOK information for the given dataset')
                rc = 1
            if record[Col.RECFM.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing record format RECFM information for the given dataset'
                )
                rc = 1
            if record[Col.VSAM.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing VSAM information for the given dataset')
                rc = 1
            if record[Col.KEYOFF.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing KEYOFF information for the given dataset')
                rc = 1
            if record[Col.KEYLEN.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing KEYLEN information for the given dataset')
                rc = 1
            if record[Col.MAXLRECL.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing MAXLRECL information for the given dataset')
                rc = 1
            if record[Col.AVGLRECL.value] in unset_list:
                Log().logger.warning(
                    root_skipping_message +
                    'Missing AVGLRECL information for the given dataset')
                rc = 1

        elif record[Col.DSORG.value] in unset_list:
            Log().logger.warning(
                root_skipping_message +
                'Missing DSORG information for the given dataset')
            rc = 1

        else:
            Log().logger.error(
                root_skipping_message +
                'Invalid DSORG information for the given dataset')
            rc = 1

        # Evaluating potential reasons of skipping if dataset consideration are ok
        if rc == 0:
            if record[Col.IGNORE.value] == 'Y':
                Log().logger.info(root_skipping_message + 'IGNORE set to "Y"')
                rc = 1
            elif record[Col.DSMIGIN.value] == 'N':
                Log().logger.debug(root_skipping_message +
                                   'Dataset already successfully migrated')
                rc = 1
            elif record[Col.DSMIGIN.value] in ('', 'Y', 'F'):
                Log().logger.debug('')
                rc = 0
            elif record[Col.FTP.value] == 'F':
                Log().logger.info(root_skipping_message +
                                  'FTP set to "F", failed download')
                rc = 1

        return rc

    def _cobgensch(self, record):
        """Generate the schema file from the COPYBOOK specified in the CSV file for the given dataset.

            Args:
                record: A list, the dataset data where to retrieve COPYBOOK location.
            
            Returns:
                An integer, the return code of the method."""
        rc = 0
        # COPYBOOK name needs to be manually entered in the CSV file and then this generation is performed for the migration
        cobgensch_command = 'cobgensch ' + Context().copybook_directory
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
        po_directory = Context().dataset_directory + '/' + record[Col.DSN.value]
        os.chdir(po_directory)
        rc = 0

        if Context().conversion:
            # Creating directory for dataset conversion
            try:
                dataset_conv_dir = Context().conversion_directory + record[
                    Col.DSN.value]
                if not os.path.exists(dataset_conv_dir):
                    os.mkdirs(dataset_conv_dir)
                else:
                    print('This directory already exist... skipping mkdir')
            except:
                dataset_conv_dir = ''
                print(
                    'Dataset conversion directory creation failed. Permission denied.'
                )

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
                #TODO Change the line below, that is not going to work
                options += ' -' + Context().conversion + ' '
                options += ' -sosi 6'
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

        os.chdir(Context().dataset_directory)

        return rc

    def _migrate_PS(self, record):
        """Execute migration with the tool dsmigin for a PS dataset.

            Args:
                record: A list, the dataset data to perform the migration.
            
            Returns:
                An integer, the return code of the method."""
        rc = 0

        # ? Useless since we force migration by default?
        # dsdelete command
        src_file = record[Col.DSN.value]
        dsdelete_command = 'dsdelete ' + src_file

        dsdelete_command = Utils().format_command(dsdelete_command)
        _, _, rc = Utils().execute_shell_command(dsdelete_command)

        # dsmigin command
        src_file = Context().dataset_directory + '/' + record[Col.DSN.value]
        if Context().conversion:
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
        options += ' -F'  # Forced migration
        if Context().conversion:
            options += ' -C'

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
        file_name = Context().prefix + record[Col.DSN.value]

        # dsmigin command
        src_file = file_name
        if Context().conversion:
            dst_file = Context().conversion_directory + '/' + file_name
        else:
            dst_file = file_name

        options = ' -e ' + Context().encoding_code
        options += ' -s ' + record[Col.COPYBOOK.value].rsplit('.',
                                                              1)[0] + '.conv'
        options += ' -f ' + record[Col.RECFM.value]
        options += ' -R'
        options += ' -sosi 6'
        options += ' -F'  # Forced migration
        if Context().conversion:
            options += ' -C'

        dsmigin_command = 'dsmigin ' + src_file + ' ' + dst_file + options
        dsmigin_command = Utils().format_command(dsmigin_command)
        _, _, rc = Utils().execute_shell_command(dsmigin_command)

        # idcams delete command
        src_file = file_name
        options = ' -t CL'

        idcams_delete_command = 'idcams delete' + ' -n ' + src_file + options
        idcams_delete_command = Utils().format_command(idcams_delete_command)
        _, _, rc = Utils().execute_shell_command(idcams_delete_command)

        # idcams define command
        src_file = file_name
        options = ' -o ' + record[Col.VSAM.value]
        options += ' -l ' + record[Col.AVGLRECL.value]
        options += ',' + record[Col.MAXLRECL.value]
        options += ' -k ' + record[Col.KEYLEN.value]
        options += ',' + record[Col.KEYOFF.value]
        options += ' -c SYS1.MASTER.ICFCAT'
        options += ' -t CL'
        options += ' -v DEFVOL'

        idcams_define_command = 'idcams define' + ' -n ' + src_file + options
        idcams_define_command = Utils().format_command(idcams_define_command)
        _, _, rc = Utils().execute_shell_command(idcams_define_command)

        # idcams repro command
        src_file = file_name
        dst_file = record[Col.DSN.value]

        idcams_repro_command = 'idcams repro' + ' -i ' + src_file + ' -o ' + dst_file
        idcams_repro_command = Utils().format_command(idcams_repro_command)
        _, _, rc = Utils().execute_shell_command(idcams_repro_command)

        # dsdelete command on the NVSAM dataset
        dsdelete_command = 'dsdelete ' + file_name
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
        print('')
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
        os.chdir(Context().dataset_directory)
        rc = 0

        # Skipping dataset migration under specific conditions
        rc = self._analyze(record)
        if rc == 1:
            return rc

        rc = self._cobgensch(record)
        if rc != 0:
            return rc
            # Add a certain condition

        rc = self._migrate(record)
        if rc == 0:
            self._storage_resource.write()
            self._number_migrated += 1
            Log().logger.info('[migration] Current dataset migration count: ' +
                              str(self._number_migrated))

        self._clear_conversion_directory()
        Log().logger.debug('[migration] Ending Job')

        return rc