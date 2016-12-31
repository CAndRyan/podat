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
            initialLatLng: [41.8240, -71.4128],
            initialZoom: 13,
            maxZoom: 18,
            layerId: me.name //'React-Prov'
        }, options);

        me.map = null;
        me.markers = {};
        me.numRows = 0;
        me.$tableHead = $(".custom-head", me.$element);
        me.$tableBody = $(".custom-body", me.$element);

        try
        {
          me.setupMap();
          me.attach_EventHandlers();
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

      me.$tableBody.append($rows);
    }

    maptable.prototype.updateTimestamp = function (dateStr) {
      var date = new Date(dateStr);
      return date.toLocaleString();
    }

    maptable.prototype.ajaxData = function () {
      var me = this;

      me.$tableBody.html("");
      me.numRows = 0;
      var options = {
        limit: 10
      }

      $.ajax({
        url: "/api",
        method: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(options),
        error: function (jqXHR, textStatus, errorThrown) {
          console.error(me.name + " encountered a '" + textStatus + "' ajax error: " + errorThrown);
        },
        success: function (dat, textStatus, jqXHR) {
          me.buildTable(dat);
        }
      });
    }

    maptable.prototype.attach_EventHandlers = function ()
    {
        var me = this;

        $("#apiLink", me.$element).click(function (event) {
          me.ajaxData();
        })
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
