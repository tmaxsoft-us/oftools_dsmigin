#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""This module runs the Listcat Job.

    Typical usage example:
        job = ListcatJob(storage_resource)
        job.run()
    """

# Generic/Built-in modules

# Third-party modules

# Owned modules
from .Context import Context
from .GDG import GDG
from .Job import Job
from .ListcatEnum import LCol
from .Log import Log
from .MigrationEnum import Col
from .Utils import Utils


class ListcatJob(Job):
    """A class used to run the Listcat Job.

        This class contains a run method that executes all the steps of the job. It handles both dataset info retrieval from the Mainframe as well as the VSAM dataset info retrieval from a listcat file.
        
        Attributes:
            Inherited from Job module.

        Methods:
            _analyze(record) -- Assesses listcat eligibility.
            _recall(dataset_name) -- Executes FTP command to make dataset available to download.
            _get_migrated(record, fields) -- Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.
            _update_record(record, fields) -- Updates migration dataset record with parameters extracted from the FTP command output.
            _get_from_mainframe(record) -- Executes the FTP command on Mainframe to retrieve dataset info.
            _get_from_file(record) -- Reads the listcat CSV file to retrieve dataset info.
            run(record) -- Performs all the steps to exploit Mainframe info, the provided listcat file and updates the CSV file accordingly.
        """

    def _analyze(self, record):
        """Assesses listcat eligibility.

            This method double check multiple parameters in the migration dataset records to make sure that the given dataset listcat can be processed without error:
                - check IGNORE and LISTCAT status

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns:
                integer -- Return code of the method.
            """
        Log().logger.debug('[listcat] Assessing dataset eligibility: ' +
                           record[Col.DSN.value])
        skip_message = '[listcat] Skipping dataset: ' + record[
            Col.DSN.value] + ': '

        if record[Col.LISTCAT.value] == 'F':
            Log().logger.debug('[listcat] LISTCAT set to "F"')
            rc = 0

        else:
            if record[Col.IGNORE.value] == 'Y':
                Log().logger.info(skip_message + 'IGNORE set to "Y"')
                rc = 1
            elif record[Col.LISTCAT.value] == 'N':
                Log().logger.debug(skip_message + 'LISTCAT set to "N"')
                rc = 1
            elif record[Col.LISTCAT.value] in ('', 'Y'):
                Log().logger.debug('[listcat] LISTCAT set to "' +
                                   record[Col.LISTCAT.value] + '"')
                rc = 0
            else:
                rc = 0

        if rc == 0:
            Log().logger.debug('[listcat] Proceeding, dataset eligible: ' +
                               record[Col.DSN.value])

        return rc

    def _recall(self, dataset_name):
        """Executes FTP command to make dataset available to download.

            If a dataset has VOLSER set to 'Migrated', the program executes this recall method just to open the diretory containing the dataset to trigger download execution from the mainframe.

            Arguments:
                dataset_name {string} -- Dataset name.

            Returns:
                integer -- Return code of the method.
            """
        Log().logger.info('[listcat] Recalling migrated dataset: ' +
                          dataset_name)
        ftp_command = 'cd ' + dataset_name
        Log().logger.debug('[listcat] ' + ftp_command)
        _, _, rc = Utils().execute_ftp_command(ftp_command)

        return rc

    def _get_migrated(self, record, fields):
        """Executes the FTP command on Mainframe to retrieve dataset info in the case where VOLSER is set to Migrated.

            Arguments:
                record {list} -- The given migration record containing dataset info.
                fields {list} -- The list of parameters extracted from the FTP command currently being processed.

            Returns:
                list -- The new list of parameters extracted from the FTP command after the recall.
            """
        Log().logger.info('[listcat] Dataset marked as "Migrated"')
        record[Col.VOLSER.value] = fields[0]
        self._recall(fields[-1])

        Log().logger.debug('[listcat] Running the ftp ls command once again')
        ftp_command = 'ls ' + record[Col.DSN.value]
        Log().logger.debug('[listcat] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            lines = stdout.splitlines()
            if len(lines) > 1:
                fields = lines[1].split()
            else:
                Log().logger.debug('[listcat] FTP result empty')
                fields = []
        else:
            fields = []

        return fields

    def _update_record(self, record, fields):
        """Updates migration dataset record with parameters extracted from the FTP command output.

        Arguments:
            record {list} -- The given migration record containing dataset info.
            fields {list} -- The list of parameters extracted from the FTP command currently being processed.
        """
        record[Col.RECFM.value] = fields[-5]
        record[Col.LRECL.value] = fields[-4]
        record[Col.BLKSIZE.value] = fields[-3]
        record[Col.DSORG.value] = fields[-2]
        record[Col.VOLSER.value] = fields[0]

    def _get_from_mainframe(self, index, record):
        """Executes the FTP command on Mainframe to retrieve dataset info.

            It executes the ftp command and then the ls command on Mainframe to retrieve general info about dataset such as RECFM, LRECL, BLKSIZE, DSORG and VOLSER. It uses the submethod formatting_dataset_info to parse the output.

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns:
                integer -- Return code of the method.
            """
        Log().logger.info('[listcat] Retrieving dataset info from Mainframe: ' +
                          record[Col.DSN.value])

        ftp_command = 'ls ' + record[Col.DSN.value]
        Log().logger.debug('[listcat] ' + ftp_command)
        stdout, _, rc = Utils().execute_ftp_command(ftp_command)

        if rc == 0:
            lines = stdout.splitlines()
            if len(lines) > 1:
                fields = lines[1].split()

                if len(fields) > 0:

                    if fields[0] == 'Migrated':
                        fields = self._get_migrated(record, fields)

                    # New evaluation of len(fields) required after migrated update
                    if len(fields) == 0:
                        Log().logger.info(
                            '[listcat] Fields still empty after recall')
                        status = 'FAILED'

                    elif len(fields) > 1:
                        status = 'SUCCESS'
                        # record[Col.COPYBOOK.value] = record[Col.DSN.value] + '.cpy'

                        if fields[1] == 'Tape':
                            Log().logger.info(
                                '[listcat] Dataset in "Tape" volume')
                            record[Col.VOLSER.value] = fields[1]

                        elif fields[0] == 'VSAM':
                            record[Col.DSORG.value] = fields[0]

                        elif fields[0] == 'GDG':
                            Log().logger.info('[listcat] GDG dataset detected')
                            record[Col.DSORG.value] = fields[0]
                            self._gdg = GDG(index, record)
                            self._gdg.get_dataset_records()

                        elif len(fields) > 7:
                            self._update_record(record, fields)

                        else:
                            Log().logger.info(
                                '[listcat] Scenario not supported')
                            status = 'FAILED'
                            rc = -1
                    else:
                        Log().logger.info('[listcat] Fields incomplete')
                        status = 'FAILED'
                        rc = -1
                else:
                    Log().logger.info('[listcat] Fields empty')
                    status = 'FAILED'
                    rc = -1
            else:
                Log().logger.info('[listcat] FTP result empty')
                status = 'FAILED'
                rc = -1
        elif rc == -1:
            Log().logger.error(
                '[listcat] FTPListcatError: No such dataset on Mainframe: ' +
                record[Col.DSN.value])
            status = 'FAILED'
        else:
            status = 'FAILED'

        Log().logger.info('LISTCAT MAINFRAME ' + status)

        return rc

    def _get_from_file(self, record):
        """Reads the listcat CSV file to retrieve dataset info.

            First, this method search for the dataset in the listcat CSV file. If it finds the dataset, it updates the corresponding migration record. This method is used only for VSAM datasets.

            Arguments:
                record {list} -- The given migration record containing dataset info.

            Returns:
                integer -- Return code of the method.
            """
        dsn = record[Col.DSN.value]

        #? Handle FileNotFound before doing that, because tried to access .keys() on a NoneType object is raising an exception
        if dsn in Context().listcat.data.keys():
            Log().logger.debug(
                '[listcat] Dataset found in the Listcat file: Updating migration record'
            )

            listcat_record = [dsn] + Context().listcat.data[dsn]

            record[Col.RECFM.value] = listcat_record[LCol.RECFM.value]
            record[Col.VSAM.value] = listcat_record[LCol.VSAM.value]
            record[Col.KEYOFF.value] = listcat_record[LCol.KEYOFF.value]
            record[Col.KEYLEN.value] = listcat_record[LCol.KEYLEN.value]
            record[Col.MAXLRECL.value] = listcat_record[LCol.MAXLRECL.value]
            record[Col.AVGLRECL.value] = listcat_record[LCol.AVGLRECL.value]
            record[Col.CISIZE.value] = listcat_record[LCol.CISIZE.value]
            record[Col.CATALOG.value] = listcat_record[LCol.CATALOG.value]

            status = 'SUCCESS'
            rc = 0
        else:
            Log().logger.info(
                '[listcat] Dataset not found in the Listcat file: Skipping dataset'
            )
            status = 'FAILED'
            rc = -1

        Log().logger.info('LISTCAT FILE ' + status)

        return rc

    def run(self, index, record):
        """Performs all the steps to exploit Mainframe info, the provided listcat file and updates the migration records accordingly.

            It first run the analyze method to check if the given dataset is eligible for listcat. Then it executes the FTP command to get the dataset info from the Mainframe and retrieves data from a listcat file, this last step being for VSAM datasets only. Finally, it writes the changes to the CSV file.

            Arguments:
                index {integer} -- The position of the record in the Context().records list.
                record {list} -- The given migration record containing dataset info.

            Returns:  
                integer -- Return code of the job.
            """
        Log().logger.debug('[listcat] Starting Job')
        rc1, rc2 = 0, 0

        # Skipping dataset listcat under specific conditions
        rc = self._analyze(record)
        if rc != 0:
            return rc

        # Retrieve info from mainframe using FTP
        if Context().ip_address != None:
            rc1 = self._get_from_mainframe(index, record)

        # Retrieving info from listcat file for VSAM datasets
        if record[Col.DSORG.value] == 'VSAM':
            rc2 = self._get_from_file(record)

        # Processing the result of the listcat
        if rc1 == 0 and rc2 == 0:
            status = 'SUCCESS'
            record[Col.LISTCATDATE.value] = Context().timestamp
            if record[Col.LISTCAT.value] != 'F':
                record[Col.LISTCAT.value] = 'N'
            rc = 0
        #TODO Return codes study
        # elif rc1 != 0 and rc2 != 0:
        #     status = 'FAILED'
        else:
            status = 'FAILED'
            if rc1 != 0:
                rc = rc1
            else:
                rc = rc2

        if record[Col.DSORG.value] == 'GDG':
            self._gdg.update_listcat_result()

        Log().logger.info('LISTCAT ' + status)

        self._storage_resource.write()
        Log().logger.debug('[listcat] Ending Job')

        return rc