kinase

Kinase Is Not An SNMP Engine

Kinase is also an enzyme that transfers phosphate groups...

kinase is juat a small, simple, pure-python implementation of SNMPv2 protocol.
I plan to eventually add support for v3 with encryption methods and other features!

It was designed as a replacement for command line tools like Net-SNMP so that I could
quickly and natively send SNMP commands to remote network devices and query them for
information, as such the get and walk features are the most fully tested.

In the future I plan on adding full support for v3 and adding more of the features of
v2 and possibly support for v1 packet types but as that protocol is rarely used it is
low on the list. Top of the list is really moving from hand rolled packets and hex
conversions to the use of structs and more dynamic and flexible packet creation.

This is partially a learning experiment for myself to try and implement an the
necessary RFCs in pure Python, so development may be staggered and features may not
be completed for a long time!
