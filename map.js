var mymap = L.map('mapid').setView([15, 0], 2);

var myStyle = {
    "color": "#ff7800",
    "weight": 1,
    "opacity": 1
};

var mapLayerRequest = new XMLHttpRequest();
mapLayerRequest.addEventListener("load", function() {L.geoJSON(JSON.parse(this.responseText), {style: myStyle}).addTo(mymap);});
mapLayerRequest.open("GET", "https://maythird.ddns.net/letsencrypt/countries.geojson");
mapLayerRequest.send();

function plotCord() {
    var ipDataset = JSON.parse(this.responseText);
    for (ipData in ipDataset) {
        console.log(ipData)
        L.marker([ipDataset[ipData].latitude, ipDataset[ipData].longitude]).addTo(mymap);
    }
}

var ipDataRequest = new XMLHttpRequest();
ipDataRequest.addEventListener("load", plotCord);
ipDataRequest.open("GET", "http://localhost:5000");
ipDataRequest.send();