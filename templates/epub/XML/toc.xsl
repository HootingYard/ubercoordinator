<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Content page at the beginning of the ebook, made from book.xml metadata -->
    <!-- The "sections" elements in "contents" describe the nesting of the book's contents  -->

    <!-- Sections with toc="no" attributes do not go in the contents page -->

    <xsl:template match="/book">
        <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <title>Contents</title>
                <meta name="author" content="{author/text()}"/>
                <meta name="description" content="{description/text()}"/>
                <meta name="language" content="{@language}"/>
                <meta name="date" content="{@date}"/>
                <meta http-equiv="content-type" content="text/html;charset=utf-8"/>
                <xsl:for-each select="styling/style">
                    <link href="../Styles/{@file}" rel="stylesheet" type="text/css"/>
                </xsl:for-each>
            </head>
            <body id="toc" class="toc">
                <h1>Contents</h1>

                <xsl:for-each select="contents/section[not(@toc='no')]">
                    <xsl:choose>
                        <xsl:when test="@separate='yes'">
                            <ul class="index-top-level">
                                <!-- Link to a separated top-level section -->
                                <li>
                                    <a href="#{generate-id(title)}">
                                        <strong>
                                            <xsl:value-of select="title"/>
                                        </strong>
                                    </a>
                                </li>
                            </ul>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:call-template name="top-level-section"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>

                <!-- Separated top-level sections -->
                <xsl:for-each select="contents/section[not(@toc='no') and @separate='yes']">
                    <h2 id="{generate-id(title)}">
                        <xsl:value-of select="title"/>
                    </h2>
                    <xsl:for-each select="section[not(@toc='no')]">
                        <xsl:call-template name="top-level-section"/>
                    </xsl:for-each>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>

    <!-- The first level of each top level section has no bullets -->
    <xsl:template name="top-level-section">
        <ul class="index-top-level">
            <li>
                <xsl:call-template name="page-link"/>
            </li>
        </ul>
        <xsl:call-template name="subsections"/>
    </xsl:template>

    <!-- deeper sections are in bulleted lists -->
    <xsl:template name="subsections">
        <xsl:if test="section">
            <ul class="index-inner-level">
                <xsl:for-each select="section[not(@toc='no')]">
                    <li>
                        <xsl:call-template name="page-link"/>
                        <xsl:call-template name="subsections"/>
                    </li>
                </xsl:for-each>
            </ul>
        </xsl:if>
    </xsl:template>

    <!-- Either a link to a text file or a subsection heading -->
    <xsl:template name="page-link">
        <xsl:choose>
            <xsl:when test="@file">
                <a href="{@file}">
                    <xsl:value-of select="title"/>
                </a>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="title"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
