import logging
import sys

class Loggable:


    def init_log(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.propagate = False
        self.log.setLevel(logging.DEBUG)
        if self.log.hasHandlers():
            for handler in self.log.handlers:
                if type(handler) == logging.FileHandler and not hasattr(self, 'fileHandler'):
                    self.fileHandler = handler
            return

        self.fileHandler = logging.FileHandler("{0}.log".format(self.__class__.__name__))
        if not hasattr(self, 'log_format'):
            self.log_format = "%(levelname)-10s [%(asctime)s] {0}: %(message)s".format(self.__class__.__name__)
        self.formatter = logging.Formatter(self.log_format)
        self.fileHandler.setLevel(logging.DEBUG)
        self.fileHandler.setFormatter(self.formatter)
        self.log.addHandler(self.fileHandler)
        if hasattr(self, 'debug') and self.debug:
            debugHandler = logging.StreamHandler(sys.stderr)
            debugHandler.setLevel(logging.ERROR)
            if not hasattr(self, 'debug_log_format'):
                debug_log_format = "%(filename)s:%(lineno)d: %(message)s"
            else:
                debug_log_format = self.debug_log_format

            debugFormatter = logging.Formatter(debug_log_format)
            debugHandler.setFormatter(debugFormatter)
            self.log.addHandler(debugHandler)
            # self.log.error("Running in debug mode: all errors are in stderr, for further info check log file")

    def create_additional_log(self, name):
        log = logging.getLogger(name)
        log.propagate = False
        log.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}.log".format(name))
        log_format = "%(levelname)-10s [%(asctime)s] {0}: %(message)s".format(name)
        formatter = logging.Formatter(log_format)
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        log.addHandler(fileHandler)
        if hasattr(self, 'debug') and self.debug:
            debugHandler = logging.StreamHandler(sys.stderr)
            debugHandler.setLevel(logging.ERROR)
            if not hasattr(self, 'debug_log_format'):
                debug_log_format = "%(filename)s:%(lineno)d: %(message)s"
            debugFormatter = logging.Formatter(debug_log_format)
            debugHandler.setFormatter(debugFormatter)
            log.addHandler(debugHandler)

        return log