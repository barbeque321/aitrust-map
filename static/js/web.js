var latLngs = 0;
var theRadius = 0;
var theAdressInfo = 0;

$(document).ready(function(){
// create map instance 
var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a>',
osm = L.tileLayer(osmUrl, { maxZoom: 17, attribution: osmAttrib }),
map = new L.Map('map', { 
    center: new L.LatLng(52.415823, 18.874512), 
    zoom: 6 
}),
drawnItems = L.featureGroup().addTo(map);
drawnItems2 = L.featureGroup().addTo(map);
drawnItems3 = L.featureGroup().addTo(map);
drawnItems4 = L.featureGroup().addTo(map);

// create layers control panel
L.control.layers({
    'Mapa': osm.addTo(map),
    "Satelita": L.tileLayer('http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}', {
        attribution: '&copy; Google'
    })
}, { 'Zaznaczenie obszaru': drawnItems, 'Kody pocztowe': drawnItems2, 'Zagęszczenie punktów adresowych': drawnItems3 }, { position: 'topleft', collapsed: false }).addTo(map);

// create figure drawing panel 
var drawControlFull = new L.Control.Draw({
    draw: {
        polyline: false,
        marker: false,
        circle: true,
        polygon: false,
        circlemarker: false,
        rectangle: false,     
    },
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

// get geo parameters of area
map.on('draw:created', function (e) {
var type = e.layerType;
var layer = e.layer;

if (type === 'circle') {
    theRadius = layer.getRadius();
    latLngs = layer.getLatLng();
    }
if (type === 'polygon') {
    latLngs = layer.getLatLngs();
    theRadius = 0;
    }
if (type === 'rectangle') {
    latLngs = layer.getLatLngs();
    theRadius = 0;
    }    

});

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

// add map scale
L.control.scale().addTo(map);

// add search option
var searchControl = L.esri.Geocoding.geosearch({
    placeholder: "Wyszukaj lokalizację siedziby",
    title: "Wyszukaj siedzibę",
    zoomToResult: false
    }).addTo(map);

// reverse geocoding if needed
// not in use actually
var results = L.layerGroup().addTo(map);
var geocodeService = L.esri.Geocoding.geocodeService();

searchControl.on('results', function (data) {
    results.clearLayers();
    for (var i = data.results.length - 1; i >= 0; i--) {
    results.addLayer(L.marker(data.results[i].latlng));
    }
    results.eachLayer(function (layer) {
    if (layer instanceof L.Marker){
        var theAdresslatlng;
        theAdresslatlng = layer.getLatLng();
        console.log("Coordinates: " + theAdresslatlng.toString());
        map.setView(theAdresslatlng, 11, { animation: true });  
        geocodeService.reverse().latlng(layer.getLatLng()).run(function (error, result) {
            if (error) {
                return;
            }
        theAdressInfo = result.address.Match_addr;
        console.log("Adress: " + result.address.Match_addr);
        });
        }
    });
});

// generate data from selected area
$(function(){
    $("#update_log_button").bind('click', function(){
            // show loading image
            $('#loadingmessage').show();
            // get geo params of circle
            if (latLngs != 0 && theRadius != 0){
                if (theRadius > 80000) {
                
                    $('#loadingmessage').hide();
                    alert("Maksymalny promień obszaru to 80km. Proszę użyć narzędzia edycji i zmniejszyć obszar.");
                }
                else {
                    console.log('Sending data...');
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
                            $('#loadingmessage').hide();
                            console.log("Ready");
                            $('#points_sum').contents()[0].textContent = data.points_sum;
                            $('#postal_code_sum').contents()[0].textContent = data.postal_code_sum;
                            postal_list_to_draw = data.postal_code;
                            postal_code_sum = data.postal_code_sum;
                            // dynamiclly change values of html elements
                            document.getElementById("postal_code").innerHTML = data.postal_code;
                            document.getElementById("postal_codes_popupbox").innerHTML = data.postal_code;
                            document.getElementById("info_radius").innerHTML = data.rad + "km";
                            document.getElementById("info_postal_code_sum").innerHTML = data.postal_code_sum;
                            document.getElementById("info_adress_sum").innerHTML = data.points_sum;
                            document.getElementById("info_radius_10").innerHTML = data.rad_up_10 + "km";
                            document.getElementById("info_postal_code_sum_10").innerHTML = data.postal_code_sum_up_10;
                            document.getElementById("info_adress_sum_10").innerHTML = data.points_sum_up_10;
                            document.getElementById("info_postal_code_sum_difference").innerHTML = " (+" + data.difference_postal_num + ")";
                            document.getElementById("info_adress_sum_difference").innerHTML = " (+" + data.differene_points_num + ")";
                            clamp(document.getElementById('postal_code'), 3);
                        }, 
                        error: function (jqXhr, textStatus, errorThrown) {
                            $('#loadingmessage').hide();
                            console.log('ERROR');
                            console.log(jqXhr);
                        },

                });
                }
            }
            else if (latLngs != 0 && theRadius == 0){
                // get geo params of polygon
                console.log('Sending data...');
                $.ajax({
                    type: "GET",
                    url: 'process_loc2/',
                    data: {
                        "latLngs": JSON.stringify(latLngs),
                    },
                    contentType: 'application/json; charset=utf-8',
                    dataType: 'json',
                    success: function(data){
                        $('#loadingmessage').hide();
                        console.log("Zwracam otrzymane wartości punktów: " + JSON.stringify(data));
                    }, 
                    error: function (jqXhr, textStatus, errorThrown) {
                        $('#loadingmessage').hide();
                        console.log('ERROR');
                        console.log(jqXhr);
                     },
                });
            }          
                else {
                    // if no figure is drawn on map show popup
                    $('#loadingmessage').hide();
                    alert("Brak współrzędnych!");
                };
    });
});
           

// edition of tooltip messages text - translation to polish
L.drawLocal = {
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
                    subtext: 'Kliknij anuluj by odrzucić zmiany lub zapisz by je zatwierdzić'
                }
            },
            remove: {
                tooltip: {
                    text: 'Kliknij na znacznik by usunąć'
                }
            }
        }
    }
};

// handling information box switching transitions
let frameTransitionTime = 500;
let $frame = $('.js-frame');
let $postal = $('.js-postal');
let $map_points_box = $('.js-map_points_box');
let switching = false;

$(function(){
    $("#postal.js-postal, #map_points_box.js-map_points_box, #info_back_button").bind('click', function(){
        if (switching) {
              return false
           }
           switching = true;
           $frame.toggleClass('is-switched');
           $postal.toggleClass('is-switched');
           $map_points_box.toggleClass('is-switched');
           window.setTimeout(function () {
              $frame.children().children().toggleClass('is-active');
              switching = false;
           }, 
           frameTransitionTime / 2);
        });
});

// dinamiclly clamping great number of postal codes to smaller box 
if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {
    if (typeof this !== "function") {
        throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
    }
 
    var aArgs = Array.prototype.slice.call(arguments, 1),
        fToBind = this,
        fNOP = function () {},
        fBound = function () {
            return fToBind.apply(this instanceof fNOP && oThis ? this : oThis, aArgs.concat(Array.prototype.slice.call(arguments)));
        };
    fNOP.prototype = this.prototype;
    fBound.prototype = new fNOP();
    return fBound;
  };
}

(function(w, d){
    var clamp, measure, text, lineWidth,
        lineStart, lineCount, wordStart,
        line, lineText, wasNewLine,
    ce = d.createElement.bind(d),
    ctn = d.createTextNode.bind(d);
    
    // measurement element is made a child of the clamped element to get it's style
    measure = ce('span');  
    (function(s){
        s.position = 'absolute'; // prevent page reflow
        s.whiteSpace = 'pre'; // cross-browser width results
        s.visibility = 'hidden'; // prevent drawing
    })(measure.style);
    
    clamp = function (el, lineClamp) {
    // make sure the element belongs to the document
    if(!el.ownerDocument || !el.ownerDocument === d) return;
        // reset to safe starting values
        lineStart = wordStart = 0;
        lineCount = 1;
        wasNewLine = false; 
        lineWidth = el.clientWidth;
        // get all the text, remove any line changes
        text = (el.textContent || el.innerText).replace(/\n/g, ' ');
        // remove all content
        while(el.firstChild !== null)
            el.removeChild(el.firstChild);
        // add measurement element within so it inherits styles
        el.appendChild(measure);
        // http://ejohn.org/blog/search-and-dont-replace/
        text.replace(/ /g, function(m, pos) {
            // ignore any further processing if we have total lines
        if(lineCount === lineClamp) return;
            // create a text node and place it in the measurement element
            measure.appendChild(ctn(text.substr(lineStart, pos - lineStart)));
            // have we exceeded allowed line width?
            if(lineWidth < measure.clientWidth) {
                if(wasNewLine) {
                    // we have a long word so it gets a line of it's own
                    lineText = text.substr(lineStart, pos + 1 - lineStart);
                    // next line start position
                    lineStart = pos + 1;
                } else {
                    // grab the text until this word
                    lineText = text.substr(lineStart, wordStart - lineStart);
                    // next line start position
                    lineStart = wordStart;
                }
                // create a line element
                line = ce('span');
                // add text to the line element
                line.appendChild(ctn(lineText));
                // add the line element to the container
                el.appendChild(line);
                // yes, we created a new line
                wasNewLine = true;
        lineCount++;
        } 
        else {
            // did not create a new line
            wasNewLine = false;
        }
        // remember last word start position
        wordStart = pos + 1;
        // clear measurement element
        measure.removeChild(measure.firstChild);
        });
        // remove the measurement element from the container
        el.removeChild(measure);
        // create the last line element
        line = ce('span');
        // give styles required for text-overflow to kick in
        (function(s){
            s.display = 'block';
            s.overflow = 'hidden';
            s.textOverflow = 'ellipsis';
            s.whiteSpace = 'nowrap';
            s.width = '100%';
        })(line.style);
        // add all remaining text to the line element
        line.appendChild(ctn(text.substr(lineStart)));
        // add the line element to the container
        el.appendChild(line);
    }
    w.clamp = clamp;
})(window, document);

$(window).bind('load', function() {
  clamp(document.getElementById('postal_code'), 3);
});

// dynamiclly generate window with all postal codes  
// add overlay to dimm rest of site
const openPopupboxButtons = document.querySelectorAll('[data-popupbox-target]');
const closePopupboxButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

openPopupboxButtons.forEach(button => {
    button.addEventListener('click', () => {
    const popupbox = document.querySelector(button.dataset.popupboxTarget);
    openPopupbox(popupbox);
    })
});

overlay.addEventListener('click', () => {
    const popupbox = document.querySelectorAll('.popupbox.active')
    popupbox.forEach(popupbox => {
    closePopupbox(popupbox)
    })
});

closePopupboxButtons.forEach(button => {
    button.addEventListener('click', () => {
    const popupbox = button.closest('.popupbox')
    closePopupbox(popupbox)
    })
});

function openPopupbox(popupbox) {
    if (popupbox == null) return
    popupbox.classList.add('active');
    overlay.classList.add('active');
};

function closePopupbox(popupbox) {
    if (popupbox == null) return
    popupbox.classList.remove('active');
    overlay.classList.remove('active');
};

var myStyle = {
    "color": "#ff7800",
    "weight": 5,
    "opacity": 0.65
};

// add dynamiclly generated layers to group
function addNonGroupLayers(sourceLayer, targetGroup) {
    if (sourceLayer instanceof L.LayerGroup) {
        sourceLayer.eachLayer(function (layer) {
            addNonGroupLayers(layer, targetGroup);
        });
    } 
    else {
        targetGroup.addLayer(sourceLayer);
    }
};


// draw area of postal codes front
$(function(){
    $("#poly").bind('click', function(){
            // allow only 70 postal codes at once
            if (postal_code_sum > 1100) {
                alert("Maksymalna liczba obszarów do jednoczesnego generowania na mapie to 70. Proszę użyć narzędzia edycji i zmniejszyć obszar.");
            }
            // check if there is at least 1 postal code
            if (postal_code_sum == 0) {
                alert("Brak danych. Proszę zaznaczyć obszar i wygenerować dane.");
            }
            else {
                // show loading image
                $('#loadingmessage').show();
                    console.log('Sending data...');
                    $.ajax({
                        type: "GET",
                        data: {
                            "postal_list_to_draw": postal_list_to_draw,
                            "lat": latLngs.lat,
                            "lng": latLngs.lng,
                            "rad": theRadius,
                        },
                        url: 'draw_polygon_better/',
                        contentType: 'application/json; charset=utf-8',
                        dataType: 'json',
                        success: function(data){
                            $('#loadingmessage').hide();
                            console.log("Ready");
                            console.log(data.debug_info);
                            console.log(data.sql_data);
                            var postal_data = data.postal_alpha_shape_points_dict_list;
                            var points_data = data.lat_lng_list;
                            if(Object.keys(postal_data).length) {
                                Object.keys(postal_data).forEach(key => {
                                var heat_points = points_data[key];
                                var heat_points_arr = [];
                                var innerArrayLength_heat_points = heat_points.length;
                                for (let j = 0; j < innerArrayLength_heat_points; j++) {
                                    heat_points_arr.push([heat_points[j][1], heat_points[j][0]]); 
                                    }
                                var heat = L.heatLayer(heat_points_arr,{
                                    radius: 17,
                                    blur: 15, 
                                    maxZoom: 17,
                                }).addTo(map);
                                addNonGroupLayers(heat, drawnItems3);

                                var polygonus = postal_data[key];
                                var postal_no = key;
                                let arr = [];
                                var innerArrayLength = polygonus[0][0][0].length;
                                for (let j = 0; j < innerArrayLength; j++) {
                                    arr.push([polygonus[0][0][0][j][0], polygonus[0][0][0][j][1]]); 
                                    }
                                var number_of_points = points_data[key];
                                var innerArrayLength_number_of_points = number_of_points.length;
                                var options = {
                                style: function (feature) {
                                    var random_color = (0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6)
                                    return {
                                        "color": "#"+random_color,
                                        "weight": 2,
                                        "opacity": 1,
                                        "fillColor": '#'+random_color,
                                        "fillOpacity": 0.6
                                    };
                                }
                                };
                                var polygonus_geo_form = {
                                    type: "FeatureCollection",
                                    features: [{ 
                                        type:"Feature", 
                                        properties: {
                                            popupContent: []
                                        }, 
                                        geometry: { 
                                            type: "Polygon", 
                                            coordinates: []
                                        }
                                    }]
                                };
                                polygonus_geo_form.features[0].geometry.coordinates.push(arr);
                                var layerpoly = new L.geoJson(polygonus_geo_form.features, options).addTo(map).bindPopup("<strong>Kod pocztowy: </strong>"+postal_no+"<br /><strong>Liczba punktów adresowych: </strong>"+innerArrayLength_number_of_points);
                                addNonGroupLayers(layerpoly, drawnItems2);
                                });
                            }
                        },
                        error: function (jqXhr, textStatus, errorThrown) {
                            $('#loadingmessage').hide();
                            console.log('ERROR');
                            console.log(jqXhr);
                        }
                }); 
            }            
    });
});








// generate data from selected area
$(function(){
    $("#search_airports").bind('click', function(){
            // show loading image
            $('#loadingmessage').show();
            // get geo params of circle
            if (latLngs != 0 && theRadius != 0){
                if (theRadius > 600000) {
                
                    $('#loadingmessage').hide();
                    alert("Maksymalny promień obszaru to 600km. Proszę użyć narzędzia edycji i zmniejszyć obszar.");
                }
                if (theRadius < 600000){
                    console.log('Sending data...');
                    $.ajax({
                        type: "GET",
                        url: 'search_for_airports/',
                        data: {
                            "lat": latLngs.lat,
                            "lng": latLngs.lng,
                            "rad": theRadius,
                        },
                        contentType: 'application/json; charset=utf-8',
                        dataType: 'json',
                        success: function(data){
                            $('#loadingmessage').hide();
                            console.log("Ready");
                            console.log(data.airports);
                            var airports_data = data.airports;
                            if(Object.keys(airports_data).length) {
                                Object.keys(airports_data).forEach(key => {
                                var airport_info = airports_data[key];
                                var airport_name = key;
                                var country_name = airport_info[0][3]
                                var city_name = airport_info[0][2]
                                var IATA_name = airport_info[0][4]
                                var ICAO_name = airport_info[0][5]
                                var marker_layer = new L.marker([airport_info[0][1], airport_info[0][0]]).addTo(map).bindPopup("<strong>Lotnisko: </strong>"+airport_name+"<br /><strong>Country: </strong>"+country_name+"<br /><strong>City: </strong>"+city_name+"<br /><strong>IATA: </strong>"+IATA_name+"<br /><strong>ICAO: </strong>"+ICAO_name);
                                addNonGroupLayers(marker_layer, drawnItems4);
                                });
                            }  
                        }, 
                        error: function (jqXhr, textStatus, errorThrown) {
                            $('#loadingmessage').hide();
                            console.log('ERROR');
                            console.log(jqXhr);
                        },

                });
                }
            }        
                else {
                    // if no figure is drawn on map show popup
                    $('#loadingmessage').hide();
                    alert("Brak współrzędnych!");
                };
    });
});










});

