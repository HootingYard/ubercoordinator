<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- The navigation file for the ebook reader's index. -->
  <!-- See http://www.idpf.org/epub/20/spec/OPF_2.0_latest.htm#Section2.4.1 -->
  
  <xsl:template match="/book">
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">
      
      <head> <meta name="dtb:uid" content="{@uuid}"/> </head>
      
      <docTitle><text><xsl:value-of select="title"/></text></docTitle>
      <docAuthor><text><xsl:value-of select="author"/></text></docAuthor>
      
      <navMap>
        <!-- Book content sections are turned into "navPoint" elements. -->
        <xsl:for-each select="contents/section">
          <xsl:call-template name="section-navPoints" />
        </xsl:for-each>
      </navMap>
    </ncx>
  </xsl:template>

  <!-- The navPoint for a section. Note that these can be nested. -->
  <xsl:template name="section-navPoints">
    <navPoint id="{generate-id(title)}">
      <navLabel> <text> <xsl:value-of select="title"/> </text> </navLabel>
      
      <!-- Which content page to land on when this navigation point is picked; -->
      <!-- either this section's file, or the first file in its subsections. -->
      <xsl:choose>
        <xsl:when test="@file"> <content src="Text/{@file}"/> </xsl:when>
        <xsl:otherwise> <content src="Text/{.//section/@file[1]}"/> </xsl:otherwise>
      </xsl:choose>

      <!-- subsections -->
      <xsl:for-each select="section">
        <xsl:call-template name="section-navPoints" />
      </xsl:for-each>
    </navPoint>
  </xsl:template>

  <xsl:template name="content-src">
  </xsl:template>
      
</xsl:stylesheet>
