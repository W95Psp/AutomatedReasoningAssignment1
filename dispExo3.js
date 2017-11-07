let W = 40;
let H = 7;
let dec = 45;

let canvas = document.getElementById('draw');

totalHeight = Math.max.apply(Math, exportedJSON.map(([a,b]) => a+b));
canvas.width = Math.max.apply(Math, exportedJSON.map(([,,id]) => dec*id))+W+2;
canvas.height = totalHeight * H+2 + 15 + 10;

function shadeColor(color, percent) {   
    var f=parseInt(color.slice(1),16),t=percent<0?0:255,p=percent<0?percent*-1:percent,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
    return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
}
let active = null;
let mousedown = false;
let display = () => {
	let ctx = canvas.getContext('2d');

	ctx.globalAlpha = 1;
	ctx.fillStyle = 'white';
	ctx.fillRect(0, 0, canvas.width+2, canvas.height+2);

	ctx.translate(1,1+15);
	
	let colors = ['#16a085', '#d35400', '#9b59b6', '#2980b9', '#2c3e50', '#2ecc71', '#34495e', '#3498db', '#7f8c8d', '#8e44ad', '#95a5a6', '#27ae60', '#bdc3c7', '#c0392b', '#1abc9c', '#e67e22'];
	exportedJSON.forEach(([actualStartingTime, runningTime, id]) => {
		let c = colors.pop();
		ctx.fillStyle = c;
		ctx.strokeStyle = 'black';
		ctx.globalAlpha = 0.4;
		if(mousedown && active!==null && actualStartingTime + runningTime <= active)
			ctx.strokeStyle = 'brown';
		let d = id*dec;
		ctx.fillRect(d, actualStartingTime*H, W, runningTime*H)
		ctx.globalAlpha = 1;
		ctx.strokeRect(d, actualStartingTime*H, W, runningTime*H)
	});

	ctx.font = '12px Arial';

	ctx.globalAlpha = 1;
	ctx.textAlign = "center";
	ctx.textBaseline = 'middle';
	exportedJSON.forEach(([actualStartingTime, runningTime, id]) => {
		let d = id*dec;
		ctx.fillStyle = 'black';
		ctx.fillText('Job '+id, d+W/2, actualStartingTime*H + runningTime*H/2);
	});

	ctx.fillStyle = 'black';
	ctx.textAlign = "left";
	ctx.font = '8px Consolas';
	ctx.globalAlpha = 0.06;
	for(let i=0; i<=totalHeight; i++){
		if(i%5==0 || active===i){
			ctx.globalAlpha = ((active===i) ? 0.7 : 0.5);
			ctx.fillText(('00'+i).slice(-3), 2, i*H);
			ctx.globalAlpha = ((active===i) ? 0.2 : 0.1);
			let deca = 20;
			ctx.fillRect(deca, i*H, canvas.width-10, 1);
		}else{
			ctx.globalAlpha = 0.06;
			ctx.fillRect(0, i*H, canvas.width, 1);
		}
	}
	
	ctx.translate(-1,-1-15);
};

display();
canvas.onmousedown 	= (e) => mousedown==false && (mousedown = true, display());
canvas.onmouseup 	= (e) => mousedown==true && (mousedown = false, display());
canvas.onmousemove 	= (e) => (active = Math.round((e.offsetY-16)/H), display(), e.stopPropagation());
document.body.onmousemove = (e) => active!==null && (active = null, mousedown=false, display())