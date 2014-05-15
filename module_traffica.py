# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:
#
# https://wiki.python.org/moin/BitManipulation

import json
import logging
import unittest
import struct

sessions = []

class FieldMap:
    def __init__(self, fieldsDef):
        self.fields = fieldsDef

    def getStructFmt(self):
        fmt = '<'
        for fieldDef in self.fields:
            fmt += fieldDef[1]
        return fmt

    def parseFromBytes(self, data):
        fmt = self.getStructFmt()
        if len(data) < struct.calcsize(fmt):
            raise Exception('Data to be parsed have invalid size, expected size > %d, real data size: %d.' % (struct.calcsize(fmt), len(data)))

        fields = struct.unpack(fmt, data[0:struct.calcsize(fmt)])

        for i in range(len(self.fields)):
            self.fields[i][2] = fields[i]      

    def toBytes(self):
        r = b'' 
        for fieldDef in self.fields:
            r += struct.pack('<' + fieldDef[1], fieldDef[2])
        return r

    def parseFromJson(self, data):
        jsonData = json.loads(data)
        if not isinstance(jsonData, dict):
            raise Exception('Invalid json structure')

        for fieldDef in self.fields:
            if not fieldDef[0] in jsonData:
                raise Exception('Invalid json structure, field %s not found.' % fieldDef[0])
            self.setFieldValue(fieldDef[0], jsonData[fieldDef[0]])

    def toJson(self):
        jsonInput = dict()

        for fieldDef in self.fields:
            jsonInput[fieldDef[0]] = fieldDef[2]

        #return json.dumps(jsonInput)
        return jsonInput

    def dump(self):
        for fieldDef in self.fields:
            print fieldDef

    def setFieldValue(self, fieldId, fieldVal):
        for fieldDef in self.fields:
            if fieldDef[0] == fieldId:
                fieldDef[2] = fieldVal

    def getFieldValue(self, fieldId):
        result = None
        for fieldDef in self.fields:
            if fieldDef[0] == fieldId:
                result = fieldDef[2]
                break
        return result

class TrafReport:
    """Class represents common part of all traffica reports"""

    # Trigger points
    TRIGGER_SIP_REG_SUCCESSFUL    = 0  # SIP registration successful 
    TRIGGER_SIP_REREG_SUCCESSFUL  = 1  # SIP re-registration successful 
    TRIGGER_SIP_DEREG_SUCCESSFUL  = 2  # SIP de-registration successful 
    TRIGGER_SIP_REG_FAILED        = 3  # SIP registration failed 
    TRIGGER_SIP_REREG_FAILED      = 4  # SIP re-registration failed 
    TRIGGER_SIP_DEREG_FAILED      = 5  # SIP de-registration failed 
    TRIGGER_SIP_CALL_ENDED        = 6  # SIP Call ended
    TRIGGER_CFX5000_STAT          = 7  # Internal CFX-5000 statistics
    TRIGGER_SIP_SIP_INSTANT_MSG   = 8  # SIP Instant messaging report
    TRIGGER_SIP_SIP_PRESENCE_MSG  = 9  # SIP presence report
    TRIGGER_SIP_USER_PLANE_QOS    = 10 #  SIP User plane QoS report

    # Report types
    TYPE_SIP_REGISTRATION      = 0x8300 # SIP registration
    TYPE_SIP_CALL_ENDED        = 0x8301 # SIP Call ended
    TYPE_CFX5000_STAT          = 0x8302 # Internal CFX-5000 statistics
    TYPE_SIP_SIP_INSTANT_MSG   = 0x8303 # SIP Instant messaging report
    TYPE_SIP_SIP_PRESENCE_MSG  = 0x8304 # SIP presence report
    TYPE_SIP_USER_PLANE_QOS    = 0x8305 # SIP User plane QoS report

    def __init__(self):
        pass

    def getFieldsDef(self):
        fieldsDef = [
            ['reportType',      'H', 0, 'Report Type'],
            ['reportLength',    'H', 0, 'Report Length'],
            ['vendorId',        'I', 0, 'Vendor Id'],
            ['senderId',        'I', 0, 'Sender Id'],
            ['localTimestamp',  'Q', 0, 'Local Timestamp'],
            ['count',           'I', 0, 'Count'],
            ['reportReason',    'b', 0, 'Report reason']
        ]
        return fieldsDef

class TrafReportStat(TrafReport):
    """Class represents CFX5000 traffica report"""

    def __init__(self):
        TrafReport.__init__(self)

        self.fields = FieldMap(self.getFieldsDef())
        self.fields.setFieldValue('reportType', TrafReport.TYPE_CFX5000_STAT)
        self.fields.setFieldValue('reportLength', 117)

    def getFieldsDef(self):

        fieldsDef = [
            ['cpuLoadNode1',         'b',   0, 'CPU load - node 1'],
            ['cpuLoadNode2',         'b',   0, 'CPU load - node 2'],
            ['memUsageNode1',        'b',   0, 'Memory usage - node 1'],
            ['memUsageNode2',        'b',   0, 'Memory usage - node 2'],
            ['activeSipTranPcscf',   'I',   0, 'Active SIP transactions P-CSCF'],
            ['activeSipTranIcscf',   'I',   0, 'Active SIP transactions I-CSCF'],
            ['activeSipTranScscf',   'I',   0, 'Active SIP transactions S-CSCF'],
            ['activeSipTranBcscf',   'I',   0, 'Active SIP transactions B-CSCF'],
            ['activeSipTranMcff',    'I',   0, 'Active SIP transactions MCF'],
            ['activeSipTranIbcf',    'I',   0, 'Active SIP transactions IBCF'],
            ['activeSipTranEatf',    'I',   0, 'Active SIP transactions EATF'],
            ['activeSipInvPcscf',    'I',   0, 'Active SIP Invite P-CSCF'],
            ['activeSipInvScscf',    'I',   0, 'Active SIP Invite S-CSCF'],
            ['activeSipInvIbcf',     'I',   0, 'active SIP Invite IBCF'],
            ['fullyRegUsersPcscf',   'I',   0, 'Fully registered users P-CSCF'],
            ['fullyRegUsersScscf',   'I',   0, 'Fully registered users S-CSCF'],
            ['successfulRegsScscf',  'I',   0, 'Successful registrations on S-CSCF'],
            ['failedRegsScscf',      'I',   0, 'Failed registrations on S-CSCF'],
            ['reserved',             '32s', '', 'Reserved for future']
        ]

        return TrafReport.getFieldsDef(self) + fieldsDef

    def parseFromBytes(self, data):
        self.fields.parseFromBytes(data)
        if self.fields.getFieldValue('reportType') != TrafReport.TYPE_CFX5000_STAT:
            raise Exception('Invalid report type: %d, expected value: %d' % (self.fields.getFieldValue('reportType'), TrafReport.TYPE_CFX5000_STAT))
        
    def toBytes(self):
        return self.fields.toBytes()

class TrafReportRegistration(TrafReport):
    """Class represents Registration traffica report"""
    def __init__(self):
        TrafReport.__init__(self)

        self.fields = FieldMap(self.getFieldsDef())
        self.fields.setFieldValue('reportType', TrafReport.TYPE_SIP_REGISTRATION)
        self.fields.setFieldValue('reportLength', 1159)

    def getFieldsDef(self):

        fieldsDef = [
            ['successfulRegs',            'I',    0,    'Successful Registrations'],
            ['sipVersion',                'b',    0,    'SIP version'],
            ['sipSessionId',              '80s',  '',   'SIP Session-ID'],
            ['sipSessionIdComplete',      'b',    0,    'SIP Session-ID complete'],
            ['emergency',                 'b',    0,    'Emeregency'],
            ['ueAccess',                  'b',    0,    'UE access'],
            ['locationInfo',              '32s',  '',   'Location-info'],
            ['networkProvided',           'b',    0,    'network provided'],
            ['accessNetworks',            'b',    0,    'Access-networks'],
            ['userAgent',                 '50s',  '',   'User Agent'],
            ['sipFromUriUserName',        '22s',  '',   'SIP From URI User Name'],
            ['sipFromUriTelSub',          '20s',  '',   'SIP From URI Telephone subscriber'],
            ['sipFromUriDomain',          '102s', '',   'SIP From URI Domain'],
            ['sipContactUriUserName',     '22s',  '',   'SIP Contact URI User Name'],
            ['sipContactUriTelSub',       '20s',  '',   'SIP Contact URI Telephone subscriber'],
            ['sipContactUriDomainName',   '102s', '',   'SIP Contact URI Domain Name'],
            ['sipContactUriIpPort',       'H',    0,    'SIP Contact URI IP Port'],
            ['sipInitialRegTimeStamp',    'Q',    0,    'SIP Initial Register time stamp'],
            ['sip401ResponseTimeStamp',   'Q',    0,    'SIP 401 Response time stamp'],
            ['sip2ndRegTimeStamp',        'Q',    0,    'SIP 2nd Register time stamp'],
            ['sipFinalResponseTimeStamp', 'Q',    0,    'SIP final response time stamp'],
            ['sipRegResponseCode',        'H',    0,    'SIP Register response code'],
            ['regResponseCodeDesc',       '30s',  '',   'Register response code description'],
            ['sipReasonHeader',           '30s',  '',   'SIP Reason header'],
            ['regResponseCodeIP',         '16s',  '',   'Register response code Initiating element Ethernet IP Address'],
            ['statusInitElementType',     'b',    0,    'Status Initiating element type'],
            ['errorCode1',                'H',    0,    'ErrorCode_1'],
            ['errorCode2',                'H',    0,    'ErrorCode_2'],
            ['errorCode3',                'H',    0,    'ErrorCode_3'],
            ['sipRegResponseDuration1',   'I',    0,    'SIP Register response duration_1'],
            ['sipRegResponseDuration2',   'I',    0,    'SIP Register response duration_2'],
            ['sipExpiresPeriod',          'I',    0,    'SIP Expires Period'],
            ['ueIP',                      '16s'   '',   'UE Ethernet IP address'],
            ['uePort',                    'I',    0,    'UE Ethernet IP port'],
            ['pcscfIp',                   '16s',  '',   'P-CSCF IP address'],
            ['icscfIp',                   '16s',  '',   'I-CSCF IP address'],
            ['scscfIp',                   '16s',  '',   'S-CSCF IP address'],
            ['hssIp',                     '16s',  '',   'HSS IP address'],
            ['pcscfDomainName',           '102s', '',   'P-CSCF domain name'],
            ['icscfDomainName',           '102s', '',   'I-CSCF domain name'],
            ['scscfDomainName',           '102s', '',   'S-CSCF domain name'],
            ['asAddress1',                '16s',  '',   'AS address_1'],
            ['asAddress2',                '16s',  '',   'AS address_2'],
            ['asAddress3',                '16s',  '',   'AS address_3'],
            ['diaOperationsPerformed',    'b',    0,    'Diameter operations performed'],
            ['diaOperationCode',          'I',    0,    'Diameter Operation Code'],
            ['diaResponseCode',           'I',    0,    'Diameter Response code'],
            ['serverAssignmentType',      'b',    0,    'Server Assignment Type'],
            ['deregReasonCode',           'b',    0,    'De-registration Reason Code'],
            ['diaResponseSessionId',      '64s',  '',   'Diameter Response session_ID'],
            ['reserved',                  '32s',  '',   'reserved for future']
        ]

        return TrafReport.getFieldsDef(self) + fieldsDef

    def parseFromBytes(self, data):
        self.fields.parseFromBytes(data)
        if self.fields.getFieldValue('reportType') != TrafReport.TYPE_SIP_REGISTRATION:
            raise Exception('Invalid report type: %d, expected value: %d' % (self.fields.getFieldValue('reportType'), TrafReport.TYPE_SIP_REGISTRATION))
        
    def toBytes(self):
        return self.fields.toBytes()

def initialize(nsim):
    logger = logging.getLogger('nsim.traffica')
    logger.debug('Module initialized')

def getCommands():
    commands = []
    commands.append({'name': 'status', 'description': 'Module status'})
    commands.append({'name': 'session-open', 'description': ''})
    commands.append({'name': 'session-close', 'description': ''})
    return commands;

def cmdStatus(data):
    global sessions
    result = { "return": "ok" }
    result['sessions'] = len(sessions)
    return result

def cmdSessionOpen(data):
    global sessions

    if 'sid' in data:
        if data['sid'] in sessions:
            result = { "return": "error", 'description': 'Session (%s) is already open' % data['sid']}
        else:
            sessions.append(data['sid'])
            result = { "return": "ok" }
    else:
        result = { "return": "error", "description": "Missing session id" }
    return result

def cmdSessionClose(data):
    global sessions

    if 'sid' in data:
        if not data['sid'] in sessions:
            result = { 'return': 'error', 'description': 'Session (%s) does not exist' % data['sid']}
        else:    
            sessions.remove(data['sid'])
            result = { 'return': 'ok' }
    else:
        result = { 'return': 'error', 'description': 'Missing session id' }
    return result

def cmdSendHbRequest(data):
    if not 'sid' in data:
        return { "return": "error", "description": "Missing session id (sid)" }
    if not data['sid'] in sessions:
        return { "return": "error", 'description': 'Session (%s) does not exist' % data['sid']}

    #  todo: code to send HB request
    result = { "return": "ok" }
    return result

def cmdGetReports(data):
    if not 'sid' in data:
        return { "return": "error", "description": "Missing session id" }
    if not data['sid'] in sessions:
        return { "return": "error", 'description': 'Session (%s) does not exist' % data['sid']}

    #  todo: code to send HB request
    result = { "return": "ok" }
    result['reports'] = [];

    repSrc = TrafReportStat()
    repSrc.fields.setFieldValue('fullyRegUsersPcscf', 20)

    result['reports'].append(repSrc.fields.toJson())

    return result

def processRequest(data):
    # process commands
    if 'cmd' in data:
        if data['cmd'] == 'status':
            result = cmdStatus(data)
        elif data['cmd'] == 'session-open':
            result = cmdSessionOpen(data)
        elif data['cmd'] == 'session-close':
            result = cmdSessionClose(data)
        elif data['cmd'] == 'send-hb-request':
            result = cmdSendHbRequest(data)
        elif data['cmd'] == 'get-reports':
            result = cmdGetReports(data)
        else:
            result = { "return": "error", "description": 'Unknown command'}
    else:
        result = { 'return': 'error', 'description': 'Unknown request type'}

    return result

def createHbRequest(subscriptionType, reportTypes):
    """
    UINT16  2   Header  It represents the report identification. Agreed between CFX and Traffica PL.    0x4600
    UINT16  2   Length  It represents the report length.    0x000D
    UINT8   1   Subscription type   It indicates the subscription of the reports. 0 = stop sending reports. 1 = start sending reports   0x0-0x1 
    UINT64  8   Report types    It indicates the report types the TNES requires to receive.     Range 
    """
    #result = struct.pack('IIHQ', header, 0xD, subscriptionType, reportTypes)
    result = struct.pack('<HHBQ', 0x4600, 0x0d, subscriptionType, reportTypes)
    return result 

def parseHbResponse(data):
    """
    UINT16  2   Header  It represents the report identification. Agreed between CFX and Traffica PL.    0x4601
    UINT16  2   Length  It represents the report length.    0x0010
    UINT32  4   Sender ID   It represents the CFX identification. Sender ID number. Little-Endian byte order used.    Range
    UINT64  8   Report types    It indicates the types of reports the CFX will provide to TNES..    Range 
    """
    fmt = '<HHIQ'
    if len(data) != struct.calcsize(fmt):
        raise Exception('Heart beat response data have invalid size, expected size: %d, real data size: %d.' % (struct.calcsize(fmt), len(data)))

    parts = struct.unpack(fmt, data)

    if len(parts) != 4:
        raise Exception('Invalid heart beat response data')

    # check header
    if parts[0] != 0x4601:
        raise Exception('Invalid heart beat response data - header does not have expected value 0x4601')

    # check length 
    if parts[1] != 0x10:
        raise Exception('Invalid heart beat response data - incorrect length (must be 0x10)')

def parseReport(data):
    """
    General method for parsing single report. Report type is detected from first two bytes of data block. 
    UINT16  2   Header  It represents the report identification. Agreed between CFX and Traffica PL.
    UINT16  2   Length  It represents the report length.
    """
    fmt = '<HH'
    if len(data) < struct.calcsize(fmt):
        raise Exception('Report data have invalid size, expected size > %d, real data size: %d.' % (struct.calcsize(fmt), len(data)))

    reportHeader, reportLength = struct.unpack(fmt, data[0:4])

    if len(data) != reportLength:
        raise Exception('Report data have invalid size, expected size %d, real data size: %d.' % (reportLength, len(data)))

    if reportHeader == TrafReport.TYPE_CFX5000_STAT:
        r = TrafReportStat()
        r.parseFromBytes(data)
        return r

def getBit(val, pos):
    return ((val & (1 << pos)) != 0)

def setBit(val, pos):
    return (val | (1 << pos))

def clearBit(val, pos):
    return (val & (~(1 << offset)))


# --- Unit Testing -------------------------------------------

class TestSequenceFunctions(unittest.TestCase):

    def test_sessionOpenAndClose(self):
        global sessions

        self.assertEqual(len(sessions), 0)

        r = cmdSessionOpen({'sid': 'x'})
        self.assertEqual(r['return'], 'ok')
        self.assertEqual(len(sessions), 1)
 
        r = cmdSessionOpen({'sid': 'x'})
        self.assertEqual(r['return'], 'error')

        r = cmdSessionOpen({'sid': 'y'})
        self.assertEqual(r['return'], 'ok')
        self.assertEqual(len(sessions), 2)
 
        r = cmdSessionClose({'sid': 'z'})
        self.assertEqual(r['return'], 'error')

        r = cmdSessionClose({'sid': 'y'})
        self.assertEqual(r['return'], 'ok')
        self.assertEqual(len(sessions), 1)

        r = cmdSessionClose({'sid': 'x'})
        self.assertEqual(r['return'], 'ok')
        self.assertEqual(len(sessions), 0)

    def test_hbRequestCreate(self):
        p = createHbRequest(0, 0)
        self.assertEqual(p, b'\x00\x46\x0d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        p = createHbRequest(1, 0)
        self.assertEqual(p, b'\x00\x46\x0d\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00')

        p = createHbRequest(1, 1)
        self.assertEqual(p, b'\x00\x46\x0d\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00')

    def test_hbReplyParse(self):
        parseHbResponse(b'\x01\x46\x10\x00\x06\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00')

    def test_triggerBitMask(self):
        m = struct.unpack('<Q', b'\x00\x00\x00\x00\x00\x00\x00\x00')[0]
        m = setBit(m, TrafReport.TRIGGER_SIP_REG_SUCCESSFUL)
        m = setBit(m, TrafReport.TRIGGER_SIP_REREG_FAILED)
        self.assertTrue(getBit(m, TrafReport.TRIGGER_SIP_REG_SUCCESSFUL))
        self.assertTrue(getBit(m, TrafReport.TRIGGER_SIP_REREG_FAILED))
        self.assertFalse(getBit(m, TrafReport.TRIGGER_SIP_CALL_ENDED))
        self.assertFalse(getBit(m, TrafReport.TRIGGER_CFX5000_STAT))

    def test_fieldMap(self):
        fd = [ ['f1', 'b', 0, 'field1'], ['f2', 'H', 0, 'field2']] 
        fm = FieldMap(fd)

        # setters and getters
        fm.setFieldValue('f1', 3)
        fm.setFieldValue('f2', 4)
        self.assertEqual(fm.getFieldValue('f1'), 3)
        self.assertEqual(fm.getFieldValue('f2'), 4)

        # binary output and input
        fbytes = fm.toBytes()
        self.assertEqual(len(fbytes), 3)
        self.assertEqual(fbytes, b'\x03\x04\x00')

        fm.parseFromBytes(b'\x07\x03\x45')
        self.assertEqual(fm.getFieldValue('f1'), 7)
        self.assertEqual(fm.getFieldValue('f2'), 0x4503)

        # json input and output
        #TODO: Check print fm.toJson()

        jsonData = '{ "f1": 156, "f2": 3459 }'
        fm.parseFromJson(jsonData)
        self.assertEqual(fm.getFieldValue('f1'), 156)
        self.assertEqual(fm.getFieldValue('f2'), 3459)

        #fm.dump()

    def test_StatReport(self):
        # prepare report data
        repSrc = TrafReportStat()
        repSrc.fields.setFieldValue('vendorId', 1)
        repSrc.fields.setFieldValue('senderId', 2)
        repSrc.fields.setFieldValue('localTimestamp', 3)
        repSrc.fields.setFieldValue('count', 4)
        repSrc.fields.setFieldValue('reportReason', 5)
        repSrc.fields.setFieldValue('cpuLoadNode1', 6)
        repSrc.fields.setFieldValue('cpuLoadNode2', 7)
        repSrc.fields.setFieldValue('memUsageNode1', 8)
        repSrc.fields.setFieldValue('memUsageNode2', 9)
        repSrc.fields.setFieldValue('activeSipTranPcscf', 10)
        repSrc.fields.setFieldValue('activeSipTranIcscf', 11)
        repSrc.fields.setFieldValue('activeSipTranScscf', 12) 
        repSrc.fields.setFieldValue('activeSipTranBcscf', 13) 
        repSrc.fields.setFieldValue('activeSipTranMcff', 14)
        repSrc.fields.setFieldValue('activeSipTranIbcf', 15) 
        repSrc.fields.setFieldValue('activeSipTranEatf', 16) 
        repSrc.fields.setFieldValue('activeSipInvPcscf', 17) 
        repSrc.fields.setFieldValue('activeSipInvScscf', 18) 
        repSrc.fields.setFieldValue('activeSipInvIbcf', 19)
        repSrc.fields.setFieldValue('fullyRegUsersPcscf', 20)
        repSrc.fields.setFieldValue('fullyRegUsersScscf', 21)
        repSrc.fields.setFieldValue('successfulRegsScscf', 22)
        repSrc.fields.setFieldValue('failedRegsScscf', 23)
        #repSrc.fields.dump()

        # parse report data
        raw = repSrc.toBytes()
        #print ':'.join(x.encode('hex') for x in raw)
        repDst = parseReport(raw) 

        # check parsed data
        self.assertEqual(repDst.fields.getFieldValue('vendorId'), 1)
        self.assertEqual(repDst.fields.getFieldValue('senderId'), 2)
        self.assertEqual(repDst.fields.getFieldValue('localTimestamp'), 3)
        self.assertEqual(repDst.fields.getFieldValue('count'), 4)
        self.assertEqual(repDst.fields.getFieldValue('reportReason'), 5)
        self.assertEqual(repDst.fields.getFieldValue('cpuLoadNode1'), 6)
        self.assertEqual(repDst.fields.getFieldValue('cpuLoadNode2'), 7)
        self.assertEqual(repDst.fields.getFieldValue('memUsageNode1'), 8)
        self.assertEqual(repDst.fields.getFieldValue('memUsageNode2'), 9)
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranPcscf'), 10)
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranIcscf'), 11)
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranScscf'), 12) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranBcscf'), 13) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranMcff'), 14)
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranIbcf'), 15) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipTranEatf'), 16) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipInvPcscf'), 17) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipInvScscf'), 18) 
        self.assertEqual(repDst.fields.getFieldValue('activeSipInvIbcf'), 19)
        self.assertEqual(repDst.fields.getFieldValue('fullyRegUsersPcscf'), 20)
        self.assertEqual(repDst.fields.getFieldValue('fullyRegUsersScscf'), 21)
        self.assertEqual(repDst.fields.getFieldValue('successfulRegsScscf'), 22)
        self.assertEqual(repDst.fields.getFieldValue('failedRegsScscf'), 23)

    def test_RegisterReport(self):
        # prepare report data
        repSrc = TrafReportRegistration()
        repSrc.fields.setFieldValue('successfulRegs', 1)
        repSrc.fields.setFieldValue('sipVersion', 2)
        repSrc.fields.setFieldValue('sipSessionId', 'sip-session-id')
        repSrc.fields.setFieldValue('sipSessionIdComplete', 3)
        repSrc.fields.setFieldValue('emergency', 4)
        repSrc.fields.setFieldValue('ueAccess', 5)
        repSrc.fields.setFieldValue('locationInfo', 'Brno')
        repSrc.fields.setFieldValue('networkProvided',6)
        repSrc.fields.setFieldValue('accessNetworks', 7)
        repSrc.fields.setFieldValue('userAgent', 'Brno User Agent')
        repSrc.fields.setFieldValue('sipFromUriUserName', 'Bob Brown')
        repSrc.fields.setFieldValue('sipFromUriTelSub', '343434')
        repSrc.fields.setFieldValue('sipFromUriDomain', 'bob.brno.cz')
        repSrc.fields.setFieldValue('sipContactUriUserName', 'bob')
        repSrc.fields.setFieldValue('sipContactUriTelSub', '343434-2')
        repSrc.fields.setFieldValue('sipContactUriDomainName', 'bob.brno.cz-2')
        repSrc.fields.setFieldValue('sipContactUriIpPort', 5060)
        repSrc.fields.setFieldValue('sipInitialRegTimeStamp', 8)
        repSrc.fields.setFieldValue('sip401ResponseTimeStamp', 9)
        repSrc.fields.setFieldValue('sip2ndRegTimeStamp', 10)
        repSrc.fields.setFieldValue('sipFinalResponseTimeStamp', 11)
        repSrc.fields.setFieldValue('sipRegResponseCode', 200)
        repSrc.fields.setFieldValue('regResponseCodeDesc', 'OK')
        repSrc.fields.setFieldValue('sipReasonHeader', 'OK, Registered')
        repSrc.fields.setFieldValue('regResponseCodeIP', '100.101.102.103')
        repSrc.fields.setFieldValue('statusInitElementType', 12)
        repSrc.fields.setFieldValue('errorCode1', 13)
        repSrc.fields.setFieldValue('errorCode2', 14)
        repSrc.fields.setFieldValue('errorCode3', 15)
        repSrc.fields.setFieldValue('sipRegResponseDuration1', 16)
        repSrc.fields.setFieldValue('sipRegResponseDuration2', 17)
        repSrc.fields.setFieldValue('sipExpiresPeriod', 18)
        repSrc.fields.setFieldValue('ueIP', '101.102.103.105')
        repSrc.fields.setFieldValue('uePort', 5061)
        repSrc.fields.setFieldValue('pcscfIp', '101.102.103.106')
        repSrc.fields.setFieldValue('icscfIp', '101.102.103.107')
        repSrc.fields.setFieldValue('scscfIp', '101.102.103.108')
        repSrc.fields.setFieldValue('hssIp', '101.102.103.109')
        repSrc.fields.setFieldValue('pcscfDomainName', 'pcscf.brno.cz')
        repSrc.fields.setFieldValue('icscfDomainName', 'icscf.brno.cz')
        repSrc.fields.setFieldValue('scscfDomainName', 'scscf.brno.cz')
        repSrc.fields.setFieldValue('asAddress1', '101.102.103.109')
        repSrc.fields.setFieldValue('asAddress2', '101.102.103.110')
        repSrc.fields.setFieldValue('asAddress3', '101.102.103.111')
        repSrc.fields.setFieldValue('diaOperationsPerformed', 19)
        repSrc.fields.setFieldValue('diaOperationCode', 20)
        repSrc.fields.setFieldValue('diaResponseCode', 21)
        repSrc.fields.setFieldValue('serverAssignmentType', 22)
        repSrc.fields.setFieldValue('deregReasonCode', 23)
        repSrc.fields.setFieldValue('diaResponseSessionId', 'dia-session-id')
 
        #repSrc.fields.dump()

        raw = repSrc.toBytes()
        #print ':'.join(x.encode('hex') for x in raw)

        #print repSrc.fields.toJson()

if __name__ == '__main__':
    unittest.main()

