import logging


def use_logger(method):
    def decorator(self, *args, **kwargs):
        oldFormatter = self.xen.fileHandler.formatter
        self.xen.fileHandler.setFormatter(
            logging.Formatter(
                "%(levelname)-10s [%(asctime)s] {0}: {1}: %(message)s".format(self.__class__.__name__,
                                                                                             self.uuid))
        )
        ret = method(self, *args, **kwargs)
        self.xen.fileHandler.setFormatter(oldFormatter)
        return ret

    return decorator