#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
    """

# Generic/Built-in modules
import argparse
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
# from .Statistics import Statistics
from .Utils import Utils


def main():
    return Main().run()


class Main(object):
    """Main class containing the methods for parsing the command arguments and running OpenFrame Tools 
    Dataset Migration.

        Methods:
            _parse_arg() -- Parsing command-line options.
            _create_jobs(args, csv) -- Creates job depending on the input parameters.
            run() -- Perform to execute jobs of OpenFrame Tools Dataset Migration."""

    def _parse_arg(self):
        """Parses command-line options.

            The program defines what arguments it requires, and argparse will figure out how to parse 
            those out of sys.argv. The argparse module also automatically generates help, usage 
            messages and issues errors when users give the program invalid arguments.

            Returns:
                ArgumentParser object -- Program input arguments."""
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
            metavar='CSV',
            required=True,
            type=str)

        required.add_argument('-w',
                              '--working-directory',
                              action='store',
                              dest='working_directory',
                              help='path to the working directory',
                              metavar='DIRECTORY',
                              required=True,
                              type=str)

        # Jobs arguments
        jobs.add_argument(
            '-l',
            '--listcat',
            action='store_true',
            dest='listcat',
            help=
            'flag to trigger listcat execution, retrieve dataset info from the Mainframe as well as VSAM dataset info from a listcat file',
            required=False)

        jobs.add_argument(
            '-f',
            '--ftp',
            action='store_true',
            dest='ftp',
            help=
            'flag to trigger FTP execution, download datasets from Mainframe',
            required=False)

        jobs.add_argument(
            '-m',
            '--migration',
            action='store_true',
            dest='migration',
            help=
            '''flag to trigger dsmigin, executes dataset conversion and generation in the OpenFrame environment to start dataset migration''',
            required=False)

        # Optional arguments
        optional.add_argument(
            '-C',
            '--conversion',
            action='store_true',
            dest='conversion',
            help=
            'flag to modify the behavior of dsmigin, executes conversion only',
            required=False)

        optional.add_argument(
            '-i',
            '--ip-address',
            action='store',
            dest='ip_address',
            help=
            'ip address required for any command that involves FTP connection to Mainframe (listcat and ftp)',
            metavar='IP_ADDRESS',
            required=False,
            type=str)

        optional.add_argument(
            '--init',
            action='store_true',
            dest='init',
            help='Initializes the CSV file and the working directory specified',
            required=False)

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

        # It is not possible to handle all dataset downloads at once, there is a certain timeout using FTP to download from the Mainframe, it is then necessary to set up a number of datasets to download for the current execution, and download little by little. This also allows to limit CPU load on the Mainframe
        optional.add_argument(
            '-n',
            '--number',
            action='store',
            dest='number',
            help='number of datasets to be downloaded from the Mainframe',
            metavar='NUMBER',
            required=False,
            type=int)

        optional.add_argument('-p',
                              '--prefix',
                              action='store',
                              dest='prefix',
                              help='prefix used for VSAM datasets download',
                              metavar='PREFIX',
                              required=False,
                              type=str)

        optional.add_argument('-t',
                              '--tag',
                              action='store',
                              dest='tag',
                              help='tag for the CSV backup and log file names',
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
            status = Utils().check_file_extension(args.csv, 'csv')
            if status is False:
                raise TypeError()
        except TypeError:
            Log().logger.critical(
                'TypeError: Invalid -c, --csv option: Expected .csv extension')
            sys.exit(-1)

        # Analyze missing optional arguments
        try:
            if args.listcat and args.ip_address is None:
                raise Warning()
        except Warning:
            Log().logger.warning(
                'Warning: Missing -i, --ip-address: Listcat will skip dataset info retrieval from Mainframe and focus only on VSAM dataset info from listcat file'
            )

        try:
            if args.ftp and args.ip_address is None:
                raise SystemError()
        except SystemError:
            Log().logger.critical(
                'MissingArgumentError: -i, --ip-address option must be specified for dataset download from Mainframe'
            )
            sys.exit(-1)

        # Analyze if the argument ip_address respect a valid format
        if args.ip_address:
            try:
                status = Utils().analyze_ip_address(args.ip_address)
                if status is False:
                    raise SystemError()
            except SystemError:
                Log().logger.critical(
                    'FormatError: Invalid -i, --ip-address option: Must respect either IPv4 or IPv6 standard format'
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

        #TODO listcat file is going to have a fixed name, like listcat.txt. MAke sure this file exist before proceeding
        # Analyze if listcat has been properly specified
        #NO EXTENSION
        # if args.listcat:
        #     try:
        #         listcat_path = os.path.expandvars(args.listcat)
        #         if os.path.isdir(listcat_path):
        #             Log().logger.debug('Listcat directory specified.')
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

    def _create_jobs(self, args, storage_resource):
        """Creates job depending on the input parameters.

            Arguments:
                args {ArgParse object} -- Contains all the input parameters of the program.
                storage_resource {Storage Resource object} -- Could be a CSV file or a database object, used to store dataset records.

            Raises:
                #TODO Complete docstrings, maybe change the behavior to print traceback only with DEBUG as log level

            Returns:
                list -- List of jobs."""
        jobs = []
        job_factory = JobFactory(storage_resource)

        try:
            if args.listcat:
                Context().ip_address = args.ip_address
                job = job_factory.create('listcat')
                jobs.append(job)
            if args.ftp:
                Context().ip_address = args.ip_address
                Context().prefix = args.prefix
                job = job_factory.create('ftp')
                jobs.append(job)
            if args.migration:
                Context().encoding_code = 'US'
                Context().conversion = args.conversion
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
                integer -- General return code of the program."""
        # For testing purposes. allow to remove logs when executing coverage
        # logging.disable(logging.CRITICAL)
        Log().open_stream()

        # Parse command-line options
        args = self._parse_arg()

        # Set log level
        Log().set_level(args.log_level)

        # Variables initialization for program execution
        rc = 0
        number_dataset = 0
        Context().tag = args.tag
        Context().initialization = args.init
        Context().number_datasets = args.number
        Context().working_directory = args.working_directory

        # Initialize log file
        log_file_name = 'oftools_dsmigin' + Context().tag + '_' + Context(
        ).full_timestamp + '.log'
        log_file_path = Context().log_directory + '/' + log_file_name
        Log().open_file(log_file_path)

        # CSV file initialization
        storage_resource = CSV(args.csv)

        # statistics = Statistics()

        # Create jobs
        jobs = self._create_jobs(args, storage_resource)

        try:
            for i in range(len(Context().records)):
                record = Context().records[i].columns

                # Run jobs
                for job in jobs:
                    rc = job.run(record)
                    if rc != 0:
                        # Skipping dataset
                        if rc == 1:
                            continue
                        else:
                            Log().logger.error(
                                'An error occurred. Aborting program execution')
                            break

                if rc == 0:
                    number_dataset += 1

                    if Context().number_datasets != 0:
                        Log().logger.info('Current dataset count: ' +
                                          str(number_dataset) + '/' +
                                          str(Context().number_datasets))
                        if number_dataset >= Context().number_datasets:
                            Log().logger.info('Limit of dataset reached')
                            Log().logger.info('Terminating program execution')
                            break
                    else:
                        Log().logger.info('Current dataset count: ' +
                                          str(number_dataset))
        except KeyboardInterrupt:
            storage_resource.write()
            raise KeyboardInterrupt()

        # rc = statistics.run()
        # if rc < 0:
        #     Log().logger.error(
        #         'An error occurred. Aborting statistics processing')

        # Need to clear context completely and close log at the end of the execution
        Context().clear_all()
        Log().close_file()
        Log().close_stream()

        return rc