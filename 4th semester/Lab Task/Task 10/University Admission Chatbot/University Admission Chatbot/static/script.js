const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');

function appendMessage(sender, text) {
	const el = document.createElement('div');
	el.className = 'message ' + (sender === 'user' ? 'user' : 'bot');
	el.innerText = text;
	chatWindow.appendChild(el);
	chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage(text) {
	appendMessage('user', text);
	messageInput.value = '';
	try {
		const res = await fetch('/chat', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ message: text })
		});
		const data = await res.json();
		appendMessage('bot', data.reply || 'Sorry, no reply.');
	} catch (err) {
		appendMessage('bot', 'Error contacting server.');
		console.error(err);
	}
}

chatForm.addEventListener('submit', function (e) {
	e.preventDefault();
	const text = messageInput.value.trim();
	if (text) sendMessage(text);
});

messageInput.addEventListener('keydown', function (e) {
	if (e.key === 'Enter' && !e.shiftKey) {
		e.preventDefault();
		const text = messageInput.value.trim();
		if (text) sendMessage(text);
	}
});

// welcome message
appendMessage('bot', "Hello — I'm the University Admission Chatbot. How can I help?");

