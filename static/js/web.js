var latLngs = 0;
var theRadius = 0;

$(document).ready(function(){


var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a>',
        osm = L.tileLayer(osmUrl, { maxZoom: 17, attribution: osmAttrib }),
        map = new L.Map('map', { center: new L.LatLng(52.415823, 18.874512), zoom: 6 }),
        drawnItems = L.featureGroup().addTo(map);
L.control.layers({
    'Mapa': osm.addTo(map),
    "Satelita": L.tileLayer('http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}', {
        attribution: '&copy; Google'
    })
}, { 'Zaznaczenia': drawnItems }, { position: 'topleft', collapsed: false }).addTo(map);


var drawControlFull = new L.Control.Draw({
    draw: {
        polyline: false,
        marker: false,
        circle: true,
        polygon: true,
        circlemarker: false,
        rectangle: true,
        polygon: {
            allowIntersection: false,
            showArea: true
    }},
    edit: {
        featureGroup: drawnItems
    }
});
var drawControlEditOnly = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    },
    draw: false
});
map.addControl(drawControlFull);

map.on(L.Draw.Event.CREATED, function (e) {
    drawnItems.addLayer(e.layer);
    map.removeControl(drawControlFull);
    map.addControl(drawControlEditOnly);
});

map.on(L.Draw.Event.DELETED, function(e) {
    if (drawnItems.getLayers().length === 0){
        map.removeControl(drawControlEditOnly);
        map.addControl(drawControlFull);
    }
});


map.on('draw:created', function (e) {
var type = e.layerType;
var layer = e.layer;

if (type === 'circle') {
    theRadius = layer.getRadius();
    latLngs = layer.getLatLng();
                        }
if (type === 'polygon') {
    latLngs = layer.getLatLngs();
    console.log(latLngs);
    theRadius = 0;
                        }
if (type === 'rectangle') {
    latLngs = layer.getLatLngs();
    console.log(latLngs);
    theRadius = 0;
                        }    

                                    })


map.on('draw:edited', function (e) {
    var layers = e.layers;
    layers.eachLayer(function (layer) {
        if (layer instanceof L.Circle){
            theRadius = layer.getRadius();
            latLngs = layer.getLatLng();
            }
        if (layer instanceof L.Polyline){
             latLngs = layer.getLatLngs();
        }
        
    });
});


$(function(){
    $("#update_log_button").bind('click', function(){
        console.log('Sending data from client to server');
        if (latLngs != 0 && theRadius != 0){
            $.ajax({
                type: "GET",
                url: 'process_loc/',
                data: {
                    "lat": latLngs.lat,
                    "lng": latLngs.lng,
                    "rad": theRadius,
                },
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function(data){
                         console.log("Zwracam otrzymaną wartość centrum okręgu i jego promień: " + JSON.stringify(data))

                }, 
                error: function (jqXhr, textStatus, errorThrown) {
                       console.log('ERROR');
                       console.log(jqXhr);
                 },
                });}
        else if (latLngs != 0 && theRadius == 0){
            $.ajax({
                type: "GET",
                url: 'process_loc2/',
                data: {
                    "latLngs": latLngs,
                },
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function(data){
                         console.log("Zwracam otrzymane wartości punktów: " + JSON.stringify(data))

                }, 
                error: function (jqXhr, textStatus, errorThrown) {
                       console.log('ERROR');
                       console.log(jqXhr);
                 },
                });}
        
        else {
            console.log("Brak współrzędnych!");
        };
            

                                                    });
            });






L.control.scale().addTo(map);

var searchControl = L.esri.Geocoding.geosearch({
    placeholder: "Wyszukaj lokalizację siedziby",
    title: "Wyszukaj siedzibę",
    zoomToResult: false
    }).addTo(map);

var results = L.layerGroup().addTo(map);

searchControl.on('results', function (data) {
    results.clearLayers();
    for (var i = data.results.length - 1; i >= 0; i--) {
    results.addLayer(L.marker(data.results[i].latlng));
    }
    

    results.eachLayer(function (layer) {
    if (layer instanceof L.Marker){
        var theAdress;
        theAdress = layer.getLatLng();
        console.log("Coordinates: " + theAdress.toString());
        map.setView(theAdress, 11, { animation: true });  
        }
    }
    )
  });





L.drawLocal = {
    // format: {
    //  numeric: {
    //      delimiters: {
    //          thousands: ',',
    //          decimal: '.'
    //      }
    //  }
    // },
    draw: {
        toolbar: {
            buttons: {
                edit: 'Edytuj obiekty',
                editDisabled: 'Brak obiektów do edycji',
                remove: 'Usuń obiekty',
                removeDisabled: 'Brak obiektów do usunięcia',
                polygon: 'Rysuj wielokąt',
                circle: 'Rysuj okrąg',
                rectangle: 'Rysuj czworokąt'
            },
            actions: {
                title: 'Anuluj rysowanie',
                text: 'Anuluj'
            },
            finish: {
                title: 'Zakończ rysowanie',
                text: 'Zakończ'
            },
            undo: {
                title: 'Usuń ostatni punkt',
                text: 'Usuń ostatni punkt'
            },
        },
        handlers: {
            circle: {
                tooltip: {
                    start: 'Kliknij i przeciągnij by rysować okrąg'
                },
                radius: 'Promień'
            },
            circlemarker: {
                tooltip: {
                    start: 'Kliknij by umieścić znacznik kołowy'
                }
            },
            marker: {
                tooltip: {
                    start: 'Kliknij by umieścić znacznik'
                }
            },
            polygon: {
                tooltip: {
                    start: 'Kliknij by rozpocząć rysowanie',
                    cont: 'Kliknij ponownie by kontynuować rysowanie',
                    end: 'Jeśli chcesz zakończyć kliknij na pierwszy znacznik'
                }
            },
            polyline: {
                error: '<strong>Błąd:</strong> linie nie mogą się przecinać!',
                tooltip: {
                    start: 'Kliknij by rozpocząć rysowanie',
                    cont: 'Kliknij by kontynuować rysowanie.',
                    end: 'Kliknij na ostatni punkt by zakończyć rysowanie'
                }
            },
            rectangle: {
                tooltip: {
                    start: 'Kliknij i przeciągnij by rysować czworokąt'
                }
            },
            simpleshape: {
                tooltip: {
                    end: 'Puść przycisk by przestać rysować'
                }
            }
        }
    },
    edit: {
        toolbar: {
            actions: {
                save: {
                    title: 'Zapisz zmiany',
                    text: 'Zapisz'
                },
                cancel: {
                    title: 'Anuluj edycję, odrzuć wszystkie zmiany',
                    text: 'Anuluj'
                },
                clearAll: {
                    title: 'Usuń wszystko',
                    text: 'Usuń wszystko'
                }
            },
            buttons: {
                edit: 'Edytuj obiekty',
                editDisabled: 'Brak obiektów do edycji',
                remove: 'Usuń obiekty',
                removeDisabled: 'Brak obiektów do usunięcia',
                polygon: 'Rysuj wielokąt',
                circle: 'Rysuj okrąg',
                rectangle: 'Rysuj czworokąt'
            }
        },
        handlers: {
            edit: {
                tooltip: {
                    text: 'Przeciągnij znaczniki by dokonać zmian',
                    subtext: 'Kliknij anuluj by odrzucić zmiany'
                }
            },
            remove: {
                tooltip: {
                    text: 'Kliknij na znacznik by usunąć'
                }
            }
        }
    }
}




})








