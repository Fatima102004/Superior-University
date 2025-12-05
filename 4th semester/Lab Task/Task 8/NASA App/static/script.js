document.addEventListener('DOMContentLoaded', function() {
	const apodLoad = document.getElementById('apod-load');
	const apodToday = document.getElementById('apod-today');
	const apodDate = document.getElementById('apod-date');
	const apodContent = document.getElementById('apod-content');

	const marsLoad = document.getElementById('mars-load');
	const roverSelect = document.getElementById('rover-select');
	const marsGallery = document.getElementById('mars-gallery');

	function renderAPOD(data) {
		if (!data || data.error) {
			apodContent.innerHTML = '<div class="error">Unable to load APOD.</div>';
			return;
		}
		let html = `<h3>${data.title}</h3><p class="apod-date">${data.date}</p>`;
		if (data.media_type === 'video') {
			html += `<div class="media"><iframe src="${data.url}" frameborder="0" allowfullscreen></iframe></div>`;
		} else {
			html += `<div class="media"><img src="${data.url}" alt="${data.title}" /></div>`;
		}
		html += `<p class="explain">${data.explanation}</p>`;
		apodContent.innerHTML = html;
	}

	async function fetchAPOD(date) {
		try {
			const url = '/api/apod' + (date ? `?date=${date}` : '');
			const res = await fetch(url);
			const data = await res.json();
			renderAPOD(data);
		} catch (e) {
			apodContent.innerHTML = '<div class="error">APOD fetch failed.</div>';
		}
	}

	async function fetchMars(rover) {
		try {
			const res = await fetch(`/api/mars?rover=${rover}`);
			const data = await res.json();
			if (!data.photos) {
				marsGallery.innerHTML = '<p>No Mars photos found.</p>';
				return;
			}
			marsGallery.innerHTML = data.photos.map(p => `\
				<figure class="mars-item">\
					<img src="${p.img_src}" alt="Mars" />\
					<figcaption>${p.rover.name} - ${p.camera.full_name} (Sol ${p.sol})</figcaption>\
				</figure>`).join('');
		} catch (e) {
			marsGallery.innerHTML = '<p>Error loading Mars photos.</p>';
		}
	}

	apodLoad.addEventListener('click', () => {
		const date = apodDate.value;
		fetchAPOD(date);
	});

	apodToday.addEventListener('click', () => {
		apodDate.value = '';
		fetchAPOD();
	});

	marsLoad.addEventListener('click', () => {
		const rover = roverSelect.value;
		fetchMars(rover);
	});

	// initial load
	fetchAPOD();
	fetchMars(roverSelect.value);
});

