"""
AIMsgTypes module:
Contains AI specific network message types
"""

from otp.distributed.OtpDoGlobals import *
from direct.showbase.PythonUtil import invertDictLossless

# top level object (root):
OTP_SERVER_ROOT_DO_ID =         4007

CHANNEL_CLIENT_BROADCAST =      4014

BAD_CHANNEL_ID =                0 # 0xffffffffffffffff # -1
BAD_ZONE_ID =                   0 # 0xffffffff # -1
BAD_DO_ID =                     0 # 0xffffffff # -1

# Control Transactions
CONTROL_MESSAGE =               4001
CONTROL_SET_CHANNEL =           2001
CONTROL_REMOVE_CHANNEL =        2002

CONTROL_SET_CON_NAME =          2004
CONTROL_SET_CON_URL =           2005

CONTROL_ADD_RANGE   =         2008
CONTROL_REMOVE_RANGE  =       2009
CONTROL_ADD_POST_REMOVE   =   2010 # ADD A MESSAGE TO THE CLOSING EVENT ON A DIRECTOR SOCKET
CONTROL_CLEAR_POST_REMOVE =   2011 # CLEAR ALL THE EVENTS..

AIMsgName2Id = {
    # State Server Transactions
    'STATESERVER_OBJECT_GENERATE_WITH_REQUIRED':                2001,
    'STATESERVER_OBJECT_GENERATE_WITH_REQUIRED_OTHER':          2003,
    'STATESERVER_OBJECT_UPDATE_FIELD':                          2004,
    'STATESERVER_OBJECT_UPDATE_FIELD_MULTIPLE':                 2005,
    'STATESERVER_OBJECT_DELETE_RAM':                            2007,
    'STATESERVER_OBJECT_SET_ZONE':                              2008,
    'STATESERVER_OBJECT_CHANGE_ZONE':                           2009,
    'STATESERVER_OBJECT_NOTFOUND':                              2015,

    'STATESERVER_QUERY_OBJECT_ALL':                             2020,
    'STATESERVER_QUERY_ZONE_OBJECT_ALL':                        2021,
    'STATESERVER_OBJECT_LOCATE':                                2022,
    'STATESERVER_OBJECT_LOCATE_RESP':                           2023,
    'STATESERVER_OBJECT_QUERY_FIELD':                           2024, # See 2062
    'STATESERVER_QUERY_OBJECT_ALL_RESP':                        2030,

    'STATESERVER_SHARD_REST':                                   2061,
    'STATESERVER_ADD_AI_RECV':                                  2045,
    'STATESERVER_QUERY_ZONE_OBJECT_ALL_DONE':                   2046,
    'STATESERVER_OBJECT_CREATE_WITH_REQUIRED_CONTEXT':          2050,
    'STATESERVER_OBJECT_CREATE_WITH_REQUIR_OTHER_CONTEXT':      2051,
    'STATESERVER_OBJECT_CREATE_WITH_REQUIRED_CONTEXT_RESP':     2052,
    'STATESERVER_OBJECT_CREATE_WITH_REQUIR_OTHER_CONTEXT_RESP': 2053,
    'STATESERVER_OBJECT_DELETE_DISK':                           2060,
    'STATESERVER_OBJECT_QUERY_FIELD_RESP':                      2062, # See 2024

    'STATESERVER_OBJECT_ENTERZONE_WITH_REQUIRED_OTHER':         2066,
    'STATESERVER_OBJECT_ENTER_AI_RECV':                         2067,
    'STATESERVER_OBJECT_LEAVING_AI_INTEREST':                   2033, # This is the new name for 2033

    'STATESERVER_OBJECT_ENTER_OWNER_RECV':                      2068, # new obj with owner
    'STATESERVER_OBJECT_CHANGE_OWNER_RECV':                     2069, # obj has new owner
    'STATESERVER_OBJECT_SET_OWNER_RECV':                        2070, # ???

    'STATESERVER_OBJECT_QUERY_FIELDS':                          2080,
    'STATESERVER_OBJECT_QUERY_FIELDS_RESP':                     2081,
    'STATESERVER_OBJECT_QUERY_FIELDS_STRING':                   2082,
    'STATESERVER_OBJECT_QUERY_MANAGING_AI':                     2083, # Should not be received by python code (it's for roger's server) 
    'STATESERVER_BOUNCE_MESSAGE':                               2086,

    'STATESERVER_QUERY_OBJECT_CHILDREN_LOCAL':                  2087,
    'STATESERVER_QUERY_OBJECT_CHILDREN_LOCAL_DONE':             2089,
    'STATESERVER_QUERY_OBJECT_CHILDREN_RESP':                   2087,                        

    'ACCOUNT_AVATAR_USAGE':                  3005, # Avatar online or offline
    'ACCOUNT_ACCOUNT_USAGE':                 3006, # Account login or log off

    'CLIENT_AGENT_OPEN_CHANNEL':             3104,
    'CLIENT_AGENT_CLOSE_CHANNEL':            3105,
    'CLIENT_AGENT_SET_INTEREST':             3106,
    'CLIENT_AGENT_REMOVE_INTEREST':          3107,


    'CHANNEL_PUPPET_ACTION':                 4004, # Account and Avatar online or offline

    # direct-to-database-server transactions
    'DBSERVER_MAKE_FRIENDS':                                 1017,
    'DBSERVER_MAKE_FRIENDS_RESP':                            1031,
    'DBSERVER_REQUEST_SECRET':                               1025,
    'DBSERVER_REQUEST_SECRET_RESP':                          1026,
    'DBSERVER_SUBMIT_SECRET':                                1027,
    'DBSERVER_SUBMIT_SECRET_RESP':                           1028,

    'DBSERVER_CREATE_STORED_OBJECT':                         1003,
    'DBSERVER_CREATE_STORED_OBJECT_RESP':                    1004,
    'DBSERVER_DELETE_STORED_OBJECT':                         1008,

    'DBSERVER_GET_STORED_VALUES':                            1012,
    'DBSERVER_GET_STORED_VALUES_RESP':                       1013,
    'DBSERVER_SET_STORED_VALUES':                            1014,

    'SERVER_PING':                                           5002,
    }

# create id->name table for debugging
AIMsgId2Names = invertDictLossless(AIMsgName2Id)

# put msg names in module scope, assigned to msg value
for name, value in AIMsgName2Id.items():
    exec '%s = %s' % (name, value)
del name, value

# The ID number of the database server.  The above direct-to-dbserver
# transactions are sent to this ID.
DBSERVER_ID = 4003

# District
STATESERVER_UPDATE_SHARD = 2091