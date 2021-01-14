<?xml version="1.0" encoding="UTF-8"?>  <!-- -*-xml-*- -->
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">

    <sch:title>Schematron Schema for Validating KeyML XHTML Pages.</sch:title>

    <!-- This performs tests on KeyML XHTML files that the bigbook.dtd cannot.
         It checks for odd inline formatting, empty elements, missing metadata,
         relative links pointing to the wrong places, malformed illustrations
         and verse and missing or misused attributes.
    -->

    <sch:ns uri="http://www.w3.org/1999/xhtml" prefix="xhtml"/>

    <!-- This is a handy Xpath extension that lxml provides: -->
    <sch:ns uri="http://exslt.org/regular-expressions" prefix="regexp"/>


    <sch:pattern id="head-and-metadata">
        <sch:title>Test that the head element contains the necessary metadata.</sch:title>
        <!-- Epub requires these meta tags to present. -->

        <sch:rule context="/ xhtml:html / xhtml:head">
            <sch:assert test="count(xhtml:title) = 1">
                There is one title tag.
            </sch:assert>

            <sch:assert test="count(xhtml:meta [@name = 'author']) = 1">
                There is one author tag.
            </sch:assert>

            <sch:assert test="count(xhtml:meta [@name = 'description']) = 1">
                There is one description tag.
            </sch:assert>

            <sch:assert test="count(xhtml:meta [@name = 'language']) = 1">
                There is one language tag.
            </sch:assert>

            <sch:assert test="count(xhtml:meta [@name = 'date']) = 1">
                There is one date tag.
            </sch:assert>

            <sch:assert test="count(xhtml:link [@type = 'text/css']) = 1">
                There is one CSS tag.
            </sch:assert>
        </sch:rule>

        <sch:rule context="/ xhtml:html / xhtml:head / xhtml:title">
            <sch:assert test="normalize-space(text()) != ''">The title is not empty.</sch:assert>
        </sch:rule>

        <sch:rule context="/ xhtml:html / xhtml:head / xhtml:meta [@name = 'date']">
            <sch:assert test="regexp:test(@content, '\d\d\d\d-\d\d-\d\d.*')">
                The date is in ISO format.
            </sch:assert>
        </sch:rule>

        <sch:rule context="/ xhtml:html / xhtml:head / xhtml:link [@rel = 'stylesheet']">
            <sch:assert test="@type = 'text/css' and @href = '../Styles/style.css'">
                There is a link to the ebook stylesheet.
            </sch:assert>
        </sch:rule>

        <sch:rule context="/ xhtml:html / xhtml:head / xhtml:meta [@http-equiv]">
            <sch:assert test="@content='text/html; charset=utf-8'">
                The file is in UTF-8.
            </sch:assert>
        </sch:rule>

    </sch:pattern>


    <sch:pattern id="general">

        <sch:rule context="/ xhtml:html / xhtml:body //
                           * [not(regexp:test(name(), 'img|hr|br'))]">
            <sch:assert test="* or normalize-space(text()) != ''">
                Only 'img', 'hr' and 'br' elements are allowed to have no contents.
            </sch:assert>
        </sch:rule>

    </sch:pattern>


    <sch:pattern id="lists">

        <sch:rule context="// xhtml:ol [@start]">
            <sch:assert test="regexp:test(@start, '[0-9]+')">
                The 'start' attribute of an ordered list is a number.
            </sch:assert>
        </sch:rule>

    </sch:pattern>

    
    <sch:pattern id="paragraphs">

        <sch:rule context="// xhtml:p [@class = 'textbreak']">
            <sch:assert test="not(*)">
                Text break elements only contain text.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:p [@class = 'lines']">
            <sch:assert test="xhtml:br">
                Paragraphs with separate lines contain linebreaks.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:p [@class = 'footnote']">
            <sch:assert test="xhtml:span [@class = 'mark'] or xhtml:strong [@class = 'mark']">
                All footnotes have a mark.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:div [@class = 'blockparagraphs']">
            <sch:assert test=". // xhtml:p">
                A 'div.blockparagraph' contains paragraphs.
            </sch:assert>
        </sch:rule>

    </sch:pattern>

    
    <sch:pattern id="inline-formatting">

        <sch:rule context="// xhtml:small">
            <sch:assert test="not(. // xhtml:small)">
                'small' elements are not nested.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:sup">
            <sch:assert test="not(. // xhtml:sup)">
                'sup' elements are not nested.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:strong">
            <sch:assert test="not(. // xhtml:strong)">
                'strong' elements are not nested.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:del ">
            <sch:assert test="not(. // xhtml:del)">
                'del' elements are not nested.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:span [@class = 'broken']">
            <sch:assert test="@title">
                'span.broken' must have a title.
            </sch:assert>
        </sch:rule>

    </sch:pattern>

    
    <sch:pattern id="illustrations">
        <sch:title>
            Illustrations are containers for images that have a particular structure.
        </sch:title>

        <sch:rule context="// xhtml:img">
            <sch:assert test="parent::xhtml:p [@class = 'imagerow'] or
                              parent::xhtml:a [parent::xhtml:p [@class = 'imagerow']]">
                Images can only appear in illustration image rows or 'a' elements within those.
            </sch:assert>

            <sch:assert test="regexp:match(@src, '\.\./Images/.+\.(png|jpg|gif|jpeg)', 'i')">
                Images are always image files in the Images directory.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:div [@class = 'illustration']">
            <sch:assert test="not(*[not(@class) or
                                    @class != 'imagerow' and @class != 'caption'])">
                Nothing but an image row or caption can appear in an illustration division.
            </sch:assert>

            <sch:assert test="count(xhtml:p [@class = 'imagerow']) = 1">
                Illustrations must contain one image row.
            </sch:assert>

            <sch:assert test="count(xhtml:p [@class = 'caption']) &lt;= 1">
                Illustrations contain one optional caption.
            </sch:assert>
       </sch:rule>

        <sch:rule context="// xhtml:p [@class = 'imagerow']">
            <sch:assert test="parent::xhtml:div [@class = 'illustration']">
                An image row is the child of an illustration division.
            </sch:assert>
        </sch:rule>

        <sch:rule context="//xhtml:p[@class='caption']">
            <sch:assert test="preceding-sibling::xhtml:p [@class = 'imagerow']">
                A caption always comes after an image row.
            </sch:assert>
        </sch:rule>

    </sch:pattern>


    <sch:pattern id="links">
        <sch:rule context="// xhtml:a [@class = 'external']">
            <sch:assert test="regexp:test(@href, 'https?://.*')">
                External links point to Web resources.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'hootingyard']">
            <sch:assert test="regexp:test(@href, 'https?://(www\.)?hootingyard\.org.*')">
                Hooting Yard links should lead to the hootingyard.org site.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'internal']">
            <sch:assert test="regexp:test(@href, '[a-z0-9-]+\.xhtml')">
                Internal link hrefs should be a simple XHTML filename.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'internal-pdf']">
            <sch:assert test="regexp:test(@href, '\.\./Media/.+\.pdf')">
                All internal-pdf links point to PDF files in the Media directory.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'internal-audio']">
            <sch:assert test="regexp:test(@href, '\.\./Media/.+\.(wav|aif|mp3|mid)')">
                All internal-audio links point to audio files in the Media directory.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'internal-audio']">
            <sch:assert test="@title">
                Internal audio links must have a title for the player to use.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [@class = 'internal-image']">
            <sch:assert test="regexp:test(@href, '\.\./Images/.+\.(png|jpg|gif|jpeg)', 'i')">
                All internal-image links point to image files in the Images directory.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [starts-with(@class, 'internal')]">
            <sch:assert test="@title and @title != ''">
                All types of internal link have a title attribute.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a">
            <sch:assert test="not(. // xhtml:a)"> No 'a' elements are nested. </sch:assert>

            <sch:assert test="ancestor::* [@class = 'contents'] or xhtml:a [@class]">
                Links that aren't in the table of contents must have a class.
            </sch:assert>
        </sch:rule>

    </sch:pattern>

    
    <sch:pattern id="table-of-contents">

        <sch:rule context="// xhtml:div [@class = 'contents']">
            <sch:assert test="not(* [name() != 'p'])">
                The Big Book contents division should only contain paragraphs.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:div [@class = 'contents'] / xhtml:p">
            <sch:assert test="regexp:test(text(), '[0-9]{4}-[0-9]{2}-[0-9]{2} — .*')">
                A Big Book contents item starts with an ISO date.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:a [ancestor::* [@class = 'contents']]">
            <sch:assert test="regexp:test(@href, '[a-z0-9-]+\.xhtml')">
                Links in the table of contents must be to internal XHTML files.
            </sch:assert>
        </sch:rule>

    </sch:pattern>


    <sch:pattern id="verse">

        <sch:rule context="// xhtml:div [@class = 'verse']">
            <sch:assert test="xhtml:p">
                Verse divisions only contain paragraphs, representing stanzas.
            </sch:assert>

            <sch:assert test="xhtml:p [not(@*)]">
                Verse paragraphs have no attributes.
            </sch:assert>

            <sch:assert test="not(xhtml:p // * [not(regexp:test(name(), 'em|strong|br'))])">
                Verse paragraphs only contain em, strong and br elements.
            </sch:assert>
        </sch:rule>

        <sch:rule context="// xhtml:p [@class = 'verse']">
            <sch:assert test="not(. // * [not(regexp:test(name(), 'em|strong|br'))])">
                Verse paragraphs only contain em, strong and br elements.
            </sch:assert>
        </sch:rule>

    </sch:pattern>

</sch:schema>
