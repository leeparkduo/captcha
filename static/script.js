let taskId = -1;
let img = new Image();
let boxes = [];

// canvas element
let canvas = null; 

// canvas context
let ctx = null;

// start position for drawing
let start = null;

window.onload=async ()=>{
  canvas=document.getElementById("canvas");
  ctx=canvas.getContext("2d");

  await newTask();

  canvas.addEventListener("mousedown",e=>{
      start=getPos(e);
  });

  canvas.addEventListener("mouseup",e=>{
      if(!start) return;
      const end=getPos(e);
      const box={x:start.x, y:start.y, w:end.x-start.x, h:end.y-start.y};
      boxes.push(box); draw();
      start=null;
  });

  document.getElementById("submit").onclick=submit;
}

function getPos(e){
  const r=canvas.getBoundingClientRect();
  return {x: e.clientX-r.left, y: e.clientY-r.top};
}

function draw(){
  ctx.drawImage(img,0,0);
  ctx.strokeStyle="red"; ctx.lineWidth=2;

  boxes.forEach(b=>{
    ctx.strokeRect(b.x,b.y,b.w,b.h);
  });
}

async function newTask(){
  boxes = [];
  const res = await fetch("/captcha").then(r=>r.json());

  taskId = res.id;

  document.getElementById("question").innerText=res.question;
  
  img.src = res.image_url;
  img.onload=draw;
}

async function submit(){
  const body = { masks:boxes };

  const response = await fetch(`/captcha/${taskId}/answer`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  }).then(r => r.json());

  document.getElementById("status").innerText = response.passed ? "✅ 통과" : "❌ 실패";

  await newTask();
}
