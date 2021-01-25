<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- A page displaying the book's cover image full-screen. -->
  
  <xsl:template match="/book">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
      <head>
        <title>Cover</title>
        <meta name="author" content="{author/text()}" />
        <meta name="description" content="{description/text()}" />
        <meta name="language" content="{@language}" />
        <meta name="date" content="{date}" />
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        <xsl:for-each  select="style">
          <link href="../Styles/{@file}" rel="stylesheet" type="text/css" />
        </xsl:for-each>
      </head>
      <body>
        <div><img class="cover" src="../Images/cover.png" alt="Front cover of {title}" /></div>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
