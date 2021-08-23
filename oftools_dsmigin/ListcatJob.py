#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Module to run the Listcat Job.

    Typical usage example:
      job = ListcatJob(storage_resource)
      job.run()
"""

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .ListcatEnum import LCol
from .MigrationEnum import Col
from .Context import Context
from .Job import Job
from .Log import Log
from .Utils import Utils


class ListcatJob(Job):
    """A class used to run the Listcat Job.

        It handles both dataset info retrieval from the Mainframe as well as the VSAM dataset info retrieval from a listcat file.
        
        Attributes:
            Inherited from Job module.

        Methods:
            analyze(record) -- Assesses listcat eligibility.
            get_dataset_info(record) -- Executes the FTP command on Mainframe to retrieve dataset info.
            run(record) -- Performs all the steps to exploit Mainframe info, the provided listcat file and update the CSV file accordingly."""

    def _analyze(self, record):
        """Assesses listcat eligibility.

            This method double check multiple parameters in the record columns to make sure that the listcat job can proceed without error:
                - check IGNORE and LISTCAT status

            Arguments:
                record {list} -- List of dataset parameters.

            Returns:
                integer -- Return code of the method."""
        Log().logger.debug('[listcat] Assessing dataset eligibility: ' +
                           record[Col.DSN.value])

        skip_message = '[listcat] Skipping dataset: ' + record[
            Col.DSN.value] + ': '

        if record[Col.IGNORE.value] == 'Y':
            Log().logger.info(skip_message + 'IGNORE set to "Y"')
            rc = 1
        elif record[Col.LISTCAT.value] == 'N':
            Log().logger.debug(skip_message + 'LISTCAT set to "N"')
            rc = 1
        elif record[Col.LISTCAT.value] in ('', 'Y', 'F'):
            Log().logger.debug('[listcat] LISTCAT set to "' +
                               record[Col.LISTCAT.value] + '"')
            rc = 0
        else:
            rc = 0

        if rc == 0:
            Log().logger.debug('[listcat] Proceeding, dataset eligible: ' +
                               record[Col.DSN.value])

        return rc

    def _recall(self, record):
        """Executes FTP command to make dataset available to download.

            If a dataset has 'Migrated' as VOLSER parameter, the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Args:
                record: A list, the dataset data to execute the recall using the DSN.

            Returns:
                An integer, the return code of the method."""
        Log().logger.info('[listcat] Recalling migrated dataset:' +
                          record[Col.DSN.value])
        ftp_command = 'cd ' + record[Col.DSN.value]
        Log().logger.debug('[listcat] ' + ftp_command)
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _get_dataset_record(self, record):
        """Executes the FTP command on Mainframe to retrieve dataset info.

            It executes the ftp command and then the ls command on Mainframe to retrieve general info about dataset such as RECFM, LRECL, BLKSIZE, DSORG and VOLSER. It uses the submethod formatting_dataset_info to parse the output.

            Arguments:
                record {list} -- List of dataset parameters.

            Returns:
                integer -- Return code of the method."""
        Log().logger.info('[listcat] Retrieving dataset info from Mainframe: ' +
                          record[Col.DSN.value])

        ftp_command = 'ls ' + record[Col.DSN.value]
        Log().logger.debug('[listcat] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            lines = stdout.splitlines()
            if len(lines) > 0:
                fields = lines[1].split()

                if fields[0] == 'Migrated':
                    record[Col.VOLSER.value] = fields[0]
                    Log().logger.info('[listcat] Dataset marked as "Migrated"')
                    self._recall(record)
                    Log().logger.debug(
                        '[listcat] Running the ftp ls command once again')
                    stdout, _, rc = Utils().execute_ftp_command(ftp_command)
                    if rc == 0:
                        line = stdout.splitlines()
                        fields = line[1].split()
                    else:
                        status = 'FAILED'
                        Log().logger.info('LISTCAT MAINFRAME ' + status)
                        return rc

                if fields[0] == 'VSAM':
                    record[Col.DSORG.value] = fields[0]

                if len(fields) > 7:
                    record[Col.RECFM.value] = fields[-5]
                    record[Col.LRECL.value] = fields[-4]
                    record[Col.BLKSIZE.value] = fields[-3]
                    record[Col.DSORG.value] = fields[-2]
                    record[Col.VOLSER.value] = fields[0]

                status = 'SUCCESS'
            else:
                status = 'FAILED'
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT MAINFRAME ' + status)

        return rc

    def _update_dataset_record(self, record):
        """
        """
        dsn = record[Col.DSN.value]
        
        if dsn in Context().listcat.data.keys():
            listcat_record = [dsn] + Context().listcat.data[dsn]

            record[Col.RECFM.value] = listcat_record[LCol.RECFM.value]
            record[Col.VSAM.value] = listcat_record[LCol.VSAM.value]
            record[Col.KEYOFF.value] = listcat_record[LCol.KEYOFF.value]
            record[Col.KEYLEN.value] = listcat_record[LCol.KEYLEN.value]
            record[Col.MAXLRECL.value] = listcat_record[LCol.MAXLRECL.value]
            record[Col.AVGLRECL.value] = listcat_record[LCol.AVGLRECL.value]
            record[Col.CISIZE.value] = listcat_record[LCol.CISIZE.value]

            status = 'SUCCESS'
            rc = 0
        else:
            Log().logger().info('[listcat] Dataset not found in the Listcat file: Skipping dataset')
            status = 'SKIPPED'
            rc = 0

        Log().logger.info('LISTCAT FILE ' + status)

        return rc

    def run(self, record):
        """Performs all the steps to exploit Mainframe info, the provided listcat file and update the CSV file accordingly.

            It first analyzes if the listcat job can run for the given dataset, then it executes the FTP command to get the dataset info from the Mainframe and retrieves data from a listcat file. Finally, it writes the changes to the CSV file.

            Arguments:
                record {list} -- List of dataset parameters.

            Returns:  
                integer -- Return code of the job."""
        Log().logger.debug('[listcat] Starting Job')
        rc1, rc2 = 0, 0

        # Skipping dataset listcat under specific conditions
        rc = self._analyze(record)
        if rc != 0:
            return rc

        # Retrieve info from mainframe using FTP
        if Context().ip_address != None:
            rc1 = self._get_dataset_record(record)

        # Retrieving info from listcat file for VSAM datasets
        if record[Col.DSORG.value] == 'VSAM':
            rc2 = self._update_dataset_record(record)
            # rc = listcat.update_dataset_record()

        # Processing the result of the listcat
        if rc1 == 0 and rc2 == 0:
            status = 'SUCCESS'
            record[Col.LISTCATDATE.value] = Context().timestamp
            if record[Col.LISTCAT.value] != 'F':
                record[Col.LISTCAT.value] = 'N'
            rc = 0
        else:
            status = 'FAILED'
            if rc1 != 0:
                rc = rc1
            else:
                rc = rc2

        Log().logger.info('LISTCAT ' + status)

        self._storage_resource.write()
        Log().logger.debug('[listcat] Ending Job')

        return rc