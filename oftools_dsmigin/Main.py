#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main module of OpenFrame Tools Dataset Migration.
"""

# Generic/Built-in modules
# import argcomplete
import argparse
import signal
import sys
import traceback
# import logging

# Third-party modules

# Owned modules
from . import __version__
from .Context import Context
from .CSV import CSV
from .enums.MessageEnum import ErrorM, LogM
from .handlers.FileHandler import FileHandler
from .jobs.JobFactory import JobFactory
from .Listcat import Listcat
from .Log import Log
# from .Statistics import Statistics

# Global variables
INTERRUPT = False


def main():
    return Main().run()


class Main(object):
    """Main class containing the methods for parsing the command arguments and running OpenFrame Tools Dataset Migration.

    Methods:
        _parse_arg() -- Parses command-line options.
        _signal_handler(signum, frame) -- Handles signal SIGQUIT for the program execution.
        _create_jobs(args, csv) -- Creates job depending on the input parameters.
        run() -- Perform all the steps to execute jobs of oftools_dsmigin.
    """

    @staticmethod
    def _parse_arg():
        """Parses command-line options.

        The program defines what arguments it requires, and argparse will figure out how to parse 
        those out of sys.argv. The argparse module also automatically generates help, usage 
        messages and issues errors when users give the program invalid arguments.

        Returns:
            args {ArgumentParser} -- Program input arguments.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            description='OpenFrame Tools Dataset Migration',
            formatter_class=argparse.RawTextHelpFormatter)

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
            'CSV file name, contains the datasets list and their parameters',
            metavar='FILE',
            required=True,
            type=str)

        required.add_argument('-w',
                              '--working-directory',
                              action='store',
                              dest='working_directory',
                              help='working directory name',
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
            'flag used to trigger listcat execution, retrieve dataset info from Mainframe as well as VSAM dataset info from a listcat file',
            required=False)

        jobs.add_argument(
            '-F',
            '--ftp',
            action='store_true',
            dest='ftp',
            help=
            'flag used to trigger FTP execution, download datasets from Mainframe',
            required=False)

        jobs.add_argument(
            '-M',
            '--migration',
            action='store_true',
            dest='migration',
            help=
            'flag used to trigger dsmigin, execute dataset conversion and generation in the OpenFrame environment',
            required=False)

        # Optional arguments
        optional.add_argument('--clear',
                              action='store_true',
                              dest='clear',
                              help=argparse.SUPPRESS,
                              required=False)

        optional.add_argument(
            '-d',
            '--dsn',
            action='store',  # optional because default action is 'store'
            dest='dsn',
            help=
            'colon-separated list of datasets to automatically add them to the CSV file',
            metavar='FILE',
            required=False,
            type=str)

        optional.add_argument(
            '-C',
            '--conversion',
            action='store_true',
            dest='conversion',
            help='flag used to execute conversion only in dataset migration',
            required=False)

        optional.add_argument(
            '-e',
            '--encoding-code',
            action='store',
            choices=['US'],
            default='US',
            dest='encoding_code',
            help=
            'encoding code for dataset migration, potential values:\n- US (default)',
            metavar='CODE',
            required=False,
            type=str)

        optional.add_argument(
            '--enable-column',
            action='store',
            dest='enable_column',
            help=
            'enable CSV columns instead of the default value, colon-separated. Supported columns:\n- CATALOG (default is SYS1.MASTER.ICFCAT)\n- VOLSER (default is DEFVOL)',
            metavar='COLUMN',
            required=False,
            type=str)

        optional.add_argument('-f',
                              '--force',
                              action='store_true',
                              dest='force',
                              help='flag used to force dataset migration',
                              required=False)

        optional.add_argument(
            '-g',
            '--generations',
            action='store',
            dest='generations',
            help=
            'number of generations to be processed specifically for GDG datasets',
            metavar='GENERATIONS',
            required=False,
            type=int)

        optional.add_argument(
            '-i',
            '--ip-address',
            action='store',
            dest='ip_address',
            help=
            'ip address required for any command that involves a connection to Mainframe (listcat and ftp)',
            metavar='ADDRESS',
            required=False,
            type=str)

        optional.add_argument(
            '--init',
            action='store_true',
            dest='init',
            help=
            'flag used to initialize the CSV file and the working directory specified',
            required=False)

        optional.add_argument(
            '--listcat-gen',
            action='store',
            dest='listcat_gen',
            help=
            'text file name to append datasets record to a CSV file for listcat information',
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
            'log level, potential values:\n- DEBUG\n- INFO (default)\n- WARNING\n- ERROR\n- CRITICAL',
            metavar='LEVEL',
            required=False,
            type=str)

        # It is not possible to handle all dataset downloads at once, there is a certain timeout using FTP to download from the Mainframe, it is then necessary to set up a number of datasets to download for the current execution, and download little by little. This also allows to limit CPU load on the Mainframe
        optional.add_argument('-n',
                              '--number',
                              action='store',
                              dest='number',
                              help='number of datasets to be processed',
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

        optional.add_argument(
            '-t',
            '--tag',
            action='store',
            dest='tag',
            help='add a tag to the name of the CSV backup and the log file',
            metavar='TAG',
            required=False,
            type=str)

        optional.add_argument(
            '-T',
            '--test',
            action='store_true',
            dest='test',
            help=
            'flag used to modify the behavior of dsmigin, executes conversion only and delete the created file',
            required=False)

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
        except argparse.ArgumentError as error:
            Log().logger.critical(ErrorM.ARGUMENT.value % error)
            Log().logger.critical(ErrorM.ABORT.value)
            sys.exit(-1)

        # Analyze CSV file, making sure a file with .csv extension is specified
        is_valid_ext = FileHandler().check_extension(args.csv, 'csv')
        if is_valid_ext is False:
            Log().logger.critical(ErrorM.ABORT.value)
            sys.exit(-1)

        # Analyze optional arguments dependencies
        try:
            if args.listcat and args.ip_address is None:
                raise Warning()
        except Warning:
            Log().logger.warning(ErrorM.MISSING_IP_WARNING.value)

        try:
            if args.ftp and args.ip_address is None:
                raise SystemError()
        except SystemError:
            Log().logger.critical(ErrorM.MISSING_IP_ERROR.value)
            sys.exit(-1)

        return args

    @staticmethod
    def _signal_handler(signum, frame):
        """Handles signal SIGQUIT for the program execution.
        """
        global INTERRUPT
        INTERRUPT = True
        raise KeyboardInterrupt()

    @staticmethod
    def _create_jobs(args, storage_resource):
        """Creates job depending on the input parameters.

        Arguments:
            args {ArgParse} -- Contains all the input parameters of the program.
            storage_resource {Storage Resource} -- Could be a CSV file or a database object, used to store dataset records.

        Returns:
            list[Job] -- List of Jobs.

        Raises:
            #TODO Complete docstring, maybe change the behavior to print traceback only with DEBUG as log level
        """
        jobs = []
        job_factory = JobFactory(storage_resource)

        try:
            if args.listcat:
                listcat = Listcat(args.listcat_gen)
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
                Context().conversion = args.conversion
                Context().enable_column_list = args.enable_column
                Context().encoding_code = args.encoding_code
                Context().force = args.force
                Context().test = args.test
                job = job_factory.create('migration')
                jobs.append(job)
        except:
            traceback.print_exc()
            Log().logger.critical(ErrorM.JOB.value)
            Log().logger.critical(ErrorM.ABORT.value)
            sys.exit(-1)
        else:
            return jobs

    def run(self):
        """Performs all the steps to execute jobs of oftools_dsmigin.

        Returns:
            integer -- General return code of the program.
            
        Raises:
            KeyboardInterrupt -- Exception raised if the user press Ctrl + C.
        """
        rc = 0
        # Normal if there is an error on Windows, SIGQUIT only exist on Unix
        signal.signal(signal.SIGQUIT, self._signal_handler)

        # For testing purposes. allow to remove logs when executing coverage
        # logging.disable(logging.CRITICAL)
        Log().open_stream()
        Log().set_level(args.log_level)
        Log().logger.debug(' '.join((arg for arg in sys.argv)))

        # Parse command-line options
        args = self._parse_arg()

        # Initialize variables for program execution
        Context().init = args.init
        Context().number = args.number
        Context().tag = args.tag
        Context().working_directory = args.working_directory
        count_dataset = 0

        try:
            # Initialize log file
            log_file_name = 'oftools_dsmigin' + Context().tag + '_' + Context(
            ).full_timestamp + '.log'
            log_file_path = Context().log_directory + '/' + log_file_name
            Log().open_file(log_file_path)

            # CSV file initialization
            storage_resource = CSV(args.csv)

            # Adding manual dataset input to the records
            if args.dsn:
                dataset_names = args.dsn.split(':')
                for dsn in dataset_names:
                    storage_resource.add_record(dsn)

            # Create jobs
            jobs = self._create_jobs(args)

            for index, value in enumerate(Context().records):
                try:
                    # Initialization of variables before running the jobs
                    record = value.columns
                    for job in jobs:
                        rc = job.run(record, index)
                        if rc == 0:
                            storage_resource.write(index)
                        else:
                            if rc == 1:
                                Log().logger.debug(LogM.MAIN_SKIP.value % rc)
                                continue
                            else:
                                Log().logger.error(ErrorM.ABORT.value)
                                break

                    if rc == 0:
                        count_dataset += 1

                        if Context().number != 0:
                            Log().logger.info(LogM.COUNT_MAX.value %
                                              (count_dataset, Context().number))
                            if count_dataset == Context().number:
                                Log().logger.info(LogM.LIMIT.value)
                                Log().logger.info(LogM.TERMINATE.value)
                                break
                        else:
                            Log().logger.info(LogM.COUNT.value % count_dataset)

                except KeyboardInterrupt:
                    #TODO Find what goes here

                    if INTERRUPT is True:
                        raise KeyboardInterrupt()

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

            Context().clear_all()
            Log().close_file()
            Log().close_stream()

        # Need to clear context completely and close log at the end of the execution
        Context().clear_all()
        Log().close_file()
        Log().close_stream()

        return rc