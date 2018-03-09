# -*- coding: UTF-8 -*-
# logging.py
# Noah Rubin
# 03/08/2018

import logging
from os import fspath, path, getpid
from collections import defaultdict

def addProcessScopedHandler(filename, logger=logging.root, mode='a', encoding='UTF-8'):
    '''
    Adds new stream to first ProcessAwareFileHandler encountered in logger.handlers
    '''
    for handler in logger.handlers:
        if isinstance(handler, ProcessAwareFileHandler):
            if handler.get_stream_config() is None:
                handler.set_stream_config(dict(\
                    filename=filename, 
                    mode=mode, 
                    encoding=encoding\
                ))

class ProcessAwareFileHandler(logging.FileHandler):
    '''
    A handler class which writes formatted logging records to disk files,
    but that can be configured to write to different files based on PID
    '''

    def __init__(self, filename, mode='a', encoding='UTF-8', delay=False):
        # Issue #27493: add support for Path objects to be passed in
        filename = fspath(filename)
        logging.Handler.__init__(self)
        self.streams = defaultdict(dict)
        self.set_filename(path.abspath(filename))
        self.set_mode(mode)
        self.set_encoding(encoding)
        if delay:
            self.stream = None
        else:
            self._open()
    def _getpid(self, pid=None):
        '''
        '''
        return str(getpid()) if pid is None else str(pid)
    def _get_stream_attribute(self, attribute, pid):
        '''
        '''
        self.acquire()
        try:
            return self.streams.get(self._getpid(pid), dict()).get(attribute)
        finally:
            self.release()
    def _set_stream_attribute(self, attribute, value, pid):
        '''
        '''
        self.acquire()
        try:
            self.streams[self._getpid(pid)][attribute] = value
        finally:
            self.release()
    def get_filename(self, pid=None):
        '''
        '''
        return self._get_stream_attribute('filename', pid)
    def set_filename(self, filename, pid=None):
        '''
        '''
        assert filename is not None, 'Filename is not of type String'
        self._set_stream_attribute('filename', filename, pid)
    def get_mode(self, pid=None):
        '''
        '''
        return self._get_stream_attribute('mode', pid)
    def set_mode(self, mode='a', pid=None):
        '''
        '''
        self._set_stream_attribute('mode', mode, pid)
    def get_encoding(self, pid=None):
        '''
        '''
        return self._get_stream_attribute('encoding', pid)
    def set_encoding(self, encoding='UTF-8', pid=None):
        '''
        '''
        self._set_stream_attribute('encoding', encoding, pid)
    def get_stream(self, pid=None):
        '''
        '''
        return self._get_stream_attribute('stream', pid)
    def set_stream(self, stream=None, pid=None):
        '''
        '''
        current_PID = self._getpid() if pid is None else pid
        assert stream is not None or (\
            self.get_filename(current_PID) is not None and \
            self.get_mode(current_PID) is not None\
        ), 'Stream is not file-like object'
        if stream is None:
            self.set_stream(open(\
                self.get_filename(current_PID), 
                self.get_mode(current_PID), 
                encoding=self.get_encoding(current_PID)\
            ), current_PID)
        else:
            self._set_stream_attribute('stream', stream, pid)
    def get_stream_config(self, pid=None):
        '''
        '''
        return self.streams.get(self._getpid(pid), None)
    def set_stream_config(self, stream_config, pid=None):
        '''
        '''
        assert stream_config is not None, 'Stream_config is not dict-like object'
        if 'filename' in stream_config and 'mode' in stream_config:
            for attribute in ['filename', 'mode', 'encoding', 'stream']:
                if attribute in stream_config:
                    getattr(self, 'set_' + attribute)(stream_config.get(attribute), pid)
    def close(self):
        '''
        Closes all streams in self.streams
        '''
        self.acquire()
        try:
            try:
                exception = None
                for key in self.streams:
                    try:
                        self.get_stream(key).flush()
                    except Exception as e:
                        exception = e
                    finally:
                        current_stream = self.get_stream(key)
                        self.set_stream(None, key)
                        if hasattr(current_stream, 'close'):
                            current_stream.close()
                if exception is not None:
                    raise exception
            finally:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay is set
                logging.StreamHandler.close(self)
        finally:
            self.release()
    def _open(self, pid=None):
        current_PID = self._getpid(pid)
        if current_PID in self.streams and \
                self.get_stream(current_PID) is None and \
                (self.get_filename(current_PID) is not None and\
                 self.get_mode(current_PID) is not None):
            self.set_stream(pid=current_PID)
    def emit(self, record):
        '''
        '''
        self._open()
        self.stream = self.get_stream()
        logging.StreamHandler.emit(self, record)
