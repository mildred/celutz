if (ref_points == undefined) var ref_points = new Array();
if (image_loop == undefined) var image_loop = false;

var debug_mode = false;
var canvas;
var cntext;
var point_list = new Array();
var zoom = 0;
var zooms = new Array();
var prev_zm;
var zm;
var tile = {width:256, height:256};
var ntiles = {x:228, y:9};
var border_width = 2;
var imageObj = new Array();

// minimum and maximum azimuth
var alpha_domain = {start:0, end:360};

var fingr = 0;  // mémorisation de lécart entre doigts;
var last  = {x:0,y:0};
var shift = {x:0,y:0};
var mouse = {x:0,y:0};
var speed = {x:0,y:0};
var canvas_pos = {x:0,y:0};
var tmt;
var is_located = false;
var point_colors = {
	'pano_point' : '255,128,128', // red
	'ref_point'  : '128,128,255', // blue
	'loc_point'  : '128,255,128', // green
	'temporary'  : '255,255,128', // yellow
	'unlocated'  : '255,255,255'  // white
};
var map_never_drawn = true; //Pour empecher d'enlever des Layers inexistants
var map; // minimap object
var viewField; // cone drawn on the minimap
var viewDirection; // blue line drawn on the minimap

function getXMLHttpRequest() {
	var xhr = null;
	
	if (window.XMLHttpRequest || window.ActiveXObject) {
		if (window.ActiveXObject) {
			try {
				xhr = new ActiveXObject("Msxml2.XMLHTTP");
			} catch(e) {
				xhr = new ActiveXObject("Microsoft.XMLHTTP");
			}
		} else {
			xhr = new XMLHttpRequest(); 
		}
	} else {
		alert("Votre navigateur ne supporte pas l'objet XMLHTTPRequest...");
		return null;
	}
	
	return xhr;
}



function nmodulo(val, div) {                // pour obtenir un modulo dans l'espace des nombres naturels N.
    return Math.floor((val%div+div)%div);   // il y a peut être plus simple, mais en attendant ....
}

function fmodulo(val, div) {                // pour obtenir un modulo dans l'espace des nombres réels positifs.
    return (val%div+div)%div;               // il y a peut être plus simple, mais en attendant ....
}

function distort_canvas(p, x, y) {
    if (p == 0) distort = 0;
    else {
	cntext.save();
	distort++;
        cntext.clearRect(0, 0, canvas.width, 2*canvas.height);
	var ratio = (canvas.width-2*distort)/canvas.width;
	var shift = canvas.height/2*(1-ratio);
	cntext.scale(1, ratio);
	if (p == 1) cntext.translate(0, 0);
	else if (p == -1) cntext.translate(0, 0);
	draw_image(x, y);
	cntext.restore();
    }
}

function draw_image(ox, oy) {
    var ref_vals  = {x:last.x, y:last.y, zoom:zoom};
    ox = nmodulo(ox-canvas.width/2, zm.im.width);        // pour placer l'origine au centre du canvas
    oy = Math.floor(oy-canvas.height/2);                 // pas de rebouclage vertical

    cntext.clearRect(0, 0, canvas.width, canvas.height);
    cntext.fillStyle = "rgba(128,128,128,0.8)";

    if (canvas.height > zm.im.height) {
	var fy = Math.floor((oy+canvas.height/2-zm.im.height/2)/(tile.height*zm.ntiles.y))*zm.ntiles.y;
	if (fy < 0) fy = 0;
	var ly = fy + zm.ntiles.y;
    } else {
	var fy = Math.floor(oy/tile.height);
	var ly = Math.floor((oy+canvas.height+tile.height-1)/tile.height+1);
	if (fy < 0) fy = 0;
	if (ly > zm.ntiles.y) ly = zm.ntiles.y;
    }

    for (var j=fy; j<ly; j++) {
	var delta_y = (Math.floor(j/zm.ntiles.y) - Math.floor(fy/zm.ntiles.y)) * (tile.height - zm.last_tile.height);
	var dy = j*tile.height - oy - delta_y;
	var ny = j%ntiles.y;
	var wy = zm.tile.width;
	if (ny == zm.ntiles.y - 1) wy = zm.last_tile.height;

	var cpx = 0;
	var i = 0;
	var Nx = zm.ntiles.x;
	while (cpx < ox+canvas.width) {
	    var cur_width = zm.tile.width;
	    if (i%Nx == zm.ntiles.x-1) cur_width = zm.last_tile.width;
	    if (cpx >= ox-cur_width) {
		var nx = i%Nx;
		var idx = nx+'-'+ny+'-'+ref_vals.zoom;
		if (imageObj[idx] && imageObj[idx].complete) {
		    draw_tile(idx, cpx-ox, dy); // l'image est déja en mémoire, on force le dessin sans attendre.
		} else {
		    var fname = get_file_name(nx, ny, ref_vals.zoom);
		    imageObj[idx] = new Image();
		    imageObj[idx].src = fname;
		    var ts = zm.get_tile_size(nx, ny);
		    cntext.fillRect(cpx-ox, dy, ts.width, ts.height);
		    imageObj[idx].addEventListener('load', (function(ref, idx, dx, dy, ox, oy, ts) {
			return function() {        // closure nécéssaire pour gestion assynchronisme !!!
			    draw_tile_del(ref, idx, dx, dy, ox, oy, ts.width, ts.height);
			};
		    })(ref_vals, idx, cpx-ox, dy, ox, oy, ts), false);
		}
//		load_image(zoom, nx, ny, shx, shy, cpx-ox, dy, ox, oy);
	    }
	    cpx += cur_width;
	    i++;
	}
    }
    drawDecorations(ox, oy);
    var cap_ele = zm.get_cap_ele(last.x, zm.im.height/2-last.y);
    angle_control.value = cap_ele.cap.toFixed(2);
    elvtn_control.value = cap_ele.ele.toFixed(2);
    update_url();
}

function draw_tile_del(ref, idx, tx, ty, ox, oy, twidth, theight) {
    if (ref.zoom == zoom && ref.x == last.x && ref.y == last.y) {
	draw_tile(idx, tx, ty);
	drawDecorations(ox, oy, tx, ty, twidth, theight);
    }
}

function draw_tile(idx, ox, oy) {
    var img = imageObj[idx];
    cntext.drawImage(img, ox, oy);
}

/** Draws the colored circles and the central line
 */
function drawDecorations(ox, oy, tx, ty, twidth, theight) {
    if (twidth) {
	cntext.save();
	cntext.beginPath();
        cntext.rect(tx, ty, twidth, theight);
        cntext.clip();
    }
    var wgrd = zm.im.width/360;
    var od = ((ox+canvas.width/2)/wgrd)%360;
    var el = (zm.im.height/2 - (oy+canvas.height/2))/wgrd;

    // draw a vertical blue line with the central dot
    // the dot is centered on (ox, oy) = (canvas.width/2, canvas.width/2)
    var line_width = 3;
    cntext.fillStyle = "rgba(43, 130, 203, 0.7)";
    cntext.strokeStyle = "yellow";
    cntext.lineWidth = 2;
    cntext.fillRect(canvas.width/2-line_width/2, 0, line_width, canvas.height);
    cntext.strokeRect(canvas.width/2-line_width, canvas.height/2-line_width, line_width*2, line_width*2);
    for(var i = 0; i < zm.pt_list.length; i++) {
      if (zm.pt_list[i]['type'] != 'unlocated') {
	    cntext.fillStyle = 'rgba('+point_colors[zm.pt_list[i]['type']]+',0.5)';
	    var cx = nmodulo(zm.pt_list[i]['xc'] - ox, zm.im.width);
	    var cy = zm.pt_list[i]['yc'] - oy;
	    cntext.beginPath();
	    cntext.arc(cx, cy, 20, 0, 2*Math.PI, true);
	    cntext.fill();
        }
    }
    if (twidth) {
	cntext.restore();
    }
}

function insert_drawn_point(lat, lon, alt) {
    var rt = 6371;  // Rayon de la terre
    var pt_alt = document.getElementById('pos_alt').childNodes[0].nodeValue;
    var pt_lat = document.getElementById('pos_lat').childNodes[0].nodeValue;
    var pt_lon = document.getElementById('pos_lon').childNodes[0].nodeValue;

    var alt1 = pt_alt;
    var lat1 = pt_lat*Math.PI/180;
    var lon1 = pt_lon*Math.PI/180;
    var alt2 = alt;
    var lat2 = lat*Math.PI/180;
    var lon2 = lon*Math.PI/180;

    var dLat = lat2-lat1;
    var dLon = lon2-lon1;

    var a = Math.sin(dLat/2)*Math.sin(dLat/2) + Math.sin(dLon/2)*Math.sin(dLon/2)*Math.cos(lat1)*Math.cos(lat2);  //
    var angle = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d = angle*rt;                    // distance du point en Kms

    var y = Math.sin(dLon) * Math.cos(lat2);
    var x = Math.cos(lat1)*Math.sin(lat2) - Math.sin(lat1)*Math.cos(lat2)*Math.cos(dLon);
    var cap = Math.atan2(y,x);                 // cap pour atteindre le point en radians
    var e = Math.atan2((alt2 - alt1)/1000 - d*d/(2*rt),d);  // angle de l'élévation en radians

    return {d:d, cap:cap*180/Math.PI, ele:e*180/Math.PI};   // les résultats sont en degrés
}

function localate_point() {
    var lat = document.getElementById("loca_latitude").value;
    var lon = document.getElementById("loca_longitude").value;
    var alt = document.getElementById("loca_altitude").value;
    if (lat == '' || isNaN(lat) || lat <= -90 || lat > 90) {
	alert("La latitude "+lat+"n'est pas correcte");
	return;
    }
    if (lat == '' || isNaN(lon) || lon <= -180 || lon > 180) {
	alert("La longitude "+lon+"n'est pas correcte");
	return;
    }
    if (lat == '' || isNaN(alt) || alt < -400 || alt > 10000000) {
	alert("l'altitude "+alt+"n'est pas correcte");
	return;
    }
    var opt_ced = new Array();
    opt_dce = insert_drawn_point(lat, lon, alt);
    display_temp(opt_dce.d, opt_dce.cap, opt_dce.ele);
}

function display_temp(d,cap,ele) {
    point_list[point_list.length] = new Array("point temporaire", d,cap,ele, "temporary");
    reset_zooms();
    putImage(last.x, last.y);
}

function arrayUnset(array, value){
    array.splice(array.indexOf(value), 1);
}

function erase_point() {
	for (var i=0; i<point_list.length; i++) {
		if(point_list[i][0] == "point temporaire"){
			arrayUnset(point_list,point_list[i]);
			loop = erase_point();
		}
	}
	reset_zooms();
    putImage(last.x, last.y);
}

/** Returns a 3-width zero-padded version of an int
 * ex: 3 -> "003"
 */
function zero_pad(number) {
	var temp = number.toString(10);
	while (temp.length < 3) {
		temp = '0' + temp;
	}
	return temp;
}

function get_file_name(x, y, z) { // recherche du fichier correspondant au zoom et à la position
    return img_prefix+'/'+zero_pad(z)+'-'+zero_pad(x)+'-'+zero_pad(y)+'.jpg';
}

function get_base_name() {
	/** 
	 * @returns the base name, which is the name (not path) of the folder where
	 * the tiles are.
	 */
	return img_prefix.split('/').reverse()[0];
}


function keys(key) {
    hide_links();
    evt = key || event;
    //evt.preventDefault();
    //evt.stopPropagation();
    if (!key) {
	key = window.event;
	key.which = key.keyCode;
    }
    //alert(key);
    //if (!evt.shiftKey) return;
    
    switch (key.which) {
    case 36: // home
    case 35: // end
        angle_control = document.getElementById('angle_ctrl');
        angle_control.value = parseFloat(angle_control.value) + 180;
        change_angle();
    case 39: // left
	    putImage(last.x+40, last.y);
	    break;
    case 40: // up
	    putImage(last.x, last.y+20);
	    break;
    case 37: // right
	    putImage(last.x-40, last.y);
	    break;
    case 38: // down
	    putImage(last.x, last.y-20);
	    break;
    case 33: // pageup
	    zoom_control.value--;
	    change_zoom()
	    break;
    case 34: // pagedown
        zoom_control.value++;
        change_zoom()
        break;
    default:
    //	alert(key.which)
        break;
    }
    // Always update map when a key is pressed
    update_map();

}

function onImageClick(e) {
    hide_contextmenu();
    var index = {};
    if (e.touches && e.touches.length == 2) {
	e.preventDefault();
	fingr = Math.sqrt((e.touches[0].clientX - e.touches[1].clientX)^2 +
			  (e.touches[0].clientY - e.touches[1].clientY)^2);
    } else {
	if (e.touches) {
	    e.preventDefault();
	    index.x = e.changedTouches[0].clientX;
	    index.y = e.changedTouches[0].clientY;
	} else {
	    index.x = e.pageX;
	    index.y = e.pageY;
	}

	shift.x = last.x;
	shift.y = last.y;
	speed.x = 0;
	speed.y = 0;
	mouse.x = index.x;
	mouse.y = index.y;
    }
    clearTimeout(tmt);  //arrêt de l'éffet eventuel d'amorti en cours.
    canvas.addEventListener('mousemove', stickImage, false);
    canvas.addEventListener('touchmove', stickImage, false);
    canvas.addEventListener('mouseup', launchImage, false);
    canvas.addEventListener('touchend', launchImage, false);
    //canvas.addEventListener('mouseout', launchImage, false);
    canvas.style.cursor='move';
    //document.onmousemove = stickImage;
    //document.onmouseup = launchImage;
    hide_links();
}


function stickImage(e) {
    var index = {};
    if (e.changedTouches && e.changedTouches.length == 2) {
	e.preventDefault();
	// cas du zoom à 2 doigts
	var nfingr = Math.sqrt((e.changedTouches[0].clientX - e.changedTouches[1].clientX)^2 +
			       (e.changedTouches[0].clientY - e.changedTouches[1].clientY)^2);
	var evt = {}
	evt.pageX = (e.changedTouches[0].clientX + e.changedTouches[1].clientX)/2;
	evt.pageY = (e.changedTouches[0].clientY + e.changedTouches[1].clientY)/2;
	if (fingr > nfingr*2 || fingr < nfingr/2) {
	    evt.wheelDelta = fingr - nfingr;
	    fingr = nfingr;
	    return wheel_zoom(evt);
	} else {
	    return;
	}
    }
    if (e.touches) {
	e.preventDefault();
	index.x = e.changedTouches[0].clientX;
	index.y = e.changedTouches[0].clientY;
    } else {
	index.x = e.pageX;
	index.y = e.pageY;
    }

    var xs = mouse.x - index.x + shift.x;
    var ys = mouse.y - index.y + shift.y;
    speed.x = xs - last.x;  //mémorisation des vitesses horizontales
    speed.y = ys - last.y;  //et verticales lors de ce déplacement
    putImage(xs, ys);
}

function launchImage(e) {
    var index = {};
    if (e.touches) {
	e.preventDefault();
	index.x = e.changedTouches[0].clientX;
	index.y = e.changedTouches[0].clientY;
    } else {
	index.x = e.pageX;
	index.y = e.pageY;
    }
    distort_canvas(0);
    canvas.removeEventListener('mousemove', stickImage, false);
    canvas.removeEventListener('touchmove', stickImage, false);
    //document.onmousemove = null;
    shift.x = index.x - mouse.x + shift.x;
    shift.y = index.y - mouse.y + shift.y;
    tmt = setTimeout(inertialImage, 100);
}

function putImage(x, y) { // est destiné à permettre l'effet d'amortissement par la mémorisation de la position courante.
    if (!zm.is_updated) return;
    if (x >= zm.im.width) {   // rebouclage horizontal
	shift.x -= zm.im.width;
	x -= zm.im.width;
    } else if (x < 0) {
	shift.x += zm.im.width;
	x += zm.im.width;
    }
    if (y >= zm.im.height) {   // pas de rebouclage vertical mais blocage
	//distort_canvas(1, x, y);
	shift.y = zm.im.height-1;
	y = zm.im.height-1;
    } else if (y < 0) {
	//distort_canvas(-1, x, y);
	shift.y = 0;
	y = 0;
    }

    last.x = x;
    last.y = y;
    draw_image(x, y);
}

function inertialImage() {
    speed.x *= 0.9;
    speed.y *= 0.9;
    if (Math.abs(speed.x) > 2 || Math.abs(speed.y) > 2) {
	putImage(last.x+speed.x, last.y+speed.y);
	tmt = setTimeout(inertialImage, 100);
    } else {
	show_links();
    }
    update_map();
}

function tri_ref_points(v1, v2) {
    return v1['x'] - v2['x'];
}



function tzoom(zv) {
    this.value = zv;
    this.ntiles = {x:0,y:0};
    this.tile = {width:0,height:0};
    this.last_tile = {width:0,height:0};
    this.max_tile = {width:0,height:0};
    this.im = {width:0,height:0};
    this.is_updated = false;

    this.refresh = function() {
	    this.im.visible_width = this.tile.width*(this.ntiles.x-1)+this.last_tile.width;
	    this.is_updated = true;

	    this.im.width = this.im.visible_width;
	    this.im.height = this.tile.height*(this.ntiles.y-1)+this.last_tile.height;
	    if (this.last_tile.width > this.tile.width) {
		    this.max_tile.width = this.im.last_tile.width;
	    } else {
		    this.max_tile.width = this.tile.width;
	    }
	    if (this.last_tile.height > this.tile.height) {
		    this.max_tile.height = this.im.last_tile.height;
	    } else {
		    this.max_tile.height = this.tile.height;
	    }

	    var ord_pts = new Array();
	    for(var label in ref_points) {
		    ord_pts.push(ref_points[label]);
	    }
	    ord_pts = ord_pts.sort(tri_ref_points);
	    is_located = (ord_pts.length > 1) 
	                  || image_loop && (ord_pts.length > 0);


	    alpha_domain = {start:0, end:360};
	    this.pixel_y_ratio = this.im.width/360;
	    if (is_located) {
		    this.ref_pixels = new Array;
		    this.ref_pixels[0] = new Array();    // Attention il faut compter un intervalle de plus !
		    for (var i=0; i < ord_pts.length; i++) { // premier parcours pour les paramètres cap/x
			    this.ref_pixels[i+1] = new Array();
			    this.ref_pixels[i+1].x = Math.floor(ord_pts[i].x*this.im.width);
			    this.ref_pixels[i+1].cap = fmodulo(ord_pts[i].cap, 360);
			    if (i != ord_pts.length-1) {
				    this.ref_pixels[i+1].ratio_x = (ord_pts[i+1].x - ord_pts[i].x) /
					    fmodulo(ord_pts[i+1].cap - ord_pts[i].cap, 360)*this.im.width;
			    }
		    }
		    if (image_loop == true) {
			    var dpix = this.im.width;
			    var dangle = 360;
			    if (ord_pts.length > 1) {
				    dpix = this.im.width - this.ref_pixels[this.ref_pixels.length-1].x + this.ref_pixels[1].x;
				    dangle = fmodulo(this.ref_pixels[1].cap - this.ref_pixels[this.ref_pixels.length-1].cap, 360);
			    }
			    this.ref_pixels[0].ratio_x = dpix/dangle;
			    this.ref_pixels[ord_pts.length].ratio_x = this.ref_pixels[0].ratio_x;
			    dpix = this.im.width - this.ref_pixels[ord_pts.length].x;
			    this.ref_pixels[0].cap = fmodulo(this.ref_pixels[ord_pts.length].cap + dpix / this.ref_pixels[0].ratio_x, 360);
		    } else {
			    this.ref_pixels[0].ratio_x = this.ref_pixels[1].ratio_x;
			    this.ref_pixels[ord_pts.length].ratio_x = this.ref_pixels[ord_pts.length-1].ratio_x;
			    this.ref_pixels[0].cap = fmodulo(this.ref_pixels[1].cap - this.ref_pixels[1].x / this.ref_pixels[1].ratio_x, 360);
			    alpha_domain.start = this.ref_pixels[0].cap;
			    alpha_domain.end = fmodulo(this.ref_pixels[ord_pts.length].cap+(this.im.width-this.ref_pixels[ord_pts.length].x)/this.ref_pixels[ord_pts.length].ratio_x, 360);
			    this.pixel_y_ratio = this.im.width/fmodulo(alpha_domain.end-alpha_domain.start, 360);
		    }
		    this.ref_pixels[0].x = 0;

		    for (var i=0; i < ord_pts.length; i++) { // second parcours pour les paramètres elevation/y
			    this.ref_pixels[i+1].shift_y = Math.floor(this.pixel_y_ratio*ord_pts[i].ele - ord_pts[i].y*this.im.height);
			    if (i != ord_pts.length-1) {
				    var next_shift = Math.floor(this.pixel_y_ratio*ord_pts[i+1].ele - ord_pts[i+1].y*this.im.height);
				    this.ref_pixels[i+1].dshft_y = (next_shift - this.ref_pixels[i+1].shift_y)/(this.ref_pixels[i+2].x - this.ref_pixels[i+1].x);
			    }
		    }

		    if (image_loop == true) {
			    var dpix  = this.im.width;
			    var delt = 0;
			    if (ord_pts.length > 1) {
				    dpix  = this.im.width - this.ref_pixels[this.ref_pixels.length-1].x + this.ref_pixels[1].x;
				    delt = this.ref_pixels[this.ref_pixels.length-1].shift_y - this.ref_pixels[1].shift_y;
			    }
			    this.ref_pixels[0].dshft_y = -delt/dpix;
			    this.ref_pixels[ord_pts.length].dshft_y = this.ref_pixels[0].dshft_y;
			    dpix = this.im.width - this.ref_pixels[ord_pts.length].x;
			    this.ref_pixels[0].shift_y = this.ref_pixels[ord_pts.length].shift_y + dpix*this.ref_pixels[0].dshft_y;
		    } else {
			    this.ref_pixels[0].shift_y = this.ref_pixels[1].shift_y;
			    this.ref_pixels[0].dshft_y = 0;
			    this.ref_pixels[ord_pts.length].dshft_y = 0;
		    }
	    }

	    this.pt_list = new Array();
	    for (var i=0; i<point_list.length; i++) {
		    var lbl = point_list[i][0];
		    var dst = point_list[i][1];
		    var cap = point_list[i][2];
		    var ele = point_list[i][3];
		    var lnk = point_list[i][4];
		    var url = point_list[i][5];
		    var typ = 'unlocated';
		    var rxy = this.get_pos_xy(cap, ele);
		    var is_visible = (
			    fmodulo(cap - alpha_domain.start, 360) 
				    <= 
				    fmodulo(alpha_domain.end - 
				            alpha_domain.start -0.0001, 360)+0.0001 
				    && is_located);

		    this.pt_list[i] = new Array();
		    if (ref_points[lbl] != undefined && lnk == '') {
			    typ = 'ref_point';
			    if (!is_located) { 
				    rxy = {
					    x:ref_points[lbl].x*this.im.width, 
					    y:ref_points[lbl].y*this.im.height
				    };
			    }
		    } else if(lnk == '' && is_visible && lbl != 'point temporaire') {
			    typ = 'loc_point';
		    }else if(is_visible && lbl =='point temporaire') {
			    typ = 'temporary';

		    } else if(is_visible) {
			    typ = 'pano_point';
		    }
		    this.pt_list[i]['type'] = typ;
		    this.pt_list[i]['cap'] = cap;
		    this.pt_list[i]['ele'] = ele;
		    this.pt_list[i]['dist'] = dst;
		    this.pt_list[i]['label'] = lbl;
		    this.pt_list[i]['lnk'] = lnk;
		    this.pt_list[i]['url'] = url;
		    this.pt_list[i]['xc'] = rxy.x;
		    this.pt_list[i]['yc'] = Math.floor(this.im.height/2 - rxy.y);
	    }
    },

    this.get_tile_size = function(nx, ny) {
	var res = {width:0, height:0};
	if (nx == this.ntiles.x-1) res.width = this.last_tile.width;
	else res.width = this.tile.width;
	if (ny == this.ntiles.y-1) res.height = this.last_tile.height;
	else res.height = this.tile.height;
	return res;
    }

    this.get_cap_ele = function(px, py) {               // recherche d'un cap et d'une élévation à partir d'un pixel X,Y.
	if (is_located) {
	    for (var i=0; i < this.ref_pixels.length; i++) {
		if (i == this.ref_pixels.length - 1 || px < this.ref_pixels[i+1].x) {
		    var dpix = px-this.ref_pixels[i].x;
		    var cp = fmodulo(this.ref_pixels[i].cap + dpix/this.ref_pixels[i].ratio_x, 360);
		    var el = (py+this.ref_pixels[i].shift_y+this.ref_pixels[i].dshft_y*dpix)/this.pixel_y_ratio;
		    return {cap:cp, ele:el};
		}
	    }
	} else {
	    var cp = 360*px/this.im.width;
	    var el = 360*py/this.im.height;
	    return {cap:cp, ele:el};
	}
    }

    this.get_pos_xy = function(cap, ele) {                  // recherche des coordonnées pixel à partir d'un cap et d'une élévation.
	if (is_located) {
	    var dcap = fmodulo(cap-this.ref_pixels[0].cap, 360);
	    for (var i=0; i < this.ref_pixels.length; i++) {
		if (i == this.ref_pixels.length - 1 || dcap < fmodulo(this.ref_pixels[i+1].cap-this.ref_pixels[0].cap, 360)) {
		    var px = this.ref_pixels[i].x + this.ref_pixels[i].ratio_x*fmodulo(cap - this.ref_pixels[i].cap, 360);
		    var dpix = px-this.ref_pixels[i].x;
		    var py = this.pixel_y_ratio*ele - this.ref_pixels[i].shift_y - this.ref_pixels[i].dshft_y*dpix;
                    if (image_loop || (dcap < fmodulo(alpha_domain.end - alpha_domain.start, 360)))
                        // Position is inside the view
		        return {x: px, y: py};
                    else {
                        // Position is outside the view, find out which edge is closest
                        if (fmodulo(alpha_domain.start - cap, 360) < fmodulo(cap - alpha_domain.end, 360))
                            // Left edge
                            return {x: 0, y: py};
                        else
                            // Right edge
                            return {x: image_width - 1, y: py};
                    }
		}
	    }
	} else {
	    var px = fmodulo(cap, 360)/360*this.im.width;
	    var py = ele/360*this.im.height;
	    return {x:px, y:py};
	}
    }
}

function reset_zooms () {
    for(i=0; i<zooms.length; i++) zooms[i].is_updated = false;
    zm.refresh();
}

function wheel_zoom (event) {
    var zshift = {x:0, y:0};
    if (event.pageX != undefined && event.pageX != undefined) {
	zshift.x = event.pageX-canvas.width/2-canvas_pos.x;
	zshift.y = event.pageY-canvas.height/2-canvas_pos.y;
    }
    //event.preventDefault();

    var delta = (event.wheelDelta || -event.detail);
    if (delta < 0 && zoom_control.value < zoom_control.max) {
	zoom_control.value++;
	change_zoom(zshift.x, zshift.y);
    } else if (delta > 0 && zoom_control.value > zoom_control.min) {
	zoom_control.value--;
	change_zoom(zshift.x, zshift.y);
    }
}

function change_zoom(shx, shy) {
    var zoom_control = document.getElementById("zoom_ctrl");
    var v = zoom_control.value;

    prev_zm = zm;

    if (zooms[v]) {
	if (!zooms[v].is_updated) zooms[v].refresh();
    } else {
	zooms[v] = new tzoom(v);
    }

    if (zooms[v].is_updated) {
	if (shx == undefined || shy == undefined) {
	    shx=0;
	    shy=0;
	}
	zm = zooms[v];
	var px = (last.x+shx)*zm.im.width/prev_zm.im.width - shx;
	var py = (last.y+shy)*zm.im.height/prev_zm.im.height - shy;
	if (py < zm.im.height && py >= 0) {
	    zoom = zm.value;
	    tile = zm.tile;
	    ntiles = zm.ntiles;
            update_url();
	    putImage(px, py);
	} else {
	    zm = prev_zm;
	    zoom_control.value = zm.value;
	}
    }
    update_map();
}

function change_angle() {
    var elvtn_control = document.getElementById('elvtn_ctrl');
    var angle_control = document.getElementById('angle_ctrl');
    var resxy = zm.get_pos_xy(angle_control.value, elvtn_control.value);
    var pos_x = resxy.x;
    var pos_y = Math.floor(zm.im.height/2 - resxy.y);
    putImage(pos_x, pos_y);
}

function check_prox(x, y, r) {   //verification si un point de coordonnées x, y est bien dans un cercle de rayon r centré en X,Y.
    return Math.sqrt(x*x + y*y) < r;
}

function check_links(e) {
    var mouse_x = e.pageX-canvas_pos.x;
    var mouse_y = e.pageY-canvas_pos.y;
    var pos_x = nmodulo(last.x + mouse_x - canvas.width/2, zm.im.width);
    var pos_y = last.y + mouse_y - canvas.height/2;
    for(var i = 0; i < zm.pt_list.length; i++) {
	if (is_located && zm.pt_list[i]['type'] == 'pano_point') {
	    if (check_prox(zm.pt_list[i]['xc']-pos_x, zm.pt_list[i]['yc']-pos_y, 20)) {
		if (zm.pt_list[i]['lnk'] != '') window.location = zm.pt_list[i]['lnk'];
		break;
	    }
	}
    }
}

function display_links(e) {
    var index = {};
    if (e.touches) {
	e.preventDefault();
	index.x = e.changedTouches[0].clientX;
	index.y = e.changedTouches[0].clientY;
    } else {
	index.x = e.pageX;
	index.y = e.pageY;
    }
    var info = document.getElementById('info');
    var mouse_x = index.x-canvas_pos.x;
    var mouse_y = index.y-canvas_pos.y;
    var pos_x = nmodulo(last.x + mouse_x - canvas.width/2, zm.im.width);
    var pos_y = last.y + mouse_y - canvas.height/2;
    //var cap = ((pos_x/zm.im.width)*360).toFixed(2);
    var res = zm.get_cap_ele(pos_x, zm.im.height/2 - pos_y);
    //var ele = ((zm.im.height/2 - pos_y)/zm.im.width)*360;
    info.innerHTML = 'élévation : '+res.ele.toFixed(2)+'&#176;<br/>cap : '+res.cap.toFixed(2)+'&#176;';
    info.style.top = index.y+'px';
    info.style.left = index.x+'px';
    info.style.backgroundColor = '#222';
    info.style.opacity = '0.6'
    info.style.color = 'white'
    info.style.display = 'block';
    canvas.style.cursor='crosshair';
    for(var i = 0; i < zm.pt_list.length; i++) {
	if (is_located || zm.pt_list[i]['type'] == 'ref_point') {
	    if (check_prox(zm.pt_list[i]['xc']-pos_x, zm.pt_list[i]['yc']-pos_y, 20)) {
		info.innerHTML = zm.pt_list[i]['label'];
                info.style.opacity = '0.8'
                info.style.color = 'black'
		if (zm.pt_list[i]['dist'] < 10) var dst = Math.round(zm.pt_list[i]['dist']*1000)+' m';
		else var dst = zm.pt_list[i]['dist'].toFixed(1)+' kms';
		info.innerHTML += '<br/>(' + dst + ')';
		info.style.backgroundColor = 'rgb('+point_colors[zm.pt_list[i]['type']]+')';
		canvas.style.cursor='auto';
		break;
	    }
	}
    }
}

function hide_links() {
    canvas.removeEventListener( "mousemove", display_links, false);
    canvas.removeEventListener( "touchmove", display_links, false);
    var info = document.getElementById('info');
    info.style.display = 'none';
}

function show_links() {
    canvas.addEventListener( "mousemove", display_links, false);
    canvas.addEventListener( "touchmove", display_links, false);
//    var info = document.getElementById('info');
//    info.style.display = 'block';
}

function hide_contextmenu() {
    document.getElementById('insert').style.display = 'none';
}

function manage_ref_points(e) {
    //event.preventDefault();
    //event.stopPropagation();
	var sel_pt = document.getElementById('sel_point');
    var do_insert = document.getElementById('do-insert');
	var do_delete = document.getElementById('do-delete');
	var do_cancel = document.getElementById('do-cancel');
	//var show_cap = document.getElementById('show-cap');
	var insrt = document.getElementById('insert');

    var pos_x = nmodulo(last.x + e.pageX - canvas_pos.x - canvas.width/2, zm.im.width);
	var pos_y = last.y + e.pageY - canvas_pos.y - canvas.height/2;

	insrt.style.left = e.pageX+'px';
	insrt.style.top = e.pageY+'px';
	insrt.style.display = 'block';

	if (do_insert) {// true if there are ref points
		    for(var i = 0; i < zm.pt_list.length; i++) {
			    if (zm.pt_list[i]['type'] == 'ref_point') {
				    if (check_prox(zm.pt_list[i]['xc']-pos_x,
				                   zm.pt_list[i]['yc']-pos_y, 20)) {
					    sel_pt.value = zm.pt_list[i]['label'];
				    }
			    }
		    }
		do_delete.onclick = function() {delete_ref_point(insrt)};
		do_insert.onclick = function() {insert_ref_point(insrt, e.pageX-canvas_pos.x, e.pageY-canvas_pos.y)};
		// TODO: adapt to the new backend
		//show_cap.onclick = function() {
		//	window.open('show_capline.php?title='+encodeURIComponent(btoa(title))+'&cap='+res.cap+'&org_lat='+pt_lat+'&org_lon='+pt_lon+'&dist=120000');
		//};
	}

	do_cancel.onclick = hide_contextmenu;
    var res = zm.get_cap_ele(pos_x, zm.im.height/2 - pos_y);
    var pt_lat = document.getElementById('pos_lat').childNodes[0].nodeValue;
    var pt_lon = document.getElementById('pos_lon').childNodes[0].nodeValue;
    return false;
}

function insert_ref_point(el, x, y) {
    var label, posx, posy;
    el.style.display = 'none';
    var selected_label = document.getElementById('sel_point').value;
    var found = false;
    var refpoint_url;
    for(var i = 0; i < zm.pt_list.length; i++) {
	label = zm.pt_list[i]['label'];
	if(label == selected_label) {
	    refpoint_url = zm.pt_list[i]['url'];
	    posx = nmodulo(last.x + x - canvas.width/2, zm.im.width)/zm.im.width;
	    posy = 0.5 - (last.y + y - canvas.height/2)/zm.im.height;
	    var pval = {x:posx, y:posy, cap:zm.pt_list[i]['cap'], ele:zm.pt_list[i]['ele'], label:label};
	    ref_points[label] = pval;
	    reset_zooms();
	    putImage(last.x, last.y);
	    found = true;
	    break;
	}
    }
	if (!found) {
		alert('unknown ref_point: '+label);
	}
	
	// Then push the modif
	var xhr = getXMLHttpRequest();
	xhr.open("POST", "/api/v1/references/", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
	xhr.send("reference_point=" + refpoint_url
	         + "&panorama=" + panorama_url
	         + "&x=" + Math.floor(posx * image_width)
                 + "&y=" + Math.floor((posy + 0.5) * image_height));

    // update the course of the panorama boundaries
    // (update cap_min/cap_max of the panorama object)
	var xhr = getXMLHttpRequest();
	xhr.open("POST", "/api/v1/panoramas/", true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
}

function delete_ref_point(el) {
    var ref_name = document.getElementById('sel_point').value;
    el.style.display = 'none';
    var url = ref_points[ref_name].url;
    delete ref_points[ref_name];
    reset_zooms();
    putImage(last.x, last.y);

    // Then push the modif
    var xhr = getXMLHttpRequest();
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.send();
}

function clean_canvas_events(e) {
    canvas.removeEventListener('mousemove', stickImage, false);
    canvas.removeEventListener('touchmove', stickImage, false);
    document.getElementById('info').style.display = 'none';
    speed.x = 0;
    speed.y = 0;
}

canvas_set_size = function() {
    canvas.style.border = border_width+"px solid black";
    canvas.width = window.innerWidth-2*border_width;
    canvas.height = window.innerHeight-2*border_width;
    canvas_pos.x = canvas.offsetLeft+border_width;
    canvas_pos.y = canvas.offsetTop+border_width;
}

canvas_resize = function() {
    canvas_set_size();
    putImage(last.x, last.y);
    update_map();
}

function paramIn(e) {
    e = e || window.event;
    var relatedTarget = e.relatedTarget || e.fromElement;

    while (relatedTarget != adding && relatedTarget.nodeName != 'BODY' && relatedTarget != document && relatedTarget != localisation) {
	relatedTarget = relatedTarget.parentNode;
    }

    if (relatedTarget != adding && relatedTarget != localisation) {
	document.removeEventListener('keydown', keys, false);
    }
}

function paramOut(e) {

    e = e || window.event;
    var relatedTarget = e.relatedTarget || e.toElement;

    while (relatedTarget != adding && relatedTarget.nodeName != 'BODY' && relatedTarget != document && relatedTarget != localisation) {
        relatedTarget = relatedTarget.parentNode;
    }

    if (relatedTarget != adding && relatedTarget != localisation) {
    	document.addEventListener('keydown', keys, false);
    }

}

/* Parse initial orientation from URL, either:
   #zoom=A/x=B/y=C
   #zoom=A/cap=B/elev=C
   In the first case, (x, y) is an image coordinate in pixels, where (0, 0)
   is the lower left corner.
   In the second case, point to the given cap and elevation, assuming the
   current panorama is already calibrated.
*/
function get_orientation_from_url() {
    // Parse window.location.hash to get either x/y or cap/ele
    var regexp1 = /^#zoom=(\d)\/cap=(-?\d+|-?\d+\.\d+)\/ele=(-?\d+|-?\d+\.\d+)$/;
    var regexp2 = /^#zoom=(\d)\/x=(\d+)\/y=(\d+)$/;
    var res = window.location.hash.match(regexp1);
    if (res) {
        return { zoom: parseInt(res[1], 10),
                 cap: parseFloat(res[2]),
                 elevation: parseFloat(res[3]) };
    }
    else {
        res = window.location.hash.match(regexp2);
        if (res) {
        return { zoom: parseInt(res[1], 10),
                 x: parseInt(res[2], 10),
                 y: parseInt(res[3], 10) };
        }
        else {
            /* By default, center the view */
            return { zoom: 2, x: image_width / 2, y: image_height / 2 };
        }
    }
}

/* Update the URL to reflect the current zoom/orientation, so that it acts
 * as a permalink. */
function update_url() {
    var x = last.x << zm.value;
    var y = image_height - (last.y << zm.value);
    // Important: don't set window.location.hash directly, because it
    // records a new entry in the browser history...
    window.location.replace("#zoom=" + zm.value + "/x=" + x + "/y=" + y);
}

function load_pano() {
    localisation = document.getElementById("locadraw");
    adding = document.getElementById("adding");
    canvas = document.getElementById("mon-canvas");
    cntext = canvas.getContext("2d");
    canvas_set_size();
    canvas.addEventListener("click", check_links, false);
    //canvas.addEventListener("oncontextmenu", manage_ref_points, false);
    canvas.oncontextmenu = manage_ref_points;
    canvas.addEventListener("mouseout" , clean_canvas_events, false);
    show_links();

    var initial_orientation = get_orientation_from_url();
    var to_zoom = initial_orientation.zoom;

    var max_zoom = zooms.length - 1;
    zoom_control = document.getElementById("zoom_ctrl");
    zoom_control.onchange = change_zoom;
    zoom_control.max = max_zoom;
    if (to_zoom > max_zoom) to_zoom = Math.floor(max_zoom/2);
    zm = zooms[to_zoom];
    zoom_control.value = to_zoom;
    zm.refresh();

    zoom = zm.value;
    tile = zm.tile;
    ntiles = zm.ntiles;

    if (!("cap" in initial_orientation)) {
        /* Compute cap and elevation from (x, y) coordinates */
        var res = zm.get_cap_ele(initial_orientation.x >> zoom,
                                 (initial_orientation.y - image_height / 2) >> zoom);
        initial_orientation.cap = res.cap;
        initial_orientation.elevation = res.ele;
    }

    angle_control = document.getElementById("angle_ctrl");
    angle_control.value = initial_orientation.cap;
    angle_control.addEventListener('change', change_angle, false);
    angle_control.addEventListener('change', update_map, false);
    angle_control.addEventListener('onclick', change_angle, false);
    elvtn_control = document.getElementById("elvtn_ctrl");
    elvtn_control.value = initial_orientation.elevation;
    elvtn_control.onchange = change_angle;
    elvtn_control.onclick = change_angle;

    change_angle();
    loca_temp = document.getElementById("loca_show");
    if (loca_temp) {
	loca_temp.onclick = showLoca;
	loca_temp = document.getElementById("loca_hide");
	loca_temp.onclick = hideLoca;
	loca_temp = document.getElementById("loca_button");
	loca_temp.onclick = localate_point;
	loca_erase = document.getElementById("loca_erase");
	loca_erase.onclick = erase_point;
	localisation.addEventListener('mouseover',paramIn,false);
	localisation.addEventListener('mouseout',paramOut,false);
    }
    canvas.addEventListener('mousedown', onImageClick, false);
    canvas.addEventListener('touchstart', onImageClick, false);
    document.addEventListener('keydown', keys, false);
    canvas.addEventListener('mousewheel', wheel_zoom, false);
    canvas.addEventListener('DOMMouseScroll', wheel_zoom, false);
    //map events
    canvas.addEventListener('mousewheel', update_map, false);
    canvas.addEventListener('DOMMouseScroll', update_map, false);
    canvas.addEventListener('mousedown', update_map, false);
    canvas.addEventListener('mouseup', update_map, false);
    //
    window.onresize = canvas_resize;
    if (adding) {
	document.getElementById("paramFormHide").onclick = hideForm;
	document.getElementById("paramFormShow").onclick = showForm;
	adding.addEventListener('mouseover', paramIn, false);
	adding.addEventListener('mouseout', paramOut, false);
    }
};
function toRad(n) {
    return n * Math.PI / 180;
}
function toDeg(n) {
    return n * 180 / Math.PI;
}
function destVincenty(lat1, lon1, brng, dist) {
	/* JavaScript function to calculate the destination point given start point
    * latitude / longitude (numeric degrees), bearing (numeric degrees) and
    * distance (in m).
    * Original scripts by Chris Veness
    * Taken from http://movable-type.co.uk/scripts/latlong-vincenty-direct.html
    * and optimized / cleaned up by Mathias Bynens <http://mathiasbynens.be/>
    *
    * Based on the Vincenty direct formula by T. Vincenty, “Direct and Inverse
    * Solutions of Geodesics on the Ellipsoid with application of nested
    * equations”, Survey Review, vol XXII no 176, 1975
    * <http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf>
    */
	var a = 6378137,
		b = 6356752.3142,
		f = 1 / 298.257223563, // WGS-84 ellipsiod
		s = dist,
		alpha1 = toRad(brng),
		sinAlpha1 = Math.sin(alpha1),
		cosAlpha1 = Math.cos(alpha1),
		tanU1 = (1 - f) * Math.tan(toRad(lat1)),
		cosU1 = 1 / Math.sqrt((1 + tanU1 * tanU1)), sinU1 = tanU1 * cosU1,
		sigma1 = Math.atan2(tanU1, cosAlpha1),
		sinAlpha = cosU1 * sinAlpha1,
		cosSqAlpha = 1 - sinAlpha * sinAlpha,
		uSq = cosSqAlpha * (a * a - b * b) / (b * b),
		A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq))),
		B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq))),
		sigma = s / (b * A),
		sigmaP = 2 * Math.PI;
    while (Math.abs(sigma - sigmaP) > 1e-12) {
	    var cos2SigmaM = Math.cos(2 * sigma1 + sigma),
		    sinSigma = Math.sin(sigma),
		    cosSigma = Math.cos(sigma),
		    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM) - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma * sinSigma) * (-3 + 4 * cos2SigmaM * cos2SigmaM)));
	        sigmaP = sigma;
	        sigma = s / (b * A) + deltaSigma;
	};
	var tmp = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1,
	    lat2 = Math.atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1, (1 - f) * Math.sqrt(sinAlpha * sinAlpha + tmp * tmp)),
	    lambda = Math.atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1),
	    C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha)),
	    Lo = lambda - (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM))),
	    revAz = Math.atan2(sinAlpha, -tmp); // final bearing	

	return {lat: toDeg(lat2), lng: lon1 + toDeg(Lo)};
};
/*
function getCone(lat, lng, bearing, angle, distance){
	// Returns a polygon to be drawn to the map to show the current visual field
	//
	var conepoints = [];
	// by default, points are drawn every 5°, but if the angle to draw is
	// smaller than 5°, we draw no intermediary points
	var delta = 5;
	if (angle < 5){delta=angle};

	conepoints.push ([lat,lng]);

	for (i=0; i<=angle; i+=delta){
	    conepoints.push([destVincenty(lat, lng, bearing-(angle/2.0)+i, distance).lat,
		destVincenty(lat, lng, bearing-(angle/2.0)+i, distance).lng]);
	}

	var p = L.polygon(conepoints, {
	    color: 'grey',
	    fillColor: 'grey',
	    fillOpacity: 0.5
	});
	return p;
};
*/
function getCone(lat, lng, bearing, cap, distance){
	/* Returns a polygon to be drawn to the map to show the current visual field
	*/
	var conepoints = [];
	// by default, points are drawn every 5°, plus the end-point.
	var delta = 5;

    var total_angle = cap.cap_max - cap.cap_min;
    if (cap.cap_max<cap.cap_min){total_angle+=360}

	conepoints.push ([lat,lng]);
    for (i=0; i<=total_angle; i+=delta){
        angle = cap.cap_min+i;
        if (angle > 360){angle-=360}
        conepoints.push([destVincenty(lat, lng, angle, distance).lat,
            destVincenty(lat, lng, angle, distance).lng])
    }
    // add extrem point
    conepoints.push([destVincenty(lat, lng, cap.cap_max, distance).lat,
        destVincenty(lat, lng, cap.cap_max, distance).lng])

	var p = L.polygon(conepoints, {
	    color: 'black',
            weight: '1',
	    fillColor: 'grey',
	    fillOpacity: 0.5
	    });
	return p;
};

function getCapMinMaxVisible(){
    /* Return the minimun and maximum cap visible
    */
    var cw = canvas.width;

    var initial_orientation = get_orientation_from_url();
    var x = initial_orientation.x ;
    var to_zoom = initial_orientation.zoom ;
    
    zm = zooms[to_zoom];

    // x min and max visible in the screen
    // 1 pixel_screen = X pixel_photo = pixel_photo / ((nb_tiles-1) * pixel_tile + pixel_last_tile)
    // (nb_tiles-1)*pixel_tile + pixel_last_tile = zm.im.visible_width
    var half_width = (cw - 2*border_width) * ( image_width / (zm.im.visible_width)) / 2 ;

    var total_angle = fmodulo(image_cap_max - image_cap_min, 360); // panorama total angle
    if (total_angle == 0){total_angle = 360}; // if panorama loops
    var half_angle = total_angle * (half_width / image_width);

    // min and max visible cap
    var bearing = parseInt($('#angle_ctrl').val());
    var cap_min = fmodulo(bearing - half_angle, 360);
    var cap_max = fmodulo(bearing + half_angle, 360);

    // check outside border
    if (! image_loop){
        if (x - half_width < 0){cap_min = image_cap_min};
        if (x + half_width > image_width){cap_max = image_cap_max};
    };

    // check if we repeat the pano
    if ( half_angle > 180 && image_loop){
        var cap_min = 0;
        var cap_max = 360;
    };

    return {cap_min: cap_min, cap_max : cap_max}
};

function load_map(){
    /* Create the map object with the view cone and bearing object 
    */
    
    // initialize the map object (global, to be view from update_map())
    map = L.map('mapid').setView([panorama_lat, panorama_lng], 13);

    // create the tile layer with correct attribution
	var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});		
	map.addLayer(osm);
        map.addLayer( markerClusters );
        map.addLayer(pointsOfInterest);


	L.marker([panorama_lat, panorama_lng]).addTo(map);

    map.on('click', function(e) { 
        /* Compute the new cap to show given the clic lat/lng */
        var lat = toRad(e.latlng.lat); // latitude
        var phi = toRad(e.latlng.lng); // longitude
        var lat_ref = toRad(panorama_lat);
        var phi_ref = toRad(panorama_lng);
        // angle between the ref_point and the clic_point
        var a = Math.acos( Math.cos(lat_ref) * Math.cos(phi - phi_ref) * Math.cos(lat) + Math.sin(lat_ref) * Math.sin(lat) );
        // azimuth between the ref_point and the clic_point (=new cap)
        var B = Math.asin( Math.sin(phi - phi_ref) * Math.sin(Math.PI/2 - lat)/Math.sin(a));
        // little hack because asin give an angle in [-pi/2, pi/2] and we want
        // in [0 360]
        if (lat>lat_ref){   
            var newCap = toDeg(B);
        } else {
            var newCap = toDeg(Math.PI-B);
        }
        if (newCap < 0 ){
            newCap += 360;
        }

        // cap_min < cap < cap_max
        if (newCap < image_cap_min){
            newCap = image_cap_min;
        } else if (newCap > image_cap_max){
            newCap = image_cap_max;
        }
        // change the cap
        angle_control = document.getElementById('angle_ctrl');
        angle_control.value = newCap;
        
        // update the panorama & minimap
        change_angle(); // update panorama
        update_map(); // update minimap
    });
    update_map();

};

function update_map(){
    /* Update the map: view cone and bearing 
    */
    if (map_never_drawn){
        map_never_drawn = false;
    } else {
        map.removeLayer(viewField);
        map.removeLayer(viewDirection);
    };
        
    var bearing = $('#angle_ctrl').val();
    var cap = getCapMinMaxVisible();

    /* TODO: allow to configure the maximum distance. */
    viewField = getCone(panorama_lat,panorama_lng,bearing,cap,50000);
    viewDirection = L.polygon([[panorama_lat, panorama_lng],[destVincenty(panorama_lat, panorama_lng, bearing, 50000).lat,destVincenty(panorama_lat, panorama_lng, bearing, 50000).lng]],{color: '#2880ca', opacity: 1, weight: 2});
    
    viewField.addTo(map);
    viewDirection.addTo(map);

}
