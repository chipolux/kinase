# -*- coding: utf-8 -*-
"""
kinase.exceptions
Kinase Exception Definitions

Created on Fri Dec 20 14:59:13 2013

@author: chipolux
"""

# Base Exception Class
class KinaseException(Exception):
    """An undefined error occured in kinase."""

# SNMP Specific Exceptions
class SNMPException(KinaseException):
    """An undefined SNMP error occured in kinase."""

class IncompleteMessage(SNMPException):
    """SNMP message not completely recieved."""
