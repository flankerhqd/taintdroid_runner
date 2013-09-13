################################################################################
#
# Copyright (c) 2011-2012, Daniel Baeumges (dbaeumges@googlemail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

from common import TaintLogActionEnum, TaintTagEnum
import json


# ================================================================================
# Enum Classes
# ================================================================================
class CipherActionEnum:
    INIT_ACTION = 'init'
    UPDATE_ACTION = 'update'
    DO_FINAL_ACTION = 'doFinal'
    CLEANED = 'cleaned'

class CipherModeEnum:
    ENCRYPT_MODE = 1
    DECRYPT_MODE = 2

class SimulatorActionEnum:
    DUMMY_ACTION = "dummy"
    INSTALL_APP_ACTION = 'install_app'
    SIMULATE_SEND_SMS_ACTION = 'simulate_send_sms'
    SIMULATE_PHONE_CALLIN_ACTION = 'simulate_phone_callin'
    SIMULATE_GPS_MOVE_ACTION = 'simulate_gps_move'
    

# ================================================================================
# Json Base Class
# ================================================================================
class JsonBase:
    _json = True
    
    def __init__(self, **keys):
        self.__dict__.update(keys)
        
    def append(self, name, value):
        setdefault(self.__dict__, name, []).append(value)
        
    def insert(self, name, index, value):
        setdefault(self.__dict__, name, []).insert(index, value)
        
    def update(self, name, **keys):
        setdefault(self, name, {}).update(keys)


# ================================================================================
# Json Reporting Objects
# ================================================================================
class BaseReportEntry(JsonBase):
    pass

class AppReportEntry(BaseReportEntry):
    """
    """
    id = 0
    appPackage = ''
    appPath = ''
    appName = ''
    logcatFile = ''
    md5Hash = ''
    startTime = ''
    endTime = ''
    actionList = []
    simulatorActions = []

class MainReportEntry(BaseReportEntry):
    """
    """
    workingDir = ''
    startTime = ''
    endTime = ''
    appList = []


# ================================================================================
# Json Log Objects (comming from TaintDroid)
# ================================================================================
class BaseLogEntry(JsonBase):
    def doesActionMatch(self, theOther):
        #if theOther.action != 0 and theOther.action != self.action:
        #    return False
        if theOther.__dict__.has_key('actionList') and len(theOther.actionList) > 0:
            match = False
            for action in theOther.actionList:
                if self.action == action:
                    match = True
                    break
            if not match:
                return False
            else:
                return True
        else:
            return True
            
    def doesStackTraceMatch(self, theOther):
        if theOther.stackTraceStr == '' or theOther.stackTraceStr is None:
            return True
        if self.stackTraceStr.find(theOther.stackTraceStr) != -1:
            return True
        return False

    def doesTagMatch(self, theOther):
        if theOther.tag == -1 and int(self.tag, 16) != 0:
            return False
        if theOther.__dict__.has_key('tagList') and len(theOther.tagList) > 0:
            match = False
            for tag in theOther.tagList:
                if int(self.tag, 16) & tag:
                    match = True
            if not match:
                return False
            else:
                return True
        else:
            return True

class ErrorLogEntry(BaseLogEntry):
    """
    """
    message = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

class CallActionLogEntry(BaseLogEntry):
    """
    """
    tag = TaintTagEnum.TAINT_CLEAR
    dialString = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, CallActionLogEntry):
            return False
        #if not self.doesTagMatch(theOther):
        #    return False     
        if theOther.dialString != '' and theOther.dialString != self.dialString:
            return False
        if not self.doesStackTraceMatch(theOther):
            return False
        return True

    def getOverviewLogStr(self):
        return 'CallAction, dialString: %s' % (self.dialString)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        columnList.append(self.dialString)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList
    
    
class CipherUsageLogEntry(BaseLogEntry):
    """
    """
    action = '' # CipherActionEnum
    id = 0    
    mode = 0 # CipherModeEnum
    tag = TaintTagEnum.TAINT_CLEAR
    input = ''
    output = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, CipherUsageLogEntry):
            return False
        if not self.doesActionMatch(theOther):
            return False
        if not self.doesTagMatch(theOther):
            return False        
        if not self.doesStackTraceMatch(theOther):
            return False
        return True
    
    def getOverviewLogStr(self):
        return 'CipherUsage (%s), id: %d, tag: %s, mode: %d' % (self.action, self.id, TaintTagEnum.getTaintString(self.tag), self.mode)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        if self.mode == CipherModeEnum.ENCRYPT_MODE:
            columnList.append('encrypt')
            columnList.append(self.input)
        else:
            columnList.append('decrypt')
            columnList.append(self.output)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList
        
class FileSystemLogEntry(BaseLogEntry):
    """
    """
    action = 0 # TaintLogActionEnum.FS_*
    tag = TaintTagEnum.TAINT_CLEAR
    fileDescriptor = 0
    filePath = '' # filled by postProcess
    taintLogId = 0
    data = ''
    stackTraceStr = ''    
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, FileSystemLogEntry):
            return False
        if not self.doesActionMatch(theOther):
            return False
        if not self.doesTagMatch(theOther):
            return False
        if theOther.filePath != '' and theOther.filePath != self.filePath:
            return False
        if not self.doesStackTraceMatch(theOther):
            return False
        return True

    def getOverviewLogStr(self):
        return 'FileSystemAccess (%s), tag: %s, file: %s (%d)' % (TaintLogActionEnum.getActionString(self.action), TaintTagEnum.getTaintString(self.tag), self.filePath, self.fileDescriptor)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        columnList.append(TaintLogActionEnum.getActionString(self.action))
        columnList.append(self.filePath)
        if theDetailsFlag: columnList.append('%d' % self.taintLogId)
        columnList.append(self.data)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList
    
class NetworkSendLogEntry(BaseLogEntry):
    """
    """
    action = 0 # TaintLogActionEnum.NET_*
    tag = TaintTagEnum.TAINT_CLEAR
    destination = ''
    port = 0
    taintLogId = 0
    data = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, NetworkSendLogEntry):
            return False
        if not self.doesActionMatch(theOther):
            return False
        if not self.doesTagMatch(theOther):
            return False
        if theOther.destination != '' and theOther.destination != self.destination:
            return False
        if theOther.port != 0 and theOther.port != self.port:
            return False
        if not self.doesStackTraceMatch(theOther):
            return False
        return True
    
    def getOverviewLogStr(self):
        return 'NetworkAccess (%s), tag: %s, destination: %s:%d' % (TaintLogActionEnum.getActionString(self.action), TaintTagEnum.getTaintString(self.tag), self.destination, self.port)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        columnList.append(TaintLogActionEnum.getActionString(self.action))
        columnList.append('%s:%d' % (self.destination, self.port))
        if theDetailsFlag: columnList.append('%d' % self.taintLogId)
        columnList.append(self.data)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList

class SSLLogEntry(BaseLogEntry):
    """
    """
    action = 0 # TaintLogActionEnum.SSL_*
    tag = TaintTagEnum.TAINT_CLEAR
    destination = ''
    port = 0
    data = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, SSLLogEntry):
            return False
        if not self.doesActionMatch(theOther):
            return False
        if not self.doesTagMatch(theOther):
            return False
        if theOther.destination != '' and theOther.destination != self.destination:
            return False
        if not self.doesStackTraceMatch(theOther):
            return False
        return True
    
    def getOverviewLogStr(self):
        return 'SSL (%s), tag: %s, destination: %s:%d' % (TaintLogActionEnum.getActionString(self.action), TaintTagEnum.getTaintString(self.tag), self.destination, self.port)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        columnList.append(TaintLogActionEnum.getActionString(self.action))
        columnList.append('%s:%d' % (self.destination, self.port))
        columnList.append(self.data)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList

class SendSmsLogEntry(BaseLogEntry):
    """
    """
    action = 0 # TaintLogActionEnum.SMS_*
    tag = TaintTagEnum.TAINT_CLEAR
    destination = ''
    destinationTag = TaintTagEnum.TAINT_CLEAR
    scAddress = ''
    text = ''
    stackTraceStr = ''
    stackTrace = [] # filled by postProcess
    timestamp = ''

    def doesMatch(self, theOther):
        if not isinstance(theOther, SendSmsLogEntry):
            return False
        if not self.doesActionMatch(theOther):
            return False
        if not self.doesTagMatch(theOther):
            return False
        if theOther.destination != '' and theOther.destination != self.destination:
            return False
        if theOther.destinationTag == -1 and int(self.destinationTag, 16) != 0:
            return False
        if theOther.__dict__.has_key('destinationTagList') and len(theOther.destinationTagList) > 0:
            match = False
            for tag in theOther.destinationTagList:
                if int(self.destinationTag, 16) & tag:
                    match = True
            if not match:
                return False        
        if not self.doesStackTraceMatch(theOther):
            return False
        return True
    
    def getOverviewLogStr(self):
        return 'SMS (%s), tag: %s, destination: %s (%s), source: %s, text: %s, timestamp: %s' % (TaintLogActionEnum.getActionString(self.action), TaintTagEnum.getTaintString(self.tag), self.destination, TaintTagEnum.getTaintString(self.destinationTag), self.scAddress, self.text, self.timestamp)

    def getHtmlReportColumnList(self, theDetailsFlag=True):
        columnList = [TaintTagEnum.getTaintString(self.tag)]
        columnList.append(TaintLogActionEnum.getActionString(self.action))
        columnList.append(self.scAddress)
        columnList.append(self.destination)
        columnList.append(TaintTagEnum.getTaintString(self.destinationTag))
        columnList.append(self.text)
        if theDetailsFlag: columnList.append(self.timestamp)
        if theDetailsFlag: columnList.append(self.stackTraceStr)
        return columnList

class SimulatorActionLogEntry(BaseLogEntry):
    timestamp = ''
    
    @staticmethod
    def makeInstallAction(pk,tm):
        return SimulatorInstallAppAction(package = pk,timestamp = tm)
    
    @staticmethod
    def makeSmsAction(number,content,timestamp):
        return SimulatorSmsAction(number = number,content = content,timestamp = timestamp)
    
    @staticmethod
    def makeGpsAction(x,y,timestamp):
        return SimulatorGpsMoveAction(timestamp = timestamp,x = x,y = y)
    
    @staticmethod
    def makeCallInAction(number,timestamp):
        return SimulatorCallInAction(number = number,timestamp = timestamp)

class SimulatorGpsMoveAction(SimulatorActionLogEntry):
    action = SimulatorActionEnum.SIMULATE_GPS_MOVE_ACTION
    x = 0.0
    y = 0.0
    
class SimulatorCallInAction(SimulatorActionLogEntry):
    action = SimulatorActionEnum.SIMULATE_PHONE_CALLIN_ACTION
    number = ""
    
class SimulatorSmsAction(SimulatorActionLogEntry):
    action = SimulatorActionEnum.SIMULATE_SEND_SMS_ACTION
    number = ""
    content = ""
    
class SimulatorInstallAppAction(SimulatorActionLogEntry):
    action = SimulatorActionEnum.INSTALL_APP_ACTION
    package = ""
# ================================================================================
# Json En-/Decoder
# ================================================================================
looker = {'__CallActionLogEntry__':CallActionLogEntry,
              '__CipherUsageLogEntry__':CipherUsageLogEntry,
              '__FileDescriptorLogEntry__':None,
              '__FileSystemLogEntry__':FileSystemLogEntry,
              '__NetworkSendLogEntry__':NetworkSendLogEntry,
              '__SSLLogEntry__':SSLLogEntry,
              '__SendSmsLogEntry__':SendSmsLogEntry,
              '__SimulatorGpsMoveAction__':SimulatorGpsMoveAction,
              '__SimulatorCallInAction__':SimulatorCallInAction,
              '__SimulatorSmsAction__':SimulatorSmsAction,
              
              #report objects
              "__AppReportEntry__":AppReportEntry,
              '__MainReportEntry__':MainReportEntry,
              }
 
 
class _JSONEncoder(json.JSONEncoder):
    
    def default(self, theObject):
        if hasattr(theObject, '_json'):
            res = {}
            if theObject._json == True:
                for key in theObject.__dict__:
                    if not key.startswith('_'):
                        res[key] = theObject.__dict__[key]
            else:
                for key in theObject._json:
                    res[key] = theObject.__dict__[key]
            res['__' + theObject.__class__.__name__ + '__'] = True
            return res
        return json.JSONEncoder.default(self, theObject)

def _JSONDecoder(theDict):
    objtype = None

    for t in theDict.keys():
        if t.startswith("__") and t.endswith("__") and t in looker:
            objtype = t
            break
        
    if objtype == None: return theDict
    
    obj = looker[objtype]()
    '''
    objstr = objtype[2:-2]
    klass = type(str(objstr),(object,),{})
    #object = looker[objstr]()
    obj = klass()
    '''

    '''
    # Log objects
    if '__CallActionLogEntry__' == type:
        object = CallActionLogEntry()
    elif '__CipherUsageLogEntry__' == type:
        object = CipherUsageLogEntry()
    elif '__FileDescriptorLogEntry__' == type:
        object = FileDescriptorLogEntry()
    elif '__FileSystemLogEntry__' == type:
        object = FileSystemLogEntry()
    elif '__NetworkSendLogEntry__' == type:
        object = NetworkSendLogEntry()
    elif '__SSLLogEntry__' == type:
        object = SSLLogEntry()
    elif '__SendSmsLogEntry__' == type:
        object = SendSmsLogEntry()
    elif '__SimulatorGpsMoveAction__' == type:
        object = SimulatorGpsMoveAction()
    elif '__SimulatorCallInAction__' == type:
        object = SimulatorCallInAction()
    elif '__SimulatorSmsAction__' == type:
        object = SimulatorSmsAction()

    # Report objects
    elif '__AppReportEntry__' == type:
        object = AppReportEntry()
    elif '__MainReportEntry__' == type:
        object = MainReportEntry()
        
    # Else...
    else:
        raise Exception('Unkown type \'%s\' found' % type)
    '''

    if not object: 
        print "unknow type "+type
        return theDict

    obj.__dict__.update(theDict)

    return obj


# ================================================================================
# Json Factory
# ================================================================================ 
class JsonFactory:
    def py2Json(self, theObject, theIndentFlag=False):
        if theIndentFlag:
            return json.dumps(theObject, cls=_JSONEncoder, indent=2, sort_keys=True)
        else:
            return json.dumps(theObject, cls=_JSONEncoder, sort_keys=True)

    def json2Py(self, theString):
        return json.loads(theString, object_hook=_JSONDecoder)
    
