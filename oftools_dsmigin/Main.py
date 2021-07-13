#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
"""

# Generic/Built-in modules
import argparse
import os
import traceback

# Third-party modules

# Owned modules
from . import __version__
from .Context import Context
from .JobFactory import JobFactory
from .Log import Log


def main():
    return Main().run()


class Main(object):
    """

    Methods:
        _parse_arg(): Parsing command-line options.
        _evaluate_ip_address(ip_address): Checking the format of the ip address used as a parameter.
        run(): Perform to execute jobs of OFTools DSMigin.
    """

    def _parse_arg(self):
        """Parsing command-line options.

        The program defines what arguments it requires, and argparse will figure out how to parse 
        those out of sys.argv. The argparse module also automatically generates help and usage 
        messages and issues errors when users give the program invalid arguments.

        Returns:
            args, an ArgumentParser object.
        """
        arg_parser = argparse.ArgumentParser(prog='oftools_dsmigin')

        # Mandatory arguments
        arg_parser.add_argument(
            '-c',
            '--csv',
            action='store',  # optional because default action is 'store'
            dest='input_csv',
            help=
            'Mandatory CSV file name for either csv update, liscat, dataset dowload or migration',
            metavar='FILENAME',
            required=True)

        arg_parser.add_argument(
            '-w',
            '--work-directory',
            action='store',
            dest='work_directory',
            help='Set working directory for dataset migration',
            metavar='DIRECTORY',
            required=True)

        # Optional arguments
        arg_parser.add_argument('-d',
                                '--download',
                                action='store_false',
                                dest='download',
                                help='Trigger FTP to start dataset download',
                                required=False)

        arg_parser.add_argument(
            '-m',
            '--migration',
            action='store',
            dest='migration',
            help='''Trigger dsmigin for dataset migration. Potential options:
                                'G' for dataset conversion & generation 
                                'C' for dataset conversion ONLY''',
            metavar='FLAG',
            required=False)

        arg_parser.add_argument(
            '-l',
            '--listcat',
            action='store',
            dest='listcat_result',
            help=
            'Listcat result file name / directory, required for CSV file containing VSAM dataset info',
            metavar='FILENAME/DIRECTORY',
            required=False)

        arg_parser.add_argument(
            '-u',
            '--update',
            action='store_false',
            dest='update',
            help='Trigger CSV file update based on FTP information',
            required=False)

        # It is not possible to handle datasets download at once, there is a certain timeout using FTP to download from the mainframe, it is then necessary to set up a number of datasets to download for the current execution, and download little by little.
        arg_parser.add_argument('-n',
                                '--number',
                                action='store',
                                dest='number',
                                help='Number of datasets to be handled',
                                metavar='INTEGER',
                                required=False,
                                type=int)

        arg_parser.add_argument(
            '-p',
            '--ip-address',
            action='store',
            dest='ip_address',
            help=
            'IP address required for any command that required an FTP execution',
            metavar='IP_ADDRESS',
            required=False)

        arg_parser.add_argument(
            '-C',
            '--copybook-directory',
            action='store',
            dest='copybook_directory',
            help='Set copybook directory for dataset migration',
            metavar='DIRECTORY',
            required=False)

        arg_parser.add_argument('-t',
                                '--tag',
                                action='store',
                                dest='tag',
                                help='Add tag to the name of CSV file and ...',
                                metavar='TAG',
                                required=False)

        arg_parser.add_argument(
            '-L',
            '--log-level',
            action='store',
            default='INFO',
            dest='log_level',
            help=
            'Set log level (DEBUG|INFO|WARNING|ERROR|CRITICAL). Default is INFO',
            metavar='LEVEL',
            required=False)

        arg_parser.add_argument('-v',
                                '--version',
                                action='store_true',
                                help='Print version information',
                                required=False)

        #    arg_parser.add_argument('-l',
        #    '--log-directory',
        #    action='store',
        #    dest='log',
        #    help='Specify log directory',
        #    metavar='DIRECTORY',
        #    required=False)

        #    arg_parser.add_argument('-b',
        #                     '--backup-directory',
        #                     action='store',
        #                     dest='backup',
        #                     help='Specify backup directory for csv file',
        #                     metavar='DIRECTORY',
        #                     required=False)

        # Do the parsing
        args = arg_parser.parse_args()

        # With the argument version specified the method execution stops
        if args.version is True:
            return args

        # Analyze missing arguments
        if args.input_csv is None:
            print('-c or --csv option is not specified')
            exit(-1)
        if args.update_csv:
            if args.ip_address is None:
                print(
                    '-p or --ip-address option must be specified for CSV file update'
                )
                exit(-1)
        if args.download:
            if args.ip_address is None or args.number is None:
                if args.ip_address is None:
                    print(
                        '-p or --ip-address option must be specified for dataset download'
                    )
                if args.number is None:
                    print(
                        '-n or --number option must be specified for dataset download'
                    )
                exit(-1)
        if args.migration:
            if args.copybook_directory is None:
                print(
                    '-C or --copybook-directory option must be specified for dataset migration'
                )
                exit(-1)

        # Analyze CSV file extension
        if args.input_csv:
            extension = args.input_csv.split('.')[1]
            if extension != 'csv':
                print(
                    'Invalid CSV file. Please specify a file with a .csv extension'
                )
                exit(-1)
        # Analyze Listcat file extension
        if args.listcat_result:
            if os.path.isdir(args.listcat_result):
                print('Listcat directory specified.')
            else:
                print('Listcat file specified.')
                extension = args.listcat_result.split('.')[1]
                if extension != 'txt':
                    print(
                        'Invalid Listcat file. Please specify a file with a .txt extension'
                    )
                    exit(-1)

        # Analyze if migration flag has a valid value
        if args.migration:
            if args.migration not in ('C', 'G'):
                print(
                    'Invalid migration option value. Please see the help below for valid values'
                )
                arg_parser.print_help()
                exit(-1)

        # Check that number is above 0
        if args.number:
            if args.number <= 0:
                print('Invalid -n, --number option. Must be positive')
                exit(-1)

        # Check that the ip address respect valid format
        if args.ip_address:
            status = self._evaluate_ip_address(args.ip_address)
            if status is False:
                print(
                    'Invalid -p, --ip-address option. The IP address specified must respect either IPv4 or IPv6 standard format'
                )
                exit(-1)

        # Check that the working directory is accessible
        if args.work_directory:
            try:
                os.chdir(args.work_directory)
            except:
                print(
                    'Invalid -w, --working-directory option. Directory specified not accessible'
                )
                exit(-1)

        # Analyze if log level has a valid value
        if args.log_level:
            if args.log_level not in ('CRITICAL', 'DEBUG', 'ERROR', 'INFO',
                                      'WARNING'):
                print(
                    'Invalid -L, --log-level option. Please see the help below for valid values'
                )
                arg_parser.print_help()
                exit(-1)

        return args

    def _evaluate_ip_address(self, ip_address):
        """Checking the format of the ip address used as a parameter.

        This method is able to detect both IPv4 and IPv6 addresses. It is a really simple pattern analysis.

        Args:
            ip_address: A string, the ip address used as as a parameter.

        Returns:
            A boolean, if the ip address used as input is a fully qualified ip address or not.
        """
        is_valid_ip = False

        # IPv4 pattern detection
        if ip_address.count('.') == 3:
            fields = ip_address.split('.')
            is_IPv4 = False
            for field in fields:
                if str(int(field)) == field and 0 <= int(field) <= 255:
                    is_IPv4 = True
                else:
                    is_IPv4 = False
                    break
            is_valid_ip = is_IPv4
        # IPv6 pattern detection
        if ip_address.count(':') == 7:
            fields = ip_address.split(':')
            is_IPv6 = False
            for field in fields:
                if len(field) > 4:
                    is_IPv6 = False
                    break
                if int(field, 16) >= 0 and field[0] != '-':
                    is_IPv6 = True
                else:
                    is_IPv6 = False
                    break
            is_valid_ip = is_IPv6

        return is_valid_ip

    def run(self):
        """Perform to execute jobs of OFTools DSMigin.

        Returns:
            An integer, the general return code of the program.
        """
        rc = 0
        # Parse command-line options
        args = self._parse_arg()

        # Handle version option
        if args.version is True:
            version = 'oftools-dsmigin ' + __version__
            print(version)
            return rc

        # Initialize execution context
        Context().set_input_csv(args.input_csv)
        Context().set_migration_type(args.migration)
        Context().set_encoding_code('US')
        Context().set_number(args.number)
        Context().set_ip_address(args.ip_address)
        Context().set_listcat_result(args.listcat_result)
        Context().set_tag(args.tag)
        Context().set_today_date()
        Context().set_work_directory(args.work_directory)
        Context().set_dataset_directory()
        Context().set_conversion_directory()
        Context().set_copybook_directory(args.copybook_directory)
        Context().set_log_directory()

        # Set log level
        Log().set_level(args.log)

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
            exit(-1)

        # Run jobs
        for job in jobs:
            job.run()

        return rc