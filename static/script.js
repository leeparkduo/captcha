let taskId = -1;
let img = new Image();
let boxes = [];

// canvas element
let canvas = null; 

// canvas context
let ctx = null;

window.onload=async ()=>{
  canvas=document.getElementById("canvas");
  ctx=canvas.getContext("2d");

  await newTask();

  canvas.addEventListener("mousedown",e=>{
    let position = getPos(e);
    const box={x:position.x-15, y:position.y-15, w:30, h:30};
    boxes.push(box);
    draw();
  });

  document.getElementById("submit").onclick=submit;
}

function getPos(e){
  const r=canvas.getBoundingClientRect();
  return {x: e.clientX-r.left, y: e.clientY-r.top};
}

function draw(){
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  ctx.strokeStyle="red"; ctx.lineWidth=2;

  boxes.forEach((b, idx) => {
    // Calculate center and radius
    const centerX = b.x + b.w / 2;
    const centerY = b.y + b.h / 2;
    const radius = Math.max(Math.abs(b.w), Math.abs(b.h)) / 2;

    // Draw black filled circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = 'black';
    ctx.fill();

    // Draw white number centered in circle
    ctx.fillStyle = 'white';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = `${Math.floor(radius)}px Arial`;
    ctx.fillText(idx + 1, centerX, centerY);
  });
}

async function newTask(){
  boxes = [];
  const res = await fetch("/problem").then(r=>r.json());

  taskId = res.id;

  document.getElementById("question").innerText=res.prompt;
  
  img.src = "data:image/png;base64," + res.image_base64;
  img.onload = function() {
    canvas.height = img.height;
    draw();
  }
}

async function submit(){
  const body = { masks:boxes };

  const response = await fetch(`/problem/${taskId}/answer`,{
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  }).then(r => r.json());

  document.getElementById("status").innerText = response.passed ? "✅ 통과" : "❌ 실패";

  await newTask();
}
