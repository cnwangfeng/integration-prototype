"""The master controller states and actions

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 5 events; "online", "offline", "shutdown, "cap", "configure done", and 
"unconfigure done".  "cap", "online", "offline" and "shutdown are external 
and the others are generated internally.
"""
__author__ = 'David Terrett'

import sys

from sip_common import logger
from sip_common.state_machine import StateMachine
from sip_common.state_machine import State
from sip_common.state_machine import _End

from sip_master.capability import Capability
from sip_master.configure import Configure
from sip_master.un_configure import UnConfigure
from sip_master.shutdown import Shutdown

class Standby(State):
    """ Standby state
    """
    def __init__(self, sm):
        logger.info('state->standby')

class Configuring(State):
    """ Configuring state
    """
    def __init__(self, sm):
        logger.info('state->configuring')

class UnConfiguring(State):
    """ Unconfiguring state
    """
    def __init__(self, sm):
        logger.info('state->unconfiguring')

class Available(State):
    """ Available state
    """
    def __init__(self, sm):
        logger.info('state->available')

class Degraded(State):
    """ Degraded state
    """
    def __init__(self, sm):
        logger.info('state->degraded')

class Unavailable(State):
    """ Unavailable state
    """
    def __init__(self, sm):
        logger.info('state->unavailable')

class MasterControllerSM(StateMachine):
    def __init__(self):
        super(MasterControllerSM, self).__init__(self.state_table, Standby)

    def online(self, event):
        """Action routine that starts configuring the controller
        """

        # Start a configure thread
        Configure().start()

    def cap(self, event, *args):
        """ Action routine that starts a capability
        """
        Capability(*args).start()

    def offline(self, event):
        """Action routine that starts un-configuring the controller
        """
        # Start an un-configure thread
        UnConfigure().start()

    def shutdown(self, event):
        """Action routine that shuts down the controller
        """
        # Start a shutdown thread
        Shutdown().start()

    state_table = {
        'Standby': {
            'all services':     (1, Available, None),
            'offline':          (0, None, None),
            'online':           (1, Configuring, online),
            'shutdown':         (1, _End, shutdown)
        },
        'Configuring': {
            'all services':     (1, Available, None),
            'offline':          (1, UnConfiguring, offline),
            'online':           (0, None, None),
            'shutdown':         (0, None, None)
        },
        'Available': {
            'no tasks':         (1, Standby, None),
            'some services':    (1, Unavailable, None),
            'offline':          (1, UnConfiguring, offline),
            'online':           (0, None, None),
            'cap':              (1, None, cap),
            'shutdown':         (0, None, None),
            'degrade':          (1, Degraded, None)
        },
        'Degraded': {
            'no tasks':         (1, Standby, None),
            'some services':    (1, Unavailable, None),
            'all services':     (1, Available, None),
            'offline':          (1, UnConfiguring, offline),
            'online':           (0, None, None),
            'shutdown':         (0, None, None)
        },
        'Unavailable': {
            'no tasks':         (1, Standby, None),
            'all services':     (1, Available, None),
            'offline':          (1, UnConfiguring, offline),
            'online':           (0, None, None),
            'shutdown':         (0, None, None)
        },
        'UnConfiguring': {
            'no tasks':         (1, Standby, None),
            'offline':          (0, None, None),
            'online':           (0, None, None),
            'shutdown':         (0, None, None)
        }
}
