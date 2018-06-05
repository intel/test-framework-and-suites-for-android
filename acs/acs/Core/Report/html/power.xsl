<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/pnp">
        <html>
        <head>
        <title>PowerMeasurement results</title>
        <style type="text/css">
           table.summary {
            font-family: verdana,arial,sans-serif;
            font-size:12pt;
            color:#333333;
            border-width: 1px;
            border-color: #a9c6c9;
            border-collapse: collapse;
            }
            table.summary th {
                font-size: 15pt;
                border-width: 1px;
                border-style: solid;
                border-color: #a9c6c9;
                background-color:#c4d3d5;
            }
            table.summary td {
                padding-left: 3px;
                padding-right: 3px;
                border-width: 1px;
                border-style: solid;
                border-color: #a9c6c9;
            }

            table tr td {
                vertical-align: top;
                }
            #menu{
                float: left;
                width: 400px;
                border: 1px solid #000;
                margin: 2px;
                padding: 2px;
            }
            #container {
                margin: 0;
                padding-left: 0;
                font-size: 10pt;
                font-family: Verdana, sans-serif;
            }
            #test_cases{
                float: left;
                border: 1px solid #000;
            }

            #tclist ul,
            #tclist li {
                float: left;
                clear: both;
                margin: 2px;
                color: #339;
                font-weight: bold;
            }
            #tclist li {
                 padding-right: 10px;
            }
            #container a.ghost  {
                color: #555;
                font-style: italic;
                text-decoration: none;
            }
            #container a.current  {
                color: black;
                padding: 1px;
                background-color: #eee;
                text-decoration: none;
            }

            #container .on {
                display: block;
            }
            #container .off {
                display: none;
            }

            #power_analyzer_tool,
            .sysdebug {
                float: left;
                margin: 5px;
            }

            table.alert,
            .alert {
               color: red;
           }

           .line {
              clear: both;
           }
           .data {
              white-space: pre;
              font-family: Courier, monospace;
              font-size: 11pt;
           }
        </style>
        <script type="text/javascript">
        <![CDATA[
        function showcontent(eltId) {
            testcases = document.getElementsByClassName("testcase");
            arrIds = new Array();
            for (i=0; i < testcases.length; i++) {
                arrIds[i] = testcases[i].id;
            }
            intNbLinkElt = new Number(arrIds.length);
            arrClassLink = new Array('current','ghost');
            strLinkId = new String();
            for (i=0; i < intNbLinkElt; i++) {
                strLinkId = "_" + arrIds[i];
                if ( strLinkId == eltId) {
                    document.getElementById(strLinkId).className = arrClassLink[0];
                    document.getElementById(arrIds[i]).className = 'on testcase';
                } else {
                    document.getElementById(strLinkId).className = arrClassLink[1];
                    document.getElementById(arrIds[i]).className = 'off testcase';
                }
            }
        }
        ]]>
        </script>
        </head>
        <body>
            <div id="container">
                <div id="menu">
                    <ul id="tclist">
                        <xsl:for-each select="TestCase">
                            <xsl:variable name="id">
                                <xsl:text>_</xsl:text><xsl:value-of select="@id" />_<xsl:value-of select="position()" />
                            </xsl:variable>
                            <xsl:variable name="class">
                                <xsl:if test="position()=1">current</xsl:if>
                                <xsl:if test="position()!=1">ghost</xsl:if>
                            </xsl:variable>
                            <li>
                                <a class="{$class}" id="{$id}" onclick="showcontent(this.id)" href="#">
                                    <xsl:value-of select="@id" /><br />
                                    <i>(<xsl:value-of select="@date" />)</i>

                                </a>
                            </li>
                        </xsl:for-each>
                    </ul>
                </div>
                <div id="test_cases">
                    <xsl:for-each select="TestCase">
                        <xsl:variable name="id">
                            <xsl:value-of select="@id" />_<xsl:value-of select="position()" />
                        </xsl:variable>
                        <xsl:variable name="class">
                            <xsl:if test="position()=1">on</xsl:if>
                            <xsl:if test="position()!=1">off</xsl:if>
                        </xsl:variable>
                        <div id="{$id}" class="{$class} testcase">
                            <h1><xsl:value-of select="@id" /></h1>
                            <xsl:if test="@duration != ''">
                                <h2>Test duration: <xsl:value-of select="@duration" />s</h2>
                            </xsl:if>
                            <xsl:apply-templates select="PowerAnalyzerTool"/>
                            <xsl:apply-templates select="scores"/>
                            <xsl:apply-templates select="SysDebug"/>
                        </div>
                    </xsl:for-each>
                </div>
            </div>
        </body>
        </html>
    </xsl:template>

    <xsl:template match="PowerAnalyzerTool">
        <div id="power_analyzer_tool">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="6"><b>Power Measurement Data</b></th></tr>
                <tr>
                    <td><b>Power rail</b></td>
                    <td><b>AverageMeasure (mA)</b></td>
                    <td><b>MinMeasure (mA)</b></td>
                    <td><b>MaxMeasure (mA)</b></td>
                    <td><b>FailAverageMeasure (mA)</b></td>
                    <td><b>TargetAverageMeasure (mA)</b></td>
                </tr>
                <xsl:for-each select="PwrRail">
                <tr>
                    <td><xsl:value-of select="@name"/></td>
                    <td><xsl:value-of select="@average"/></td>
                    <td><xsl:value-of select="@min"/></td>
                    <td><xsl:value-of select="@max"/></td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="@failure != ''">
                                <xsl:value-of select="@failure"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>Undefined</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="@target != ''">
                                <xsl:value-of select="@target"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>Undefined</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </tr>
                </xsl:for-each>
            </table>
            <table border="0" class="summary">
                <xsl:for-each select="PwrIndicators">
                <tr bgcolor="#d1d190"><th colspan="{count(@*)}"><b>Power indicators :</b></th></tr>
                <tr>
                    <xsl:for-each select="@*">
                    <td><b><xsl:value-of select="name()"/></b></td>
                    </xsl:for-each>
                </tr>
                <tr>
                    <xsl:for-each select="@*">
                    <td><xsl:value-of select="."/></td>
                    </xsl:for-each>
                </tr>
                </xsl:for-each>
            </table>
        </div>
        <xsl:for-each select="PwrGraph">
            <div id="power_graph_{@dir}">
                <div class="line">
                   <iframe class="powergraph" src="{@dir}/power_graph.html" width="1250px" height="550px"></iframe>
                </div>
            </div>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="scores">
        <div class="scores_container">
            <div class="line">
                <table border="0" class="summary">
                    <tr><th colspan="5"><b>Performances results</b></th></tr>
                    <tr>
                        <td><b>Name</b></td>
                        <td><b>Value</b></td>
                        <td><b>Failure</b></td>
                        <td><b>Target</b></td>
                        <td><b>Runs</b></td>
                    </tr>
                    <xsl:for-each select="item" >
                    <tr>
                        <td><xsl:apply-templates select="@name" /></td>
                        <td><xsl:apply-templates select="@value" /></td>
                        <td>
                            <xsl:choose>
                                <xsl:when test="@failure != ''">
                                    <xsl:value-of select="@failure"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Undefined</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </td>
                        <td>
                            <xsl:choose>
                                <xsl:when test="@target != ''">
                                    <xsl:value-of select="@target"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Undefined</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </td>
                        <td><xsl:apply-templates select="@runs" /></td>
                    </tr>
                    </xsl:for-each>
                </table>
            </div>
        </div>
    </xsl:template>

    <xsl:template match="SysDebug">
        <div class="sysdebug_container">
            <div class="line">
                <xsl:apply-templates select="Residencies" />
                <xsl:apply-templates select="thermals" />
            </div>
            <div class="line">
                <xsl:apply-templates select="CrashInfo" />
                <xsl:apply-templates select="S3Failures" />
                <xsl:apply-templates select="ActiveWakeupSource" />
            </div>
            <div class="line">
                <xsl:apply-templates select="WakeLocks" />
            </div>
            <div class="line">
                <xsl:apply-templates select="Alarms" />
            </div>
            <div class="line">
                <xsl:apply-templates select="Pmu" />
            </div>
            <div class="line">
                <xsl:apply-templates select="Dstates" />
            </div>
        </div>
    </xsl:template>

    <xsl:template match="Residencies">
        <div class="sysdebug">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="4"><b>Residency results</b></th></tr>
                <tr>
                    <td><b>Mode</b></td>
                    <td><b>Wakup Count</b></td>
                    <td><b>Sleep Time (s)</b></td>
                    <td><b>Residency (%)</b></td>
                </tr>
                <xsl:for-each select="Residency">
                    <tr>
                        <td><xsl:value-of select="@mode"/></td>
                        <td><xsl:value-of select="@wakup_count"/></td>
                        <td><xsl:value-of select="@sleep_time"/></td>
                        <td><xsl:value-of select="@residency"/></td>
                    </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>

    <xsl:template match="thermals">
        <div class="sysdebug">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="4"><b>Thermals results</b></th></tr>
                <tr>
                    <td><b>Name</b></td>
                    <td><b>Value (°C)</b></td>
                </tr>
                <xsl:for-each select="thermal">
                    <tr>
                        <td><xsl:value-of select="@name"/></td>
                        <td><xsl:value-of select="@value"/></td>
                    </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>

    <xsl:template match="WakeLocks">
        <div class="sysdebug">
            <xsl:if test="count(WakeLock) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th><b>Wakelocks</b></th></tr>
                <tr><td><b>No WakeLocks occurs during measure</b></td></tr>
            </table>
            </xsl:if>
            <xsl:if test="count(WakeLock) != 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="7"><b>Wakelocks</b></th></tr>
                <tr>
                    <td><b>Name</b></td>
                    <td><b>Acquired</b></td>
                    <td><b>Released</b></td>
                    <td><b>Spent time (ms)</b></td>
                </tr>
                <xsl:for-each select="WakeLock">
                    <tr>
                        <td><xsl:value-of select="@name"/></td>
                        <td><xsl:value-of select="@acquired"/></td>
                        <td><xsl:value-of select="@released"/></td>
                        <td>
                            <span style="float:right">
                                <xsl:value-of select="format-number(@spent, '#.000')"/>
                            </span>
                        </td>
                    </tr>
                </xsl:for-each>
            </table>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="Alarms">
        <div class="sysdebug">
            <xsl:if test="count(alarm) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th><b>Alarms</b></th></tr>
                <tr><td><b>No alarms during measure</b></td></tr>
            </table>
            </xsl:if>
            <xsl:if test="count(alarm) != 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="7"><b>Alarms</b></th></tr>
                <tr>
                    <td><b>Intent</b></td>
                    <td><b>Pkg</b></td>
                    <td><b>Date</b></td>
                </tr>
                <xsl:for-each select="alarm">
                    <tr>
                        <td><xsl:value-of select="@intent"/></td>
                        <td><xsl:value-of select="@pkg"/></td>
                        <td><xsl:value-of select="@date"/></td>
                    </tr>
                </xsl:for-each>
            </table>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="S3Failures">
        <div class="sysdebug">
        <xsl:if test="count(failure) = 0">
        <table border="0" class="summary">
            <tr bgcolor="#d1d190"><th><b>S3 Failures</b></th></tr>
            <tr><td><b>No S3 Failure occurs during measure</b></td></tr>
        </table>
        </xsl:if>
        <xsl:if test="count(failure) != 0">
            <table border="0" class="summary alert">
                <tr bgcolor="#d1d190"><th colspan="3"><b>S3 Failures</b></th></tr>
                <tr>
                    <td><b>Device</b></td>
                    <td><b>Date</b></td>
                    <td><b>Reason</b></td>
                </tr>
                <xsl:for-each select="failure">
                <tr>
                    <td><xsl:value-of select="@device"/></td>
                    <td><xsl:value-of select="@date"/></td>
                    <td><xsl:value-of select="@reason"/></td>
                </tr>
                </xsl:for-each>
            </table>
        </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="ActiveWakeupSource">
        <div class="sysdebug">
        <xsl:if test="count(failure) = 0">
        <table border="0" class="summary">
            <tr bgcolor="#d1d190"><th><b>Active wakeup sources</b></th></tr>
            <tr><td><b>No active wakeup source during measure</b></td></tr>
        </table>
        </xsl:if>
        <xsl:if test="count(failure) != 0">
            <table border="0" class="summary alert">
                <tr bgcolor="#d1d190"><th colspan="3"><b>Active wakeup sources</b></th></tr>
                <tr>
                    <td><b>Wakeup Source</b></td>
                    <td><b>Date</b></td>
                </tr>
                <xsl:for-each select="failure">
                <tr>
                    <td><xsl:value-of select="@wakeupsource"/></td>
                    <td><xsl:value-of select="@date"/></td>
                </tr>
                </xsl:for-each>
            </table>
        </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="SState">
        <xsl:if test="count(SubSystem) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190">
                    <th><b><xsl:value-of select="@name" /></b></th>
                </tr>
                <tr><td><b>No Pmu Stats log dumped during measure</b></td></tr>
            </table>
        </xsl:if>
        <xsl:if test="count(SubSystem) != 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190">
                    <th colspan="3"><b><xsl:value-of select="@name" /></b></th>
                </tr>
                <tr>
                    <td><b>Subsystem</b></td>
                    <td><b>Initial value</b></td>
                    <td><b>History</b></td>
                </tr>
                <xsl:for-each select="SubSystem">
                <tr>
                    <td><xsl:value-of select="@name"/></td>
                    <td><xsl:value-of select="@initial_value"/></td>
                    <td><xsl:value-of select="@history"/></td>
                </tr>
                </xsl:for-each>
            </table>
        </xsl:if>
    </xsl:template>

    <xsl:template name="tmplSState">
        <xsl:param name="sstate" />
        <xsl:apply-templates select="SState[@name = $sstate]" />
    </xsl:template>

    <xsl:template match="Pmu">
        <div class="sysdebug">
        <xsl:if test="count(SState) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th><b>Pmu Stats Log</b></th></tr>
                <tr><td><b>No Pmu Stats log dumped during measure</b></td></tr>
            </table>
        </xsl:if>
        <xsl:if test="count(SState) != 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="{count(SState)}"><b>Pmu Stats Log</b></th></tr>
                <tr>
                <xsl:for-each select="SState">
                    <td><xsl:apply-templates select="." /></td>
                </xsl:for-each>
                </tr>
            </table>
        </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="CrashInfo">
        <div class="sysdebug">
            <xsl:if test="count(crash) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th><b>CrashInfo</b></th></tr>
                <tr><td><b>No Crash during measure</b></td></tr>
            </table>
            </xsl:if>
            <xsl:if test="count(crash) != 0">
                <table border="0" class="summary">
                    <tr bgcolor="#d1d190"><th colspan="7"><b>CrashInfo</b></th></tr>
                    <tr>
                        <td><b>Id</b></td>
                        <td><b>Date</b></td>
                        <td><b>Event Name</b></td>
                        <td><b>Type</b></td>
                        <td><b>data0</b></td>
                        <td><b>data1</b></td>
                        <td><b>data2</b></td>
                    </tr>
                    <xsl:for-each select="crash">
                    <tr>
                        <td><xsl:value-of select="@id"/></td>
                        <td><xsl:value-of select="@date"/></td>
                        <td><xsl:value-of select="@eventname"/></td>
                        <td><xsl:value-of select="@type"/></td>
                        <td><xsl:value-of select="@data0"/></td>
                        <td><xsl:value-of select="@data1"/></td>
                        <td><xsl:value-of select="@data2"/></td>
                    </tr>
                    </xsl:for-each>
                </table>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template match="Dstates">
        <div class="sysdebug">
        <xsl:if test="count(device) = 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th><b>D-states</b></th></tr>
                <tr><td><b>D-states are not available</b></td></tr>
            </table>
        </xsl:if>
        <xsl:if test="count(device) != 0">
            <table border="0" class="summary">
                <tr bgcolor="#d1d190"><th colspan="3"><b>D-states</b></th></tr>
                <xsl:for-each select="device">
                <tr>
                    <td class="data"><xsl:value-of select="@line"/></td>
                </tr>
                </xsl:for-each>
            </table>
        </xsl:if>
        </div>
    </xsl:template>

</xsl:stylesheet>

