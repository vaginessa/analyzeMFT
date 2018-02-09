# -*- coding: UTF-8 -*-
# exceptions.py
# Noah Rubin
# 01/31/2018

class BaseAMFTException(Exception):
    '''
    Base exception for amft module
    '''
    _MESSAGE = None

    def __init__(self, err, **kwargs):
        self._err = err if isinstance(err, str) else str(err)
        self._extra_parameters = kwargs
    def __str__(self):
        if self._MESSAGE is None:
            return self.err
        parameters = {'err': self._err}
        for parameter in self._extra_parameters:
            parameters.update({parameter: self._extra_parameters.get(parameter)})
        return self._MESSAGE%(parameters)
    def __repr__(self):
        if len(self._extra_parameters) > 0:
            extra_parameters = ', '.join(('%s=\'%s\'' if isinstance(value, str) else '%s=%s')%(key, str(value)) for key,value in self._extra_parameters.items())
            return '%(classname)s(\'%(err)s\', %(extra_params)s)'%({\
                'classname':    type(self).__name__, \
                'err':          self._err, \
                'extra_params': extra_parameters})
        else:
            return '%(classname)s(\'%(err)s\')'%({\
                'classname':    type(self).__name__, \
                'err':          self._err})

class PathInitializationError(BaseAMFTException):
    '''
    Exception thrown when unable to add dependencies in lib
    directory to sys.path
    '''
    _MESSAGE = 'Unable to append lib directory to path (%(err)s)'

class FieldBoundDictKeyError(BaseAMFTException):
    '''
    Exception thrown when KeyError raised on DictItem object.
    For example:
        class ThisItem(BaseItem):
            f1 = Field()
            f2 = Field()
            f3 = Field()

        this_item = ThisItem()
        print(this_item['f4'])
    This will raise an error because instances of ThisItem do
    not contain the key 'f4'
    '''
    _MESSAGE = '%(classname)s does not contain the field %(fieldname)s'
