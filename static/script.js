
let topic = "";
let index = -1;
let img = new Image();
let boxes = [];
let BOX_RADIUS = 20; // Radius of the box to be drawn

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
    const box={
      x: position.x - BOX_RADIUS,
      y: position.y - BOX_RADIUS,
      width: BOX_RADIUS * 2,
      height: BOX_RADIUS * 2,
      index: boxes.length + 1
    };
    boxes.push(box);
    draw();
  });

  document.getElementById("submit").onclick=submit;

  document.getElementById("download").onclick = function() {
    window.location.href = "/download";
  };

  // Handle Ctrl+Z or Cmd+Z to undo the last box
  window.addEventListener("keydown", function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "z") {
      if (boxes.length > 0) {
        boxes.pop();
        draw();
        e.preventDefault();
      }
    }
  });
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
    const centerX = b.x + b.width / 2;
    const centerY = b.y + b.height / 2;
    const radius = Math.max(Math.abs(b.width), Math.abs(b.height)) / 2;

    // Draw 20% darker red filled circle with 50% alpha
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(204,0,0,0.7)';
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

  topic = res.topic;
  index = res.index;

  console.log(res);

  document.getElementById("question").innerText=res.prompt;
  document.getElementById("userInput").value = res.ground_truth || "";

  document.getElementById("progress").innerText = `진행: ${res.solved_count} / ${res.total_count}`;

  img.src = "data:image/png;base64," + res.image_base64;
  img.onload = function() {
    canvas.height = img.height;
    canvas.width = img.width;
    draw();
  }
}

async function submit() {
  // input 값 가져오기
  const userAnswer = document.getElementById("userInput").value;

  // API에 보낼 데이터 구성
  const body = {
    topic: topic,
    index: index,
    user_masks: boxes,
    user_answer: userAnswer
  };

  console.log(body);

  // API 호출
  const response = await fetch("/answer", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }).then(r => r.json());

  // 결과 표시
  if (response.task_id) {
    document.getElementById("status").innerText = "✅ 답안 제출 완료 (task_id: " + response.task_id + ")";
  } else {
    document.getElementById("status").innerText = "❌ 제출 실패";
  }

  await newTask();
}