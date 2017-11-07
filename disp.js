let W = 12;
let H = 12;

let mw = 30;
let mh = 30;

let canvas = document.getElementById('draw');
let canvas_width = mw * W+2 + 200;
let canvas_height = mh * H+2;
let scaleFactor = 2;
canvas.lineWidth = 100;
canvas.width = canvas_width * scaleFactor;
canvas.height = canvas_height * scaleFactor;

function shadeColor(color, percent) {   
    var f=parseInt(color.slice(1),16),t=percent<0?0:255,p=percent<0?percent*-1:percent,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
    return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
}

let display = () => {
	let ctx = canvas.getContext('2d');
	ctx.scale(scaleFactor,scaleFactor);

	ctx.globalAlpha = 1;
	ctx.fillStyle = 'white';
	ctx.fillRect(0, 0, canvas_width+2, canvas_height+2);

	ctx.translate(1,1);
	
	let colors = ['#16a085', '#d35400', '#9b59b6', '#2980b9', '#2c3e50', '#2ecc71', '#34495e', '#3498db', '#7f8c8d', '#8e44ad', '#95a5a6', '#27ae60', '#bdc3c7', '#c0392b', '#1abc9c', '#e67e22'];
	exportedJSON.forEach(({x, y, w, h, specw, spech, isPower, name}) => {
		let c = colors.pop();
		ctx.fillStyle = c;
		ctx.globalAlpha = 0.4;
		ctx.fillRect(x*W, y*H, w*W, h*H)
		if(isPower){
			ctx.strokeStyle = 'blue';
			ctx.globalAlpha = 0.8;
		}else
			ctx.strokeStyle = shadeColor(c, -0.3);
		ctx.strokeRect(x*W, y*H, w*W, h*H)
	});

	ctx.fillStyle = 'black';
	ctx.globalAlpha = 0.04;
	for(let i=0; i<=mw; i++)
		ctx.fillRect(i*W, 0, 1, mh * H);
	for(let i=0; i<=mh; i++)
		ctx.fillRect(0, i*W, mh * H, 1);

	ctx.font = '12px Arial';

	ctx.globalAlpha = 1;
	ctx.textAlign = "center";
	ctx.textBaseline = 'middle';
	exportedJSON.forEach(({x, y, w, h, specw, spech, isPower, name}) => {
		ctx.font = '11px Arial';
		ctx.fillStyle = 'gray';
		if(w!=specw)
			ctx.fillText('[rot'+(spech > 5 ? 'ated' : '.')+']', x*W + w*W/2, y*H + h*H/2 - 15);
		ctx.font = '12px Arial';
		if(specw > 4 && spech > 4)
			ctx.font = '14px Arial';
		ctx.fillStyle = 'black';
		ctx.fillText(name+' '+specw+'x'+spech, x*W + w*W/2, y*H + h*H/2);
	});


	ctx.translate(-1,-1);
	ctx.scale(1/scaleFactor,1/scaleFactor);
};

function makeAnImage(){
	document.write('<img src="'+document.getElementById("draw").toDataURL("image/png")+'"/>');
}

display();
let getPair = (e) => [e.offsetX, e.offsetY].map(o => Math.floor((o-1)/W));
let firstPosition = null;
canvas.onmousedown = (e) =>	firstPosition = getPair(e);
canvas.onmouseup = (e) => 	firstPosition = null;
canvas.onmousemove = (e) => {
	let [x,y] = getPair(e);
	display();
	let ctx = canvas.getContext('2d');
	ctx.fillStyle = 'black';
	if(x < mw){
		ctx.globalAlpha = 0.1;
		if(firstPosition){
			let [fx, fy] = firstPosition;
			let ax = Math.min(x+1, fx);
			let ay = Math.min(y+1, fy);
			let zx = Math.max(x+1, fx);
			let zy = Math.max(y+1, fy);
			ctx.fillRect(ax*W+1, ay*H+1, (zx - ax)*W+1, (zy - ay)*H+1);
			ctx.globalAlpha = 1;
			ctx.fillText(JSON.stringify([zx-ax,zy-ay]), canvas_width - 100, 50);
		}else
			ctx.fillRect(x*W+1, y*H+1, W, H);
	}

	console.log(x,y);
};