var mymap = L.map('mapid', {maxZoom: 19}).setView([15, 0], 2);

var myStyle = {
    "fillColor": "BlanchedAlmond",
    "color": "black",
    "weight": .5,
    "opacity": 1,
    "fill": true,
    "fillOpacity": 0.7
};

var popupData = function(ip) {
    return function() {
        var popupDataReq = new XMLHttpRequest();
        popupDataReq.open("GET", "http://localhost:5000/" + ip, false);
        popupDataReq.send();
        var returnString = "";
        var dateOptions = {
            month: 'short', day: 'numeric', year: 'numeric',
            timeZone: 'America/Los_Angeles' 
        };
        JSON.parse(popupDataReq.responseText).forEach(element => returnString += (new Date(element * 1000).toLocaleTimeString("en-US", dateOptions) + '<br/>'));
        return returnString;
    }
}

var mapLayerRequest = new XMLHttpRequest();
mapLayerRequest.addEventListener("load", function() {L.geoJSON(JSON.parse(this.responseText), {style: myStyle}).addTo(mymap);});
mapLayerRequest.open("GET", "https://maythird.ddns.net/letsencrypt/countries.geojson");
mapLayerRequest.send();

function plotCord() {
    var ipDataset = JSON.parse(this.responseText);    
    var myIcon = L.icon({
        iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/b/b6/PuTTY_icon_128px.png',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
        popupAnchor: [8, 8],
        // shadowUrl: 'my-icon-shadow.png',
        // shadowSize: [68, 95],
        // shadowAnchor: [22, 94]
    });
    var markers = L.markerClusterGroup();
    for (ipData in ipDataset) {
        markers.addLayer(L.marker([ipDataset[ipData].latitude, ipDataset[ipData].longitude], {icon: myIcon}).bindPopup(popupData(ipDataset[ipData].ip)).openPopup());
    }
    mymap.addLayer(markers);
}

var ipDataRequest = new XMLHttpRequest();
ipDataRequest.addEventListener("load", plotCord);
ipDataRequest.open("GET", "http://localhost:5000");
ipDataRequest.send();