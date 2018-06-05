<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
   <html>
   <head>
   <title>EnergyManagementData</title>
   <style type="text/css">
   table.summary td {
      border-width: 1px;
      padding: 1px;
      border-style: dashed;
      border-color: green;
      background-color: white;
      -moz-border-radius: 3px 3px 3px 3px;
   }
   </style>
   </head>
   <body>
   <div style="position:absolute;left:400px;top:10px;">
   <xsl:for-each select="EnergyManagementData/Measurements/Measurement">
   <table border="0" style="font-family:Tahoma" class="summary" width="500">
      <tr><th colspan="3" bgcolor="#d1d190"><a><xsl:attribute name="name">#<xsl:value-of select="@name" /></xsl:attribute><b><xsl:value-of select="@name" /></b></a></th></tr>
      <tr><td style="font-size:12px;" width="100"><i>Test</i></td><td  style="font-size:14px;"><xsl:value-of select="Test" /></td></tr>
      <tr><td  style="font-size:12px;"><i>Comment</i></td><td style="font-size:14px;"><xsl:value-of select="Comment" /></td></tr>
      <tr><td  style="font-size:12px;"><i>LowLimit</i></td><td style="font-size:14px;"><xsl:value-of select="LowLimit" /></td></tr>
      <tr><td  style="font-size:12px;"><i>HighLimit</i></td><td style="font-size:14px;"><xsl:value-of select="HighLimit" /></td></tr>
      <tr><td  style="font-size:12px;"><i>ExpectedValue</i></td><td style="font-size:14px;"><xsl:value-of select="ExpectedValue" /></td></tr>
	  <tr><td  style="font-size:12px;"><i>Verdict</i></td><td style="font-size:14px;"><xsl:value-of select="Verdict" /></td></tr>
   </table>
   </xsl:for-each>
   </div>
  </body>
  </html>

</xsl:template>
</xsl:stylesheet>
