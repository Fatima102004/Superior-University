// ==================== DOM Elements ====================
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const registerForm = document.getElementById('registerForm');
const faceImageInput = document.getElementById('faceImage');
const previewImg = document.getElementById('previewImg');
const imagePreview = document.getElementById('imagePreview');
const registerStatus = document.getElementById('registerStatus');
const refreshBtn = document.getElementById('refreshBtn');
const clearBtn = document.getElementById('clearBtn');
const downloadBtn = document.getElementById('downloadBtn');
const attendanceTableBody = document.getElementById('attendanceTableBody');
const registeredList = document.getElementById('registeredList');
const registeredCount = document.getElementById('registeredCount');
const attendanceCount = document.getElementById('attendanceCount');
const totalPresent = document.getElementById('totalPresent');
// New Camera Elements
const toggleCameraBtn = document.getElementById('toggleCameraBtn');
const videoFeed = document.getElementById('videoFeed');
const cameraPlaceholder = document.getElementById('cameraPlaceholder');

let isCameraOn = true;

// ==================== Event Listeners ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadInitialData();
    startAutoRefresh();
});

function initializeEventListeners() {
    // Tab navigation
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Form submission
    registerForm.addEventListener('submit', handleRegisterFace);

    // File input preview
    faceImageInput.addEventListener('change', handleImagePreview);

    // Camera Toggle
    if(toggleCameraBtn) {
        toggleCameraBtn.addEventListener('click', toggleCamera);
    }

    // Drag and drop
    const fileLabel = document.querySelector('.file-label');
    if(fileLabel) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileLabel.addEventListener(eventName, preventDefaults, false);
        });
        fileLabel.addEventListener('drop', handleDrop, false);
    }

    // Button actions
    refreshBtn.addEventListener('click', refreshAttendance);
    clearBtn.addEventListener('click', confirmAndClearAttendance);
    downloadBtn.addEventListener('click', downloadAttendanceCSV);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// ==================== Camera Toggle Logic ====================
function toggleCamera() {
    isCameraOn = !isCameraOn;
    
    if (isCameraOn) {
        // Turn ON
        videoFeed.src = "/video_feed";
        videoFeed.style.display = "block";
        cameraPlaceholder.style.display = "none";
        toggleCameraBtn.innerHTML = '<span class="btn-icon">🛑</span> Stop Camera';
        toggleCameraBtn.classList.replace('btn-success', 'btn-primary');
    } else {
        // Turn OFF
        videoFeed.src = "";
        videoFeed.style.display = "none";
        cameraPlaceholder.style.display = "flex";
        toggleCameraBtn.innerHTML = '<span class="btn-icon">📹</span> Start Camera';
        toggleCameraBtn.classList.replace('btn-primary', 'btn-success');
    }
}

// ==================== Tab Switching ====================
function switchTab(tabName) {
    tabContents.forEach(content => content.classList.remove('active'));
    tabBtns.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    if (tabName === 'attendance') {
        refreshAttendance();
    }
}

// ==================== Image Preview ====================
function handleImagePreview(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            previewImg.src = event.target.result;
            previewImg.style.display = 'block';
            imagePreview.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    faceImageInput.files = files;
    handleImagePreview({ target: { files: files } });
}

// ==================== Register Face ====================
async function handleRegisterFace(e) {
    e.preventDefault();

    const name = document.getElementById('personName').value.trim();
    const file = faceImageInput.files[0];

    if (!name || !file) {
        showStatus('Please enter a name and select an image', 'error');
        return;
    }

    const submitBtn = registerForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span>Processing...';

    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);

    try {
        const response = await fetch('/api/register-face', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus(`✓ ${data.message}`, 'success');
            registerForm.reset();
            previewImg.style.display = 'none';
            imagePreview.style.display = 'none';
            loadRegisteredFaces();
        } else {
            showStatus(`✗ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error registering face. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function showStatus(message, type) {
    registerStatus.textContent = message;
    registerStatus.className = `status-message status-${type}`;
    registerStatus.style.display = 'block';

    setTimeout(() => {
        registerStatus.style.display = 'none';
    }, 4000);
}

// ==================== Attendance Management ====================
async function refreshAttendance() {
    try {
        const response = await fetch('/api/attendance');
        const attendanceData = await response.json();

        if (attendanceData.length === 0) {
            attendanceTableBody.innerHTML = '<tr class="empty-row"><td colspan="4">No attendance records yet</td></tr>';
        } else {
            attendanceTableBody.innerHTML = attendanceData.map((record, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${record.name}</strong></td>
                    <td>${formatDate(record.time)}</td>
                    <td><span class="status-badge status-present">${record.status}</span></td>
                </tr>
            `).join('');
        }

        totalPresent.textContent = attendanceData.length;
        attendanceCount.textContent = attendanceData.length;
    } catch (error) {
        console.error('Error fetching attendance:', error);
    }
}

function confirmAndClearAttendance() {
    if (confirm('Are you sure you want to clear all records?')) {
        clearAttendance();
    }
}

async function clearAttendance() {
    try {
        const response = await fetch('/api/attendance/clear', { method: 'POST' });
        if (response.ok) {
            refreshAttendance();
            alert('Attendance records cleared successfully');
        }
    } catch (error) {
        console.error('Error clearing attendance:', error);
    }
}

function downloadAttendanceCSV() {
    const rows = attendanceTableBody.querySelectorAll('tr:not(.empty-row)');
    if (rows.length === 0) {
        alert('No attendance records to download');
        return;
    }

    let csv = 'S.No,Name,Check-in Time,Status\n';
    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        const name = cells[1].textContent;
        const time = cells[2].textContent;
        const status = cells[3].textContent;
        csv += `${index + 1},"${name}","${time}","${status}"\n`;
    });

    const link = document.createElement('a');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    link.href = url;
    link.download = `attendance_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
}

// ==================== Registered Faces Management ====================
async function loadRegisteredFaces() {
    try {
        const response = await fetch('/api/registered-faces');
        const data = await response.json();

        registeredCount.textContent = data.count;

        if (data.faces.length === 0) {
            registeredList.innerHTML = '<p class="empty-message">No registered faces yet</p>';
        } else {
            // UPDATED: Added Flexbox layout and Delete Button
            registeredList.innerHTML = data.faces.map(face => `
                <div class="person-item" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>👤 <strong>${face}</strong></span>
                    <button onclick="deleteRegisteredFace('${face}')" class="btn btn-danger" style="padding: 5px 10px; font-size: 0.8rem;">
                        🗑️
                    </button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading registered faces:', error);
    }
}

// NEW FUNCTION: Handle Deletion
async function deleteRegisteredFace(name) {
    if (!confirm(`Are you sure you want to delete ${name}? This cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch('/api/delete-face', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name })
        });

        const data = await response.json();

        if (response.ok) {
            // Show small alert or toast
            // Re-load the list to show it's gone
            loadRegisteredFaces();
            // Also refresh attendance counts if needed, though usually not strictly linked
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error deleting face:', error);
        alert('Failed to connect to server');
    }
}

function startAutoRefresh() {
    setInterval(loadRegisteredFaces, 10000);
    setInterval(() => {
        if (document.getElementById('attendance').classList.contains('active')) {
            refreshAttendance();
        }
    }, 5000);
}

function loadInitialData() {
    loadRegisteredFaces();
    refreshAttendance();
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}