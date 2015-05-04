##
##  python3-patts - Python bindings for libpatts
##  Copyright (C) 2015 Delwink, LLC
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, version 3 only.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from ctypes import *

__title__ = 'patts'
__version__ = '0.0.0'
__author__ = 'David McMackins II'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright 2015 Delwink, LLC'

## Version of the supported C API
PATTS_VERSION = '0.0.0'

## Copyright information for the C API
PATTS_COPYRIGHT = \
"""libpatts - Backend library for PATTS Ain't Time Tracking Software
Copyright (C) 2014-2015 Delwink, LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, version 3 only.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

_ERRORS = {
    # inherited from libsqon
    -12: (MemoryError, 'An error occurred while allocating memory'),
    -13: ('BufferOverflowError', 'A buffer overflow error occurred while '
                                 'handling the query'),
    -14: (NotImplementedError, ''),
    -20: ('ConnectionError', 'There was an error establishing a connection '
                             'with the database'),
    -21: ('NoColumnsInSetError', 'No columns were in the result set'),
    -23: ('NoPrimaryKeyError', 'Requested primary key was not found in '
                               'the table'),
    -24: ('PrimaryKeyNotUniqueError', 'Requested primary key was not unique'),

    # actual libpatts error codes
    -60: ('LoadError', 'An error occurred when internally loading JSON-encoded'
                       ' data'),
    -62: (MemoryError, 'An error occurred while allocating memory'),
    -63: ('BufferOverflowError', 'A buffer overflow error occurred while '
                                 'handling the query'),
    -64: ('UnexpectedError', 'An error occurred which was not anticipated'),
    -65: ('TaskUnavailableError', 'Invalid task chosen for clocking in'),
    -73: ('InvalidUserError', 'Selected user was not found in the database')
}
_UNKNOWN_ERROR_STRING = 'Error code {} occurred while processing the request'

_PATTS_CONNECTION_TYPES = {
    'mysql': 1
}

_libpatts_so = CDLL('libsqon.so.0')

def _check_for_error(rc):
    if 0 == rc:
        return

    error, message = _ERRORS.get(rc, (Exception,
                                      _UNKNOWN_ERROR_STRING.format(rc)))

    if type(error) is str:
        error = type(error, (Exception,), {})
    raise error(message)

## Initialize the connection to the PATTS database.
#  @param type A string representation of the database type; currently
# supported: 'mysql' (default).
#  @param host The hostname or IP address of the database server.
#  @param user Username with which to log into the server.
#  @param passwd Password by which to authenticate with the server (default is
# no password).
#  @param database The name of the PATTS database.
#  @param port String representation of the port number.
def init(type='mysql', host='localhost', user='root', passwd=None,
         database=None, port='0'):
    real_passwd = None if None == passwd else passwd.encode('utf-8')
    real_db = None if None == database else database.encode('utf-8')

    rc = _libpatts_so.patts_init(
        _PATTS_CONNECTION_TYPES[type],
        host.encode('utf-8'),
        user.encode('utf-8'),
        real_passwd,
        real_db,
        port.encode('utf-8')
    )
    _check_for_error(rc)

## Cleans up memory allocated internally by libpatts; call after finished
# using the library before a second call to init().
def cleanup():
    _libpatts_so.patts_cleanup()

## Gets the active username.
def get_user():
    return _libpatts_so.patts_get_user().value.decode('utf-8')

## Checks user's admin rights.
def have_admin():
    return _libpatts_so.patts_have_admin().value

## Checks the database schema version on the remote server.
def get_db_version():
    out = c_uint32()

    rc = _libpatts_so.patts_get_db_version(byref(out))
    _check_for_error(rc)

    return out.value

## Creates and sets up a new PATTS database.
#  @param type A string representation of the database type; currently
# supported: 'mysql' (default).
#  @param host The hostname or IP address of the database server.
#  @param user Username with which to log into the server.
#  @param passwd Password by which to authenticate with the server (default is
# no password).
#  @param database The name of the PATTS database to be created.
#  @param port String representation of the port number.
def setup(type='mysql', host='localhost', user='root', passwd=None,
          database=None, port='0'):
    real_passwd = None if None == passwd else passwd.encode('utf-8')
    real_db = None if None == database else database.encode('utf-8')

    rc = _libsqon_so.patts_setup(
        _PATTS_CONNECTION_TYPES[type],
        host.encode('utf-8'),
        user.encode('utf-8'),
        real_passwd,
        real_db,
        port.encode('utf-8')
    )
    _check_for_error(rc)

## Compares the current database schema to the version supported by this
# interface.
#  @return Positive when update needed, negative when interface is out of date,
# and zero when up-to-date.
def version_check():
    out = c_int64()

    rc = _libpatts_so.patts_version_check(byref(out))
    _check_for_error(rc)

    return out.value

