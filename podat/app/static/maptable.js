; (function ($, window, document, undefined)
{
    var pluginName = "maptable";

    function maptable(options, $element)
    {
        this.name = pluginName;
        this.$element = $element;

        this.init(options);
    }

    maptable.prototype.init = function (options)
    {
        var me = this;

        // Establish default settings
        me.options = $.extend({
            mapDivId: "mapDiv",
            initialLatLng: [41.8240, -71.4128], //center of Providence, RI
            initialZoom: 13,
            maxZoom: 18,
            layerId: me.name, //'React-Prov'
            loadingClass: "loading"
        }, options);

        me.map = null;
        me.markers = {};
        me.numRows = 0;
        me.currentTimestamp = 0;
        me.tableCollapsed = true;   // to be updated during initialization

        me.$tableHead = $(".custom-head", me.$element);
        me.$tableBody = $(".custom-body", me.$element);
        me.$apiLink = $("#apiLink", me.$element);

        me.$apiOptions = {
          "limit": $("#apiLimit", me.$element)
        }

        try
        {
          me.setupMap();
          me.handleWindowSize();
          me.attach_EventHandlers();
          me.ajaxData();
        }
        catch (ex)
        {
            console.error(me.name + ": " + ex.toString());
        }
    }

    maptable.prototype.setupMap = function () {
      var me = this;
      me.map = L.map(me.options.mapDivId).setView(me.options.initialLatLng, me.options.initialZoom);

      L.tileLayer('/get-tiles-proxy?z={z}&x={x}&y={y}',
        {
          attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
          maxZoom: me.options.maxZoom,
          id: me.options.layerId
        }
      ).addTo(me.map);
    }

    // coord in the form of {lat: 0.0, lng: 0.0}
    maptable.prototype.mapLocation = function (coord, key, details) {
      var me = this;

      if (!me.markers.hasOwnProperty(key)) {
        if (!details) {
          details = null;
        }

        me.markers[key] = { // lat lng data accessible from _latlng property of the marker
          marker: L.marker([coord.lat, coord.lng]).addTo(me.map),
          details: details
        };
      }

      if (me.markers[key].details !== null) {
        me.markers[key].marker.bindPopup(me.markers[key].details).openPopup();
      }
    }

    // item has the following properties:
    // id, reported_date, offense_desc, formatted_address, latitude, longitude, statute_code, statute_desc, counts
    maptable.prototype.buildRow = function (item) {
      var me = this;
      var $row = $(me.$tableHead.html());
      var $cols = $(".custom-cell", $row);

      var coord = {
        lat: item.latitude,
        lng: item.longitude
      };
      var popupDetails = "<b>" + item.formatted_address + "</b></br>" + item.offense_desc;

      // columns are date, address, offense, statute, counts
      try {
        var $mapLink = $("<a>" + item.formatted_address + "</a>");
        $mapLink.click(function () {
          me.mapLocation(coord, item.id, popupDetails);
        });

        $($cols[0]).text(me.updateTimestamp(item.reported_date));
        $($cols[1]).html($mapLink);
        $($cols[2]).text(item.offense_desc);
        $($cols[3]).text(item.statute_code).prop("title", item.statute_desc);
        $($cols[4]).text(item.counts).addClass("large-text");
      }
      catch (ex)
      {
        console.error(me.name + " encountered an issue updating a row: " + ex.toString());
      }

      if (me.numRows % 2 == 0) {
        $row.addClass("swap-color");
      }

      return $row;
    }

    maptable.prototype.buildTable = function (dat) {
      var me = this;
      var $rows = [];

      $.each(dat, function(index, item) {
        $rows.push(me.buildRow(item));
        me.numRows++;
      });

      me.currentTimestamp = (new Date()).toLocaleString();

      $(".timestamp", me.$apiLink).text(me.currentTimestamp);
      me.$tableBody.append($rows);
      $("[data-toggle='tooltip']", me.$tableBody).tooltip();
    }

    maptable.prototype.updateTimestamp = function (dateStr) {
      var date = new Date(dateStr);
      return date.toLocaleString();
    }

    maptable.prototype.buildUrlWithQuery = function (url, queryObj) {
      var args = [];

      $.each(Object.keys(queryObj), function(index, element) {
        args.push(element + "=" + queryObj[element]);
      });

      if (args.length > 0) {
        url = url + "?" + args.join("&");
      }

      return url;
    }

    maptable.prototype.ajaxData = function () {
      var me = this;

      me.$tableBody.html("");
      me.$apiLink.addClass(me.options.loadingClass);
      me.numRows = 0;
      var options = {
        limit: me.$apiOptions["limit"].val()
      }

      $.ajax({
        url: me.buildUrlWithQuery("/api", options),
        method: "GET",
        contentType: "application/json; charset=utf-8",
        error: function (jqXHR, textStatus, errorThrown) {
          console.error(me.name + " encountered an ajax error: " + textStatus + " - " + errorThrown);
          me.$apiLink.removeClass(me.options.loadingClass);
        },
        success: function (dat, textStatus, jqXHR) {
          me.buildTable(dat);
          me.$apiLink.removeClass(me.options.loadingClass);
        }
      });
    }

    maptable.prototype.attach_EventHandlers = function ()
    {
        var me = this;

        $("a", me.$apiLink).click(function (event) {
          me.ajaxData();
        });

        // custom window resizing event to prevent awkard overflows
        $(window).resize(function() {
          me.handleWindowSize();
        });
    }

    maptable.prototype.handleWindowSize = function () {
      var me = this;

      if ($(window).width() < 768) {
        $(".custom-table", me.$element).addClass("custom-collapse");
        $(".custom-expand").removeClass("col-xs-2").addClass("col-xs-4");
        me.tableCollapsed = true;
      }
      else if (me.tableCollapsed) {
        $(".custom-expand").removeClass("col-xs-4").addClass("col-xs-2");
        $(".custom-table", me.$element).removeClass("custom-collapse");
        me.tableCollapsed = false;
      }
    }

    // Push the plug-in into jQuery
    $.fn[pluginName] = function (options, $element)
    {
        if (this.length > 0)
        {
            return this.each(function ()
            {
                if (!$.data(this, 'plugin_' + pluginName))
                {
                    $.data(this, 'plugin_' + pluginName, new maptable(options, $(this)));
                }
            });
        }
        else if ($element)
        {
            if (!$.data($element, 'plugin_' + pluginName))
            {
                return $.data($element, 'plugin_' + pluginName, new maptable(options, $element));
            }
        }
    }
})(jQuery, window, document);
