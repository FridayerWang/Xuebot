document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Add initial bot message
    addBotMessage("Hello! I'm your Education Assistant. How can I help you today?");

    // Send message when button is clicked
    sendButton.addEventListener('click', sendMessage);

    // Send message when Enter key is pressed (but allow Shift+Enter for new lines)
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea based on content
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.scrollHeight > 150) {
            this.style.height = '150px';
            this.style.overflowY = 'auto';
        } else {
            this.style.overflowY = 'hidden';
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addUserMessage(message);

        // Clear input field and reset height
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        // Call API to get bot response
        fetchBotResponse(message);
    }

    function fetchBotResponse(message) {
        // For demonstration purposes, we'll provide a fallback to the canned responses
        // in case the API is not available
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add bot response to chat
            addBotMessage(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            
            // Fallback to canned responses
            processUserMessageFallback(message);
        });
    }

    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.innerHTML = `<div class="message-bubble">${escapeHTML(message)}</div>`;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }

    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        
        // Check if this is a selection prompt
        if (message.includes('SELECTION REQUIRED')) {
            // Format selection prompts
            let formattedMessage = message;
            
            // First strip the raw markdown indicators
            formattedMessage = formattedMessage.replace('📋 SELECTION REQUIRED:', '');
            formattedMessage = formattedMessage.replace(/\n\nType either ['"]personalized['"] or ['"]authoritative['"]/, '');
            
            // Build a cleaner HTML version
            formattedMessage = `<strong>📋 SELECTION REQUIRED:</strong>
                <div class="selection-required">Choose your question type:</div>
                <div class="option"><strong>Personalized</strong> - Questions generated specifically for you</div>
                <div class="option"><strong>Authoritative</strong> - Questions from our verified database</div>
                <div style="margin-top: 10px;">Please respond with either <strong>"personalized"</strong> or <strong>"authoritative"</strong>.</div>`;
            
            const bubble = document.createElement('div');
            bubble.className = 'message-bubble selection-message-bubble';
            bubble.innerHTML = formattedMessage;
            messageElement.appendChild(bubble);
        } else {
            messageElement.innerHTML = `<div class="message-bubble">${escapeHTML(message)}</div>`;
        }
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
        
        // Add click event listeners to options if they exist
        const options = messageElement.querySelectorAll('.option');
        options.forEach(option => {
            option.addEventListener('click', function() {
                // Extract the option text (personalized or authoritative)
                const optionText = this.querySelector('strong').textContent.toLowerCase();
                // Set the user input field value
                userInput.value = optionText;
                // Send the message
                sendMessage();
            });
        });
    }

    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message typing-indicator';
        typingIndicator.id = 'typing-indicator';
        typingIndicator.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    // Fallback function if API call fails
    function processUserMessageFallback(message) {
        // Canned responses
        const lowerMessage = message.toLowerCase();
        let response;

        if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
            response = "Hello! How can I assist you with your education today?";
        } else if (lowerMessage.includes('how are you')) {
            response = "I'm just a program, but I'm functioning well! How can I help you?";
        } else if (lowerMessage.includes('bye') || lowerMessage.includes('goodbye')) {
            response = "Goodbye! Feel free to come back if you have more questions.";
        } else if (lowerMessage.includes('thank')) {
            response = "You're welcome! Is there anything else I can help you with?";
        } else if (lowerMessage.includes('math') || lowerMessage.includes('mathematics')) {
            response = "I can help with mathematics! What specific topic or problem are you interested in?";
        } else if (lowerMessage.includes('science')) {
            response = "Science is fascinating! What area of science are you studying? Biology, Chemistry, Physics, or something else?";
        } else if (lowerMessage.includes('history')) {
            response = "History is full of important lessons. Which historical period or event would you like to discuss?";
        } else {
            response = "I'm here to help with your educational questions. Could you provide more details about what you'd like to learn?";
        }

        // Add bot response to chat
        addBotMessage(response);
    }
}); 