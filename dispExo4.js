let W = 60;
let H = 14;
let dec = 2;

exportedJSON = window.exportedJSON || window.ExportedJSONs[0];

let canvas = document.getElementById('draw');

totalHeight = Math.max.apply(Math, exportedJSON.processes.map(([e,,]) => e.length));
canvas.width = W*6+W/2+dec*6;
if(window.ExportedJSONs)
	canvas.width = (W+dec*2) * window.ExportedJSONs.length;
// canvas.width = W+dec*2;
canvas.height = totalHeight * (H+dec)+2 + 15 + 10;

function shadeColor(color, percent) {   
	var f=parseInt(color.slice(1),16),t=percent<0?0:255,p=percent<0?percent*-1:percent,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
	return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
}
// let active = null;
// let mousedown = false;
let display = (exportedJSON, shiftX, hideSB) => {
	let ctx = canvas.getContext('2d');

	ctx.globalAlpha = 1;
	if(shiftX){
		ctx.translate(shiftX, 0);
	}else{
		ctx.fillStyle = 'white';
		ctx.fillRect(0, 0, canvas.width+2, canvas.height+2);
	}

	ctx.translate(1,1+15);


	ctx.font = '12px Arial';

	ctx.textAlign = "center";
	ctx.textBaseline = 'middle';
	
	let colors = ['#16a085', '#d35400', '#9b59b6', '#2980b9', '#2c3e50', '#2ecc71', '#34495e', '#3498db', '#7f8c8d', '#8e44ad', '#95a5a6', '#27ae60', '#bdc3c7', '#c0392b', '#1abc9c', '#e67e22'];
	let isBusyYet = new Array(totalHeight).fill(0);
	exportedJSON.processes.forEach(p => {
		let [emplacements, id, maxI] = p;
		let color = p.color = colors.pop();
		let i = 1;
		emplacements.forEach((e,i) => {
			console.log(e);
			if(e){
				let [_i, _c] = exportedJSON.steps[i];
				let x = isBusyYet[i]*(W+dec)+dec;
				ctx.globalAlpha = 0.4;
				ctx.fillStyle = color;
				ctx.fillRect(x, i*(H+dec), W, H);
				ctx.strokeRect(x, i*(H+dec), W, H);
				ctx.globalAlpha = 1.0;
				ctx.fillStyle = shadeColor(color, -0.4);
				ctx.fillText("i:"+_i+", c:"+_c, x+W/2, i*(H+dec)+H/2, W, H);
			}
			isBusyYet[i] += +e;
		})
	});

	let c = 0;
	exportedJSON.processes.map(_ => _.i = 1);
	if(!hideSB){
		for(let i = 0; i < totalHeight; i++){
			let [_i, _c] = exportedJSON.steps[i];
			let p = exportedJSON.processes.filter(([emplacements, id, maxI]) => emplacements[i])[0];
			ctx.fillStyle = shadeColor(p.color, -0.4);
			let x = isBusyYet[i]*(W+dec)+dec;
			c += c < 20 ? 1 : p.i;
			ctx.fillText("Should be : i="+p.i+"; c="+c+(p.i != _i || c != _c ? ' ERROR!!!' : ''), x+W/1.5, i*(H+dec)+H/2, W, H);
			p.i++;
		}
	}

	// ctx.font = '12px Arial';

	// ctx.globalAlpha = 1;
	// ctx.textAlign = "center";
	// ctx.textBaseline = 'middle';
	// exportedJSON.processes.forEach(([actualStartingTime, runningTime, id]) => {
	// 	let d = id*dec;
	// 	ctx.fillStyle = 'black';
	// 	ctx.fillText('Job '+id, d+W/2, actualStartingTime*H + runningTime*H/2);
	// });

	if(shiftX){
		ctx.translate(-shiftX, 0);
	}

	ctx.translate(-1,-1-15);
};

if(window.ExportedJSONs)
	for(let i in window.ExportedJSONs)
		display(window.ExportedJSONs[i], i * (W + dec*2), true);
else
	display(exportedJSON, 0);
// canvas.onmousedown 	= (e) => mousedown==false && (mousedown = true, display());
// canvas.onmouseup 	= (e) => mousedown==true && (mousedown = false, display());
// canvas.onmousemove 	= (e) => (active = Math.round((e.offsetY-16)/H), display(), e.stopPropagation());
// document.body.onmousemove = (e) => active!==null && (active = null, mousedown=false, display())