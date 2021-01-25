<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- default title page -->
    <!-- Title, description and author from the book.xml file. -->

    <xsl:template match="/book">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
            <head>
                <title>Title Page</title>
                <meta name="author" content="{author/text()}"/>
                <meta name="description" content="{description/text()}"/>
                <meta name="language" content="{@language}"/>
                <meta name="date" content="{date}"/>
                <meta http-equiv="content-type" content="text/html;charset=utf-8"/>
                <xsl:for-each select="styling/style">
                    <link href="../Styles/{@file}" rel="stylesheet" type="text/css"/>
                </xsl:for-each>
            </head>
            <body>
                <h1 id="book-title">
                    <xsl:value-of select="title"/>
                </h1>

                <div class="linebreaks">
                    <p>
                        <xsl:value-of select="description"/>
                    </p>

                    <p>
                        <xsl:value-of select="author"/>
                    </p>
                </div>
            </body>
        </html>
    </xsl:template>

</xsl:stylesheet>
