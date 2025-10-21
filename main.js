// JavaScript code for the cultural events system

// Function to fetch events data from the JSON file
async function fetchEvents() {
    try {
        const response = await fetch('./data/events.json');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const events = await response.json();
        displayEvents(events);
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
}

// Function to display events on the page
function displayEvents(events) {
    const eventGrid = document.getElementById('eventGrid');
    eventGrid.innerHTML = '';

    events.forEach(event => {
        const card = document.createElement('div');
        card.className = 'event-card';
        card.innerHTML = `
            <div class="event-image">${event.icone}</div>
            <div class="event-details">
                <div class="event-title">${event.titulo}</div>
                <div class="event-info">📅 ${formatDate(event.data)}</div>
                <div class="event-info">📍 ${event.local}</div>
                <div class="event-info">👥 ${event.inscritos}/${event.capacidade} inscritos</div>
                <div class="event-info">⭐ ${event.avaliacao}/5.0</div>
                <span class="event-category">${getCategoryLabel(event.categoria)}</span>
            </div>
        `;
        eventGrid.appendChild(card);
    });
}

// Utility function to format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility function to get category label
function getCategoryLabel(categoria) {
    const labels = {
        'musica': 'Música',
        'teatro': 'Teatro',
        'artes': 'Artes Visuais',
        'danca': 'Dança',
        'literatura': 'Literatura',
        'cinema': 'Cinema'
    };
    return labels[categoria] || categoria;
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    fetchEvents();
});