<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <head>
                <title>
                    <xsl:value-of select="TestReport/CampaignName"/>
                    test result for
                    <xsl:value-of select="TestReport/DeviceInfo/DeviceModel"/>
                    version
                    <xsl:value-of select="TestReport/DeviceInfo/SwRelease"/>
                </title>
                <style type="text/css">
                    table.summary {
                    font-family: verdana,arial,sans-serif;
                    font-size:11px;
                    color:#333333;
                    border-width: 1px;
                    border-color: #a9c6c9;
                    border-collapse: collapse;
                    }
                    table.summary th {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #a9c6c9;
                    background-color:#c4d3d5;
                    }
                    table.summary td {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #a9c6c9;
                    }
                    table.detail {
                    font-family: verdana,arial,sans-serif;
                    font-size:11px;
                    color:#333333;
                    border-width: 1px;
                    border-color: #a9c6c9;
                    border-collapse: collapse;
                    table-layout:fixed;
                    }
                    table.detail th {
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #a9c6c9;
                    background-color:#c4d3d5;
                    }
                    table.detail td {
                    padding: 0px;
                    }
                    .passed {
                    padding: 8px;
                    background-color:#8d4;

                    }
                    .failed {
                    padding: 8px;
                    background-color:#e88;

                    }
                    .warn {
                    padding: 8px;
                    background-color:#fa3;

                    }
                    .oddrowcolor{
                    background-color:#f6f6f6;
                    }
                    .evenrowcolor{
                    background-color:#eeeeee;
                    }
                    .bottom {
                    vertical-align: bottom;
                    }
                    a.popup {
                    position:relative;
                    text-decoration:none;
                    text-align:center;
                    font-size:11px;
                    }
                    a.popup:hover {
                    background: none;
                    z-index: 50;
                    }
                    a.popup span {
                    display: none;
                    }
                    a.popup:hover span {
                    display: block;
                    position: absolute;
                    top: -10px;
                    left: 40px;
                    font-family: Tahoma
                    text-align:justify;
                    font-size:12px;
                    font-weight:normal;
                    width:230px;
                    background: white;
                    padding: 5px;
                    border: 1px solid #62c0f4;
                    }

                </style>

            </head>
            <body>
                <h2>
                    <div style="font-family:Tahoma">
                        <br/>
                        <center>Test result for
                            <xsl:value-of select="TestReport/DeviceInfo/DeviceModel"/>
                            [Version:<xsl:value-of select="TestReport/DeviceInfo/SwRelease"/>]
                        </center>
                    </div>
                </h2>


                <table border="0" align="center">
                    <tr valign="center">


                        <td width="100%" valign="top" align="center">
                            <table border="0" cellpadding="10">
                                <tr align="center" valign="top">
                                    <td>
                                        <table border="0" style="font-family:Tahoma" class="summary" width="500"
                                               height="100%">
                                            <tr>
                                                <th colspan="3" bgcolor="#d1d190">
                                                    <b>Campaign Info</b>
                                                </th>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Campaign Name</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/CampaignInfo/CampaignName"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Campaign Type</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/CampaignInfo/CampaignType"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>User Email</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/CampaignInfo/UserEmail"/>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td>
                                        <table border="0" style="font-family:Tahoma" class="summary" width="600"
                                               height="100%">
                                            <tr>
                                                <th colspan="3" bgcolor="#d1d190">
                                                    <b>Bench Info</b>
                                                </th>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Bench Name</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/BenchInfo/BenchName"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Bench User</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/BenchInfo/BenchUser"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Bench IP</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/BenchInfo/BenchIp"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Bench OS</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/BenchInfo/BenchOs"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>ACS Version</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/BenchInfo/AcsVersion"/>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                <tr valign="top">
                                    <td>
                                        <table border="0" style="font-family:Tahoma" class="summary" width="500"
                                               height="100%">
                                            <tr>
                                                <th colspan="3" bgcolor="#d1d190">
                                                    <b>Statistics Info</b>
                                                </th>
                                            </tr>
                                            <tr>
                                                <td/>
                                                <td style="font-size:10px;">
                                                    Number (count)
                                                </td>
                                                <td style="font-size:10px;">
                                                    Rate (%)
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>TC Passed</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of
                                                            select="count(TestReport/TestCase[normalize-space(Verdict)='PASS'])"/>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/Statistics/PassRate"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>TC Failed</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of
                                                            select="count(TestReport/TestCase[normalize-space(Verdict)='FAIL'])"/>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/Statistics/FailRate"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>TC Blocked</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of
                                                            select="count(TestReport/TestCase[normalize-space(Verdict)='BLOCKED'])"/>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/Statistics/BlockedRate"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Start Execution date</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/StartExecutionDate"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Start Execution time</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/StartExecutionTime"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Execution time</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/ExecutionTime"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Critical failure nb</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/CriticalFailureCount"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Mean time before failure</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/MeanTimeBeforeFailure"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Time to first critical failure</i>
                                                </td>
                                                <td style="font-size:14px;" colspan="2">
                                                    <xsl:value-of select="TestReport/Statistics/TimeToCriticalFailure"/>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td>
                                        <table border="0" style="font-family:Tahoma" class="summary" width="600">
                                            <tr>
                                                <th colspan="3" bgcolor="#d1d190">
                                                    <b>Device Info</b>
                                                </th>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Device model</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/DeviceModel"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Software release</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/SwRelease"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Device Identifier</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/DeviceId"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Imei</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/Imei"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Model Number</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/ModelNumber"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Firmware Version</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/FwVersion"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Baseband Version</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/BasebandVersion"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>Kernel Version</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/KernelVersion"/>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="font-size:14px;">
                                                    <i>ACS Agent Version</i>
                                                </td>
                                                <td style="font-size:14px;">
                                                    <xsl:value-of select="TestReport/DeviceInfo/AcsAgentVersion"/>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                <h3>
                    <div style="font-family:Tahoma">Details</div>
                </h3>
                <hr/>
                <table border="0" class="detail" style="table-layout:fixed" width="99%" align="center">
                    <tr>
                        <th width="100">Date</th>
                        <th width="300">ID</th>
                        <th width="50%">Parameters</th>
                        <th width="2%">Exec</th>
                        <th width="2%">Max Retry</th>
                        <th width="3%">Accept</th>
                        <th width="15%">Expected Verdict</th>
                        <th width="15%">Obtained Verdict</th>
                        <th width="15%">Reported Verdict</th>
                        <th width="50%">Comment</th>
                    </tr>
                    <xsl:for-each select="TestReport/TestCase">
                        <tr height="25">
                            <xsl:choose>
                                <xsl:when test="(position() mod 2) = 0">
                                    <xsl:attribute name="bgcolor">#E0FFFF</xsl:attribute>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:attribute name="bgcolor">#FFFFFF</xsl:attribute>
                                </xsl:otherwise>
                            </xsl:choose>
                            <td>
                                <xsl:value-of select="StartExecutionDate"/>
                                -
                                <xsl:value-of select="StartExecutionTime"/>
                            </td>
                            <td>
                                <acronyms>
                                    <xsl:attribute name="title">
                                        <xsl:value-of select="Description"/>
                                    </xsl:attribute>
                                    <xsl:value-of select="@id"/>
                                </acronyms>
                            </td>
                            <td>
                                <xsl:value-of select="Parameters"/>
                            </td>
                            <td align="center">
                                <xsl:value-of select="Exec"/>
                            </td>
                            <td align="center">
                                <xsl:value-of select="MaxAttempt"/>
                            </td>
                            <td align="center">
                                <xsl:value-of select="Acceptance"/>
                            </td>
                            <td align="center">
                                <xsl:value-of select="ExpectedVerdict"/>
                            </td>
                            <td align="center">
                                <xsl:value-of select="ObtainedVerdict"/>
                            </td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="normalize-space(Verdict)='PASS'">
                                        <div style="color:green">
                                            <xsl:value-of select="Verdict"/>
                                        </div>
                                    </xsl:when>
                                    <xsl:when test="normalize-space(Verdict)='FAIL'">
                                        <div style="color:red">
                                            <xsl:value-of select="Verdict"/>
                                        </div>
                                    </xsl:when>
                                    <xsl:when test="normalize-space(Verdict)='NOT EXECUTED'">
                                        <div style="color:black">
                                            <xsl:value-of select="Verdict"/>
                                        </div>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <div style="color:#FFD700">
                                            <xsl:value-of select="normalize-space(Verdict)"/>
                                        </div>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </td>
                            <td>
                                <xsl:choose>
                                    <xsl:when test="Comment/powerurl">
                                        <div>
                                            <a>
                                                <xsl:attribute name="href">
                                                    <xsl:value-of select="Comment/powerurl"/>PowerMeasurementData.xml
                                                </xsl:attribute>
                                                <xsl:attribute name="class">popup</xsl:attribute>
                                                <xsl:attribute name="target">_blank</xsl:attribute>
                                                <xsl:value-of select="Comment/powerurl"/>
                                                <xsl:variable name="folder" select="Comment/powerurl"/>
                                                <span>
                                                    <table border="0" style="font-family:Tahoma" class="summary">
                                                        <tr>
                                                            <th colspan="3" bgcolor="#d1d190">
                                                                <b>Power Measurement Data</b>
                                                            </th>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <i>AverageMeasure</i>
                                                            </td>
                                                            <td style="font-size:14px;">
                                                                <xsl:value-of
                                                                        select="document(concat($folder, 'PowerMeasurementData.xml'))/PowerMeasurementData/PwrRail/AverageMeasure"/>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <i>FailAverageMeaure</i>
                                                            </td>
                                                            <td style="font-size:14px;">
                                                                <xsl:value-of
                                                                        select="document(concat($folder, 'PowerMeasurementData.xml'))/PowerMeasurementData/PwrRail/FailAverageMeasure"/>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <i>TargetAverageMeasure</i>
                                                            </td>
                                                            <td style="font-size:14px;">
                                                                <xsl:value-of
                                                                        select="document(concat($folder, 'PowerMeasurementData.xml'))/PowerMeasurementData/PwrRail/TargetAverageMeasure"/>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <i>MinMeasure</i>
                                                            </td>
                                                            <td style="font-size:14px;">
                                                                <xsl:value-of
                                                                        select="document(concat($folder, 'PowerMeasurementData.xml'))/PowerMeasurementData/PwrRail/MinMeasure"/>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <i>MaxMeasure</i>
                                                            </td>
                                                            <td style="font-size:14px;">
                                                                <xsl:value-of
                                                                        select="document(concat($folder, 'PowerMeasurementData.xml'))/PowerMeasurementData/PwrRail/MaxMeasure"/>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </span>
                                            </a>
                                        </div>
                                    </xsl:when>
                                    <xsl:when test="Comment/emurl">
                                        <a>
                                            <xsl:attribute name="href">
                                                <xsl:value-of select="Comment/emurl"/>Energy_Management_data_report.xml
                                            </xsl:attribute>
                                            <xsl:attribute name="class">popup</xsl:attribute>
                                            <xsl:attribute name="target">_blank</xsl:attribute>
                                            <xsl:value-of select="Comment/emurl"/>
                                        </a>
                                    </xsl:when>
                                    <xsl:when test="Comment/SubComment">
                                        <ul type="circle">
                                            <xsl:for-each select="Comment/SubComment">
                                                <li>
                                                    <xsl:value-of select="."/>
                                                </li>
                                            </xsl:for-each>
                                        </ul>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <div>
                                            <xsl:value-of select="Comment"/>
                                        </div>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
