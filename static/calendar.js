// Kalender-spezifisches JavaScript
class SchulBuddyCalendar {
    constructor() {
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        this.events = [];
        this.filteredEvents = [];
        this.currentSubjectFilter = '';
        this.currentTypeFilter = '';
        
        // Monatsnamen
        this.monthNames = [
            'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
            'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
        ];
        
        this.init();
    }
    
    // Initialisierung
    async init() {
        console.log('🔄 Kalender wird initialisiert...');
        
        await this.loadEvents();
        this.generateCalendar();
        this.debugCalendar();
        this.setupEventListeners();
        
        console.log('✅ Kalender erfolgreich geladen!');
    }
    
    // Lade Events von der API
    async loadEvents() {
        try {
            const response = await fetch('/api/events');
            this.events = await response.json();
            this.filteredEvents = [...this.events]; // Kopie für Filterung
            console.log('📅 Events geladen:', this.events);
        } catch (error) {
            console.error('❌ Fehler beim Laden der Events:', error);
        }
    }
    
    // Filtere Events basierend auf aktuellen Filtern
    filterEvents() {
        this.filteredEvents = this.events.filter(event => {
            // Fach-Filter
            if (this.currentSubjectFilter && event.subject !== this.currentSubjectFilter) {
                return false;
            }
            
            // Typ-Filter
            if (this.currentTypeFilter && event.type !== this.currentTypeFilter) {
                return false;
            }
            
            return true;
        });
        
        console.log('🔍 Events nach Filterung:', this.filteredEvents);
    }
    
    // Wende Filter an
    applyFilters() {
        this.currentSubjectFilter = document.getElementById('subject-filter').value;
        this.currentTypeFilter = document.getElementById('type-filter').value;
        
        this.filterEvents();
        this.generateCalendar();
        this.updateFilterStats();
        
        console.log(`📊 Zeige ${this.filteredEvents.length} von ${this.events.length} Events`);
    }
    
    // Aktualisiere Filterstatistiken
    updateFilterStats() {
        const totalEvents = this.events.length;
        const filteredCount = this.filteredEvents.length;
        const statsElement = document.getElementById('filter-stats');
        
        if (this.currentSubjectFilter || this.currentTypeFilter) {
            let filterText = 'Filter: ';
            if (this.currentSubjectFilter) filterText += `Fach: ${this.currentSubjectFilter} `;
            if (this.currentTypeFilter) {
                const typeNames = {
                    'homework': 'Hausaufgaben',
                    'exam': 'Klassenarbeiten',
                    'project': 'Projekte',
                    'grade': 'Noten'
                };
                filterText += `Typ: ${typeNames[this.currentTypeFilter] || this.currentTypeFilter}`;
            }
            statsElement.textContent = `${filterText} • Zeige ${filteredCount} von ${totalEvents} Events`;
        } else {
            statsElement.textContent = `Zeige alle ${totalEvents} Events`;
        }
    }
    
    // Lösche alle Filter
    clearFilters() {
        document.getElementById('subject-filter').value = '';
        document.getElementById('type-filter').value = '';
        
        this.currentSubjectFilter = '';
        this.currentTypeFilter = '';
        
        this.filteredEvents = [...this.events];
        this.generateCalendar();
        
        const statsElement = document.getElementById('filter-stats');
        statsElement.textContent = `Zeige alle ${this.events.length} Events`;
        
        console.log('🔄 Filter zurückgesetzt');
    }
    
    // Generiere Kalender für aktuellen Monat
    generateCalendar() {
        const calendarTitle = document.getElementById('calendar-title');
        calendarTitle.textContent = `${this.monthNames[this.currentMonth]} ${this.currentYear}`;
        
        const calendarGrid = document.getElementById('calendar-grid');
        
        // Entferne alle Tage (behalte nur die Wochentag-Header)
        const dayElements = calendarGrid.querySelectorAll('.calendar-day');
        dayElements.forEach(el => el.remove());
        
        // Hole Informationen über den aktuellen Monat
        const firstDay = new Date(this.currentYear, this.currentMonth, 1);
        const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
        const today = new Date();
        
        // Berechne den ersten Montag der Kalenderansicht
        const startDate = new Date(firstDay);
        const dayOfWeek = (firstDay.getDay() + 6) % 7; // 0=Montag, 1=Dienstag, ..., 6=Sonntag
        startDate.setDate(firstDay.getDate() - dayOfWeek);
        
        // Berechne den letzten Sonntag der Kalenderansicht
        const endDate = new Date(lastDay);
        const lastDayOfWeek = (lastDay.getDay() + 6) % 7;
        endDate.setDate(lastDay.getDate() + (6 - lastDayOfWeek));
        
        // Debug-Ausgabe
        console.log(`📅 Kalender für ${this.monthNames[this.currentMonth]} ${this.currentYear}`);
        console.log(`🔍 Erster Tag: ${firstDay.toDateString()}, Wochentag: ${dayOfWeek}`);
        console.log(`🔍 Kalender von ${startDate.toDateString()} bis ${endDate.toDateString()}`);
        
        // Generiere alle Tage für die Kalenderansicht
        let currentDate = new Date(startDate);
        let dayCount = 0;
        
        while (currentDate <= endDate && dayCount < 42) { // max 6 Wochen
            const dayElement = this.createDayElement(currentDate, today);
            calendarGrid.appendChild(dayElement);
            
            // Gehe zum nächsten Tag
            currentDate.setDate(currentDate.getDate() + 1);
            dayCount++;
        }
        
        console.log(`📊 Kalender generiert: ${dayCount} Tage, ${this.filteredEvents.length} Events`);
    }
    
    // Erstelle ein Tag-Element
    createDayElement(currentDate, today) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        
        const dayNumber = currentDate.getDate();
        const isCurrentMonth = currentDate.getMonth() === this.currentMonth;
        const isToday = (
            currentDate.getFullYear() === today.getFullYear() &&
            currentDate.getMonth() === today.getMonth() &&
            currentDate.getDate() === today.getDate()
        );
        
        // Styling basierend auf Monat und Tag
        if (!isCurrentMonth) {
            dayElement.classList.add('other-month');
        }
        if (isToday) {
            dayElement.classList.add('today');
        }
        
        // Tag-Nummer hinzufügen
        dayElement.innerHTML = `<div class="calendar-day-header">${dayNumber}</div>`;
        
        // Events für diesen Tag hinzufügen
        this.addEventsToDay(dayElement, currentDate);
        
        return dayElement;
    }
    
    // Füge Events zu einem Tag hinzu
    addEventsToDay(dayElement, date) {
        const dateString = date.toISOString().split('T')[0];
        const dayEvents = this.filteredEvents.filter(event => event.start === dateString);
        
        dayEvents.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = 'calendar-event';
            
            // Setze Fach-Farbe als Hintergrund
            if (event.color) {
                eventElement.style.backgroundColor = event.color;
                // Bestimme Textfarbe basierend auf Hintergrundfarbe
                const textColor = this.getContrastColor(event.color);
                eventElement.style.color = textColor;
            }
            
            // Füge Icon basierend auf Event-Typ hinzu
            let icon = '';
            if (event.type === 'exam') {
                icon = '📝 ';
            } else if (event.type === 'project') {
                icon = '🎯 ';
            } else if (event.type === 'homework') {
                icon = '📚 ';
            } else if (event.type === 'grade') {
                icon = '🏫 ';
            }
            
            eventElement.textContent = icon + event.title;
            eventElement.title = `${event.title} (${event.subject})`;
            eventElement.onclick = () => this.showEventDetails(event);
            
            // Keyboard-Zugänglichkeit
            eventElement.setAttribute('tabindex', '0');
            eventElement.setAttribute('role', 'button');
            eventElement.onkeydown = (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.showEventDetails(event);
                }
            };
            
            dayElement.appendChild(eventElement);
        });
    }
    
    // Bestimme Kontrastfarbe für Text
    getContrastColor(hexColor) {
        // Entferne # falls vorhanden
        hexColor = hexColor.replace('#', '');
        
        // Konvertiere zu RGB
        const r = parseInt(hexColor.substring(0, 2), 16);
        const g = parseInt(hexColor.substring(2, 4), 16);
        const b = parseInt(hexColor.substring(4, 6), 16);
        
        // Berechne Helligkeit
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        
        // Rückgabe weiß für dunkle Farben, schwarz für helle
        return brightness > 125 ? '#000000' : '#ffffff';
    }
    
    // Zeige Event-Details
    showEventDetails(event) {
        // Prüfe, ob es sich um eine Task oder Grade handelt
        if (event.id.startsWith('task_')) {
            // Extrahiere numerische ID von task_X
            const taskId = event.id.replace('task_', '');
            window.location.href = `/task_detail/${taskId}`;
        } else if (event.id.startsWith('grade_')) {
            // Für Noten zeige eine Info-Nachricht
            alert(`📊 Note: ${event.title}\n\nDiese Note wurde bereits bewertet und kann nicht bearbeitet werden.`);
        } else {
            // Fallback für andere Event-Typen
            console.warn('Unbekannter Event-Typ:', event.id);
            alert(`ℹ️ ${event.title}\n\nDetails: ${event.description || 'Keine weitere Beschreibung verfügbar.'}`);
        }
    }
    
    // Debug: Zeige Kalender-Informationen
    debugCalendar() {
        const firstDay = new Date(this.currentYear, this.currentMonth, 1);
        const weekdays = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
        const shortWeekdays = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
        
        console.log(`🗓️ Debug: ${this.monthNames[this.currentMonth]} ${this.currentYear}`);
        console.log(`📅 Erster Tag des Monats: ${weekdays[firstDay.getDay()]} (${firstDay.getDate()}.${firstDay.getMonth() + 1}.${firstDay.getFullYear()})`);
        console.log(`🔢 JavaScript getDay(): ${firstDay.getDay()} (0=Sonntag, 1=Montag, ..., 6=Samstag)`);
        console.log(`🔄 Umgerechnet für Montag=0: ${(firstDay.getDay() + 6) % 7} (0=Montag, 1=Dienstag, ..., 6=Sonntag)`);
        console.log(`📊 Anzahl Events: ${this.events.length}, Gefiltert: ${this.filteredEvents.length}`);
        
        // Zeige nächste 7 Tage zur Kontrolle
        console.log('📋 Nächste 7 Tage:');
        for (let i = 0; i < 7; i++) {
            const testDate = new Date(this.currentYear, this.currentMonth, 1 + i);
            const jsDay = testDate.getDay();
            const ourDay = (jsDay + 6) % 7;
            console.log(`  ${testDate.getDate()}.${testDate.getMonth() + 1}: ${shortWeekdays[jsDay]} (JS: ${jsDay}, Unser: ${ourDay})`);
        }
    }
    
    // Navigation
    previousMonth() {
        this.currentMonth--;
        if (this.currentMonth < 0) {
            this.currentMonth = 11;
            this.currentYear--;
        }
        this.generateCalendar();
    }
    
    nextMonth() {
        this.currentMonth++;
        if (this.currentMonth > 11) {
            this.currentMonth = 0;
            this.currentYear++;
        }
        this.generateCalendar();
    }
    
    goToToday() {
        const today = new Date();
        this.currentMonth = today.getMonth();
        this.currentYear = today.getFullYear();
        this.generateCalendar();
    }
    
    // Setup Event Listeners
    setupEventListeners() {
        // Filter-Änderungen
        document.getElementById('subject-filter').addEventListener('change', () => this.applyFilters());
        document.getElementById('type-filter').addEventListener('change', () => this.applyFilters());
        
        // Navigation
        document.querySelector('button[onclick="previousMonth()"]').onclick = () => this.previousMonth();
        document.querySelector('button[onclick="nextMonth()"]').onclick = () => this.nextMonth();
        document.querySelector('button[onclick="goToToday()"]').onclick = () => this.goToToday();
        
        // Filter-Buttons
        document.querySelector('button[onclick="applyFilters()"]').onclick = () => this.applyFilters();
        document.querySelector('button[onclick="clearFilters()"]').onclick = () => this.clearFilters();
        
        // Keyboard-Navigation
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        this.previousMonth();
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        this.nextMonth();
                        break;
                    case 'Home':
                        e.preventDefault();
                        this.goToToday();
                        break;
                }
            }
        });
    }
    
    // Refresh-Funktion für externe Aufrufe
    async refresh() {
        await this.loadEvents();
        this.generateCalendar();
        this.updateFilterStats();
    }
}

// Globale Funktionen für Rückwärtskompatibilität (werden durch Event-Listener ersetzt)
let calendar;

function previousMonth() {
    if (calendar) calendar.previousMonth();
}

function nextMonth() {
    if (calendar) calendar.nextMonth();
}

function goToToday() {
    if (calendar) calendar.goToToday();
}

function applyFilters() {
    if (calendar) calendar.applyFilters();
}

function clearFilters() {
    if (calendar) calendar.clearFilters();
}

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', function() {
    calendar = new SchulBuddyCalendar();
});

// Export für Module (falls später benötigt)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SchulBuddyCalendar;
}
