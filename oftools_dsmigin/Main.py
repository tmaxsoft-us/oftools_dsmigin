#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
    """

# Generic/Built-in modules
# import argcomplete
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
from .Listcat import Listcat
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
            run() -- Perform to execute jobs of OpenFrame Tools Dataset Migration.
        """

    def _parse_arg(self):
        """Parses command-line options.

            The program defines what arguments it requires, and argparse will figure out how to parse 
            those out of sys.argv. The argparse module also automatically generates help, usage 
            messages and issues errors when users give the program invalid arguments.

            Returns:
                ArgumentParser object -- Program input arguments.
            """
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
            '-L',
            '--listcat',
            action='store_true',
            dest='listcat',
            help=
            'flag to trigger listcat execution, retrieve dataset info from the Mainframe as well as VSAM dataset info from a listcat file',
            required=False)

        jobs.add_argument(
            '-F',
            '--ftp',
            action='store_true',
            dest='ftp',
            help=
            'flag to trigger FTP execution, download datasets from Mainframe',
            required=False)

        jobs.add_argument(
            '-M',
            '--migration',
            action='store_true',
            dest='migration',
            help=
            '''flag to trigger dsmigin, executes dataset conversion and generation in the OpenFrame environment to start dataset migration''',
            required=False)

        # Optional arguments
        optional.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help=argparse.SUPPRESS,
            required=False)

        optional.add_argument(
            '-C',
            '--conversion',
            action='store_true',
            dest='conversion',
            help=
            'flag to modify the behavior of dsmigin, executes conversion only',
            required=False)

        optional.add_argument(
            '-e',
            '--encoding_code',
            action='store',
            choices=['US'],
            default='US',
            dest='encoding_code',
            help=
            'encoding code for dataset migration, potential values: US. (default: US)',
            metavar='CODE',
            required=False,
            type=str)

        optional.add_argument(
            '--enable_column',
            action='store',
            dest='column_names',
            help=
            'list of CSV columns to enable instead of the default value, separated with :. Supported columns: VOLSER, CATALOG',
            metavar='COLUMN',
            required=False,
            type=str)

        optional.add_argument(
            '-g',
            '--generations',
            action='store',
            dest='generations',
            help=
            'number of generations to be processed, specifically for GDG datasets',
            metavar='INTEGER',
            required=False,
            type=int)

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
            help='initializes the CSV file and the working directory specified',
            required=False)

        optional.add_argument(
            '--listcat-gen',
            action='store',
            dest='listcat_gen',
            help=
            'appends datasets record from a text file to a CSV file for listcat information',
            metavar='FILE',
            required=False,
            type=str)

        optional.add_argument(
            '-l',
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
        optional.add_argument('-n',
                              '--number',
                              action='store',
                              dest='number',
                              help='number of datasets to be processed',
                              metavar='INTEGER',
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
            help='show the version message and exit',
            version='%(prog)s {version}'.format(version=__version__))

        # Do the parsing
        if len(sys.argv) == 1:
            parser.print_help(sys.stdout)
            sys.exit(0)
        try:
            # argcomplete.autocomplete(parser)
            args = parser.parse_args()
        except argparse.ArgumentError as e:
            Log().logger.critical('ArgumentError: ' + str(e))
            sys.exit(-1)

        # Analyze CSV file, making sure a file with .csv extension is specified
        try:
            if args.csv:
                status = Utils().check_file_extension(args.csv, 'csv')
                if status is False:
                    raise TypeError()
        except TypeError:
            Log().logger.critical(
                'TypeError: Invalid -c, --csv option: Must be .csv extension')
            sys.exit(-1)

        # Analyze missing optional arguments
        try:
            if args.listcat and args.ip_address is None:
                raise Warning()
        except Warning:
            Log().logger.warning(
                'MissingArgumentWarning: Missing -i, --ip-address option: Skipping dataset information retrieval from Mainframe'
            )

        try:
            if args.ftp and args.ip_address is None:
                raise SystemError()
        except SystemError:
            Log().logger.critical(
                'MissingArgumentError: Missing -i, --ip-address option: Must be specified for dataset download from Mainframe'
            )
            sys.exit(-1)

        return args

    def _create_jobs(self, args, storage_resource):
        """Creates job depending on the input parameters.

            Arguments:
                args {ArgParse object} -- Contains all the input parameters of the program.
                storage_resource {Storage Resource object} -- Could be a CSV file or a database object, used to store dataset records.

            Raises:
                #TODO Complete docstrings, maybe change the behavior to print traceback only with DEBUG as log level

            Returns:
                list -- List of jobs.
            """
        Log().logger.debug('Creating jobs')
        jobs = []
        job_factory = JobFactory(storage_resource)

        try:
            if args.listcat:
                listcat = Listcat(Context().listcat_directory + '/listcat.csv')
                Context().generations = args.generations
                Context().ip_address = args.ip_address
                Context().listcat = listcat
                job = job_factory.create('listcat')
                jobs.append(job)
            if args.ftp:
                Context().ip_address = args.ip_address
                Context().prefix = args.prefix
                job = job_factory.create('ftp')
                jobs.append(job)
            if args.migration:
                columns = args.column_names.split(':')
                for column in columns:
                    Context().append_enable_column(column)
                Context().encoding_code = args.encoding_code
                Context().conversion = args.conversion
                job = job_factory.create('migration')
                jobs.append(job)
        except:
            traceback.print_exc()
            Log().logger.error(
                'Unexpected error detected during the job creation')
            sys.exit(-1)
        else:
            Log().logger.debug('Number of jobs created: ' + str(len(jobs)))
            return jobs

    def run(self):
        """Performs all the steps to execute jobs of oftools_dsmigin.

            Returns:
                integer -- General return code of the program.
                
            Raises:
                KeyboardInterrupt -- Exception is raised if the user press Ctrl + C.
            """
        rc = 0
        # For testing purposes. allow to remove logs when executing coverage
        # logging.disable(logging.CRITICAL)
        Log().open_stream()

        # Parse command-line options
        args = self._parse_arg()

        # Set log level and log oftools_dsmigin command as DEBUG
        Log().set_level(args.log_level)
        Log().logger.debug(' '.join((arg for arg in sys.argv)))
        Log().logger.debug('Starting OpenFrame Tools Dataset Migration')

        # Initialize variables for program execution
        count_dataset = 0
        Context().initialization = args.init
        Context().max_datasets = args.number
        Context().tag = args.tag
        Context().working_directory = args.working_directory

        # Initialize log file
        log_file_name = 'oftools_dsmigin' + Context().tag + '_' + Context(
        ).full_timestamp + '.log'
        log_file_path = Context().log_directory + '/' + log_file_name
        Log().open_file(log_file_path)

        # CSV file initialization
        storage_resource = CSV(args.csv)

        # Listcat CSV file generation
        if args.listcat_gen:
            listcat = Listcat(args.listcat_gen)
            listcat.generate_csv()

        # Create jobs
        jobs = self._create_jobs(args, storage_resource)

        try:
            if len(jobs) > 0:

                for i in range(len(Context().records)):
                    record = Context().records[i].columns

                    for job in jobs:
                        rc = job.run(record)
                        if rc != 0:
                            if rc == 1:
                                Log().logger.debug('Skipping dataset: rc = 1')
                                continue
                            else:
                                Log().logger.error(
                                    'An error occurred. Aborting program execution'
                                )
                                break

                    if rc == 0:
                        count_dataset += 1

                        if Context().max_datasets != 0:
                            Log().logger.info('Current dataset count: ' +
                                              str(count_dataset) + '/' +
                                              str(Context().max_datasets))
                            if count_dataset >= Context().max_datasets:
                                Log().logger.info('Limit of dataset reached')
                                Log().logger.info(
                                    'Terminating program execution')
                                break
                        else:
                            Log().logger.info('Current dataset count: ' +
                                              str(count_dataset))

                # rc = statistics.run()
                # if rc < 0:
                #     Log().logger.error(
                #         'An error occurred. Aborting statistics processing')

                # Handle clear option
                #TODO Code the Clear module
                # if args.clear is True:
                #     clear = Clear()
                #     clear.run()

        except KeyboardInterrupt:
            storage_resource.write()
            storage_resource.format()

            Context().clear_all()
            Log().close_file()
            Log().close_stream()

            raise KeyboardInterrupt()

        # Need to clear context completely and close log at the end of the execution
        storage_resource.format()
        Context().clear_all()
        Log().close_file()
        Log().close_stream()

        return rc