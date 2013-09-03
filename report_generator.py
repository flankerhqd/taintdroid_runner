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

from common import Logger, LogLevel, SimulationSteps, Utils
from taintlog_json import *

import codecs

# ================================================================================
# Report Generator
# ================================================================================
class ReportGenerator:

    @staticmethod
    def generateMainReport(theFileName, theReportData):
        report = open(theFileName, "w")
        report.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>TaintDroid Runner Report</title></head><body><p>')
        report.write('<h1>TaintDroid Runner Report</h1>')

        report.write('<h2>Parameters</h2>')
        report.write('<li><b>Working Directory</b>: %s' % theReportData['workingDir'])
        report.write('<li><b>Time</b>: %s-%s - %s-%s' % (Utils.getDateAsString(theReportData['startTime']), Utils.getTimeAsString(theReportData['startTime']), Utils.getDateAsString(theReportData['endTime']), Utils.getTimeAsString(theReportData['endTime'])))
        report.write('<li><b>numThreads</b>: %d' % theReportData['numThreads'])
        report.write('<li><b>emulatorStartPort</b>: %d' % theReportData['emulatorStartPort'])
        report.write('<li><b>cleanImageDir</b>: %s' % theReportData['cleanImageDir'])

        report.write('<h2>Apps</h2>')
        report.write('<table><tr><th>ID</th><th>Package</th><th>APK Path</th><th>Call</th><th>Cipher</th><th>FS</th><th>Net</th><th>SSL</th><th>SMS</th><th>Errors</th></tr>')
        for app in theReportData['appList']:
            report.write('<tr><td><li><a href="%s">%06d</a></li></td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td>' % (app['reportName'], app['id'], app['appPackage'], app['appPath'], app['numCallAction'], app['numCipherUsage'], app['numFileSystem'], app['numNetwork'], app['numSSL'], app['numSMS'], app['numErrors']))
        report.write('</table>')
        
        report.write('<h2>Logs</h2>')
        report.write('<li><a href="%s">Main Log</li>' % (theReportData['mainLogFile']))
        for logFile in theReportData['threadLogFileList']:
            report.write('<li><a href="%s">%s</li>' % (logFile, logFile))
        report.write('</p></body></html>')        
    
    @staticmethod
    def generateAppReport(theFileName, theResultEntry):
        # Inits
        app = theResultEntry['app']
        log = None
        if theResultEntry.has_key('log'):
            log = theResultEntry['log']
        
        # Write report
        report = codecs.open(theFileName, "w", "utf-8")
        report.write('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>TaintDroid Runner Report for %s</title></head><body><p>' % app.getPackage())
        report.write('<h1>TaintDroid Runner Report for %s</h1>' % (app.getPackage()))
        
        report.write('<h2>Parameters</h2>')        
        report.write('<li><b>Package</b>: %s' % app.getPackage())
        report.write('<li><b>APK Name</b>: %s' % app.getApkFileName())
        report.write('<li><b>Path</b>: %s' % app.getApk())
        report.write('<li><b>Id</b>: %06d' % app.getId())
        report.write('<li><b>steps</b>: %s' % SimulationSteps.getStepsAsString(theResultEntry['steps']))
        report.write('<li><b>numMonkeyEvents</b>: %d' % theResultEntry['numMonkeyEvents'])
        report.write('<li><b>sleepTime</b>: %d' % theResultEntry['sleepTime'])
        report.write('<li><b>startTime</b>: %s-%s' % (Utils.getDateAsString(theResultEntry['startTime']), Utils.getTimeAsString(theResultEntry['startTime'])))
        report.write('<li><b>endTime</b>: %s-%s' % (Utils.getDateAsString(theResultEntry['endTime']), Utils.getTimeAsString(theResultEntry['endTime'])))
        report.write('<li><b>cleanImageDir</b>: %s' % theResultEntry['cleanImageDir'])        
        report.write('<li><b>MD5 (hex)</b>: %s' % app.getMd5Hash())
        report.write('<li><b>Sha256 (hex)</b>: %s' % app.getSha256Hash())
        report.write('<li><b>maxLogcatSize</b>: %d' % theResultEntry['maxLogcatSize'])        
        
        report.write('<h2>Log</h2>')
        if log is None:
            report.write('<h3>CallUsage</h3>')
            report.write('<h3>CipherUsage</h3>')
            report.write('<h3>FileSystem</h3>')
            report.write('<h3>Network</h3>')
            report.write('<h3>SSL</h3>')
            report.write('<h3>SMS</h3>')
        else:
            ReportGenerator.__generateReportLogTable(report,
                                                     'Call',
                                                     ['Tag', 'DialString', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=CallActionLogEntry)
                                                     )
            ReportGenerator.__generateReportLogTable(report,
                                                     'CipherUsage',
                                                     ['Tag', 'Mode', 'PlainText', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=CipherUsageLogEntry)
                                                     )
            ReportGenerator.__generateReportLogTable(report,
                                                     'FileSystem',
                                                     ['Tag', 'Action', 'File', 'Id', 'Data', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=FileSystemLogEntry)
                                                     )
            ReportGenerator.__generateReportLogTable(report,
                                                     'Network',
                                                     ['Tag', 'Action', 'Destination', 'Id', 'Data', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=NetworkSendLogEntry)
                                                     )
            ReportGenerator.__generateReportLogTable(report,
                                                     'SSL',
                                                     ['Tag', 'Action', 'Destination', 'Data', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=SSLLogEntry)
                                                     )
            ReportGenerator.__generateReportLogTable(report,
                                                     'SMS',
                                                     ['Tag', 'Action', 'Source', 'Destination', 'Dest Tag', 'Text', 'Timestamp', 'StackTrace'],
                                                     log.getLogEntryList(theType=SendSmsLogEntry)
                                                     )
        
        report.write('<h2>Errors</h2>')
        if theResultEntry.has_key('badCancelationFlag'):
            report.write('<li>Thread could not be finished</li>')
        for error in theResultEntry['errorList']:
            try:
                report.write('<li>%s</li>' % str(error))
            except UnicodeDecodeError, udErr:
                report.write('<li>Decode error: %s</li>' % str(udErr))
                report.write('<li>')
                report.write(error)
                report.write('</li>')
        
        report.write('</p></body></html>')

    @staticmethod
    def __generateReportLogTable(theReport, theTitle, theColumnList, theLogEntryList):
        theReport.write('<h3>%s</h3>' % (theTitle))
        theReport.write('<table>')

        theReport.write('<tr>')
        for column in theColumnList:
            theReport.write('<th><br>%s</b></th>' % (column))        
        theReport.write('</tr>')

        for logEntry in theLogEntryList:
            theReport.write('<tr>')
            for column in logEntry.getHtmlReportColumnList():
                theReport.write('<td>')
                if not column is None:
                    theReport.write(column)
                theReport.write('</td>')
            theReport.write('</tr>')
        
        theReport.write('</table>')
