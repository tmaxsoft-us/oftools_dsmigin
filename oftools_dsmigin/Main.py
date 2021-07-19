#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
"""

# Generic/Built-in modules
import argparse
import os
import sys
import traceback

# Third-party modules

# Owned modules
from . import __version__
from .Context import Context
from .JobFactory import JobFactory
from .Log import Log
from .Utils import Utils


def main():
    return Main().run()


class Main(object):
    """Main class containing the methods for parsing the command arguments and running OpenFrame Tools 
    Dataset Migration.

    Methods:
        _parse_arg(): Parsing command-line options.
        run(): Perform to execute jobs of OpenFrame Tools Dataset Migration.
    """

    def _parse_arg(self):
        """Parsing command-line options.

        The program defines what arguments it requires, and argparse will figure out how to parse 
        those out of sys.argv. The argparse module also automatically generates help, usage 
        messages and issues errors when users give the program invalid arguments.

        Returns:
            args, an ArgumentParser object.
        """
        parser = argparse.ArgumentParser(
            add_help=False, description='OpenFrame Tools Dataset Migration')
        parser._action_groups.pop()
        required = parser.add_argument_group('Required arguments')
        optional = parser.add_argument_group('Optional arguments')

        # Required arguments
        required.add_argument(
            '-c',
            '--csv',
            action='store',  # optional because default action is 'store'
            dest='input_csv',
            help=
            'name of the CSV file, contains the datasets and their parameters',
            metavar='FILENAME',
            required=True,
            type=str)

        required.add_argument('-w',
                              '--work-directory',
                              action='store',
                              dest='working_directory',
                              help='path of the work directory',
                              metavar='DIRECTORY',
                              required=True,
                              type=str)

        # Optional arguments
        #TODO MAke it possible to specify a list of directories, separated with a ':'
        optional.add_argument('-C',
                              '--copybook-directory',
                              action='store',
                              dest='copybook_directory',
                              help='path of the copybook directory',
                              metavar='DIRECTORY',
                              required=False,
                              type=str)

        optional.add_argument('-d',
                              '--download',
                              action='store_true',
                              dest='download',
                              help='trigger FTP to start dataset download',
                              required=False)

        optional.add_argument(
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

        optional.add_argument(
            '-l',
            '--listcat',
            action='store',
            dest='listcat_result',
            help=
            'name of the listcat result file/directory, required if the CSV file contains VSAM dataset info',
            metavar='FILENAME/DIRECTORY',
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
            'set log level, potential values: DEBUG, INFO, WARNING, ERROR, CRITICAL. (default: INFO)',
            metavar='LEVEL',
            required=False,
            type=str)

        # It is not possible to handle datasets download at once, there is a certain timeout using FTP to download from the mainframe, it is then necessary to set up a number of datasets to download for the current execution, and download little by little.
        optional.add_argument('-n',
                              '--number',
                              action='store',
                              dest='number_datasets',
                              help='set the number of datasets to be handled',
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

        optional.add_argument('-t',
                              '--tag',
                              action='store',
                              dest='tag',
                              help='add tag to the name of the CSV file',
                              metavar='TAG',
                              required=False,
                              type=str)

        optional.add_argument('-u',
                              '--update',
                              action='store_true',
                              dest='update',
                              help='trigger CSV file update',
                              required=False)

        optional.add_argument('-h',
                              '--help',
                              action='help',
                              help='show this help message and exit')

        optional.add_argument(
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
            csv_path = os.path.expandvars(args.input_csv)
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
        #? Maybe ip_address should be mandatory?
        if args.update_csv:
            if args.ip_address is None:
                print(
                    '-p or --ip-address option must be specified for CSV file update'
                )
                sys.exit(-1)

        if args.download:
            try:
                if args.ip_address is None:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'IpAddressError: -p or --ip-address option must be specified for dataset download'
                )
                sys.exit(-1)

            try:
                if args.number is None:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'NumberError: -n or --number option must be specified for dataset download'
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

        # Analyze if the ip address respect valid format
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

        # Analyze if the number is above 0
        if args.number:
            try:
                if args.number <= 0:
                    raise SystemError()
            except:
                Log().logger.critical(
                    'SignError: Invalid -n, --number option: Must be positive'
                )
                sys.exit(-1)

        if args.listcat_result:
            try:
                listcat_path = os.path.expandvars(args.listcat_result)
                if os.path.isdir(listcat_path):
                    Log().logger.debug('Listcat directory specified.')
                else:
                    Log().logger.debug('Listcat file specified.')
                    extension = listcat_path.rsplit('.', 1)[1]
                    if extension != 'txt':
                        raise TypeError()
            except IndexError:
                Log().logger.critical(
                    'IndexError: Given Listcat file does not have a .txt extension: '
                    + listcat_path)
                sys.exit(-1)
            except TypeError:
                Log().logger.critical(
                    'TypeError: Expected .txt extension, found ' + extension +
                    ': ' + listcat_path)
                sys.exit(-1)

        return args

    def run(self):
        """Perform to execute jobs of OFTools DSMigin.

        Returns:
            An integer, the general return code of the program.
        """
        # For testing purposes. allow to remove logs when executing coverage
        # logging.disable(logging.CRITICAL)
        Log().open_stream()

        # Parse command-line options
        args = self._parse_arg()

        # Set log level
        Log().set_level(args.log_level)

        # Initialize execution context
        Context().set_input_csv(args.input_csv)
        Context().set_migration_type(args.migration)
        Context().set_encoding_code('US')
        Context().set_number(args.number)
        Context().set_ip_address(args.ip_address)
        Context().set_listcat_result(args.listcat_result)
        Context().set_tag(args.tag)
        Context().set_today_date()
        Context().set_working_directory(args.working_directory)
        Context().set_dataset_directory()
        Context().set_conversion_directory()
        Context().set_copybook_directory(args.copybook_directory)
        Context().set_log_directory()

        # Create jobs
        job = None
        jobs = []
        job_factory = JobFactory()
        try:
            if args.update:
                job = job_factory.create('update')
            elif args.listcat_result != None:
                job = job_factory.create('listcat')
            elif args.download:
                job = job_factory.create('download')
            elif args.migration != None:
                job = job_factory.create('migration')
            jobs.append(job)
        except:
            traceback.print_exc()
            print('Unexpected error detected during the job creation')
            sys.exit(-1)

        # Run jobs
        for job in jobs:
            job.run()

        return 0