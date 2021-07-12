#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module that contains all functions required for successful dataset migration to OpenFrame.


Typical usage example:

  dsmigin = DSMIGINHandler()
  dsmigin.run(records)
"""

# Generic/Built-in modules
import os
import subprocess
import time

# Third-party modules

# Owned modules
from .Context import Context
from .MigrationEnum import Col
from .Utils import Utils


class DSMIGINHandler():
    """A class used to perform all task regarding dataset migration depending mainly on the dataset organization, the DSORG column of the CSV file.

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
        __init__(): Initializes all attributes.
        _cobgensch(record): Generate the schema file from the COPYBOOK specified in the CSV file for the given dataset.
        _migrate_PO(record): Execute migration with the tool dsmigin for a PO dataset.
        _migrate_PS(record): Execute migration with the tool dsmigin for a PS dataset.
        _migrate_VSAM(record): Execute migration with the tool dsmigin for a VSAM dataset.
        _formatting_command(shell_command): Prevent bugs in dsmigin execution by escaping some special characters.
        _clear_conversion_directory(self): Delete all files in the conversion direcotry at the end of the migration.
        _analyze(record): Assess migration eligibility.
        run(records): Main method for dataset migration from Linux environment to OpenFrame volume.
    """

    def __init__(self):
        """Initializes all attributes.
        """
        self._migration_type = Context().get_migration_type()
        self._encoding_code = Context().get_encoding_code()
        self._today_date = Context().get_today_date()
        self._dataset_directory = Context().get_dataset_directory()
        self._conversion_directory = Context().get_conversion_directory()
        self._copybook_directory = Context().get_copybook_directory()

        self._records = []

    def _cobgensch(self, record):
        """Generate the schema file from the COPYBOOK specified in the CSV file for the given dataset.

        Args:
            record: A list, the dataset data where to retrieve COPYBOOK location.
        
        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        # COPYBOOK name needs to be manually entered in the CSV file and then this generation is performed for the migration 
        cobgensch_command = 'cobgensch ' + self._copybook_directory
        cobgensch_command += record[Col.COPYBOOK.value]
        cobgensch_command = self._formatting_command(cobgensch_command)
        proc = Utils().execute_shell_command(cobgensch_command)
        if proc != None:
            rc = proc.returncode
        else:
            rc = -1

        return rc

    def _migrate_PO(self, record):
        """Execute migration with the tool dsmigin for a PO dataset.

        Args:
            record: A list, the dataset data to perform the migration.

        Returns:
            An integer, the return code of the method.
        """
        po_directory = self._dataset_directory + '/' + record[Col.DSN.value]
        os.chdir(po_directory)
        rc = 0

        if self._migration_type == 'C':
            # Creating directory for dataset conversion
            try:
                dataset_conv_dir = self._conversion_directory + record[
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
                source_file = po_directory + '/' + member
                dest_file = dataset_conv_dir + '/' + member
                options = ' -e ' + self._encoding_code
                options += ' -s ' + record[Col.COPYBOOK.value].split(
                    '.')[0] + '.conv'
                options += ' -l ' + record[Col.LRECL.value]
                options += ' -o PS'
                options += ' -b ' + record[Col.BLKSIZE.value]
                options += ' -f L'
                options += ' -' + self._migration_type + ' '
                options += ' -sosi 6'
                # Forced migration
                options += ' -F'

                dsmigin_command = 'dsmigin ' + source_file + ' ' + dest_file + options
                dsmigin_command = self._formatting_command(dsmigin_command)
                proc = Utils().execute_shell_command(dsmigin_command)
                if proc != None:
                    rc = proc.returncode
                else:
                    rc = -1
                if rc != 0:
                    break
        else:
            # ? Useless since we force migration by default?
            # dsdelete command
            dsdelete_command = 'dsdelete ' + record[Col.DSN.value]
            dsdelete_command = self._formatting_command(dsdelete_command)
            proc = Utils().execute_shell_command(dsdelete_command)
            if proc != None:
                rc = proc.returncode
            else:
                rc = -1

            if record[Col.DSN.value] is not None:
                # dscreate command
                dsname = record[Col.DSN.value]
                options = ' -o ' + record[Col.DSORG.value]
                if 'F' in record[Col.RECFM.value] and record[
                        Col.LRECL.value] == '80' and record[
                            Col.COPYBOOK.value] == 'L_80.convcpy':
                    options += ' -f L '
                else:
                    options += ' -f ' + record[Col.RECFM.value]
                options += ' -b ' + record[Col.BLKSIZE.value]
                options += ' -l ' + record[Col.LRECL.value]

                dscreate_command = 'dscreate ' + options + ' ' + dsname
                dscreate_command = self._formatting_command(dscreate_command)
                proc = Utils().execute_shell_command(dscreate_command)
                if proc != None:
                    rc = proc.returncode
                else:
                    rc = -1

            for member in os.listdir(po_directory):
                # dsmigin command
                source_file = po_directory + '/' + member
                dest_file = record[Col.DSN.value]
                options = ' -m ' + member
                options += ' -e ' + self._encoding_code
                options += ' -s ' + record[Col.COPYBOOK.value].split(
                    '.')[0] + '.conv'
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
                # Forced migration
                options += ' -F'

                dsmigin_command = 'dsmigin ' + source_file + ' ' + dest_file + options
                dsmigin_command = self._formatting_command(dsmigin_command)
                proc = Utils().execute_shell_command(dsmigin_command)
                if proc != None:
                    rc = proc.returncode
                else:
                    rc = -1
                if rc != 0:
                    break

        os.chdir(self._dataset_directory)

        return rc

    def _migrate_PS(self, record):
        """Execute migration with the tool dsmigin for a PS dataset.

        Args:
            record: A list, the dataset data to perform the migration.
        
        Returns:
            An integer, the return code of the method.
        """
        rc = 0

        # ? Useless since we force migration by default?
        # dsdelete command
        dsdelete_command = 'dsdelete ' + record[Col.DSN.value]
        dsdelete_command = self._formatting_command(dsdelete_command)
        proc = Utils().execute_shell_command(dsdelete_command)
        if proc != None:
            rc = proc.returncode
        else:
            rc = -1

        # dsmigin command
        source_file = record[Col.DSN.value]
        if self._migration_type == 'C':
            dest_file = self._conversion_directory + '/' + record[Col.DSN.value]
        else:
            dest_file = record[Col.DSN.value]

        options = ' -e ' + self._encoding_code
        options += ' -s ' + record[Col.COPYBOOK.value].split('.')[0] + '.conv'
        options += ' -l ' + record[Col.LRECL.value]
        options += ' -o ' + record[Col.DSORG.value]
        options += ' -b ' + record[Col.BLKSIZE.value]
        options += ' -f ' + record.cols[Col.RECFM.value]
        if self._migration_type == 'C':
            options += ' -C '
        options += ' -sosi 6'
        # Forced migration
        options += ' -F'

        dsmigin_command = 'dsmigin ' + source_file + ' ' + dest_file + options
        dsmigin_command = self._formatting_command(dsmigin_command)
        proc = Utils().execute_shell_command(dsmigin_command)
        if proc != None:
            rc = proc.returncode
        else:
            rc = -1

        return rc

    def _migrate_VSAM(self, record):
        """Execute migration with the tool dsmigin for a VSAM dataset.

        Args:
            record:

        Returns:
            An integer, the return code of the method.
        """
        rc = 0

        if self._migration_type != 'C':
            # idcams delete command
            idcams_delete_command = 'idcams delete -t CL' + ' -n ' + record[
                Col.DSN.value]
            idcams_delete_command = self._formatting_command(idcams_delete_command)
            proc = Utils().execute_shell_command(idcams_delete_command)
            if proc != None:
                rc = proc.returncode
            else:
                rc = -1

            # idcams define command
            idcams_define_command = 'idcams define -t CL' + ' -n ' + record[
                Col.DSN.value]
            idcams_define_command += ' -o ' + record[Col.VSAM.value]
            idcams_define_command += ' -l ' + record[
                Col.AVGLRECL.value] + ',' + record[Col.MAXLRECL.value]
            idcams_define_command += ' -k ' + record[
                Col.KEYLEN.value] + ',' + record[Col.KEYOFF.value]
            idcams_define_command = self._formatting_command(idcams_define_command)
            proc = Utils().execute_shell_command(idcams_define_command)
            if proc != None:
                rc = proc.returncode
            else:
                rc = -1

        # dsmigin command
        source_file = record[Col.DSN.value]
        if self._migration_type == 'C':
            dest_file = self._conversion_directory + '/' + record[Col.DSN.value]
        else:
            dest_file = record[Col.DSN.value]

        options = ' -e ' + self._encoding_code
        options += ' -s ' + record[Col.COPYBOOK.value].split('.')[0] + '.conv'
        options += ' -f ' + record.cols[Col.RECFM.value]
        if self._migration_type == 'C':
            options += ' -C '
        options += ' -R -sosi 6'
        # Forced migration
        options += ' -F'

        dsmigin_command = 'dsmigin ' + source_file + ' ' + dest_file + options
        dsmigin_command = self._formatting_command(dsmigin_command)
        proc = Utils().execute_shell_command(dsmigin_command)
        if proc != None:
            rc = proc.returncode
        else:
            rc = -1

        return rc

    def _formatting_command(self, shell_command):
        """Prevent bugs in dsmigin execution by escaping some special characters.

        It currently supports escaping the following characters:
            - $
            - #

        Args:
            shell_command: A string, the input shell command that needs to be formatted.

        Returns:
            A string, the shell command correctly formatted ready for execution.
        """
        shell_command = shell_command.replace('$', '\\$')
        shell_command = shell_command.replace('#', '\\#')
        print(shell_command)

        return shell_command

    def _clear_conversion_directory(self):
        """Delete all files in the conversion direcotry at the end of the migration.

        In the situation of a migration with conversion only, some files are created in this folder but they are completely useless and take some space, that is why it needs to be cleared after each migration with conversion only.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0

        for file_name in os.listdir(self._conversion_directory):
            file_path = os.path.join(self._conversion_directory, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                rc = -1
                print('Failed to delete' + file_path + '. Reason: ' + e)

        return rc

    def _analyze(self, record):
        """Assess migration eligibility. 

        This method double check multiple parameters in the CSV file to make sure that dataset migration can process without error:
            - check missing information
            - check DSMIGIN and IGNORE columns status

        Args:
            record: A list, the dataset data to perform the migration.

        Returns:
            An integer, the return code of the method.
        """
        rc = 0
        unset_list = ('', ' ', None)
        message = 'Skipping dataset: ' + record[Col.DSN.value] + '. Reason: '

        # Missing information for migration execution
        if record[Col.DSORG.value] == 'PO' or  record[Col.DSORG.value] == 'PS':
            if record[Col.COPYBOOK.value] in unset_list:
                print(message + 'missing COPYBOOK information for the given dataset.')
                rc = -1
            if record[Col.LRECL.value] in unset_list:
                print(message + 'missing record length LRECL information for the given dataset.')
                rc = -1
            if record[Col.BLKSIZE.value] in unset_list:
                print(message + 'missing block size BLKSIZE information for the given dataset.')
                rc = -1
            if record[Col.RECFM.value] in unset_list:
                print(message + 'missing record format RECFM information for the given dataset.')
                rc = -1

        elif record[Col.DSORG.value] == 'VSAM':
            if record[Col.VSAM.value] in unset_list:
                print(message + 'missing VSAM information for the given dataset.')
                rc = -1
            if record[Col.AVGLRECL.value] in unset_list:
                print(message + 'missing AVGLRECL information for the given dataset.')
                rc = -1
            if record[Col.MAXLRECL.value] in unset_list:
                print(message + 'missing MAXLRECL information for the given dataset.')
                rc = -1
            if record[Col.KEYLEN.value] in unset_list:
                print(message + 'missing KEYLEN information for the given dataset.')
                rc = -1
            if record[Col.KEYOFF.value] in unset_list:
                print(message + 'missing KEYOFF information for the given dataset.')
                rc = -1
            if record[Col.COPYBOOK.value] in unset_list:
                print(message + 'missing COPYBOOK information for the given dataset.')
                rc = -1
            if record[Col.RECFM.value] in unset_list:
                print(message + 'missing record format RECFM information for the given dataset.')
                rc = -1
        
        elif record[Col.DSORG.value] in unset_list:
            print(message + 'missing DSORG information for the given dataset.')
            rc = -1

        # Skipping dataset migration - DSMIGIN set to No
        if record[Col.DSMIGIN.value] == 'N':
            print(message + 'DSMIGIN flag set to "No".')
            rc = -1
        # Skipping dataset migration - Successful, already done
        elif record[Col.DSMIGIN.value] == 'S':
            print(message + 'already successfully migrated.')
            rc = -1

        # Skipping dataset migration - ignore   
        if record[Col.IGNORE.value] == 'Y':
            print(message + 'IGNORE flag set to "Yes".')
            rc = -1
        
        return rc

    def run(self, records):
        """Main method for dataset migration from Linux environment to OpenFrame volume.

        Args:
            records: A 2D-list, the elements of the CSV file containing all the dataset data.

        Returns:
            A 2D-list, dataset data after all the changes applied in the migration execution.
        """
        os.chdir(self._dataset_directory)
        self._records = records
        rc = 0

        for record in self._records:

            # Skipping dataset download under specific conditions
            rc = self._analyze(record)
            if rc != 0:
                continue

            # Retry dataset migration that was previously failed
            if record[Col.DSMIGIN.value] == 'F':
                print('Last migration failed. Going to try again.')

            start_time = time.time()

            rc = self._cobgensch(record)
            if rc < 0:
                continue
                # Add a certain condition

            dsorg = record[Col.DSORG.value]
            if dsorg == 'PO':
                rc = self._migrate_PO(record)
            elif dsorg == 'PS':
                rc = self._migrate_PS(record)
            elif dsorg == 'VSAM':
                rc = self._migrate_VSAM(record)
            else:
                print('Invalid DSORG ' + dsorg + ' information for the given dataset:' + record[Col.DSN.value] + '. Current supported dataset organizations: PO, PS, VSAM.')
                rc = -1
                continue

            elapsed_time = time.time() - start_time

            # Processing the result of the migration
            record[Col.DSMIGINDATE.value] = self._today_date
            if rc == 0:
                print('Dataset migration success!')
                record[Col.DSMIGIN.value] = 'S'
                record[Col.DSMIGINDURATION.value] = str(elapsed_time)
            elif rc < 0:
                print('Dataset migration failed!')
                record[Col.DSMIGIN.value] = 'F'

        self._clear_conversion_directory()

        return self._records
