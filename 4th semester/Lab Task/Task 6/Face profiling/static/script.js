const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const canvas = document.getElementById('canvas');
const resultsDiv = document.getElementById('results');
const previewSection = document.getElementById('previewSection');
const resultsSection = document.getElementById('resultsSection');
const ctx = canvas.getContext('2d');
let currentImage = null;

function loadImageToCanvas(file) {
  const reader = new FileReader();
  reader.onload = function (e) {
    const img = new Image();
    img.onload = function () {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      currentImage = img;
      previewSection.style.display = 'block';
      document.getElementById('fileName').textContent = file.name;
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

fileInput.addEventListener('change', (ev) => {
  const f = ev.target.files[0];
  if (f) loadImageToCanvas(f);
});

function drawLandmarks(landmarks) {
  if (!currentImage) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(currentImage, 0, 0);

  ctx.strokeStyle = '#667eea';
  ctx.fillStyle = '#764ba2';
  ctx.lineWidth = 2;
  for (let i = 0; i < landmarks.length; i++) {
    const p = landmarks[i];
    if (!p || p.length < 2) continue;
    ctx.beginPath();
    ctx.arc(p[0], p[1], 5, 0, Math.PI * 2);
    ctx.fill();
  }

  if (landmarks.length > 1) {
    ctx.strokeStyle = '#667eea';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(landmarks[0][0], landmarks[0][1]);
    for (let i = 1; i < landmarks.length; i++) {
      ctx.lineTo(landmarks[i][0], landmarks[i][1]);
    }
    ctx.stroke();
  }
}

analyzeBtn.addEventListener('click', async () => {
  const f = fileInput.files[0];
  if (!f) {
    alert('Please select an image file first.');
    return;
  }
  
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Analyzing...';
  resultsDiv.innerHTML = '<p style="text-align:center;color:#667eea;">Processing your image...</p>';
  resultsSection.style.display = 'block';
  
  const form = new FormData();
  form.append('image', f, f.name);

  try {
    const res = await fetch('/analyze', { method: 'POST', body: form });
    const data = await res.json();
    
    if (!res.ok) {
      const err = data;
      resultsDiv.innerHTML = `<p style="color:red;"><strong>Error:</strong> ${err.error || JSON.stringify(err)}</p>`;
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = 'Analyze';
      return;
    }
    const meas = data.measurements || {};
    const profile = data.profile || {};

    // Measurements group
    const measGroup = document.createElement('div');
    measGroup.className = 'measurement-group';
    measGroup.innerHTML = '<h3>📊 Facial Measurements</h3>';
    const ul = document.createElement('ul');
    for (const k of Object.keys(meas)) {
      const li = document.createElement('li');
      const val = typeof meas[k] === 'number' ? Math.round(meas[k]*100)/100 : meas[k];
      li.innerHTML = `<strong>${k}:</strong> <span>${val}</span>`;
      ul.appendChild(li);
    }
    measGroup.appendChild(ul);
    resultsDiv.appendChild(measGroup);

    // Profile card
    const profileCard = document.createElement('div');
    profileCard.className = 'profile-card';
    profileCard.innerHTML = `
      <div class="type">${profile.type}</div>
      <p class="description">${profile.description}</p>
    `;
    resultsDiv.appendChild(profileCard);

    if (data.landmarks) {
      drawLandmarks(data.landmarks);
    }
    
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze Again';
  } catch (e) {
    resultsDiv.innerHTML = `<p style="color:red;"><strong>Error:</strong> ${e.message}</p>`;
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze';
  }
});
