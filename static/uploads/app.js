// SchulBuddy - Hauptfunktionen

// Theme Management
function toggleTheme() {
  const html = document.documentElement;
  const themeIcon = document.getElementById('theme-icon');
  
  if (html.getAttribute('data-bs-theme') === 'dark') {
    html.setAttribute('data-bs-theme', 'light');
    themeIcon.textContent = '🌙';
    localStorage.setItem('theme', 'light');
  } else {
    html.setAttribute('data-bs-theme', 'dark');
    themeIcon.textContent = '☀️';
    localStorage.setItem('theme', 'dark');
  }
}

// Load saved theme
function loadTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  const html = document.documentElement;
  const themeIcon = document.getElementById('theme-icon');
  
  html.setAttribute('data-bs-theme', savedTheme);
  themeIcon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
}

// Aufgaben-Funktionen
function toggleTask(taskId) {
  fetch(`/toggle_task/${taskId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      location.reload();
    } else {
      alert('Fehler beim Aktualisieren der Aufgabe');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Fehler beim Aktualisieren der Aufgabe');
  });
}

function deleteTask(taskId) {
  if (confirm('Aufgabe wirklich löschen?')) {
    fetch(`/delete_task/${taskId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else {
        alert('Fehler beim Löschen der Aufgabe');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Fehler beim Löschen der Aufgabe');
    });
  }
}

// Noten-Funktionen
function deleteNote(noteId) {
  if (confirm('Note wirklich löschen?')) {
    fetch(`/delete_note/${noteId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else {
        alert('Fehler beim Löschen der Note');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Fehler beim Löschen der Note');
    });
  }
}

// Kalender-Funktionen
function initCalendar() {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;
  
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'de',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,listWeek'
    },
    buttonText: {
      today: 'Heute',
      month: 'Monat',
      week: 'Woche',
      list: 'Liste'
    },
    events: '/api/events',
    eventDisplay: 'block',
    dayMaxEvents: 3,
    moreLinkClick: 'popover',
    eventClick: function(info) {
      const event = info.event;
      
      // Erstelle Modal-Inhalt
      const modalContent = `
        <div class="modal fade" id="eventModal" tabindex="-1">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">${event.title}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                <p><strong>Fach:</strong> ${event.extendedProps.subject}</p>
                <p><strong>Datum:</strong> ${event.start.toLocaleDateString('de-DE')}</p>
                ${event.extendedProps.description ? `<p><strong>Beschreibung:</strong> ${event.extendedProps.description}</p>` : ''}
                ${event.extendedProps.file ? `<p><a href="/static/uploads/${event.extendedProps.file}" target="_blank" class="btn btn-sm btn-outline-primary">📎 Material öffnen</a></p>` : ''}
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
              </div>
            </div>
          </div>
        </div>
      `;
      
      // Entferne alte Modal falls vorhanden
      const existingModal = document.getElementById('eventModal');
      if (existingModal) {
        existingModal.remove();
      }
      
      // Füge Modal zum DOM hinzu
      document.body.insertAdjacentHTML('beforeend', modalContent);
      
      // Zeige Modal
      const modal = new bootstrap.Modal(document.getElementById('eventModal'));
      modal.show();
    },
    height: 'auto',
    aspectRatio: 1.8
  });
  
  calendar.render();
}

// Form-Verbesserungen
function setupFormEnhancements() {
  // Auto-submit forms on Enter (nur bei bestimmten Feldern)
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type !== 'file') {
      const form = e.target.closest('form');
      if (form) {
        form.submit();
      }
    }
  });
  
  // Automatisches Anpassen der Textarea-Höhe
  document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });
  });
}

// Initialisierung
document.addEventListener('DOMContentLoaded', function() {
  loadTheme();
  initCalendar();
  setupFormEnhancements();
});
