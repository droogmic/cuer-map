var map_center = {lat: -25.6846847, lng: 134.1369875};
var control_stops = [
    {name: 'Katherine', loc:{lat: -14.481516, lng: 132.325057}},
    {name: 'Daly Waters', loc:{lat: -16.307695, lng: 133.385081}},
    {name: 'Tennant Creek', loc:{lat: -19.657750, lng: 134.188500}},
    {name: 'Barrow Creek', loc:{lat: -21.531197, lng: 133.888984}},
    {name: 'Alice Springs', loc:{lat: -23.708951, lng: 133.874868}},
    {name: 'Kulgera', loc:{lat: -25.839623, lng: 133.300533}},
    {name: 'Coober Pedy', loc:{lat: -29.018070, lng: 134.754496}},
    {name: 'Glendambo', loc:{lat: -30.970391, lng: 135.750442}},
    {name: 'Port Augusta', loc:{lat: -32.508634, lng: 137.797072}},
];

var CSMarkers;
var locationMarkers;
// var updateMarkers;

function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: map_center
    });
    drawRoute(map);
    CSMarkers = dropCSMarkers(map);
    locationMarkers = dropLocationMarkers(map);
    // updateMarkers = dropUpdateMarkers(map);
}

function drawRoute(map) {
    var directionsDisplay = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        polylineOptions: {
            strokeWeight: 2
        }
    });
    directionsDisplay.setMap(map);
    var request = {
        origin: "Darwin, NT",
        destination: "Adelaide, SA",
        travelMode: google.maps.TravelMode.DRIVING
    };
    var directionsService = new google.maps.DirectionsService();
    directionsService.route(request, function(response, status) {
        if (status == 'OK') {
            directionsDisplay.setDirections(response);
        }
    });
}

function dropUpdateMarkers(map) {
    var markers = [];
    var addMarker = (function(pos, idx) {
        return (function () {
            markers.push(addUpdateMarkerMethod(map, pos, idx));
        });
    });
    locations.forEach(function(element, idx) {
        setTimeout(addMarker({lat: parseFloat(element.lat), lng: parseFloat(element.lng)}, idx), idx*100);
    });
    return markers;
}
function addUpdateMarkerMethod(map, pos, idx) {
    let size = 50/(idx+1);
    let opacity = 1/(idx/5+1);
    let label_text = (idx==0)?"Latest Position":" ";
    var marker = new google.maps.Marker({
        position: pos,
        icon: {
            url: "https://maps.google.com/mapfiles/kml/paddle/wht-blank.png",
            scaledSize: {width: size, height: size},
            labelOrigin: new google.maps.Point(0.5*size, size+10),
        },
        opacity: opacity,
        label: {
            text: label_text,
            fontWeight: 'bold',
            fontSize: 'large',
        },
        map: map,
        animation: google.maps.Animation.DROP,
    });
    return marker;
}

function dropLocationMarkers(map) {
    var poly = new google.maps.Polyline({
        strokeColor: '#f00',
        strokeWeight: 4
    });
    poly.setMap(map);
    var markers = [];
    var addMarker = (function(pos, dt, last) {
        return (function () {
            console.log(dt);
            var path = poly.getPath();
            path.push(new google.maps.LatLng(pos.lat, pos.lng));
            markers.push(addLocationMarkerMethod(map, pos, dt, last));
        });
    });
    locations.forEach(function(element, idx) {
        if (idx === locations.length - 1){
            setTimeout(addMarker({lat: parseFloat(element.lat), lng: parseFloat(element.lng)}, element.dt, true), idx*1000);
        } else {
            setTimeout(addMarker({lat: parseFloat(element.lat), lng: parseFloat(element.lng)}, element.dt, false), idx*1000);
        }
    });
    return {
        markers: markers,
        poly: poly,
    }
}
function addLocationMarkerMethod(map, pos, dt, last) {
    var infowindow = new google.maps.InfoWindow({
        content: '<div id="content">' + '<i class="material-icons">schedule</i>' + '<span>' + dt + '</span>' + '</div>',
    });
    var symbol = {
        path: google.maps.SymbolPath.CIRCLE,
        scale: last?6:4,
        strokeColor: 'blue',
    };
    var marker = new google.maps.Marker({
        position: pos,
        icon: symbol,
        map: map,
        animation: last?google.maps.Animation.BOUNCE:google.maps.Animation.DROP,
    });
    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
    marker.addListener('mouseover', function() {
        symbol.scale = last?12:8;
        marker.setIcon(symbol);
    });
    marker.addListener('mouseout', function() {
        symbol.scale = last?6:4;
        marker.setIcon(symbol);
    });
    return marker;
}

function dropCSMarkers(map) {
    var markers = [];
    var addMarker = (function(pos, label_string) {
        return (function () {
            markers.push(addCSMarkerMethod(map, pos, label_string));
        });
    });
    control_stops.forEach(function(element, idx) {
        setTimeout(addMarker(element.loc, element.name+" Control Stop"), idx*10);
    });
    return markers;
}
function addCSMarkerMethod(map, pos, label_string) {
    var infowindow = new google.maps.InfoWindow({
        content: label_string
    });
    var marker = new google.maps.Marker({
        position: pos,
        icon: {
            url: "https://maps.google.com/mapfiles/kml/paddle/wht-blank.png",
            scaledSize: {width: 40, height: 40},
            labelOrigin: new google.maps.Point(20, 13),
        },
        label: {
            text: 'CS',
            fontWeight: 'bold'
        },
        map: map,
        animation: google.maps.Animation.DROP,
    });
    marker.addListener('click', function() {
        infowindow.open(map, marker);
    });
    return marker;
}
