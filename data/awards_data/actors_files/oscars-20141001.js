(function($) {
    $.fn.oscarsContentChooser = function(options) {                                                             //create the jQuery plugin. Read more about plugin conventions here: http://docs.jquery.com/Plugins/Authoring     and here: http://www.learningjquery.com/2007/10/a-plugin-development-pattern
        var opts = $.extend({}, $.fn.oscarsContentChooser.deafults, options);                                   //allow passing in of options object
        
        //run the plugin on all selected elements and return the jQuery object        
        return this.each(function() {                                                                           
            var scope = this;                                                                                   //trap the scope as the current DOM element being operated on
            $('.' + opts.prefix + 'Links a', scope)                                                             //get the anchors we'll be operating on 
                .click(function(e) {                                                                            //attach a click handler to each anchor
                    anchorClickHandler(this, e, opts, scope);                                                   //call the internal click handler function
                    e.stopPropagation();                                                                        //prevent click event from bubbling
                    return false;                                                                               //prevent click event from bubbling
                });
        });
        
        //click handler for the anchor elements
        function anchorClickHandler(link, e, options, scope) {
            if (link.hash && (link.hash.length > 0)) {                                                              //make sure the anchor's href is a hash
                var $anchor = $('.' + options.prefix + 'Content a[name=' + link.hash.substring(1) + ']', scope);   //find the corresponding anchor within the widget
                if ($anchor.length) {                    
                    $anchor.parent('li')                                                                            //find the anchor's container LI
                        .addClass(options.activeClassName).hide().fadeIn()                                          //make sure that LI is the only "active" one, and do some flashy fade-in
                        .siblings().removeClass(options.activeClassName).hide();
                    $(link)                                                                                        //make sure the link is the only "active" one
                        .parent('li')
                            .addClass(options.activeClassName)
                            .siblings().removeClass(options.activeClassName);
                }
            }
            link.blur();                                                                                            //remove the antlines from around the clicked link
        };
    };
    $.fn.oscarsContentChooser.deafults = {                                                                          //default options for the plugin
        prefix: 'multibox',
        activeClassName: 'active' 
    };
})(jQuery);
// end of content chooser plugin


//  create the calendar functionality as a plugin to remove redundant code, as there are a lot of similarities between
//  the main calendar code and the sidebar calendar code
//  assumptions: the next/prev anchors in the calendar's title and the individual daily events anchors in the sidebar
//  calendar have an href url that takes the user to a different page (this is fallback funcitonality if no JS or if the ajax fails)
//  the plugin code will overwrite the anchor's click event to generate an ajax call from a different url (based on a date string
//  that will be extracted from the anchor's href attribute). 
//  Please note that the url parsing and creating methods in the $.fn.oscarsCalendar.parsers and the
//  $.fn.oscarsCalendar.urlFormats sections need to be changed by you to match the urls used in the actual site
//
//  (please note that inside the plugin we still use $ and not $ to reference jQuery)
;(function($) {
    $.fn.oscarsCalendar = function(options) {                                                                           //create the jQuery plugin. Read more about plugin conventions here: http://docs.jquery.com/Plugins/Authoring     and here: http://www.learningjquery.com/2007/10/a-plugin-development-pattern
        var opts = $.extend({}, $.fn.oscarsCalendar.defaults, options);                                                 //allow passing in of options object

        //run the plugin on all selected elements and return the jQuery object
        return this.each(function(i) {                                                                                  
            var widget = this,                                                                                          //trap the scope as the current DOM element being operated on
                $linksPrevNext = $('.calendarInner h3 a', widget),                                                      //get a jQuery representation of the Next/Prev links
                $calTemp = createTempContainer(i);                                                                      //create a div to hold the loaded content from the ajax call

            $linksPrevNext  
                .click(function(e) {                                                                                    //attach click handler to the next/prev arrow links
                    var filename = convertURL(this, 'CalNextPrevLinks', 'CalFromDateString');                           //parse the filename from the link (fallback name), to the filename to use for the ajax call
                    loadCalendar(filename, $calTemp, $linksPrevNext, widget, this);                                     //make the ajax call to get the new calendar
                    this.blur();                                                                                        
                    e.stopPropagation();                                                                                //prevent click from bubbling
                    return false;
                });

            if (opts.calendarType == 'main') {
                //run this code if this calendar is in the main section (big calendar)
                $('.ddlMonthYear', widget).change(function(e) {                                                         //attach onchange handlers to the month/year SELECTs
                    var month = $('#ddlMonth').get(0);                                                                  //get the selected value of the month SELECT
                    var year = $('#ddlYear').get(0);                                                                    //get the selected value of the year SELECT
                    var filename = $.fn.oscarsCalendar.urlFormats.mainCalFromDateString(year.options[year.selectedIndex].value + month.options[month.selectedIndex].value); //parse the month/year to the filename to use for the ajax call
                    loadCalendar(filename, $calTemp, $linksPrevNext, widget);                                           //make the ajax call to get the new calendar
                });

                $('#ddlEventType').change(function(e) {                                                                 //attach onchange handler to the event type SELECT
                    showEvents(getEventType(this), widget);
                });
            }
            else if (opts.calendarType == 'sidebar') {
                //run this code if this calendar is in the sidebar section (small calendar)            
                attachCalendarAnchorsEventListeners(widget);                                                            //attach onclick handlers to all anchors in the calendar
            }
        });

        //the function that does the actual ajax call, see jQuery's ajax documentation at http://docs.jquery.com/Ajax
        function loadCalendar(url, tempContainer, linksPrevNext, widget, anchor) {                                      
            $.ajax({
                type: "GET",
                url: url,
                dataType: "html",
                success: function(data, textStatus) {
                    populateCalendar(data, tempContainer, linksPrevNext, widget);                                       //if the ajax call was successful, populate the data in the calendar
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {                                              //if the ajax call was not successful, and the originating element was an anchor, redirect the browser to the fallback url
                    if (anchor)
                        window.location = anchor.href;
                }

            });
        };

        //function for populating the data from the ajax call in the calendar DIV
        function populateCalendar(html, tempContainer, linksPrevNext, widget) {                                         
            tempContainer.html(html)                                                                                    //put the data as the inner HTML of a temp DIV container
            var newPrevLink = $('h3 a.prev', tempContainer),                                                            //trap the prev link, next link, month name SPAN and calendar TABLE from the new data in variables
                newNextLink = $('h3 a.next', tempContainer),
                newMonthName = $('h3 span', tempContainer),
                newTable = $('table', tempContainer);

            var $title = $('.calendarInner h3', widget),                                                                //trap the H3 and calendar TABLE from the existing calendar in variables
                $table = $('table', widget);

            if (newPrevLink.length)                                                                                     //if we have a new prev anchor, use its href for the existing one, otherwise hide it (done this way so we don't have to rebind the click handler)
                linksPrevNext.filter('.prev').attr('href', newPrevLink.get(0).href).show();
            else
                linksPrevNext.filter('.prev').hide();

            if (newNextLink.length)                                                                                     //if we have a new next anchor, use its href for the existing one, otherwise hide it (done this way so we don't have to rebind the click handler)
                linksPrevNext.filter('.next').attr('href', newNextLink.get(0).href).show();
            else
                linksPrevNext.filter('.next').hide();

            $('span', $title).text(newMonthName.text());                                                                //populate the month name SPAN with the text from the new one
            $table.html(newTable.html());                                                                               //populate the calendar TABLE with the data from the new one

            if (opts.calendarType == 'main') {
                //run this code if this calendar is in the main section (big calendar)
                var eventType = getEventType($('#ddlEventType', widget).get(0));                                        //show events in calendar based on the event type SELECT
                showEvents(eventType);
            }
            else if (opts.calendarType == 'sidebar') {
                //run this code if this calendar is in the sidebar section (small calendar)
                attachCalendarAnchorsEventListeners(widget);                                                            //attach onclick handlers to all anchors in the calendar                                                     
                $(widget).siblings('div.sidebarEvents').hide();                                                         //hide the sidebar's events module 
                $('table td a', widget).filter(':first').click();                                                       //if we have any anchors in the calendar TABLE, click the first one (to load its data to the events module)
            }
        }

        //function for showing the events in the main calendar based on the event type SELECT
        //this is used only in the main calendar
        function showEvents(eventType, widget) {                                                                        
            var $links = $('table tbody td a', widget);                                                                 //find all the Anchors inside the table
            switch (eventType) {
                case 'all':                                                                                             //show all Anchors
                    $links.show();
                    break;
                default:
                    $links.hide().filter('.' + eventType).show();                                                       //only show the Anchors whose className matches the passed in event type
                    break;
            }
        };
        
        //utility function for converting the static URLs to the ajax ones
        function convertURL(anchor, parserType, urlFormat) {
            var dateString = $.fn.oscarsCalendar.parsers[opts.calendarType + parserType](anchor);                       //get the date string (yyyymm) from the current anchor's static URL
            return $.fn.oscarsCalendar.urlFormats[opts.calendarType + urlFormat](dateString);                           //build the url to use for the ajax call
        };

        //creates the holding div for the returned results from the ajax call
        function createTempContainer(index) {
            $('body').append('<div id="' + [opts.tempContainerName, opts.calendarType, index].join('_') + '" class="tempCal"></div>');
            return $('#' + [opts.tempContainerName, opts.calendarType, index].join('_'));
        };

        //find the events to show on the main calendar absed on the event type SELECT
        //this is used only in the main calendar
        function getEventType(selectElement) {
            return selectElement.options[selectElement.selectedIndex].value || 'all';
        };

        //function to run after a successful ajax call for the sidebar event module has finished
        //this is used only in the sidebar calendar
        function eventsLoadSuccessHandler(data, $anchor, widget) {
            $(widget).siblings('div.sidebarEvents').html(data).hide().fadeIn(800);                                      //fade in the sidebar events module
            $('table td.selected', widget).removeClass('selected');                                                     //remove the 'selected' className from all anchors in the sidebar calendar
            $anchor.parent('td').addClass('selected');                                                                  //add the 'selected' className to the Anchor that originated the call
        };

        //attadches click event listeners to the Anchors in the sidebar calendar
        //this is used only in the sidebar calendar
        function attachCalendarAnchorsEventListeners(widget) {
            $('table td a', widget).click(function(e) {                                                                 //attach click handler to the Anchors in the calendar
                var anchor = this, $anchor = $(anchor);
                var filename = convertURL(this, 'EventsLinks', 'EventsFromDateString');                                 //get new URL to use for the ajax call, based on the clicked Anchor's href attribute
                $.ajax({                                                                                                //make the ajax call
                    type: "GET",
                    url: filename,
                    dataType: "html",
                    success: function(data, textStatus) {                                                               //event handler for a successful ajax call
                        eventsLoadSuccessHandler(data, $anchor, widget);                                                
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {                                          //event handler for failed ajax call
                        if (anchor)                                                                                     
                            window.location = anchor.href;                                                              //redirect the page to the Anchor's href 
                    }
                });
                this.blur();
                e.stopPropagation();                                                                                    //stop event bubbling
                return false;
            });
        };
    };


    //configuration for the plugin
    $.fn.oscarsCalendar.defaults = {
        tempContainerName: 'calTemp',
        calendarType: 'sidebar'         //options are 'sidebar', 'main'        
    };


    //helper methods for extracting the dateString (in the format of yyyymm) from href attributes of the calendar Anchors
    /////////////////////////////////////////////////////////////////////////////////////////////
    //
    // NOTE:    You need to modify these based on the urls you'll be using in the actual site.
    //          The current methods are based on the filenames used in the HTML shells.
    //
    /////////////////////////////////////////////////////////////////////////////////////////////
    
    $.fn.oscarsCalendar.parsers = {
        //extracts dateString from href of the prev/next links next to the month name in the main calendar
        mainCalNextPrevLinks: function(anchor) {
            return anchor.pathname.match(/calendar(\d{6}).html/)[1];
        },

        //extracts dateString from href of the prev/next links next to the month name in the sidebar calendar
        sidebarCalNextPrevLinks: function(anchor) {
            return anchor.hash.substring(1);
        },

        //extracts dateString from href of the individual daily event links in the sidebar calendar - this one doesn't have a yyyymm format
        sidebarEventsLinks: function(anchor) {
            return anchor.hash.substring(1);
        }
    }

    //helper methods for building the urls to use for the ajax calls from a provided dateString (in the format of yyyymm) 
    /////////////////////////////////////////////////////////////////////////////////////////////
    //
    // NOTE:    You need to modify these based on the urls you'll be using in the actual site.
    //          The current methods are based on the filenames used in the HTML shells.
    //
    /////////////////////////////////////////////////////////////////////////////////////////////   
    $.fn.oscarsCalendar.urlFormats = {
        //build the url for the calendar ajax call for the main calendar
        mainCalFromDateString: function(dateString) {
            return '/events-exhibitions/calendar/ajax-content/' + 'snippet' + dateString + '.html';
        },

        //build the url for the calendar ajax call for the sidebar calendar
        sidebarCalFromDateString: function(dateString) {
            return '/events-exhibitions/calendar/ajax-content/' + 'side' + dateString + '.html';
        },

        //build the url for the daily events ajax call for the sidebar calendar
        sidebarEventsFromDateString: function(dateString) {
            return '/events-exhibitions/calendar/ajax-content/' + 'sideEvents' + dateString + '.html';
        }
    }
})(jQuery);
// end of calendar plugin





;$(function() {                                                                        //all the code inside this function will run as soon as the DOM is ready

    $('#main .multiboxContainer').oscarsContentChooser();                              //multibox functionality AWARDS 4X BOX
    $('#main .manyContainer').oscarsContentChooser({ prefix: 'many' });                //manybox functionality AWARDS YEAR 8X LISTED CONTENT

    $('#main .calendarContainer').oscarsCalendar({ calendarType: 'main' });            //main calendar functionality
    $('#sidebar .sidebarCalendar').oscarsCalendar({ calendarType: 'sidebar' });        //sidebar calendar functionality

    //watermark (Selects all INPUT elements with TEXT or PASSWORD type.)
//  $('#wrapperInner input[@type=text], #wrapperInner input[@type=password]')          //uses the jQuery watermark plugin for inline labels on input/password fields
//      .watermark({ watermarkCssClass: 'watermark' });

    //Accordion functionality
    /////////////////////////
    $('#main .accordionContainer .accordion li h3')                            //find all H3s inside the accordion widget
        .click(function(e) {                                                    //attach click event listeners to the H3s
            var $li = $(this).parent('li');                                    //find the H3's parent LI
            $li.siblings('.active')                                             //find the LI's "active" siblings
                .removeClass('active')                                          //remove the "active" class from the "active" siblings
                .children('div.accordionInner').hide();                         //hide the "accordionInner" div that's a direct child of any of the formerly "active" LIs
            $li.addClass('active')                                              //add the "active" class to our original LI
                .children('div.accordionInner')                                 //find it's direct child "accordionInner" DIV
                .hide().fadeIn()                                                //fade it in
                .children('img').hide().fadeIn('slow');                         //find the IMG inside the DIV and fade it in as well
        });

    //Tabs
    ///////
    $('#main .tabbedModule ul li a')                                           //find all anchors inside the tabbed module's unordered list
        .click(function(e) {                                                    //attach click event listeners
            if (this.hash && this.hash.length) {                                //make sure there's a hash
                $(this)                                                        //wrap the anchor with a jQuery object
                    .parent('li')                                               //find its parent LI element
                        .addClass('active')                                     //add the 'active' class to the LI
                        .siblings().removeClass('active').end()                 //remove the 'active' class form all other LIs
                        .parent('ul')                                           //find the LI's parent UL
                            .siblings('div.tabItem')                            //find the UL's siblings that are DIVs with the 'tabItem' class                
                                .hide()                                         //hide all those DIVs
                                .filter(this.hash)                              //filter the list of DIVs to the one whose id is the same as the anchor's hash
                                    .fadeIn(500);                               //fade it in
            }
            this.blur();
            e.stopPropagation();                                                //prevent click event from bubbling
            return false;
        })
        .filter(':first').click();                                              //after we've assigned a click event listener to all the links, activate it for the first one


 /////////////////////////////////////////////
 ////SIDE SIDE SIDE SIDE SIDE SIDE ////////////
 ///////////////////////////////////////////
 
//Parse and add classes from JS variables in page header in order to assign collapse and active states in menus
var strOpenLIElements = arrOpenLIElements.join(',');    //this will give you a comma separated list of all the ids. In our example case the string we'll get is '#li_1,#li_1_2'
$(strOpenLIElements).addClass('open');                 //this will add the "open" class to all the elements we referenced
$(strActiveLIElement).addClass('active');              //likewise, this will add the "active" class to the element we want to highlight
 
 //Collapse Functionality for Secondary Nav
    //////////////////////////////////////////
    $('#sidebar #sNav').each(function(i) {                                     //run the following function for every #sNav element (there should only be one...)
        var sNav = this;                                                        //trap the current scope in a variable (scope would be the DOM element(s) we chose in previous line)

        //1. create collapse anchors
        $('li.Coll > span', sNav)                                              //find all SPANs that are direct children of LIs (within the scope) where the LI has the "Coll" (=Collapsible) className
            .prepend('<a class="collapseAnchor" href="#">collapse</a>');        //insert the string as HTML as the first child of the SPAN

        //2. hide non-current subnavs
        $('li', sNav)                                                          //find all the LIs within the scope (all levels) 
            .not('.open')                                                       //limit the list of LIs to those that don't have the "open" className
                .children('ul').hide();                                         //change the style of all the ULs that are direct decendants of those LIs to display:none

        //3. add collapsing functionality 
        $('a.collapseAnchor', sNav)                                            //find all the anchors that we created in step 1 above
            .click(function(e) {                                                //attach a click event listener to each of the anchors
                $(this)                                                        //create a jQuery object representation of the clicked anchor
                    .parent()                                                   //find that anchor's direct parent (a SPAN element)            
                    .siblings('ul').toggle().end()                              //toggle the display of the SPAN's sibling UL (switches between display:block and display:none)
                    .parent().toggleClass('open');                              //toggle the SPAN's parent's (LI) className of "open" (adds it if it's missing, removes it if it's there)
                e.stopPropagation();                                            //prevent click event from bubbling
                return false;                                                   //prevent click event from bubbling
            });

    });


////////////////////////////////////
////END END END END END SIDE NAV ///
////////////////////////////////////



    //ie6 fixes
    ////////////
    if ($.browser.msie && $.browser.version < 7) {                            //limit the code to run only for IE6
        //the following snippet is used in order to mimic the 
        //:hover CSS pseudoclass for IE6 by adding a .hover class
        $('#mNav li, #main .accordionContainer ul.accordion li h2')            //find the elements to operate on
            .hover(                                                             //attach mouseover/mouseout listeners for the elements
                function() {                                                    //first function is the mouseover
                    $(this).addClass('hover');                                 //add the "hover" className
                },
                function() {                                                    //second function is the mouseout
                    $(this).removeClass('hover');                              //remove the "hover" className
                }
        );
    }

    //homepage "explore" widget
    ///////////////////////////
    $('#homeExperience .homeExperienceDefault').each(function(i) {

        //get references to all the required ui elements into variables
        var $widget = $(this);
        var $pane = $('.homeExperienceLinksPane', $widget);
        var $links = $('.homeExperienceLinks li', $pane);
        var $content = $('.homeExperienceContent li', $widget);

        var _first = 0;                                                                                 //variable for maintaining the current position in the links UL

        //private function for scrolling the links pane
        function scrollLinks(index, scrollSpeed, fadeInSpeed) {
            var scrollSpeed = scrollSpeed || 800;                                                       //if no speed parameter (for the scroll) was passed in, use a default of 800ms
            $pane.scrollTo($links[index], scrollSpeed, { axis: 'x' });                                        //use the scrollTo plugin to scroll to the right
            showContent($($content[index]), fadeInSpeed);
            $links                                                                                      //make sure the first link shown on the left is the "active" one
                .removeClass('active')
                .eq(index).addClass('active').end();
        }

        //private function for showing the selected link's related content
        function showContent(jSourceElement, fadeInSpeed) {
            var fadeInSpeed = fadeInSpeed || 500;                                                       //if no speed parameter (for the fade) was passed in, use a default of 500ms
            $imgContainer.html('').hide();                                                              //first empty the image container and hide it
            jSourceElement.children('a', 'img').clone().appendTo($imgContainer);                        //copy the source element's child IMG to the image container
			//added A element to CLONE and APPEND to imgContainer to allow linked images PC
            $imgContainer.fadeIn(fadeInSpeed);                                                          //fade the image into view

            $textContainer.html('').hide();                                                             //empty the text container and hide it
            jSourceElement.children('p').clone().appendTo($textContainer);                              //copy the source elements child paragraph(s) to the image container
            $textContainer.fadeIn(fadeInSpeed);                                                         //fade the text into view
        }

        if ($links.length > 0 && $content.length == $links.length) {                                    //we have to have a content LI for every link LI
            $widget.removeClass('homeExperienceDefault').addClass('homeExperienceDynamic');             //remove the No-JS CSS class, switch to JS mode

            //dynamically add the DIVs that will hold copies of the selected content's image and text, and get references to them into variables
            $widget.prepend('<div class="homeExperienceImage"></div>');
            var $imgContainer = $widget.children('.homeExperienceImage');

            $widget.append('<div class="homeExperienceText"></div>');
            var $textContainer = $widget.children('.homeExperienceText');

            //add the scrolling links dynamically and save references to them
            $widget.prepend('<a class="prev" href="#" title="previous"><span>&lt;&lt;</span></a>');
            var $prev = $('a.prev', $widget);

            $widget.append('<a class="next" href="#" title="next"><span>&gt;&gt;</span></a>');
            var $next = $('a.next', $widget);

            //move the scroller to the first link and show its content
            scrollLinks(0, 800, 100);

            //attach a click event listener to all the links
            $links.children('a')
                .click(function(e) {
                    if (this.hash && (this.hash.length > 0)) {
                        //find the correct source li based on the anchor's hash
                        var $source = $('.homeExperienceContent li a[name=' + this.hash.substring(1) + ']', $widget).parent();
                        if ($source.length > 0) {
                            //show the source LI's content
                            showContent($source);
                            //make sure the clicked link is the only "active" one
                            $(this).parent('li').addClass('active').siblings().removeClass('active');
                        }
                    }
                    this.blur();
                    e.stopPropagation();
                    return false;
                });

            //attach scroll/showcontent functionality to the prev/next links (the _first variable is used here to make sure we remain within range
            $next.click(function(e) {
                if ($links[_first + 3]) {
                    scrollLinks(_first + 3);
                    _first += 3;
                }
                this.blur();
                e.stopPropagation();
                return false;
            });

            $prev.click(function(e) {
                if ($links[_first - 3]) {
                    scrollLinks(_first - 3);
                    _first -= 3;
                }
                this.blur();
                e.stopPropagation();
                return false;
            });
        }
    });


});


