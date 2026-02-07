from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Calendar & Event Manager")

class Event(BaseModel):
    id: Optional[int] = None
    title: str
    date: str
    time: Optional[str] = ""
    priority: str
    description: Optional[str] = ""
    created: Optional[str] = None

events_db: List[dict] = []
event_counter = 1

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the calendar HTML page"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendar & Event Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
        }

        .calendar-section, .events-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #667eea;
            font-size: 28px;
        }

        .month-nav {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }

        .month-nav button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }

        .month-nav button:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }

        .month-nav h2 {
            color: #333;
            min-width: 200px;
            text-align: center;
        }

        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
        }

        .day-header {
            text-align: center;
            font-weight: bold;
            color: #667eea;
            padding: 10px;
            font-size: 14px;
        }

        .day {
            aspect-ratio: 1;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            padding: 8px;
        }

        .day:hover {
            border-color: #667eea;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }

        .day.other-month {
            color: #ccc;
        }

        .day.today {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }

        .day.selected {
            border-color: #764ba2;
            background: #f8f8ff;
        }

        .day.has-events {
            background: #fff3cd;
        }

        .day.has-events::after {
            content: '';
            position: absolute;
            bottom: 5px;
            width: 6px;
            height: 6px;
            background: #667eea;
            border-radius: 50%;
        }

        .event-form {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .events-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .event-item {
            background: white;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }

        .event-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .event-item h3 {
            color: #333;
            margin-bottom: 5px;
            font-size: 16px;
        }

        .event-item p {
            color: #666;
            font-size: 14px;
            margin: 3px 0;
        }

        .event-item .event-date {
            color: #667eea;
            font-weight: 500;
        }

        .delete-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 8px;
            transition: all 0.3s;
        }

        .delete-btn:hover {
            background: #ee5a6f;
        }

        .priority-high {
            border-left-color: #ff4757;
        }

        .priority-medium {
            border-left-color: #ffa502;
        }

        .priority-low {
            border-left-color: #26de81;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }

        .stat-card h4 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .stat-card p {
            font-size: 12px;
            opacity: 0.9;
        }

        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 1fr;
            }
        }

        .export-btn {
            background: #26de81;
            margin-top: 10px;
        }

        .export-btn:hover {
            background: #20bf6b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="calendar-section">
            <div class="header">
                <h1>📅 Calendar</h1>
            </div>

            <div class="month-nav">
                <button onclick="previousMonth()">← Previous</button>
                <h2 id="currentMonth"></h2>
                <button onclick="nextMonth()">Next →</button>
            </div>

            <div class="calendar" id="calendar"></div>
        </div>

        <div class="events-section">
            <div class="header">
                <h1>Events</h1>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <h4 id="totalEvents">0</h4>
                    <p>Total Events</p>
                </div>
                <div class="stat-card">
                    <h4 id="todayEvents">0</h4>
                    <p>Today</p>
                </div>
                <div class="stat-card">
                    <h4 id="upcomingEvents">0</h4>
                    <p>Upcoming</p>
                </div>
            </div>

            <div class="event-form">
                <h3 style="margin-bottom: 15px; color: #667eea;">Add New Event</h3>
                <div class="form-group">
                    <label>Event Title</label>
                    <input type="text" id="eventTitle" placeholder="Enter event title">
                </div>
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="eventDate">
                </div>
                <div class="form-group">
                    <label>Time</label>
                    <input type="time" id="eventTime">
                </div>
                <div class="form-group">
                    <label>Priority</label>
                    <select id="eventPriority">
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="eventDescription" rows="3" placeholder="Event details..."></textarea>
                </div>
                <button class="btn" onclick="addEvent()">Add Event</button>
                <button class="btn export-btn" onclick="exportEvents()">Export Events (JSON)</button>
            </div>

            <h3 style="margin: 20px 0 10px; color: #667eea;">Upcoming Events</h3>
            <div class="events-list" id="eventsList"></div>
        </div>
    </div>

    <script>
        // State management
        let currentDate = new Date();
        let selectedDate = new Date();
        let events = [];

        const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        // Initialize
        async function init() {
            setDefaultDate();
            await loadEvents();
            renderCalendar();
            renderEvents();
            updateStats();
        }

        function setDefaultDate() {
            const today = new Date();
            const dateStr = today.toISOString().split('T')[0];
            document.getElementById('eventDate').value = dateStr;
        }

        // API Functions
        async function loadEvents() {
            try {
                const response = await fetch('/api/events');
                events = await response.json();
            } catch (error) {
                console.error('Error loading events:', error);
            }
        }

        async function addEvent() {
            const title = document.getElementById('eventTitle').value;
            const date = document.getElementById('eventDate').value;
            const time = document.getElementById('eventTime').value;
            const priority = document.getElementById('eventPriority').value;
            const description = document.getElementById('eventDescription').value;

            if (!title || !date) {
                alert('Please enter a title and date');
                return;
            }

            const event = {
                title,
                date,
                time,
                priority,
                description,
                created: new Date().toISOString()
            };

            try {
                const response = await fetch('/api/events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(event)
                });

                if (response.ok) {
                    await loadEvents();
                    renderCalendar();
                    renderEvents();
                    updateStats();

                    // Clear form
                    document.getElementById('eventTitle').value = '';
                    document.getElementById('eventTime').value = '';
                    document.getElementById('eventDescription').value = '';
                    setDefaultDate();
                }
            } catch (error) {
                console.error('Error adding event:', error);
            }
        }

        async function deleteEvent(id) {
            if (confirm('Are you sure you want to delete this event?')) {
                try {
                    const response = await fetch(`/api/events/${id}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        await loadEvents();
                        renderCalendar();
                        renderEvents();
                        updateStats();
                    }
                } catch (error) {
                    console.error('Error deleting event:', error);
                }
            }
        }

        function renderCalendar() {
            const calendar = document.getElementById('calendar');
            calendar.innerHTML = '';

            // Add day headers
            dayHeaders.forEach(day => {
                const header = document.createElement('div');
                header.className = 'day-header';
                header.textContent = day;
                calendar.appendChild(header);
            });

            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            
            document.getElementById('currentMonth').textContent = 
                currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

            const firstDay = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const daysInPrevMonth = new Date(year, month, 0).getDate();

            // Previous month days
            for (let i = firstDay - 1; i >= 0; i--) {
                const day = createDayElement(daysInPrevMonth - i, true, year, month - 1);
                calendar.appendChild(day);
            }

            // Current month days
            for (let i = 1; i <= daysInMonth; i++) {
                const day = createDayElement(i, false, year, month);
                calendar.appendChild(day);
            }

            // Next month days
            const remainingDays = 42 - (firstDay + daysInMonth);
            for (let i = 1; i <= remainingDays; i++) {
                const day = createDayElement(i, true, year, month + 1);
                calendar.appendChild(day);
            }
        }

        function createDayElement(dayNum, isOtherMonth, year, month) {
            const day = document.createElement('div');
            day.className = 'day';
            day.textContent = dayNum;

            if (isOtherMonth) {
                day.classList.add('other-month');
            }

            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
            const today = new Date();
            const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

            if (dateStr === todayStr && !isOtherMonth) {
                day.classList.add('today');
            }

            if (hasEvents(dateStr)) {
                day.classList.add('has-events');
            }

            day.onclick = () => selectDate(dateStr);

            return day;
        }

        function hasEvents(dateStr) {
            return events.some(event => event.date === dateStr);
        }

        function selectDate(dateStr) {
            document.getElementById('eventDate').value = dateStr;
            selectedDate = new Date(dateStr);
            renderCalendar();
        }

        function previousMonth() {
            currentDate.setMonth(currentDate.getMonth() - 1);
            renderCalendar();
        }

        function nextMonth() {
            currentDate.setMonth(currentDate.getMonth() + 1);
            renderCalendar();
        }

        function renderEvents() {
            const eventsList = document.getElementById('eventsList');
            eventsList.innerHTML = '';

            const sortedEvents = [...events].sort((a, b) => {
                const dateA = new Date(a.date + ' ' + (a.time || '00:00'));
                const dateB = new Date(b.date + ' ' + (b.time || '00:00'));
                return dateA - dateB;
            });

            sortedEvents.forEach(event => {
                const eventDiv = document.createElement('div');
                eventDiv.className = `event-item priority-${event.priority}`;
                
                const eventDate = new Date(event.date);
                const formattedDate = eventDate.toLocaleDateString('en-US', { 
                    weekday: 'short', 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric' 
                });

                eventDiv.innerHTML = `
                    <h3>${event.title}</h3>
                    <p class="event-date">📅 ${formattedDate} ${event.time ? '• ⏰ ' + event.time : ''}</p>
                    ${event.description ? `<p>${event.description}</p>` : ''}
                    <p style="font-size: 12px; color: #999;">Priority: ${event.priority.toUpperCase()}</p>
                    <button class="delete-btn" onclick="deleteEvent(${event.id})">Delete</button>
                `;

                eventsList.appendChild(eventDiv);
            });

            if (events.length === 0) {
                eventsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No events scheduled</p>';
            }
        }

        function updateStats() {
            document.getElementById('totalEvents').textContent = events.length;

            const today = new Date().toISOString().split('T')[0];
            const todayCount = events.filter(e => e.date === today).length;
            document.getElementById('todayEvents').textContent = todayCount;

            const upcoming = events.filter(e => new Date(e.date) > new Date()).length;
            document.getElementById('upcomingEvents').textContent = upcoming;
        }

        async function exportEvents() {
            const dataStr = JSON.stringify(events, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `calendar-events-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            URL.revokeObjectURL(url);
        }

        // Initialize app
        init();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.get("/api/events")
async def get_events():
    """Get all events"""
    return events_db

@app.post("/api/events")
async def create_event(event: Event):
    """Create a new event"""
    global event_counter
    event_dict = event.model_dump()
    event_dict["id"] = event_counter
    event_counter += 1
    events_db.append(event_dict)
    return event_dict

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: int):
    """Delete an event"""
    global events_db
    event = next((e for e in events_db if e["id"] == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    events_db = [e for e in events_db if e["id"] != event_id]
    return {"message": "Event deleted", "id": event_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)