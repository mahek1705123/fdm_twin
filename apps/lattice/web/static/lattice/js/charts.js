const TOPOCOL=["#4FD1E8","#FFB020","#B58CFF","#FF6B8A"];
const f2=(v,n)=>Math.abs(v)>=1000?v.toFixed(0):Math.abs(v)>=100?v.toFixed(1):v.toFixed(n===undefined?2:n);
/* Lattice drawing: geometry comes from the API (paths in unit-cell coordinates). */
function drawLattice(cv,geom,eps,nu,hot){const dpr=devicePixelRatio||1,w=cv.clientWidth,h=cv.clientHeight;cv.width=w*dpr;cv.height=h*dpr;
 const c=cv.getContext("2d");c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);if(!geom)return;const css=getComputedStyle(document.documentElement);
 let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;geom.paths.forEach(p=>p.forEach(q=>{x0=Math.min(x0,q[0]);x1=Math.max(x1,q[0]);y0=Math.min(y0,q[1]);y1=Math.max(y1,q[1])}));
 const s=Math.min((w-60)/(x1-x0),(h-60)/(y1-y0)),lx=1-nu*eps,ly=1-eps,cx=(x0+x1)/2,cy=(y0+y1)/2;
 c.lineWidth=Math.max(1.4,Math.min(16,geom.wall_ratio*s));c.lineCap="round";c.lineJoin="round";
 const cool=css.getPropertyValue("--cool").trim(),acc=css.getPropertyValue("--accent").trim();c.strokeStyle=hot>0?mix(cool,acc,Math.min(1,hot)):cool;
 geom.paths.forEach(p=>{c.beginPath();p.forEach((q,k)=>{const X=w/2+(q[0]-cx)*s*lx,Y=h/2+(q[1]-cy)*s*ly;k?c.lineTo(X,Y):c.moveTo(X,Y)});c.stroke()})}
function mix(a,b,t){const A=hx(a),B=hx(b);return"rgb("+A.map((v,i)=>Math.round(v+(B[i]-v)*t)).join(",")+")"}
function hx(s){s=s.replace("#","");return[0,2,4].map(i=>parseInt(s.substr(i,2),16))}
/* ---------- canvas charts ---------- */
function cvs(cv){const dpr=devicePixelRatio||1,w=cv.clientWidth,h=cv.clientHeight;cv.width=w*dpr;cv.height=h*dpr;const c=cv.getContext("2d");c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);
 const s=getComputedStyle(document.documentElement);return{c,w,h,ink:s.getPropertyValue("--ink").trim(),mute:s.getPropertyValue("--mute").trim(),line:s.getPropertyValue("--line").trim(),acc:s.getPropertyValue("--accent").trim()}}
function axes(g,x0,x1,y0,y1,xl,yl,lg){const{c,w,h}=g,m={l:56,r:14,t:14,b:40};c.font="12px Schibsted Grotesk,system-ui";c.fillStyle=g.mute;c.strokeStyle=g.line;c.lineWidth=1;
 const fx=v=>m.l+(v-x0)/(x1-x0||1)*(w-m.l-m.r),T=v=>lg?Math.log10(Math.max(v,1e-3)):v,a=T(y0),b=T(y1),fy=v=>h-m.b-(T(v)-a)/(b-a||1)*(h-m.t-m.b);
 for(let i=0;i<=4;i++){const xv=x0+(x1-x0)*i/4,yv=lg?Math.pow(10,a+(b-a)*i/4):y0+(y1-y0)*i/4;c.beginPath();c.moveTo(fx(xv),m.t);c.lineTo(fx(xv),h-m.b);c.moveTo(m.l,fy(yv));c.lineTo(w-m.r,fy(yv));c.stroke();
  c.textAlign="center";c.fillText(f2(xv,1),fx(xv),h-m.b+16);c.textAlign="right";c.fillText(f2(yv,1),m.l-6,fy(yv)+4)}
 c.textAlign="center";c.fillText(xl,(m.l+w-m.r)/2,h-6);c.save();c.translate(13,(m.t+h-m.b)/2);c.rotate(-Math.PI/2);c.fillText(yl,0,0);c.restore();return{fx,fy}}
function scatter(cv,pts,o){const g=cvs(cv),{c}=g;let xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);if(o.mark){xs=xs.concat(o.mark.x);ys=ys.concat(o.mark.y)}
 let x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);if(o.same){x0=y0=Math.min(x0,y0);x1=y1=Math.max(x1,y1)}
 const px=(x1-x0)*.05||1,py=(y1-y0)*.05||1;x0-=px;x1+=px;if(!o.log){y0-=py;y1+=py}else y0=Math.max(y0*.8,1e-3);if(o.log)y1*=1.2;
 const A=axes(g,x0,x1,y0,y1,o.xl,o.yl,o.log);if(o.same){c.setLineDash([5,4]);c.strokeStyle=g.mute;c.beginPath();c.moveTo(A.fx(x0),A.fy(x0));c.lineTo(A.fx(x1),A.fy(x1));c.stroke();c.setLineDash([])}
 pts.forEach(p=>{c.fillStyle=p.c;c.globalAlpha=.75;c.beginPath();c.arc(A.fx(p.x),A.fy(p.y),3.4,0,7);c.fill()});c.globalAlpha=1;
 if(o.mark){const X=A.fx(o.mark.x),Y=A.fy(o.mark.y);c.strokeStyle=g.acc;c.fillStyle=g.acc;c.lineWidth=2.5;c.beginPath();for(let k=0;k<10;k++){const r=k%2?5:12,a=-Math.PI/2+k*Math.PI/5;c.lineTo(X+r*Math.cos(a),Y+r*Math.sin(a))}c.closePath();c.fill()}}
function lines(cv,series,o){const g=cvs(cv),{c}=g;let xs=[],ys=[];series.forEach(s=>s.p.forEach(q=>{xs.push(q[0]);ys.push(q[1])}));
 const x0=Math.min(...xs),x1=Math.max(...xs),mn=Math.min(...ys),mx=Math.max(...ys),y0=o.y0===undefined?Math.min(0,mn*1.08):o.y0,y1=Math.max(0,mx*1.08);const A=axes(g,x0,x1,y0,y1,o.xl,o.yl,false);
 series.forEach(s=>{c.strokeStyle=s.c;c.lineWidth=s.w||2.4;c.beginPath();s.p.forEach((q,k)=>k?c.lineTo(A.fx(q[0]),A.fy(q[1])):c.moveTo(A.fx(q[0]),A.fy(q[1])));c.stroke()});
 if(o.mx!==undefined){c.strokeStyle=g.acc;c.setLineDash([4,4]);c.beginPath();c.moveTo(A.fx(o.mx),A.fy(y0));c.lineTo(A.fx(o.mx),A.fy(y1));c.stroke();c.setLineDash([])}}
function bars(el,items,fmt,cols){const m=Math.max(...items.map(i=>Math.abs(i.v)))||1;el.innerHTML=items.map((i,k)=>`<div class="br"><span>${i.l}</span><div class="bt"><i style="width:${Math.max(2,Math.abs(i.v)/m*100)}%;background:${i.c||(cols&&cols[k])||'var(--cool)'}"></i></div><b>${fmt(i.v)}</b></div>`).join("")}
