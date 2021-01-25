<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:regexp="http://exslt.org/regular-expressions"
                extension-element-prefixes="regexp">

  <!-- This expands the book's book.xml metadata into the EPUB's Open Packaging Format file -->
  <!-- see http://www.idpf.org/epub/20/spec/OPF_2.0_latest.htm -->
  
  <xsl:template match="/book">
    <package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id">
      
      <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:contributor opf:role="edt">
          <xsl:value-of select="editor"/>
        </dc:contributor>
        <dc:creator opf:file-as="{author/@file-as}" opf:role="aut">
          <xsl:value-of select="author"/>
        </dc:creator>
        <dc:date> <xsl:value-of select="@date"/> </dc:date>
        <dc:description> <xsl:value-of select="description"/> </dc:description>
        <dc:identifier id="uuid_id" opf:scheme="uuid"> <!-- this could also be IBSN -->
          <xsl:value-of select="@uuid"/>  
        </dc:identifier>
        <dc:language> <xsl:value-of select="@language"/> </dc:language>
        <dc:publisher> <xsl:value-of select="publisher"/> </dc:publisher>
        <dc:subject> <xsl:value-of select="subject"/> </dc:subject>
        <dc:title> <xsl:value-of select="title"/> </dc:title>

        <!-- id of cover image, which is always 'cover.png' -->
        <meta name="cover" content="{generate-id(//image[file='cover.png'])}"/>  
      </metadata>

      <!-- A list of all the files in the EPUB -->
      <manifest>
        <item id="ncx" media-type="application/x-dtbncx+xml" href="toc.ncx"/>

        <!-- CSS files and fonts -->
        <xsl:for-each select="//style">
          <item id="{generate-id()}" href="Styles/{@file}" media-type="text/css"/>
        </xsl:for-each>
        <xsl:for-each select="//font">
          <item id="{generate-id()}" href="Fonts/{@file}" media-type="application/font-sfnt"/>
        </xsl:for-each>

        <!-- text files (filenames taken from contents sections that refer to files) -->
        <xsl:for-each select="//section[@file]">
          <item id="{generate-id()}" href="Text/{@file}" media-type="application/xhtml+xml"/>
        </xsl:for-each>

        <!-- image files (note: only PNG, GIF and JPEG files are are allowed in EPUBs) -->
        <xsl:for-each select="//image">
          <xsl:choose>  <!-- choose the right media-type based on file extension -->
            <xsl:when test="regexp:test(@file, '.*\.(png|PNG)$')">
              <item id="{generate-id()}" href="Images/{@file}" media-type="image/png"/>
            </xsl:when>
            <xsl:when test="regexp:test(@file, '.*\.(jpe?g|JPE?G)$')">
              <item id="{generate-id()}" href="Images/{@file}" media-type="image/jpeg"/>
            </xsl:when>
            <xsl:when test="regexp:test(@file, '.*\.(gif|GIF)$')">
              <item id="{generate-id()}" href="Images/{@file}" media-type="image/gif"/>
            </xsl:when>
          </xsl:choose>
        </xsl:for-each>
      </manifest>

      <!-- list of idenifiers for each text file in reading order -->
      <spine toc="ncx">
        <xsl:for-each select="//section[@file]">
          <itemref idref="{generate-id()}"/>
        </xsl:for-each>
      </spine>
      
      <!-- Various special pages. -->
      <guide>
        <reference type="cover" title="Cover" href="Text/cover.html"/>
        <reference type="title-page" title="Title Page" href="Text/title.html"/>
        <reference type="copyright-page" title="Copyright" href="Text/copyright.html" />
        <reference type="toc" title="Table of Contents" href="Text/toc.html" />

        <!-- The "text" reference shows where to first open the Ebook. -->
        <xsl:choose>
          <xsl:when test="contents/open-at">
            <!-- when there is an "open-at" element specified, open there -->
            <reference type="text" title="Opening Page"
                       href="Text/{contents/open-at/@file}" />
          </xsl:when>
          <xsl:otherwise>
            <!-- othwise open on the first page in table of contents -->
            <reference type="text" title="Beginning"
                       href="Text/{//section[not(@toc='no')][1]/@file}" />
          </xsl:otherwise>
        </xsl:choose>
      </guide>
      
    </package>
  </xsl:template>
  
</xsl:stylesheet>
