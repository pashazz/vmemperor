import logging
import sys

class Loggable:
    def init_log(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.propagate = False
        self.log.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler("{0}.log".format(self.__class__.__name__))
        formatter = logging.Formatter("%(levelname)-8s [%(asctime)s] %(message)s")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        self.log.addHandler(fileHandler)
        if hasattr(self, 'debug') and self.debug:
            debugHandler = logging.StreamHandler(sys.stderr)
            debugHandler.setLevel(logging.ERROR)
            debugFormatter = logging.Formatter("%(filename)s:%(lineno)d: %(message)s")
            debugHandler.setFormatter(debugFormatter)
            self.log.addHandler(debugHandler)
            # self.log.error("Running in debug mode: all errors are in stderr, for further info check log file")