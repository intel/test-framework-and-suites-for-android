<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output 
  method="html"
  encoding="ISO-8859-1"
  doctype-public="-//W3C//DTD HTML 4.01//EN"
  doctype-system="http://www.w3.org/TR/html4/strict.dtd"
  indent="yes" />
  
<xsl:template match="DeviceProperties">
  <html>
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
	</style>
  <body>
	<TABLE border="0"  class="summary" width="700">
		<TR>
			<TH colspan="3">
			<b>Device Properties List</b>
			</TH>
		</TR>
		<TR>
			<TH align="center"> Key Name</TH>
			<TH align="center"> Key Value</TH>
		</TR>
		<xsl:apply-templates select="property" />
	</TABLE>
  </body></html>
</xsl:template>

<xsl:template match="property">	
  <TR>
   <TD> <xsl:value-of select="@name" /></TD>
   <TD> <xsl:value-of select="@value" /></TD>
  </TR>
</xsl:template>
</xsl:stylesheet>