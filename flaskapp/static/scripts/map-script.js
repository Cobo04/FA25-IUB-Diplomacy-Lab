// amCharts v5 is loaded via CDN and exposes global variables (am5, am5map, am5geodata_worldLow, am5themes_Animated)
am5.ready(function() {

// Defensive checks to avoid errors when the chart container is missing or the script runs twice.
// If the element with id "chartdiv" doesn't exist, abort initialization to avoid
// amcharts calling getComputedStyle on a non-element (which causes the error you saw).
var chartDiv = document.getElementById('chartdiv');
if (!chartDiv) {
  console.warn('map-script: #chartdiv not found — aborting amCharts initialization');
  return;
}

// If a previous amCharts Root was created on this page, dispose it first so we don't get
// "You cannot have multiple Roots on the same DOM node" when the script runs again.
if (window._am5_root && typeof window._am5_root.dispose === 'function') {
  try {
    window._am5_root.dispose();
  } catch (e) {
    // swallow — we'll try to create a fresh root anyway
    console.warn('map-script: error disposing previous am5 root', e);
  }
  window._am5_root = null;
}

// Create root element
// https://www.amcharts.com/docs/v5/getting-started/#Root_element
var root = am5.Root.new("chartdiv");
// store reference globally so future re-inits can dispose it first
window._am5_root = root;


// Set themes
// https://www.amcharts.com/docs/v5/concepts/themes/
root.setThemes([
  am5themes_Animated.new(root)
]);


// Create the map chart
// https://www.amcharts.com/docs/v5/charts/map-chart/
var chart = root.container.children.push(am5map.MapChart.new(root, {
  panX: "rotateX",
  panY: "rotateY",
  projection: am5map.geoOrthographic()
}));


// Create series for background fill
// https://www.amcharts.com/docs/v5/charts/map-chart/map-polygon-series/#Background_polygon
var backgroundSeries = chart.series.push(
  am5map.MapPolygonSeries.new(root, {})
);
backgroundSeries.mapPolygons.template.setAll({
  fill: root.interfaceColors.get("alternativeBackground"),
  fillOpacity: 0.1,
  strokeOpacity: 0
});
backgroundSeries.data.push({
  geometry:
    am5map.getGeoRectangle(90, 180, -90, -180)
});


// Create main polygon series for countries
// https://www.amcharts.com/docs/v5/charts/map-chart/map-polygon-series/
var polygonSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {
  geoJSON: am5geodata_worldLow 
}));
polygonSeries.mapPolygons.template.setAll({
  fill: root.interfaceColors.get("alternativeBackground"),
  fillOpacity: 0.15,
  strokeWidth: 0.5,
  stroke: root.interfaceColors.get("background")
});


// Create polygon series for projected circles
var circleSeries = chart.series.push(am5map.MapPolygonSeries.new(root, {}));
circleSeries.mapPolygons.template.setAll({
  templateField: "polygonTemplate",
  tooltipText: "{name}:{value}"
});

// Series for drawing lines between countries (e.g., China <-> Germany)
var lineSeries = chart.series.push(am5map.MapLineSeries.new(root, {}));
lineSeries.mapLines.template.setAll({
  stroke: am5.color(0xff0000),
  strokeWidth: 2,
  strokeOpacity: 0.9
});

// Series for endpoint markers (helpful for debugging visibility)
var pointSeries = chart.series.push(am5map.MapPointSeries.new(root, {}));
pointSeries.bullets.push(function() {
  return am5.Bullet.new(root, {
    sprite: am5.Circle.new(root, {
      radius: 6,
      fill: am5.color(0x00ff00),
      stroke: am5.color(0x000000),
      strokeWidth: 1
    })
  });
});

// Define data
var colors = am5.ColorSet.new(root, {});

var data = []

var valueLow = Infinity;
var valueHigh = -Infinity;

for (var i = 0; i < data.length; i++) {
  var value = data[i].value;
  if (value < valueLow) {
    valueLow = value;
  }
  if (value > valueHigh) {
    valueHigh = value;
  }
}

// radius in degrees
var minRadius = 0.5;
var maxRadius = 5;

// Create circles when data for countries is fully loaded.
polygonSeries.events.on("datavalidated", function () {
  circleSeries.data.clear();

  for (var i = 0; i < data.length; i++) {
    var dataContext = data[i];
    var countryDataItem = polygonSeries.getDataItemById(dataContext.id);
    var countryPolygon = countryDataItem.get("mapPolygon");

    var value = dataContext.value;

    var radius = minRadius + maxRadius * (value - valueLow) / (valueHigh - valueLow);

    if (countryPolygon) {
      var geometry = am5map.getGeoCircle(countryPolygon.visualCentroid(), radius);
      circleSeries.data.push({
        name: dataContext.name,
        value: dataContext.value,
        polygonTemplate: dataContext.polygonTemplate,
        geometry: geometry
      });
    }
  }
  
  // Draw lines from China (CN) to multiple countries
  try {
    // remove previous lines and points
    lineSeries.data.clear();
    pointSeries.data.clear();

    var chinaItem = polygonSeries.getDataItemById('CN');
    if (!chinaItem) {
      console.warn('China data item not found');
      return;
    }
    var chinaPolygon = chinaItem.get('mapPolygon');
    if (!chinaPolygon) {
      console.warn('China polygon not found');
      return;
    }

    var rawC1 = chinaPolygon.visualCentroid();

    // helper: normalize various centroid shapes to [lon, lat]
    function normalizeCentroid(v) {
      if (!v) return null;
      if (Array.isArray(v) && v.length >= 2) return [v[0], v[1]];
      if (typeof v === 'object') {
        if (typeof v.longitude === 'number' && typeof v.latitude === 'number') return [v.longitude, v.latitude];
        if (typeof v.lon === 'number' && typeof v.lat === 'number') return [v.lon, v.lat];
        if (typeof v.lng === 'number' && typeof v.lat === 'number') return [v.lng, v.lat];
        if (typeof v.x === 'number' && typeof v.y === 'number') return [v.x, v.y];
        if (v.hasOwnProperty('coordinates') && Array.isArray(v.coordinates)) return v.coordinates.slice(0,2);
      }
      return null;
    }

    var c1 = normalizeCentroid(rawC1);
    console.log('raw CN centroid ->', rawC1);
    console.log('normalized CN centroid ->', c1);

    if (!Array.isArray(c1) || c1.length < 2) {
      console.warn('Invalid China centroid, aborting multi-line draw', c1);
      return;
    }

    // target country ISO codes — 7 countries in addition to Germany (DE already handled earlier if present)
    var targets = ['US','GB','AU','BR','ZA','IN','JP'];

    targets.forEach(function(tid) {
      try {
        var targetItem = polygonSeries.getDataItemById(tid);
        if (!targetItem) {
          console.warn('Target not found:', tid);
          return;
        }
        var targetPolygon = targetItem.get('mapPolygon');
        if (!targetPolygon) {
          console.warn('Target polygon not found for', tid);
          return;
        }

        var rawC2 = targetPolygon.visualCentroid();
        var c2 = normalizeCentroid(rawC2);
        console.log('raw', tid, 'centroid ->', rawC2);
        console.log('normalized', tid, 'centroid ->', c2);

        if (!Array.isArray(c2) || c2.length < 2) {
          console.warn('Invalid centroid for target', tid, c2);
          return;
        }

        // add debug point markers at both endpoints
        try {
          pointSeries.data.push({ geometry: { type: 'Point', coordinates: [c1[0], c1[1]] }, id: 'CN-point-' + tid });
          pointSeries.data.push({ geometry: { type: 'Point', coordinates: [c2[0], c2[1]] }, id: tid + '-point' });
        } catch (e) {
          console.warn('Failed to push points for', tid, e);
        }

        // create a geo line connecting the two centroids
        var lineGeometry;
        if (typeof am5map.getGeoLine === 'function') {
          lineGeometry = am5map.getGeoLine(c1, c2);
        } else {
          lineGeometry = { type: 'LineString', coordinates: [[c1[0], c1[1]], [c2[0], c2[1]]] };
        }

        lineSeries.data.push({ geometry: lineGeometry, id: 'CN-' + tid, name: 'China - ' + tid });
      } catch (e) {
        console.error('Error drawing line to', tid, e);
      }
    });

  } catch (e) {
    console.error('Error drawing CN lines', e);
  }
})


// Make stuff animate on load
chart.appear(1000, 100);

}); // end am5.ready()