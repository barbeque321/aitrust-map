var latLngs = 0;
var theRadius = 0;
var theAdressInfo = 0;
var postal_list_to_draw;

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

L.control.layers({
    'Mapa': osm.addTo(map),
    "Satelita": L.tileLayer('http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}', {
        attribution: '&copy; Google'
    })
}, { 'Zaznaczenie': drawnItems, 'Kody': drawnItems2, 'Punkty': drawnItems3 }, { position: 'topleft', collapsed: false }).addTo(map);

// create control panel 
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

// add search 
var searchControl = L.esri.Geocoding.geosearch({
    placeholder: "Wyszukaj lokalizację siedziby",
    title: "Wyszukaj siedzibę",
    zoomToResult: false
    }).addTo(map);

// reverse geocoding
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

// main js connection function
$(function(){
    $("#update_log_button").bind('click', function(){
            // show loading image
            $('#loadingmessage').show();
            // get geo params of circle
            if (latLngs != 0 && theRadius != 0){
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
                        console.log(postal_list_to_draw)
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
           

// edition of tooltip messages 
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

// js code for handling result box transitions
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

// clamping great number of postal codes to smaller window
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

// js code for handling new popupbox with all postal codes 
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

// draw area of postal codes quick algorythm
// $(function(){
//     $("#poly").bind('click', function(){
//             // show loading image
//             $('#loadingmessage').show();
//                 console.log('Sending data...');
//                 $.ajax({
//                     type: "GET",
//                     data: {
//                         "postal_list_to_draw": postal_list_to_draw,
//                     },
//                     url: 'draw_polygon/',
//                     contentType: 'application/json; charset=utf-8',
//                     dataType: 'json',
//                     success: function(data){
//                         $('#loadingmessage').hide();
//                         console.log("Ready");
//                         var postal_data = data.postal_str
//                         if(Object.keys(postal_data).length) {
//                             Object.keys(postal_data).forEach(key => {
//                             var polygonus;
//                             polygonus = postal_data[key];
//                             console.log(polygonus);
//                             let arr = [];
//                             var innerArrayLength = polygonus[0].length;
//                             // loop the inner array
//                             for (let j = 0; j < innerArrayLength; j++) {
//                                     arr.push([polygonus[0][j][1], polygonus[0][j][0]]); 
//                                     }
                            
//                             console.log(arr);
//                             var poly = L.polygon(arr).addTo(map);
//                             });
//                         }
//                     },
//                     error: function (jqXhr, textStatus, errorThrown) {
//                         $('#loadingmessage').hide();
//                         console.log('ERROR');
//                         console.log(jqXhr);
//                     }
//                 });
//     });
// });


function addNonGroupLayers(sourceLayer, targetGroup) {
    if (sourceLayer instanceof L.LayerGroup) {
        sourceLayer.eachLayer(function (layer) {
            addNonGroupLayers(layer, targetGroup);
        });
    } else {
        targetGroup.addLayer(sourceLayer);
    }
};


// draw area of postal codes precise algorythm
$(function(){
    $("#poly").bind('click', function(){
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
                        var postal_data = data.postal_alpha_shape_points_dict_list;
                        var points_data = data.lat_lng_list;
                        if(Object.keys(postal_data).length) {
                            Object.keys(postal_data).forEach(key => {
                            var heat_points = points_data[key];
                            console.log(heat_points);
                            var heat_points_arr = [];
                            var innerArrayLength_heat_points = heat_points.length;
                            for (let j = 0; j < innerArrayLength_heat_points; j++) {
                                heat_points_arr.push([heat_points[j][1], heat_points[j][0]]); 
                                }
                            var heat = L.heatLayer(heat_points_arr,{
                                radius: 10,
                                blur: 10, 
                                maxZoom: 17,
                            }).addTo(map);
                            addNonGroupLayers(heat, drawnItems3);

                            var polygonus = postal_data[key];
                            var postal_no = key;
                            let arr = [];
                            var innerArrayLength = polygonus[0][0][0].length;
                            // loop the inner array
                            for (let j = 0; j < innerArrayLength; j++) {
                                arr.push([polygonus[0][0][0][j][0], polygonus[0][0][0][j][1]]); 
                                }
                            var options = {
                            style: function (feature) {
                                return {
                                    "color": "#3a83a4e0",
                                    "weight": 1,
                                    "opacity": 1,
                                    "fillColor": '#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6),
                                    "fillOpacity": 0.5
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
                            polygonus_geo_form.features[0].properties.popupContent.push(postal_no);
                            var layerpoly = new L.geoJson(polygonus_geo_form.features, options).addTo(map).bindPopup(postal_no);
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
    });
});



















});

