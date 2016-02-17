##
##  python3-patts - Python bindings for libpatts
##  Copyright (C) 2015-2016 Delwink, LLC
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

## @package patts
#  Python API for Delwink's libpatts C library.
#  @date 02/16/2016
#  @author David McMackins II
#  @version 0.3

from sqon.error import SQON_ERRORS
from json import loads
from ctypes import *

__title__ = 'patts'
__version__ = '0.3.0'
__author__ = 'David McMackins II'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright 2015-2016 Delwink, LLC'

## Version of the supported C API
PATTS_VERSION = '1.0'

_PATTS_ERRORS = {
    -60: ('LoadError', 'An error occurred when internally loading JSON-encoded'
                       ' data'),
    -62: (MemoryError, 'An error occurred while allocating memory'),
    -63: ('BufferOverflowError', 'A buffer overflow error occurred while '
                                 'handling the query'),
    -64: ('UnexpectedError', 'An error occurred which was not anticipated'),
    -65: ('TaskUnavailableError', 'Invalid task chosen for clocking in'),
    -73: (KeyError, 'Selected user was not found in the database'),
    -74: (IndexError, 'Selected item was not found in the database or is '
                      'inactive')
}

_ERRORS = SQON_ERRORS.copy()
_ERRORS.update(_PATTS_ERRORS)

_UNKNOWN_ERROR_STRING = '{}'

_PATTS_CONNECTION_TYPES = {
    'mysql': 1
}

_libpatts_so = CDLL('libpatts.so.1')

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

## Explicitly connect to the database.
#
#  This is not absolutely necessary to use, since the other functions will
# automatically connect to the database as needed. Use this as a
# performance enhancement when making queries in rapid succession.
def connect():
    rc = _libpatts_so.patts_connect()
    _check_for_error(rc)

## Close connection to the database.
#
#  Only needed after explicitly connecting to the database.
def close():
    _libpatts_so.patts_close()

## Query the database.
#  @param query_str SQL statement to be run on the database.
#  @param primary_key If expecting a result set, the key by which to organize
# the JSON object returned.
#  @return List of result set if primary_key is None, else a dictionary in
# which the keys are primary_key and the values are the remaining results.
def query(query_str, primary_key=None):
    c_out = c_char_p()
    real_pk_param = \
            None if primary_key == None else primary_key.encode('utf-8')

    rc = _libpatts_so.patts_query(query_str.encode('utf-8'), byref(c_out),
                                  real_pk_param)
    _check_for_error(rc)

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return loads(py_out)

## Get the primary key of a table.
#  @param table Database table for which to get the primary key.
#  @return String representation of the primary key.
def get_primary_key(table):
    c_out = c_char_p()

    rc = _libpatts_so.patts_get_primary_key(table.encode('utf-8'),
                                            byref(c_out))
    _check_for_error(rc)

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return py_out

## Escape a string to be placed in a query.
#  @param input The string to be escaped.
#  @param quote Whether to surround the output in apostrophe characters.
#  @return The escaped string.
def escape_string(input, quote=False):
    c_out = c_char_p()

    rc = _libpatts_so.patts_escape(input.encode('utf-8'), byref(c_out), quote)
    _check_for_error(rc)

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return py_out

_libpatts_so.patts_get_user.restype = c_char_p
## Gets the active username.
#  @param escaped Whether to get an escaped version of the username.
def get_user(escaped=False):
    if escaped:
        return _libpatts_so.patts_get_user_esc().decode('utf-8')

    return _libpatts_so.patts_get_user().decode('utf-8')

## Checks user's admin rights.
def have_admin():
    return _libpatts_so.patts_have_admin() == 1

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

    rc = _libpatts_so.patts_setup(
        _PATTS_CONNECTION_TYPES[type],
        host.encode('utf-8'),
        user.encode('utf-8'),
        real_passwd,
        real_db,
        port.encode('utf-8')
    )
    _check_for_error(rc)

## Upgrades an existing PATTS database.
#  @param type A string representation of the database type; currently
# supported: 'mysql' (default).
#  @param host The hostname or IP address of the database server.
#  @param user Username with which to log into the server.
#  @param passwd Password by which to authenticate with the server (default is
# no password).
#  @param database The name of the PATTS database to be upgraded.
#  @param port String representation of the port number.
def upgrade_db(type='mysql', host='localhost', user='root', passwd=None,
               database=None, port='0'):
    real_passwd = None if None == passwd else passwd.encode('utf-8')
    real_db = None if None == database else database.encode('utf-8')

    rc = _libpatts_so.patts_upgrade_db(
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

## Creates a new user on the database and applies proper permissions for a new
# user.
#  @param id A username for the new user.
#  @param host The hostname (or wildcard string) from which this user will be
# allowed to connect.
#  @param passwd A password for the new user.
def create_user(id, host, passwd):
    rc = _libpatts_so.patts_create_user(id.encode('utf-8'),
                                        host.encode('utf-8'),
                                        passwd.encode('utf-8'))
    _check_for_error(rc)

## Creates a new PATTS task type.
#  @param parent_id The ID number of the parent type ('0' if top-level).
#  @param display_name The display name of the new type.
def create_task(parent_id, display_name):
    rc = _libpatts_so.patts_create_task(parent_id.encode('utf-8'),
                                        display_name.encode('utf-8'))
    _check_for_error(rc)

## Deactivates a user in the database.
#  @param id The username of the user to be deactivated.
def delete_user(id):
    rc = _libpatts_so.patts_delete_user(id.encode('utf-8'))
    _check_for_error(rc)

## Deactivates a task type.
#  @param id String representation of the ID number of the task to be
# deactivated.
def delete_task(id):
    rc = _libpatts_so.patts_delete_task(id.encode('utf-8'))
    _check_for_error(rc)

## Grants admin permissions to a PATTS user.
#  @param id Username of the new admin user.
#  @param host Hostname for which to grant user privileges.
def grant_admin(id, host):
    rc = _libpatts_so.patts_grant_admin(id.encode('utf-8'),
                                        host.encode('utf-8'))
    _check_for_error(rc)

## Revokes admin permissions from a PATTS user.
#  @param id Username of the admin user to be demoted.
#  @param host Hostname for which to deny the user privileges.
def revoke_admin (id, host):
    rc = _libpatts_so.patts_revoke_admin(id.encode('utf-8'),
                                         host.encode('utf-8'))
    _check_for_error(rc)

def _get(fn):
    c_out = c_char_p()

    rc = fn(byref(c_out))
    _check_for_error(rc)

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return loads(py_out)

def _get_arg(fn, arg):
    c_out = c_char_p()

    rc = fn(byref(c_out), arg.encode('utf-8'))
    _check_for_error(rc)

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return loads(py_out)

## Gets the active task for the current user.
#  @return Dictionary of the task data or None.
def get_active_task():
    return _get(_libpatts_so.patts_get_active_task) or None

## Gets the tree of active tasks for the user.
#  @return A dictionary of the active tasks' type, user, and start time
# organized by ID keys.
def get_tree():
    return _get(_libpatts_so.patts_get_tree)

## Clock into a task.
#  @param type String representation of the typeID of the task.
def clockin(type):
    rc = _libpatts_so.patts_clockin(type.encode('utf-8'))
    _check_for_error(rc)

## Clock out of a task and all its subtasks.
#  @param item String representation of the item ID.
def clockout(item):
    rc = _libpatts_so.patts_clockout(item.encode('utf-8'))
    _check_for_error(rc)

## Gets all PATTS users.
#  @return Dictionary of all the users with username keys.
def get_users():
    return _get(_libpatts_so.patts_get_users)

## Gets a PATTS user by username.
#  @param id Username for which to search.
#  @return Dictionary of the user's data.
def get_user_byid(id):
    return _get_arg(_libpatts_so.patts_get_user_byid, id)[id]

## Gets all PATTS task types.
#  @return Dictionary of task types with ID keys.
def get_types():
    return _get(_libpatts_so.patts_get_types)

## Gets a PATTS task type by its ID number.
#  @param id String representation of the ID number for which to search.
#  @return Dictionary of the type's data.
def get_type_byid(id):
    return _get_arg(_libpatts_so.patts_get_type_byid, id)[id]

## Gets all the child types of a particular PATTS task type.
#  @param parent_id String representation of the ID number of the parent type.
#  @return Dictionary of the child types with ID keys.
def get_child_types(parent_id):
    return _get_arg(_libpatts_so.patts_get_child_types, parent_id)

## Gets all PATTS tasks.
#  @return Dictionary of all tasks with ID keys.
def get_items():
    return _get(_libpatts_so.patts_get_items)

## Gets a PATTS task by ID number.
#  @param id String representation of the ID number for which to search.
#  @return Dictionary of the task's data.
def get_item_byid(id):
    return _get_arg(_libpatts_so.patts_get_item_byid, id)[id]

## Gets the last PATTS task ID number for a given user.
#  @param user_id Username with which to find the task ID (type str).
#  @return String representation of the task ID number or None.
def get_last_item(user_id):
    c_out = c_char_p()

    rc = _libpatts_so.patts_get_last_item(byref(c_out),
                                          user_id.encode('utf-8'))
    _check_for_error(rc)

    if c_out.value == None:
        return None

    py_out = c_out.value.decode('utf-8')
    _libpatts_so.patts_free(c_out)

    return py_out

## Gets all PATTS items for a given user.
#  @param user_id Username for which to search.
#  @return Dictionary of user's tasks with ID keys.
def get_items_byuser(user_id):
    return _get_arg(_libpatts_so.patts_get_items_byuser, user_id)

## Gets all PATTS items for a given user that are on the clock.
#  @param user_id Username for which to search.
#  @return Dictionary of user's active tasks with ID keys.
def get_items_byuser_onclock(user_id):
    return _get_arg(_libpatts_so.patts_get_items_byuser_onclock, user_id)

## Gets all child items for a PATTS task (calculated based on data).
#  @param id ID number of the parent task (type str).
#  @return Dictionary of the child tasks with ID keys.
def get_child_items(id):
    return _get_arg(_libpatts_so.patts_get_child_items, id)

_libpatts_so.patts_get_library_version.restype = c_char_p
## Gets the version of the libpatts C library.
#  @return String representation of the installed libpatts version.
def get_c_library_version():
    return _libpatts_so.patts_get_library_version().decode('utf-8')
