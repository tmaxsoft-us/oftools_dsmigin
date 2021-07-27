#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
    """

# Generic/Built-in modules
import argparse
import os
import sys
import traceback
# import logging

# Third-party modules

# Owned modules
from . import __version__
from .Context import Context
from .CSV import CSV
from .JobFactory import JobFactory
from .Log import Log
from .Statistics import Statistics
from .Utils import Utils


def main():
    return Main().run()


class Main(object):
    """Main class containing the methods for parsing the command arguments and running OpenFrame Tools 
    Dataset Migration.

        Methods:
            _parse_arg(): Parsing command-line options.
            _create_jobs(args, csv): Creates job depending on the input parameters.
            run(): Perform to execute jobs of OpenFrame Tools Dataset Migration."""

    def _parse_arg(self):
        """Parsing command-line options.

            The program defines what arguments it requires, and argparse will figure out how to parse 
            those out of sys.argv. The argparse module also automatically generates help, usage 
            messages and issues errors when users give the program invalid arguments.

            Returns:
                args, an ArgumentParser object."""
        parser = argparse.ArgumentParser(
            add_help=False, description='OpenFrame Tools Dataset Migration')

        parser._action_groups.pop()
        required = parser.add_argument_group('Required arguments')
        jobs = parser.add_argument_group('Jobs arguments')
        optional = parser.add_argument_group('Optional arguments')
        others = parser.add_argument_group('Help & version')

        # Required arguments
        required.add_argument(
            '-c',
            '--csv',
            action='store',  # optional because default action is 'store'
            dest='csv',
            help=
            'name of the CSV file, contains the datasets and their parameters',
            metavar='FILENAME',
            required=True,
            type=str)

        required.add_argument('-w',
                              '--working-directory',
                              action='store',
                              dest='working_directory',
                              help='path of the work directory',
                              metavar='DIRECTORY',
                              required=True,
                              type=str)

        # Jobs arguments
        jobs.add_argument(
            '-f',
            '--ftp',
            action='store',
            choices=['U', 'D'],
            dest='ftp',
            help=
            '''trigger FTP execution for CSV file update and dataset download. FTP server running on Mainframe required. Potential options:
                'U' for CSV file update ONLY
                'D' for CSV file update & dataset download''',
            metavar='FLAG',
            required=False,
            type=str)

        jobs.add_argument(
            '-l',
            '--listcat',
            action='store',
            dest='listcat',
            help=
            'name of the listcat result file/directory, required if the CSV file contains VSAM dataset info',
            metavar='FILENAME/DIRECTORY',
            required=False,
            type=str)

        jobs.add_argument(
            '-m',
            '--migration',
            action='store',
            choices=['C', 'G'],
            dest='migration',
            help='''trigger dsmigin to start dataset migration. Potential options:
                'C' for dataset conversion ONLY
                'G' for dataset conversion & generation''',
            metavar='FLAG',
            required=False,
            type=str)

        # Optional arguments
        #TODO Make it possible to specify a list of directories, separated with a ':'
        optional.add_argument('-C',
                              '--copybook-directory',
                              action='store',
                              dest='copybook_directory',
                              help='path of the copybook directory',
                              metavar='DIRECTORY',
                              required=False,
                              type=str)

        optional.add_argument(
            '-L',
            '--log-level',
            action='store',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            dest='log_level',
            help=
            'log level, potential values: DEBUG, INFO, WARNING, ERROR, CRITICAL. (default: INFO)',
            metavar='LEVEL',
            required=False,
            type=str)

        # It is not possible to handle datasets download at once, there is a certain timeout using FTP to download from the mainframe, it is then necessary to set up a number of datasets to download for the current execution, and download little by little.
        optional.add_argument('-n',
                              '--number',
                              action='store',
                              dest='number',
                              help='number of datasets to be handled',
                              metavar='INTEGER',
                              required=False,
                              type=int)

        optional.add_argument(
            '-p',
            '--ip-address',
            action='store',
            dest='ip_address',
            help=
            'ip address required for any command that involves FTP execution',
            metavar='IP_ADDRESS',
            required=False,
            type=str)

        optional.add_argument(
            '-t',
            '--tag',
            action='store',
            dest='tag',
            help='tag for the CSV file snd the log file names',
            metavar='TAG',
            required=False,
            type=str)

        # Other arguments
        others.add_argument('-h',
                            '--help',
                            action='help',
                            help='show this help message and exit')

        others.add_argument(
            '-v',
            '--version',
            action='version',
            help='show this version message and exit',
            version='%(prog)s {version}'.format(version=__version__))

        #    arg_parser.add_argument('-b',
        #                     '--backup-directory',
        #                     action='store',
        #                     dest='backup',
        #                     help='Specify backup directory for csv file',
        #                     metavar='DIRECTORY',
        #                     required=False)

        # Do the parsing
        if len(sys.argv) == 1:
            parser.print_help(sys.stdout)
            sys.exit(0)
        try:
            args = parser.parse_args()
        except argparse.ArgumentError as e:
            Log().logger.critical('ArgumentError: ' + str(e))
            sys.exit(-1)

        # Analyze CSV file, making sure a file with .csv extension is specified
        try:
            csv_path = os.path.expandvars(args.csv_file)
            extension = csv_path.rsplit('.', 1)[1]
            if extension != 'csv':
                raise TypeError()
        except IndexError:
            Log().logger.critical(
                'IndexError: Given CSV file does not have a .csv extension: ' +
                csv_path)
            sys.exit(-1)
        except TypeError:
            Log().logger.critical('TypeError: Expected .csv extension, found ' +
                                  extension + ': ' + csv_path)
            sys.exit(-1)

        # Analyze missing optional arguments
        if args.ftp:
            try:
                if args.ip_address is None:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'IpAddressError: -p or --ip-address option must be specified for dataset download'
                )
                sys.exit(-1)

        if args.migration:
            try:
                if args.copybook_directory is None:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'CopybookDirectoryError: -C or --copybook-directory option must be specified for dataset migration'
                )
                sys.exit(-1)

        # Analyze if the argument ip_address respect valid format
        if args.ip_address:
            try:
                status = Utils().analyze_ip_address(args.ip_address)
                if status is False:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'FormatError: Invalid -p, --ip-address option: Must respect either IPv4 or IPv6 standard format'
                )
                sys.exit(-1)

        # Analyze if the argument number is positive
        if args.number:
            try:
                if args.number <= 0:
                    raise SystemError()
            except:
                Log().logger.critical(
                    'SignError: Invalid -n, --number option: Must be positive')
                sys.exit(-1)

        # Analyze if listcat has been properly specified
        #! No extension for listcat file, just must be a file and not a directory
        #NO EXTENSION
        # if args.listcat:
        #     try:
        #         listcat_path = os.path.expandvars(args.listcat)
        #         if os.path.isdir(listcat_path):
        #             Log().logger.debug('Listcat directory specified.')
        #             #TODO Analyze extension of all listcat files
        #         else:
        #             Log().logger.debug('Listcat file specified.')
        #             extension = listcat_path.rsplit('.', 1)[1]
        #             if extension != 'txt':
        #                 raise TypeError()
        #     except IndexError:
        #         Log().logger.critical(
        #             'IndexError: Given Listcat file does not have a .txt extension: '
        #             + listcat_path)
        #         sys.exit(-1)
        #     except TypeError:
        #         Log().logger.critical(
        #             'TypeError: Expected .txt extension, found ' + extension +
        #             ': ' + listcat_path)
        #         sys.exit(-1)

        return args

    def _create_jobs(self, args, csv):
        """Creates job depending on the input parameters.

            Args:
                args:
                csv:

            Returns:
                A list of Job objects.

            Raises:
                #TODO Complete docstrings, maybe change the behavior to print traceback only with DEBUG as log level"""
        jobs = []
        job_factory = JobFactory(csv)

        try:
            if args.ftp:
                Context.ftp_type = args.ftp
                Context().ip_address = args.ip_address
                Context().number_datasets = args.number
                Context().set_dataset_directory()
                job = job_factory.create('ftp')
                jobs.append(job)
            if args.listcat != None:
                Context().listcat_file_path = args.listcat
                Context().set_listcat_directory()
                job = job_factory.create('listcat')
                jobs.append(job)
            if args.migration != None:
                Context().encoding_code = 'US'
                Context().migration_type = args.migration
                Context().set_conversion_directory()
                Context().copybook_directory = args.copybook_directory
                job = job_factory.create('migration')
                jobs.append(job)
        except:
            traceback.print_exc()
            Log().logger.error(
                'Unexpected error detected during the job creation')
            sys.exit(-1)

        return jobs

    def run(self):
        """Performs all the steps to execute jobs of oftools_dsmigin.

            Returns:
                An integer, the general return code of the program."""
        # For testing purposes. allow to remove logs when executing coverage
        # logging.disable(logging.CRITICAL)
        Log().open_stream()

        # Parse command-line options
        args = self._parse_arg()

        # Initialize variables for program execution
        Context().working_directory = args.working_directory
        Context().tag = args.tag

        # Set log level and initialize log file
        log_file_name = 'oftools_dsmigin_' + Context().tag + '_' + Context(
        ).timestamp + '.log'
        log_file_path = os.path.join(Context().log_directory, log_file_name)

        Log().set_level(args.log_level)
        Log().open_file(log_file_path)

        statistics = Statistics()

        # CSV file processing
        csv = CSV(args.csv)

        # Create jobs
        jobs = self._create_jobs(args, csv)

        # Run jobs
        for job in jobs:
            rc = job.run()
            if rc < 0:
                Log().logger.error(
                    'An error occurred. Aborting program execution')
                break

        rc = statistics.run()
        if rc < 0:
            Log().logger.error(
                'An error occurred. Aborting statistics processing')

        # Need to clear context completely and close log at the end of the execution
        Context().clear_all()
        Log().close_file()
        Log().close_stream()

        return rc