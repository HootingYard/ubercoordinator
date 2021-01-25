<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <xsl:template match="/book">
    
    <html>
      <head>
        <title></title>
        <meta name="author" content="{author/text()}" />
        <meta name="description" content="{description/text()}" />
        <meta name="language" content="{@language}" />
        <meta name="date" content="" />
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        <xsl:for-each select="styling/style">
          <link href="../Styles/{@file}" rel="stylesheet" type="text/css" />
        </xsl:for-each>
      </head>
      
      <body>
        <div id="heading" />
        <div id="content" />
        <div id="attribution" />
      </body>
    </html>
    
  </xsl:template>

</xsl:stylesheet>
