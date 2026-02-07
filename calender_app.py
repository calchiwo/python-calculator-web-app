from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import calendar
from datetime import datetime, timedelta
import json

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python Calendar App</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            h1 {
                text-align: center;
                color: white;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            
            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: white;
                padding: 20px 30px;
                border-radius: 15px 15px 0 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .month-year {
                font-size: 1.8em;
                font-weight: 600;
                color: #667eea;
            }
            
            .nav-buttons button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 0 5px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s;
            }
            
            .nav-buttons button:hover {
                background: #5568d3;
                transform: translateY(-2px);
            }
            
            .calendar-grid {
                background: white;
                padding: 30px;
                border-radius: 0 0 15px 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            
            .weekdays {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .weekday {
                text-align: center;
                font-weight: 600;
                color: #667eea;
                padding: 10px;
                font-size: 0.9em;
            }
            
            .days {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 10px;
            }
            
            .day {
                aspect-ratio: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 1.1em;
                position: relative;
            }
            
            .day:not(.empty):not(.other-month):hover {
                background: #f0f0f0;
                transform: scale(1.05);
            }
            
            .day.today {
                background: #667eea;
                color: white;
                font-weight: bold;
            }
            
            .day.selected {
                background: #764ba2;
                color: white;
                font-weight: bold;
            }
            
            .day.other-month {
                color: #ccc;
            }
            
            .day.has-event::after {
                content: '';
                position: absolute;
                bottom: 5px;
                width: 6px;
                height: 6px;
                background: #ff6b6b;
                border-radius: 50%;
            }
            
            .event-panel {
                background: white;
                margin-top: 30px;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            
            .event-panel h2 {
                color: #667eea;
                margin-bottom: 20px;
            }
            
            .event-form {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            .event-form input {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
            }
            
            .event-form button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s;
            }
            
            .event-form button:hover {
                background: #5568d3;
            }
            
            .event-list {
                list-style: none;
            }
            
            .event-item {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .event-item button {
                background: #ff6b6b;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 5px;
                cursor: pointer;
            }
            
            .event-item button:hover {
                background: #ee5a52;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📅 Python Calendar App</h1>
            
            <div class="calendar-header">
                <div class="month-year" id="monthYear"></div>
                <div class="nav-buttons">
                    <button onclick="previousMonth()">← Previous</button>
                    <button onclick="today()">Today</button>
                    <button onclick="nextMonth()">Next →</button>
                </div>
            </div>
            
            <div class="calendar-grid">
                <div class="weekdays">
                    <div class="weekday">Sun</div>
                    <div class="weekday">Mon</div>
                    <div class="weekday">Tue</div>
                    <div class="weekday">Wed</div>
                    <div class="weekday">Thu</div>
                    <div class="weekday">Fri</div>
                    <div class="weekday">Sat</div>
                </div>
                <div class="days" id="calendarDays"></div>
            </div>
            
            <div class="event-panel">
                <h2>Events for <span id="selectedDate"></span></h2>
                <div class="event-form">
                    <input type="text" id="eventInput" placeholder="Add an event..." />
                    <button onclick="addEvent()">Add Event</button>
                </div>
                <ul class="event-list" id="eventList"></ul>
            </div>
        </div>
        
        <script>
            let currentDate = new Date();
            let selectedDate = new Date();
            let events = JSON.parse(localStorage.getItem('calendarEvents') || '{}');
            
            function renderCalendar() {
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                document.getElementById('monthYear').textContent = 
                    currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
                
                const firstDay = new Date(year, month, 1).getDay();
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const daysInPrevMonth = new Date(year, month, 0).getDate();
                
                const calendarDays = document.getElementById('calendarDays');
                calendarDays.innerHTML = '';
                
                // Previous month days
                for (let i = firstDay - 1; i >= 0; i--) {
                    const day = daysInPrevMonth - i;
                    const div = createDayElement(day, 'other-month', year, month - 1);
                    calendarDays.appendChild(div);
                }
                
                // Current month days
                for (let day = 1; day <= daysInMonth; day++) {
                    const div = createDayElement(day, '', year, month);
                    
                    const today = new Date();
                    if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                        div.classList.add('today');
                    }
                    
                    if (day === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear()) {
                        div.classList.add('selected');
                    }
                    
                    calendarDays.appendChild(div);
                }
                
                // Next month days
                const totalCells = calendarDays.children.length;
                const remainingCells = 42 - totalCells;
                for (let day = 1; day <= remainingCells; day++) {
                    const div = createDayElement(day, 'other-month', year, month + 1);
                    calendarDays.appendChild(div);
                }
                
                updateEventPanel();
            }
            
            function createDayElement(day, className, year, month) {
                const div = document.createElement('div');
                div.className = 'day ' + className;
                div.textContent = day;
                
                const dateKey = `${year}-${month}-${day}`;
                if (events[dateKey] && events[dateKey].length > 0) {
                    div.classList.add('has-event');
                }
                
                div.onclick = () => {
                    selectedDate = new Date(year, month, day);
                    renderCalendar();
                };
                
                return div;
            }
            
            function previousMonth() {
                currentDate.setMonth(currentDate.getMonth() - 1);
                renderCalendar();
            }
            
            function nextMonth() {
                currentDate.setMonth(currentDate.getMonth() + 1);
                renderCalendar();
            }
            
            function today() {
                currentDate = new Date();
                selectedDate = new Date();
                renderCalendar();
            }
            
            function updateEventPanel() {
                const dateStr = selectedDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
                document.getElementById('selectedDate').textContent = dateStr;
                
                const dateKey = `${selectedDate.getFullYear()}-${selectedDate.getMonth()}-${selectedDate.getDate()}`;
                const dayEvents = events[dateKey] || [];
                
                const eventList = document.getElementById('eventList');
                eventList.innerHTML = '';
                
                dayEvents.forEach((event, index) => {
                    const li = document.createElement('li');
                    li.className = 'event-item';
                    li.innerHTML = `
                        <span>${event}</span>
                        <button onclick="deleteEvent(${index})">Delete</button>
                    `;
                    eventList.appendChild(li);
                });
            }
            
            function addEvent() {
                const input = document.getElementById('eventInput');
                const eventText = input.value.trim();
                
                if (eventText) {
                    const dateKey = `${selectedDate.getFullYear()}-${selectedDate.getMonth()}-${selectedDate.getDate()}`;
                    if (!events[dateKey]) {
                        events[dateKey] = [];
                    }
                    events[dateKey].push(eventText);
                    localStorage.setItem('calendarEvents', JSON.stringify(events));
                    input.value = '';
                    renderCalendar();
                }
            }
            
            function deleteEvent(index) {
                const dateKey = `${selectedDate.getFullYear()}-${selectedDate.getMonth()}-${selectedDate.getDate()}`;
                events[dateKey].splice(index, 1);
                if (events[dateKey].length === 0) {
                    delete events[dateKey];
                }
                localStorage.setItem('calendarEvents', JSON.stringify(events));
                renderCalendar();
            }
            
            document.getElementById('eventInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    addEvent();
                }
            });
            
            renderCalendar();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)