/* GCJ-02 -> WGS84 inverse; rendered tiles use WGS84, source coordinates remain GCJ02. */
function gcjToWgs(lat,lng){
 const pi=Math.PI,a=6378245,ee=.006693421622965943;
 if(lng<72.004||lng>137.8347||lat<.8293||lat>55.8271)return [lat,lng];
 const x=lng-105,y=lat-35;
 let dy=-100+2*x+3*y+.2*y*y+.1*x*y+.2*Math.sqrt(Math.abs(x));
 dy+=(20*Math.sin(6*x*pi)+20*Math.sin(2*x*pi))*2/3;
 dy+=(20*Math.sin(y*pi)+40*Math.sin(y/3*pi))*2/3;
 dy+=(160*Math.sin(y/12*pi)+320*Math.sin(y*pi/30))*2/3;
 let dx=300+x+2*y+.1*x*x+.1*x*y+.1*Math.sqrt(Math.abs(x));
 dx+=(20*Math.sin(6*x*pi)+20*Math.sin(2*x*pi))*2/3;
 dx+=(20*Math.sin(x*pi)+40*Math.sin(x/3*pi))*2/3;
 dx+=(150*Math.sin(x/12*pi)+300*Math.sin(x/30*pi))*2/3;
 const rad=lat*pi/180,magic=1-ee*Math.sin(rad)**2,root=Math.sqrt(magic);
 dy=dy*180/(a*(1-ee)/(magic*root)*pi);dx=dx*180/(a/root*Math.cos(rad)*pi);
 return [lat-dy,lng-dx];
}
let activeMap=null;
function drawTravelMap(data){
 if(activeMap){activeMap.remove();activeMap=null;}
 if(!window.L)return;
 const container=document.getElementById('map');container.replaceChildren();
 activeMap=L.map(container).setView([31.3,120.6],11);
 L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(activeMap);
 const bounds=[];
 for(const p of data.points||[]){const xy=gcjToWgs(p.lat,p.lng);bounds.push(xy);const label=document.createElement('span');label.textContent=`Day ${p.day} · ${p.name}`;L.marker(xy).addTo(activeMap).bindPopup(label);}
 for(const route of data.routes||[]){if(route.coordinates?.length)L.polyline(route.coordinates.map(p=>gcjToWgs(p[0],p[1])),{color:'#126b59',weight:4}).addTo(activeMap);}
 if(bounds.length)activeMap.fitBounds(bounds,{padding:[30,30],maxZoom:14});
 setTimeout(()=>activeMap.invalidateSize(),100);
}
