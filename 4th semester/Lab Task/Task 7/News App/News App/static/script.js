// 1. Function to Load News from Backend API
async function loadNews() {
    const container = document.getElementById('news-container');
    container.innerHTML = '<div class="text-center w-100 py-5">Loading headlines...</div>';

    try {
        const response = await fetch('/api/news');
        const data = await response.json();
        
        container.innerHTML = ''; // Clear loading text

        if (!data.articles || data.articles.length === 0) {
            container.innerHTML = '<div class="alert alert-info w-100">No news found. Be the first to post!</div>';
            return;
        }

        data.articles.forEach(item => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4';
            
            // Format date slightly cleaner
            const dateStr = item.published_at ? new Date(item.published_at).toLocaleDateString() : 'Just now';

            col.innerHTML = `
                <div class="card news-card h-100">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${item.title}</h5>
                        <p class="source-tag mb-2">${item.source || 'Unknown Source'} • ${dateStr}</p>
                        <p class="card-text flex-grow-1">${item.description || 'No description available.'}</p>
                        ${item.url ? `<a href="${item.url}" target="_blank" class="btn btn-sm btn-outline-primary mt-3">Read Full Story</a>` : ''}
                    </div>
                </div>
            `;
            container.appendChild(col);
        });

    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="alert alert-danger w-100">Failed to load news. Ensure Flask is running.</div>';
    }
}

// 2. Function to Submit News to Backend API
document.getElementById('newsForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = "Publishing...";
    submitBtn.disabled = true;

    const payload = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        source: document.getElementById('source').value,
        url: document.getElementById('url').value
    };

    try {
        const response = await fetch('/api/news', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById('newsForm').reset(); // Clear form
            loadNews(); // Reload list
        } else {
            alert("Failed to add news");
        }
    } catch (error) {
        console.error("Error submitting news:", error);
        alert("Error connecting to server.");
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});

// Load news immediately when page opens
document.addEventListener('DOMContentLoaded', loadNews);