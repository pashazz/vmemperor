import logging
import sys

class Loggable:


    def init_log(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.propagate = False
        self.log.setLevel(logging.DEBUG)
        if self.log.hasHandlers():
            return

        fileHandler = logging.FileHandler("{0}.log".format(self.__class__.__name__))
        if not hasattr(self, 'log_format'):
            self.log_format = "%(levelname)-10s [%(asctime)s] {0}: %(message)s".format(self.__class__.__name__)
        formatter = logging.Formatter(self.log_format)
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        self.log.addHandler(fileHandler)
        if hasattr(self, 'debug') and self.debug:
            debugHandler = logging.StreamHandler(sys.stderr)
            debugHandler.setLevel(logging.ERROR)
            if not hasattr(self, 'debug_log_format'):
                debug_log_format = "%(filename)s:%(lineno)d: %(message)s"
            debugFormatter = logging.Formatter(debug_log_format)
            debugHandler.setFormatter(debugFormatter)
            self.log.addHandler(debugHandler)
            # self.log.error("Running in debug mode: all errors are in stderr, for further info check log file")