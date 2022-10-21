#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module to log all the events of the program execution.

Typical usage example:
  Log().open_stream()
  Log().set_level(args.log_level)
  Log().close_stream()
"""

# Generic/Built-in modules
import logging
import sys

# Third-party modules

# Owned modules


class SingletonType(type):
    """This pattern restricts the instantiation of a class to one object.

    It is a type of creational pattern and involves only one class to create
    methods and specified objects. It provides a global point of access to the
    instance created.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Log(metaclass=SingletonType):
    """A class used to log all the events of the program execution.

    Attributes:
        _level_dict {dictionary} -- Associate a string and its corresponding
            log level from logging module.
        _level {string} -- Log level for the current program execution.
        _logger {getLogger} -- Logger to log all the events of the program
            execution.
        _formatter {Formatter} -- Formatter used to properly format log
            messages.
        _custom_formatter {Formatter} -- Formatter used to add color to log
            messages.
        _file_handler {FileHandler} -- Handler used to write log messages to
            the log file.
        _stream_handler_out {StreamHandler} -- Handler used to write log
            messages to stdout.
        _stream_handler_err {StreamHandler} -- Handler used to write log
            messages to stderr.

    Methods:
        __init__() -- Initializes the class with all the attributes.
        set_level(level) -- Changes log level based on user input.
        open_stream() -- Opens the stream handlers to write log messages to
            stdout.
        close_stream() -- Closes the stream handlers at the end of the program
            execution.
        open_file(path_to_file) -- Opens the file handler to write log messages
            to the log file.
        close_file() -- Closes the file handler at the end of the program.
    """

    def __init__(self):
        """Initializes the class with all the attributes.
        """
        self._level_dict = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self._level = ""

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(self._level_dict["INFO"])

        fmt = "%(asctime)-8s [%(levelname)-8s] %(message)s"
        self._formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
        self._custom_formatter = CustomFormatter(fmt, datefmt="%H:%M:%S")

        self._file_handler = None
        self._stream_handler_out = None
        self._stream_handler_err = None

    @property
    def logger(self):
        """Getter method for the attribute _logger.
        """
        return self._logger

    @property
    def level(self):
        """Getter method for the attribute _level
        """
        return self._level

    def set_level(self, level):
        """Changes log level based on user input.

        Arguments:
            level {string} -- User input for log level.
        """
        if level == "DEBUG":
            fmt = "%(asctime)-8s [%(levelname)-8s] %(message)s (%(module)s:%(lineno)s)"
            self._formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")

        self._level = level
        self._logger.setLevel(self._level_dict[level])

    def open_stream(self):
        """Opens the stream handlers to write log messages to stdout and stderr.
        """
        if self._stream_handler_out is None and \
                self._stream_handler_err is None:

            self._stream_handler_out = logging.StreamHandler(stream=sys.stdout)
            self._stream_handler_out.setFormatter(self._custom_formatter)
            self._stream_handler_out.setLevel(self._level_dict["DEBUG"])
            self._stream_handler_out.addFilter(LogFilter())
            self._logger.addHandler(self._stream_handler_out)

            self._stream_handler_err = logging.StreamHandler(stream=sys.stderr)
            self._stream_handler_err.setFormatter(self._custom_formatter)
            self._stream_handler_err.setLevel(self._level_dict["ERROR"])
            self._logger.addHandler(self._stream_handler_err)

    def close_stream(self):
        """Closes the stream handlers at the end of the program execution.
        """
        if self._stream_handler_out is not None and \
                self._stream_handler_err is not None:

            self._logger.removeHandler(self._stream_handler_out)
            self._stream_handler_out.close()
            self._stream_handler_out = None

            self._logger.removeHandler(self._stream_handler_err)
            self._stream_handler_err.close()
            self._stream_handler_err = None

    def open_file(self, file_path):
        """Opens the file handler to write log messages to the log file.

        Arguments:
            file_path {string} -- Absolute path to the current log file.
        """
        try:
            if self._file_handler is None:
                self._file_handler = logging.FileHandler(filename=file_path,
                                                         mode="a",
                                                         encoding="utf-8")
                self._file_handler.setFormatter(self._formatter)
                self._logger.addHandler(self._file_handler)
        except FileNotFoundError:
            pass

    def close_file(self):
        """Closes the file handler at the end of each file processing.
        """
        if self._file_handler is not None:
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()
            self._file_handler = None


class CustomFormatter(logging.Formatter):
    """A class used to override the default logging.Formatter and set colors
    for log messages.
    """

    # DEBUG & INFO
    white = "\x1b[39m"
    # WARNING
    yellow = "\x1b[33m"
    # ERROR & CRITICAL
    red = "\x1b[91m"

    reset = "\x1b[0m"

    def __init__(self, fmt, datefmt):
        """Initializes the class with all the attributes.
        """
        super().__init__()
        self.fmt = fmt
        self._date_fmt = datefmt
        self.FORMATS = {
            logging.DEBUG: self.white + self.fmt + self.reset,
            logging.INFO: self.white + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.red + self.fmt + self.reset
        }

    def format(self, record):
        """Apply the different colors to the log messages.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LogFilter(logging.Filter):
    """A class used to send all log messages below ERROR level (not included)
    to stdout.
    """

    def filter(self, record):
        """Filters the log messages below ERROR level (not included) to stdout.
        """
        return record.levelno in (logging.DEBUG, logging.INFO, logging.WARNING)
