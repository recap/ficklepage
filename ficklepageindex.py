__author__ = 'reggie'

import threading

class PageIndex(object):

    __instance = None

    def __init__(self):
        if PageIndex.__instance is None:
            PageIndex.__instance = PageIndex.__impl()
         # Store instance reference as the only member in the handle
        self.__dict__['_PageIndex__instance'] = PageIndex.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)


    class __impl(object):
        def __init__(self):

            self.servers = {}
            self.rlock = threading.RLock()

            pass


        def add_site(self, key, conn):
            self.rlock.acquire()
            self.servers[key] = conn
            self.rlock.release()

        def has_key(self, key):
            ret = False
            self.rlock.acquire()
            if key in self.servers.keys():
                ret = True
            self.rlock.release()

            return ret

        def get_conn(self, key):
            ret = None
            self.rlock.acquire()
            if key in self.servers.keys():
                ret = self.servers[key]
            self.rlock.release()

            return ret

        def remove_key(self, key):
            self.rlock.acquire()
            if key in self.servers.keys():
                del self.servers[key]
            self.rlock.release()