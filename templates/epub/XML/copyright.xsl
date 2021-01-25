<?xml version="1.0" encoding="utf-8" standalone="no"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <!-- Copyright page created from book.xsl metadata. -->

    <xsl:template match="/book">

        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
            <head>
                <title>Copyright</title>
                <meta name="author" content="{author/text()}"/>
                <meta name="description" content="{description/text()}"/>
                <meta name="language" content="{@language}"/>
                <meta name="date" content="{@date}"/>
                <meta http-equiv="content-type" content="text/html;charset=utf-8"/>

                <xsl:for-each select="styling/style">
                    <link href="../Styles/{@file}" rel="stylesheet" type="text/css"/>
                </xsl:for-each>
            </head>
            <body>
                <div class="linebreaks">
                    <p id="book-title">
                        <strong>
                            <xsl:value-of select="title"/>
                        </strong>
                    </p>

                    <p>
                        <a href="{author/@href}" id="author">
                            <xsl:value-of select="author"/>
                        </a>
                    </p>

                    <hr/>

                    <!-- book/license contains a few paragraphs explaining the license or copyright -->
                    <xsl:for-each select="license/p">
                        <xsl:copy-of select="."/>
                    </xsl:for-each>

                    <p>
                        Published by <xsl:value-of select="publisher"/>,
                        <xsl:value-of select="@year"/>
                    </p>
                </div>
            </body>
        </html>

    </xsl:template>

</xsl:stylesheet>
