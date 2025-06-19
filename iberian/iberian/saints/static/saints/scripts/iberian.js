var django = {
  "jQuery": jQuery.noConflict(true)
};
var jQuery = django.jQuery;
var $ = jQuery;

(function ($) {
  $(function () {
    $(document).ready(function () {
      // Initialize event listeners
      ru.iberian.init_event_listeners([]);
      $('#id_subtype >option').show();
      // Add 'copy' action to inlines
      ru.iberian.tabinline_add_copy();
      // Initialize Bootstrap popover
      // Note: this is used when hovering over the question mark button
      //$('[data-toggle="popover"]').popover();
    });
  });
})(django.jQuery);



// based on the type, action will be loaded

// var $ = django.jQuery.noConflict();

var ru = (function ($, ru) {
  "use strict";

  ru.iberian = (function ($, config) {
    // Define variables for ru.collbank here
    var loc_example = "",
      loc_divErr = "iberian_err",
      loc_typeahead_init = false,
      loc_sync_detail = {},
      loc_ta_done = [],
      loc_elInput = null,
      loc_sWaiting = " <span class=\"glyphicon glyphicon-refresh glyphicon-refresh-animate\"></span>",
      loc_cnrs_manu_url = "http://medium-avance.irht.cnrs.fr/Manuscrits/manuscritforetablissement",
      base_url = "",
      KEYS = {
        BACKSPACE: 8, TAB: 9, ENTER: 13, SHIFT: 16, CTRL: 17, ALT: 18, ESC: 27, SPACE: 32, PAGE_UP: 33, PAGE_DOWN: 34,
        END: 35, HOME: 36, LEFT: 37, UP: 38, RIGHT: 39, DOWN: 40, DELETE: 46
      },
      oSyncTimer = null;


    // Private methods specification
    var private_methods = {
      /**
       * methodNotVisibleFromOutside - example of a private method
       * @returns {String}
       */
      methodNotVisibleFromOutside: function () {
        return "something";
      },
      errMsg: function (sMsg, ex) {
        var sHtml = "Error in [" + sMsg + "]<br>";
        if (ex !== undefined && ex !== null) {
          sHtml = sHtml + ex.message;
        }
        $("#" + loc_divErr).html(sHtml);
      }
    }

    // Public methods
    return {
      /**
       * init_event_listeners
       *    Initialize event listeners for this module
       */
      init_event_listeners: function (lst_typeahead) {
        var lst_use = [],
          base_url = "",
          div_ta = "#__typeaheads__",
          i = 0,
          lst_options = [],
          item = "";

        // Get the base URL
        base_url = $("#__baseurl__").text();
        if (lst_typeahead === undefined || lst_typeahead.length === 0) {
          if ($(div_ta).length > 0 && $(div_ta).text() !== "") {
            lst_typeahead = JSON.parse($(div_ta).text());
          }
        }

        // Set the elements that should be used
        for (i = 0; i < lst_options.length; i++) {
          item = lst_options[i];
          if (lst_typeahead === undefined || lst_typeahead.indexOf(item) > -1) { lst_use.push(item); }
        }

        if (!loc_typeahead_init || lst_use.length > 0) {
          for (i = 0; i < lst_use.length; i++) {
            item = lst_use[i];
            // Has this one been done recently?
            if (loc_ta_done.indexOf(item) < 0) {
              // Make sure to add the index to the list of done ones
              loc_ta_done.push(item);
            }
          }
          loc_typeahead_init = true;
        }

        // Initialize typeahead
        ru.iberian.init_typeahead();

      },

      /**
       * init_typeahead
       *    Initialize the typeahead features, based on the existing bloodhound stuff
       */
      init_typeahead: function () {
        try {

          // Make sure we know which element is pressed in typeahead
          $(".form-row:not(.empty-form) .typeahead").on("keyup",
            function () {
              loc_elInput = $(this);
            });

          // Allow "Search on ENTER" from typeahead fields
          $(".form-row:not(.empty-form) .searching").on("keypress",
            function (evt) {
              var key = evt.which,  // Get the KEY information
                start = null,
                button = null;

              // Look for ENTER
              if (key === KEYS.ENTER) {
                // Find the 'Search' button
                button = $(this).closest("form").find("a[role=button]").last();
                // Check for the inner text
                if ($(button)[0].innerText === "Search") {
                  // Found it
                  $(button).click();
                  evt.preventDefault();
                }
              }
            });

          // Make sure the twitter typeahead spans are maximized
          $("span.twitter-typeahead").each(function () {
            var style = $(this).attr("style");
            $(this).attr("style", style + " width: 100%;");
          });


        } catch (ex) {
          private_methods.errMsg("init_typeahead", ex);
        }
      },

      /**
       *  form_submit
       *    Refer to this in an [onkeydown] item of an input box
       *    When the ENTER key is pressed, the nearest form is submitted
       */
      form_submit: function (e) {
        var target,
          targeturl = null,
          frm = null;

        try {
          // Get the event
          e = e || window.event;
          if (e.keyCode == 13) {
            // Get the target
            target = e.target || e.srcElement;
            // Find the form
            frm = $(target).closest("form");
            // If there is a downloadtype, then reset it
            $(frm).find("#downloadtype").val("");
            // if the form has a targeturl, use that in the action
            targeturl = $(frm).attr("targeturl");
            if (targeturl !== undefined && targeturl !== "") {
              $(frm).attr("action", targeturl);
            }
            // Make sure the GET method is used
            $(frm).attr("method", "GET");
            // Show we are waiting
            $("#waitingsign").removeClass("hidden");
            // Submit that form
            $(frm).submit();
          }
        } catch (ex) {
          private_methods.errMsg("form_submit", ex);
        }
      },

      /**
        * result_download
        *   Trigger creating and downloading a result CSV / XLSX / JSON
        *
        */
      post_download: function (elStart) {
        var ajaxurl = "",
          contentid = null,
          response = null,
          frm = null,
          el = null,
          sHtml = "",
          oBack = null,
          dtype = "",
          sMsg = "",
          method = "normal",
          data = [];

        try {
          // Clear the errors
          private_methods.errClear();

          // obligatory parameter: ajaxurl
          ajaxurl = $(elStart).attr("ajaxurl");
          contentid = $(elStart).attr("contentid");

          // Gather the information
          frm = $(elStart).closest(".container-small").find("form");
          if (frm.length === 0) {
            frm = $(elStart).closest("td").find("form");
            if (frm.length === 0) {
              frm = $(elStart).closest(".body-content").find("form");
              if (frm.length === 0) {
                frm = $(elStart).closest(".container-large.body-content").find("form");
              }
            }
          }
          // Check what we have
          if (frm === null || frm.length === 0) {
            // Didn't find the form
            private_methods.errMsg("post_download: could not find form");
          } else {
            // Make sure we take only the first matching form
            frm = frm.first();
          }
          // Get the download type and put it in the <input>
          dtype = $(elStart).attr("downloadtype");
          $(frm).find("#downloadtype").val(dtype);

          switch (method) {
            case "erwin":
              data = frm.serialize();
              $.post(ajaxurl, data, function (response) {
                var iready = 1;
              });
              break;
            default:
              // Set the 'action; attribute in the form
              frm.attr("action", ajaxurl);
              // Make sure we do a POST
              frm.attr("method", "POST");

              // Do we have a contentid?
              if (contentid !== undefined && contentid !== null && contentid !== "") {
                // Process download data
                switch (dtype) {
                  default:
                    // TODO: add error message here
                    return;
                }
              } else {
                // Do a plain submit of the form
                oBack = frm.submit();
              }
              break;
          }

          // Check on what has been returned
          if (oBack !== null) {

          }
        } catch (ex) {
          private_methods.errMsg("post_download", ex);
        }
      },

      /**
       * tabinline_add_copy
       *   Add a COPY button to all tabular inlines available
       */
      tabinline_add_copy: function () {
        $(".tabular .related-widget-wrapper").each(
          function (idx, obj) {
            // Find the first <a> child
            var chgNode = $(this).children("a").first();
            var sHref = $(chgNode).attr("href");
            if (sHref !== undefined) {
              // Remove from /change onwards
              var iChangePos = sHref.lastIndexOf("/change");
              if (iChangePos > 0) {
                sHref = sHref.substr(0, sHref.lastIndexOf("/change"));
                // Get the id
                var lastSlash = sHref.lastIndexOf("/");
                var sId = sHref.substr(lastSlash + 1);
                sHref = sHref.substr(0, lastSlash);
                // Get the model name
                lastSlash = sHref.lastIndexOf("/");
                var sModel = sHref.substr(lastSlash + 1);
                sHref = sHref.substr(0, lastSlash);
                // Find and adapt the history link's content to a current
                var sCurrent = $(".historylink").first().attr("href").replace("/history", "");
                // Create a new place to go to
                sHref = sHref.replace("collection", "copy") + "/?_popup=0&model=" + sModel + "&id=" + sId + "&current=" + sCurrent;
                var sAddNode = "<a class='copy-related' title='Make a copy' href='" + sHref + "'>copy</a>";
                // Append the new node
                $(this).append(sAddNode);
              }
            }
          });
      },

      /* goto_view
      *   Open the indicated view
      *
      */
      goto_view: function (elStart, sView) {
            var height = 0,
                width = 0,
                id_mapview = "#basicmap",
                id_listview = "#mainlistview"; // "#basiclist_top";
            try {
                switch (sView) {
                    case "map":   // Open the map-view
                        $(id_listview).addClass("hidden");
                        $(id_mapview).removeClass("hidden");
                        $(".map-list-switch").addClass("map-active");

                        // Calculate and set the height
                        height = $("footer").position().top - $(".iberian-map").position().top - 160;
                        width = $(id_mapview).width();
                        $(".iberian-map").css("height", height + "px");
                        $(".iberian-map").css("width", width + "px");

                        // And copy the generic search value
                        $("#generic_search").val($("#generic-search-input").val());

                        // Initiate showing a map
                        ru.mapview.iberian_map(elStart);
                        break;
                    case "list":  // Open the listview
                        $(id_mapview).addClass("hidden");
                        $(id_listview).removeClass("hidden");
                        $(".map-list-switch").removeClass("map-active");
                        break;
                }

            } catch (ex) {
                private_methods.errMsg("goto_view", ex);
            }
      },
      /**
       *  view_switch
       *      Switch from one view to the other
       *
       */
      view_switch: function (sOpen, sClose) {
        $("#" + sOpen).removeClass("hidden");
        $("#" + sClose).addClass("hidden");
        // Show/hide <li> elements
        $("li." + sOpen).removeClass("hidden");
        $("li." + sClose).addClass("hidden");
      }

    };
  }($, ru.config));

  return ru;
}(jQuery, window.ru || {})); // window.ru: see http://stackoverflow.com/questions/21507964/jslint-out-of-scope

