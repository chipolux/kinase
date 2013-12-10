# -*- coding: utf-8 -*-
"""
Created on Fri Dec 06 10:40:32 2013

@author: ***REMOVED***
"""
import socket

def community_to_hex(community):
    """Convert community name to hex array."""
    elements = []
    for c in community:
        elements.append(hex(ord(c)))
    return elements

def get_hex_int(hex_string):
    """Parse int out of hex stream."""
    if len(bin(ord(hex_string[0]))[2:]) <= 7:
        return 1, ord(hex_string[0])
    count = (ord(hex_string[0]) - 0x80) + 1
    hex_int = ''.join(['{:02x}'.format(ord(c)) for c in hex_string[1:count]])
    return count, int(hex_int, 16)

def hex_to_oid(hex_string):
    """Parse object id out of hex string."""
    assert ord(hex_string[0]) == 43, 'Invalid OID prefix.'
    hex_string = hex_string[1:]
    oid = ['1', '3']
    big_int = False
    for c in hex_string:
        if big_int:
            if len(bin(ord(c))[2:]) <= 7:
                big_int = False
                binary += bin(ord(c))[2:].zfill(7)
                oid.append(str(int(binary, 2)))
            else:
                binary += bin(ord(c))[3:]
        else:
            if len(bin(ord(c))[2:]) <= 7:
                oid.append(str(ord(c)))
            elif len(bin(ord(c))[2:]) > 7:
                big_int = True
                binary = ''
                binary += bin(ord(c))[3:]
    return '.'.join(oid)

def oid_to_hex(object_id):
    """Convert object id into hex array."""
    object_id = object_id.split('.')
    while object_id.count(''):
        object_id.remove('')
    new_elements = []
    if object_id[:2] == ['1', '3']:
        del(object_id[:2])
    new_elements.append('0x2b')
    for element in object_id:
        element = int(element)
        if len(bin(element)[2:]) > 7:
            binary = bin(element)[2:]
            i = len(binary)/7.0
            parts = []
            while i > 0:
                parts.append(binary[-7:])
                binary = binary[:-7]
                i -= 1
            parts.reverse()
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    parts = [hex(int(part, 2)) for part in parts]
                    break
                if len(part) <= 7:
                    parts[i] = '1%s' % part.rjust(7, '0')
                else:
                    parts[i] = '1%s' % part
            new_elements.extend(parts)
        else:
            new_elements.append(hex(element))
    return new_elements

def build_message(object_id, community='public', request_type='get', request_id=0):
    if request_type == 'get':
        request_type = '0xa0'
    elif request_type == 'get_next':
        request_type = '0xa1'
    elif request_type == 'set':
        request_type = '0xa3'
    else:
        raise Exception('Unsupported request type: %s' % request_type)
    components = {'header': ['0x30'],
                  'version': ['0x02', '0x01', '0x0'],
                  'community': ['0x04'],
                  'pdu': [request_type],
                  'request_id': ['0x02', '0x01', '0x0'],
                  'error': ['0x02', '0x01', '0x0', '0x02', '0x01', '0x0'],
                  'variable_sequence': ['0x30'],
                  'variable_binding': ['0x30'],
                  'oid': ['0x06'],
                  'value': ['0x05', '0x0']}
    message = []
    object_id = oid_to_hex(object_id)
    community = community_to_hex(community)
    components['oid'].append(hex(len(object_id)))
    components['oid'].extend(object_id)
    components['value'].reverse()
    message.extend(components['value'])
    components['oid'].reverse()
    message.extend(components['oid'])
    components['variable_binding'].append(hex(len(message)))
    components['variable_binding'].reverse()
    message.extend(components['variable_binding'])
    components['variable_sequence'].append(hex(len(message)))
    components['variable_sequence'].reverse()
    message.extend(components['variable_sequence'])
    components['error'].reverse()
    message.extend(components['error'])
    components['request_id'].reverse()
    message.extend(components['request_id'])
    components['pdu'].append(hex(len(message)))
    components['pdu'].reverse()
    message.extend(components['pdu'])
    components['community'].append(hex(len(community)))
    components['community'].extend(community)
    components['community'].reverse()
    message.extend(components['community'])
    components['version'].reverse()
    message.extend(components['version'])
    components['header'].append(hex(len(message)))
    components['header'].reverse()
    message.extend(components['header'])
    message.reverse()
    return ''.join([chr(int(c, 16)) for c in message])

def parse_reply(reply):
    # Check/Parse Message Header
    assert ord(reply[0]) == 48, 'Message has invalid header type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    actual_length = len(reply[count:])
    if actual_length < hex_int:
        raise Exception('Did not recv entire message: %s bytes of %s' % (actual_length, hex_int))
    reply = reply[count:]
    # Check/Parse Message Version
    assert ord(reply[0]) == 2, 'Message has invalid version type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    assert hex_int == 1, 'Unknown message version.'
    reply = reply[count:]
    count, hex_int = get_hex_int(reply)
    assert hex_int == 0, 'Message version not supported.'
    reply = reply[count:]
    # Check and Remove Message Community
    assert ord(reply[0]) == 4, 'Message has invalid community type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count + hex_int:]
    # Check Message PDU Header
    assert ord(reply[0]) == 162, 'Message has invalid PDU type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    assert len(reply) == hex_int, 'Message PDU not complete.'
    # Check/Parse Message Request ID
    assert ord(reply[0]) == 2, 'Message has invalid request id type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    count, request_id = get_hex_int(reply)
    reply = reply[count:]
    # Check/Parse Message Error
    assert ord(reply[0]) == 2, 'Message has invalid error type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    count, error_id = get_hex_int(reply)
    reply = reply[count:]
    if error_id == 1:
        raise Exception('Result of request is too large.')
    elif error_id == 2:
        raise Exception('Name not found.')
    elif error_id == 3:
        raise Exception('Bad data type.')
    elif error_id == 4:
        raise Exception('Attempted to set read only value.')
    elif error_id == 5:
        raise Exception('General error.')
    # Check/Parse Message Error Index
    assert ord(reply[0]) == 2, 'Message has invalid error index type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    count, error_index = get_hex_int(reply)
    reply = reply[count:]
    # Parse Message Variable Binding Sequence Header
    assert ord(reply[0]) == 48, 'Message has invalid varbind list header type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    assert len(reply) == hex_int, 'Message varbind list not complete.'
    # Parse Message Variable Binding Header
    assert ord(reply[0]) == 48, 'Message has invalid varbind header type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    assert len(reply) == hex_int, 'Message varbind not complete.'
    # Parse Message Variable Binding OID
    assert ord(reply[0]) == 6, 'Message has invalid OID type.'
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    object_id = hex_to_oid(reply[count:hex_int + 1])
    reply = reply[count + hex_int:]
    # Parse Message Variable Binding Value
    result_type = ord(reply[0])
    reply = reply[1:]
    count, hex_int = get_hex_int(reply)
    reply = reply[count:]
    if result_type == 2:
        response_type = 'int'
        response = ''.join(['{:02x}'.format(ord(c)) for c in reply])
        response = int(response, 16)
    elif result_type == 4:
        # Octet String
        response_type = 'str'
        response = reply
    elif result_type == 6:
        # Object ID
        response_type = 'oid'
        response = hex_to_oid(reply)
    else:
        # Unknown
        response_type = 'unk'
        response = 'Unkown response value type.'
    return request_id, object_id, response_type, response

class SNMPHelper:
    def __init__(self, host, community='public', port=161, timeout=1):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(timeout)
        self._host = host
        self._port = port
        self._community = community
        self._request_counter = 0
    
    def get(self, object_id):
        message = build_message(object_id, self._community, request_type='get')
        self._sock.sendto(message, (self._host, self._port))
        reply = self._sock.recv(1024)
        self._request_counter += 1
        return parse_reply(reply)
    
    def get_next(self, object_id):
        message = build_message(object_id, self._community, request_type='get_next')
        self._sock.sendto(message, (self._host, self._port))
        reply = self._sock.recv(1024)
        self._request_counter += 1
        return parse_reply(reply)
    
    def set(self, object_id, value):
        message = build_message(object_id, self._community, request_type='set')
        self._sock.sendto(message, (self._host, self._port))
        reply = self._sock.recv(1024)
        self._request_counter += 1
        return parse_reply(reply)
    
    def walk(self, object_id):
        base_id = object_id.strip('.')
        replies = []
        while True:
            try:
                reply = self.get_next(object_id)
                if not reply[1].startswith(base_id):
                    break
                replies.append({'sent_id': object_id,
                                'id': reply[1],
                                'type': reply[2],
                                'value': reply[3]})
                object_id = reply[1]
            except:
                break
        return replies

class SNMPRequest:
    _simple_types = {'boolean': hex(1),
                     'integer': hex(2),
                     'bit_string': hex(3),
                     'octet_string': hex(4),
                     'null': hex(5),
                     'oid': hex(6),
                     'real': hex(9),
                     'enumerated': hex(10)}
    
    _complex_types = {'sequence': hex(48),
                      'set': hex(49)}
    
    _error_types = {'no_error': hex(0),
                    'response_too_large': hex(1),
                    'name_not_found': hex(2),
                    'bad_data_type': hex(3),
                    'set_read_only': hex(4),
                    'general_error': hex(5)}
    
    _identifiers = {'get_request': hex(160),
                    'next_request': hex(161),
                    'response': hex(162),
                    'set_request': hex(163)}
    
    def __init__(self):
        pass

if __name__ == '__main__':
    snmp = SNMPHelper('***REMOVED***', '***REMOVED***')
    oids = ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.17.4.3.1.1', '1.3.6.1.2.1.2.2.1.6.10005']
    
    for oid in oids:
        try:
            result = snmp.get(oid)
            print '%s: %s' % (result[1], result[3])
        except AssertionError, e:
            print '%s: %s' % (result[1], e.message)
        except Exception, e:
            print '%s: %s' % (result[1], e.message)
