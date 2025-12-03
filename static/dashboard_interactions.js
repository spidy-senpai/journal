// ============================================
// DASHBOARD INTERACTIONS & TAB SYSTEM
// ============================================

let currentTab = 'entry';
let contentBlocks = [];
let mediaRecorder;
let audioChunks = [];
let blockCounter = 0;
let recordingInterval;
let recordingSeconds = 0;
let currentFont = 'Inter';
let currentFontSize = 16;
let currentFontColor = '#e5e5e5';
let currentTheme = 'dark';
let timeCapsuleDate = null;
let currentBackground = 'none';

function init() {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    setTimeout(() => addTextBlock(), 100);
    setupEventListeners();
    loadInitialData();
}

function setupEventListeners() {
    const addTextBtn = document.getElementById('addTextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const stopRecordBtn = document.getElementById('stopRecordBtn');
    if (addTextBtn) addTextBtn.addEventListener('click', addTextBlock);
    if (submitBtn) submitBtn.addEventListener('click', submitEntry);
    if (stopRecordBtn) stopRecordBtn.addEventListener('click', stopRecording);
    document.getElementById('imageInput')?.addEventListener('change', handleImageUpload);
    document.getElementById('videoInput')?.addEventListener('change', handleVideoUpload);
    document.getElementById('documentInput')?.addEventListener('change', handleDocumentUpload);
    document.getElementById('bgImageInput')?.addEventListener('change', handleBgImageUpload);
    document.addEventListener('input', (e) => {
        if (e.target.tagName === 'TEXTAREA' && e.target.closest('#tab-entry')) {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
            updateWordCount();
        }
        if (e.target.classList.contains('title-input')) updateWordCount();
    });
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) closeAllModals();
    });
    document.getElementById('todoInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTodo();
    });
}

async function loadInitialData() {
    await loadTodos();
    await loadGoals();
    await loadCanvas();
}

function updateDateTime() {
    const now = new Date();
    const dateEl = document.getElementById('currentDate');
    const timeEl = document.getElementById('currentTime');
    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// ============================================
// TAB SWITCHING
// ============================================

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) selectedTab.classList.add('active');
    const selectedButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedButton) selectedButton.classList.add('active');
    const titles = { 'entry': 'Journal Entry', 'canvas': 'Canvas', 'todos': 'To-Do List', 'goals': 'My Goals' };
    const titleEl = document.getElementById('pageTitle');
    if (titleEl) titleEl.textContent = titles[tabName] || 'Dashboard';
    currentTab = tabName;
    if (tabName === 'todos') loadTodos();
    else if (tabName === 'goals') loadGoals();
    else if (tabName === 'canvas') loadCanvas();
}

function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeModal = document.getElementById('themeModal');
    const closeModal = document.getElementById('closeThemeModal');
    const themeOptions = document.querySelectorAll('.theme-option');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            themeModal.classList.add('active');
        });
    }

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            themeModal.classList.remove('active');
        });
    }

    // Close modal on overlay click
    const modalOverlay = themeModal?.querySelector('.modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', () => {
            themeModal.classList.remove('active');
        });
    }

    // Theme option selection
    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const theme = option.getAttribute('data-theme');
            setTheme(theme);

            // Update active state
            themeOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');

            // Close modal after selection
            setTimeout(() => {
                themeModal.classList.remove('active');
            }, 300);
        });
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('journal-theme', theme);
    updateThemeIcon(theme);

    // Show toast notification
    showToast(`Theme changed to ${theme.charAt(0).toUpperCase() + theme.slice(1)}`);
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        const icons = {
            dark: '🌙',
            light: '☀️',
            sepia: '📜',
            ocean: '🌊',
            forest: '🌲'
        };
        themeIcon.textContent = icons[theme] || '🌙';
    }
}

// ============================================
// DATE AND TIME
// ============================================

function initializeDateTime() {
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        dateElement.textContent = now.toLocaleDateString('en-US', options);
    }

    // Update greeting based on time
    updateGreeting();
}

function updateGreeting() {
    const greetingElement = document.querySelector('.hero-greeting');
    if (greetingElement) {
        const hour = new Date().getHours();
        let greeting = 'Good Evening';

        if (hour < 12) {
            greeting = 'Good Morning';
        } else if (hour < 18) {
            greeting = 'Good Afternoon';
        }

        greetingElement.textContent = `${greeting}, User! ✨`;
    }
}

// ============================================
// MOOD CALENDAR
// ============================================

function initializeMoodCalendar() {
    const moodCalendar = document.getElementById('moodCalendar');
    if (!moodCalendar) return;

    // Generate mood data for the current month
    const moodData = generateMoodData();

    // Clear existing content
    moodCalendar.innerHTML = '';

    // Add day labels
    const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayLabels.forEach(day => {
        const dayLabel = document.createElement('div');
        dayLabel.className = 'mood-day-label';
        dayLabel.textContent = day;
        dayLabel.style.cssText = 'text-align: center; color: var(--text-tertiary); font-size: var(--text-xs); padding: var(--space-sm);';
        moodCalendar.appendChild(dayLabel);
    });

    // Get current month info
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // Add empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'mood-day';
        emptyDay.style.opacity = '0.3';
        moodCalendar.appendChild(emptyDay);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'mood-day';

        // Assign random mood for demo
        const mood = moodData[day - 1];
        if (mood) {
            dayElement.classList.add(mood.type);
            dayElement.textContent = mood.emoji;
            dayElement.title = `Day ${day}: ${mood.type}`;
        } else {
            dayElement.textContent = day;
        }

        // Add click handler
        dayElement.addEventListener('click', () => {
            showMoodDetails(day, mood);
        });

        moodCalendar.appendChild(dayElement);
    }
}

function generateMoodData() {
    const moods = [
        { type: 'amazing', emoji: '😊' },
        { type: 'good', emoji: '🙂' },
        { type: 'okay', emoji: '😐' },
        { type: 'bad', emoji: '😔' },
        { type: 'terrible', emoji: '😢' }
    ];

    const data = [];
    const now = new Date();
    const today = now.getDate();

    for (let i = 0; i < today; i++) {
        // Generate random mood for past days
        const randomMood = moods[Math.floor(Math.random() * moods.length)];
        data.push(randomMood);
    }

    return data;
}

function showMoodDetails(day, mood) {
    if (mood) {
        showToast(`Day ${day}: Feeling ${mood.type} ${mood.emoji}`);
    }
}

// ============================================
// MOOD CHART
// ============================================

function initializeMoodChart() {
    const chartCanvas = document.getElementById('moodChart');
    if (!chartCanvas || typeof Chart === 'undefined') return;

    const ctx = chartCanvas.getContext('2d');

    // Generate sample data
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const data = [4.2, 3.8, 4.5, 4.3];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Mood',
                data: data,
                borderColor: 'rgb(99, 102, 241)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: 'rgb(99, 102, 241)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    borderRadius: 8,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Set canvas height
    chartCanvas.style.height = '200px';
}

// ============================================
// FLOATING ACTION BUTTON
// ============================================

function initializeFAB() {
    const fab = document.getElementById('newEntryFab');
    if (fab) {
        fab.addEventListener('click', () => {
            // Navigate to new entry page or show modal
            showToast('Creating new entry...');
            // window.location.href = '/new-entry';
        });
    }
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const query = e.target.value.toLowerCase();
            if (query.length > 0) {
                performSearch(query);
            }
        }, 300));
    }
}

function performSearch(query) {
    console.log('Searching for:', query);
    // Implement search logic here
    // This would typically filter entries or make an API call
}

// ============================================
// ANIMATIONS
// ============================================

function initializeAnimations() {
    // Stagger animation for stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Scroll reveal animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach(el => {
        observer.observe(el);
    });
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, duration = 3000) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast toast-enter';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 100px;
        right: 30px;
        background: var(--bg-elevated);
        color: var(--text-primary);
        padding: 16px 24px;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--glass-border);
        backdrop-filter: blur(20px);
        z-index: 9999;
        font-size: var(--text-sm);
        font-weight: 500;
        max-width: 300px;
    `;

    document.body.appendChild(toast);

    // Remove toast after duration
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// RIPPLE EFFECT
// ============================================

document.addEventListener('click', (e) => {
    const button = e.target.closest('.btn, .btn-icon, .fab');
    if (!button) return;

    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
    `;

    ripple.className = 'ripple';

    if (!button.classList.contains('ripple-container')) {
        button.classList.add('ripple-container');
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
    }

    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
});

// ============================================
// ENTRY CARD INTERACTIONS
// ============================================

document.querySelectorAll('.entry-card').forEach(card => {
    card.addEventListener('click', (e) => {
        // Don't trigger if clicking on a button
        if (e.target.closest('.btn-icon')) return;

        // Navigate to entry detail
        showToast('Opening entry...');
        // window.location.href = '/entry/123';
    });
});

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Ctrl/Cmd + N for new entry
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const fab = document.getElementById('newEntryFab');
        if (fab) {
            fab.click();
        }
    }

    // Ctrl/Cmd + T for theme toggle
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.click();
        }
    }
});

// ============================================
// SMOOTH SCROLLING
// ============================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// PERFORMANCE MONITORING
// ============================================

if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
    });
}

// ============================================
// ENTRY TAB - TEXT BLOCKS
// ============================================

function addTextBlock(initialText = '') {
    const id = blockCounter++;
    contentBlocks.push({ id, type: 'text', text: initialText });
    renderBlocks();
    setTimeout(() => {
        const textarea = document.querySelector(`[data-block-id="${id}"] textarea`);
        if (textarea) {
            textarea.focus();
            if (initialText) {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
                updateWordCount();
            }
        }
    }, 100);
}

function removeBlock(id) {
    contentBlocks = contentBlocks.filter(block => block.id !== id);
    if (contentBlocks.length === 0) addTextBlock();
    else renderBlocks();
    updateWordCount();
    showNotification('Block removed');
}

function updateBlockText(id, text) {
    const block = contentBlocks.find(b => b.id === id);
    if (block) {
        block.text = text;
        updateWordCount();
    }
}

function updateBlockCaption(id, caption) {
    const block = contentBlocks.find(b => b.id === id);
    if (block) block.caption = caption;
}

function updateWordCount() {
    let totalWords = 0;
    const title = document.getElementById('entryTitle')?.value || '';
    totalWords += title.trim().split(/\s+/).filter(word => word.length > 0).length;
    contentBlocks.forEach(block => {
        if (block.type === 'text' && block.text) {
            totalWords += block.text.trim().split(/\s+/).filter(word => word.length > 0).length;
        }
    });
    const wcEl = document.getElementById('wordCount');
    if (wcEl) wcEl.textContent = totalWords;
}

function renderBlocks() {
    const container = document.getElementById('contentBlocks');
    if (!container) return;
    container.innerHTML = '';
    contentBlocks.forEach(block => {
        const blockEl = document.createElement('div');
        blockEl.className = 'content-block';
        blockEl.setAttribute('data-block-id', block.id);
        const wrapper = document.createElement('div');
        wrapper.className = 'block-wrapper';
        const actions = document.createElement('div');
        actions.className = 'block-actions';
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'block-action-btn delete';
        deleteBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`;
        deleteBtn.addEventListener('click', () => removeBlock(block.id));
        actions.appendChild(deleteBtn);
        wrapper.appendChild(actions);
        if (block.type === 'text') {
            const textDiv = document.createElement('div');
            textDiv.className = 'text-block';
            const textarea = document.createElement('textarea');
            textarea.placeholder = 'Start typing...';
            textarea.value = block.text || '';
            textarea.addEventListener('input', (e) => updateBlockText(block.id, e.target.value));
            textDiv.appendChild(textarea);
            wrapper.appendChild(textDiv);
            setTimeout(() => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            }, 0);
        }
        blockEl.appendChild(wrapper);
        container.appendChild(blockEl);
    });
}

// ============================================
// FILE UPLOADS
// ============================================

function handleImageUpload(event) { const file = event.target.files[0]; if (file) { addImageBlock(file); event.target.value = ''; } closeAttachmentModal(); }
function handleVideoUpload(event) { const file = event.target.files[0]; if (file) { addVideoBlock(file); event.target.value = ''; } closeAttachmentModal(); }
function handleDocumentUpload(event) { const file = event.target.files[0]; if (file) { addDocumentBlock(file); event.target.value = ''; } closeAttachmentModal(); }
function handleBgImageUpload(event) { const file = event.target.files[0]; if (file) { const reader = new FileReader(); reader.onload = (e) => { const bgElement = document.getElementById('entryBackground'); if (bgElement) bgElement.style.backgroundImage = `url(${e.target.result})`; currentBackground = e.target.result; showNotification('Background applied!'); }; reader.readAsDataURL(file); event.target.value = ''; } }
function addImageBlock(file) { const id = blockCounter++; const reader = new FileReader(); reader.onload = (e) => { contentBlocks.push({ id, type: 'image', url: e.target.result, fileName: file.name, caption: '' }); renderBlocks(); }; reader.readAsDataURL(file); }
function addVideoBlock(file) { const id = blockCounter++; const reader = new FileReader(); reader.onload = (e) => { contentBlocks.push({ id, type: 'video', url: e.target.result, fileName: file.name, caption: '' }); renderBlocks(); }; reader.readAsDataURL(file); }
function addDocumentBlock(file) { const id = blockCounter++; contentBlocks.push({ id, type: 'document', fileName: file.name, fileSize: formatFileSize(file.size), caption: '' }); renderBlocks(); }
function formatFileSize(bytes) { if (bytes === 0) return '0 Bytes'; const k = 1024; const sizes = ['Bytes', 'KB', 'MB', 'GB']; const i = Math.floor(Math.log(bytes) / Math.log(k)); return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]; }

// ============================================
// VOICE RECORDING
// ============================================

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        recordingSeconds = 0;
        mediaRecorder.addEventListener('dataavailable', event => audioChunks.push(event.data));
        mediaRecorder.addEventListener('stop', () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const id = blockCounter++;
            const reader = new FileReader();
            reader.onload = (e) => {
                contentBlocks.push({ id, type: 'voice', url: e.target.result, fileName: 'voice-note.webm', caption: '' });
                renderBlocks();
            };
            reader.readAsDataURL(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        });
        mediaRecorder.start();
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) indicator.classList.add('active');
        recordingInterval = setInterval(() => {
            recordingSeconds++;
            const minutes = Math.floor(recordingSeconds / 60);
            const seconds = recordingSeconds % 60;
            const timeEl = document.getElementById('recordingTime');
            if (timeEl) timeEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }, 1000);
        showNotification('Recording started', 'success');
    } catch (error) {
        showNotification('Could not access microphone', 'error');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        clearInterval(recordingInterval);
        const indicator = document.getElementById('recordingIndicator');
        if (indicator) indicator.classList.remove('active');
        recordingSeconds = 0;
        showNotification('Recording saved', 'success');
    }
}

// ============================================
// TO-DO LIST FUNCTIONS
// ============================================

function addTodo() {
    const input = document.getElementById('todoInput');
    if (!input || !input.value.trim()) return;
    const todoList = document.getElementById('todoList');
    if (!todoList) return;
    const todoItem = createTodoElement(input.value.trim(), false);
    todoList.appendChild(todoItem);
    input.value = '';
}

function createTodoElement(text, completed = false) {
    const div = document.createElement('div');
    div.className = 'todo-item' + (completed ? ' completed' : '');
    div.innerHTML = `<input type="checkbox" class="todo-checkbox" ${completed ? 'checked' : ''} onchange="toggleTodo(this)"><span class="todo-text">${escapeHtml(text)}</span><button class="todo-delete-btn" onclick="deleteTodo(this)" title="Delete"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>`;
    return div;
}

function toggleTodo(checkbox) {
    const todoItem = checkbox.closest('.todo-item');
    if (todoItem) todoItem.classList.toggle('completed', checkbox.checked);
}

function deleteTodo(button) {
    const todoItem = button.closest('.todo-item');
    if (todoItem) todoItem.remove();
}

function collectTodos() {
    const todos = [];
    document.querySelectorAll('.todo-item').forEach(item => {
        const text = item.querySelector('.todo-text')?.textContent || '';
        const completed = item.querySelector('.todo-checkbox')?.checked || false;
        todos.push({ text, completed });
    });
    return todos;
}

function renderTodos(todos) {
    const todoList = document.getElementById('todoList');
    if (!todoList) return;
    todoList.innerHTML = '';
    if (Array.isArray(todos)) {
        todos.forEach(todo => {
            const todoItem = createTodoElement(todo.text, todo.completed);
            todoList.appendChild(todoItem);
        });
    }
}

async function loadTodos() {
    try {
        const response = await fetch('/api/get-todos');
        const result = await response.json();
        if (result.success && result.data) {
            const todos = result.data.items || [];
            renderTodos(todos);
        }
    } catch (error) {
        console.error('Error loading todos:', error);
    }
}

async function saveTodos() {
    try {
        const todos = collectTodos();
        const response = await fetch('/api/save-todos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: todos })
        });
        const result = await response.json();
        if (result.success) showNotification('To-Do list saved!', 'success');
        else showNotification('Failed to save to-do list', 'error');
    } catch (error) {
        console.error('Error saving todos:', error);
        showNotification('Error saving to-do list', 'error');
    }
}

// ============================================
// GOALS FUNCTIONS
// ============================================

function addGoal() {
    const goalsContainer = document.getElementById('goalsContainer');
    if (!goalsContainer) return;
    const goalElement = createGoalElement('', '');
    goalsContainer.appendChild(goalElement);
}

function createGoalElement(title = '', description = '') {
    const div = document.createElement('div');
    div.className = 'goal-item';
    div.innerHTML = `<input type="text" class="goal-title" placeholder="Goal title..." value="${escapeHtml(title)}"><textarea class="goal-description" placeholder="Description..." rows="3">${escapeHtml(description)}</textarea><button class="goal-delete-btn" onclick="deleteGoal(this)" title="Delete"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>`;
    return div;
}

function deleteGoal(button) {
    const goalItem = button.closest('.goal-item');
    if (goalItem) goalItem.remove();
}

function collectGoals() {
    const goals = [];
    document.querySelectorAll('.goal-item').forEach(item => {
        const title = item.querySelector('.goal-title')?.value || '';
        const description = item.querySelector('.goal-description')?.value || '';
        if (title.trim()) goals.push({ title, description });
    });
    return goals;
}

function renderGoals(goals) {
    const goalsContainer = document.getElementById('goalsContainer');
    if (!goalsContainer) return;
    goalsContainer.innerHTML = '';
    if (Array.isArray(goals)) {
        goals.forEach(goal => {
            const goalElement = createGoalElement(goal.title, goal.description);
            goalsContainer.appendChild(goalElement);
        });
    }
}

async function loadGoals() {
    try {
        const response = await fetch('/api/get-goals');
        const result = await response.json();
        if (result.success && result.data) {
            const goals = result.data.items || [];
            renderGoals(goals);
        }
    } catch (error) {
        console.error('Error loading goals:', error);
    }
}

async function saveGoals() {
    try {
        const goals = collectGoals();
        const response = await fetch('/api/save-goals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: goals })
        });
        const result = await response.json();
        if (result.success) showNotification('Goals saved!', 'success');
        else showNotification('Failed to save goals', 'error');
    } catch (error) {
        console.error('Error saving goals:', error);
        showNotification('Error saving goals', 'error');
    }
}

// ============================================
// CANVAS FUNCTIONS
// ============================================

async function loadCanvas() {
    try {
        const response = await fetch('/api/get-canvas');
        const result = await response.json();
        if (result.success && result.data && result.data.elements) {
            renderCanvas(result.data.elements);
        }
    } catch (error) {
        console.error('Error loading canvas:', error);
    }
}

async function saveCanvas() {
    try {
        const elements = [];
        const response = await fetch('/api/save-canvas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ elements: elements })
        });
        const result = await response.json();
        if (result.success) showNotification('Canvas saved!', 'success');
        else showNotification('Failed to save canvas', 'error');
    } catch (error) {
        console.error('Error saving canvas:', error);
        showNotification('Error saving canvas', 'error');
    }
}

function renderCanvas(elements) {
    console.log('Canvas elements:', elements);
}

// ============================================
// ENTRY SUBMISSION
// ============================================

async function submitEntry() {
    const title = document.getElementById('entryTitle').value.trim();
    if (!title && contentBlocks.length === 0) {
        showNotification('Please add a title or content', 'error');
        return;
    }
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    try {
        const date = new Date().toISOString().split('T')[0];
        const entryData = {
            date: date,
            title: title,
            blocks: contentBlocks.map(block => ({
                type: block.type,
                text: block.text || '',
                caption: block.caption || ''
            }))
        };
        const response = await fetch('/api/save-entry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(entryData)
        });
        const result = await response.json();
        if (result.success) {
            showNotification('Entry saved successfully!', 'success');
            setTimeout(() => {
                resetEditor();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Save Entry';
            }, 1500);
        } else {
            throw new Error('Failed to save entry');
        }
    } catch (error) {
        console.error('Error saving entry:', error);
        showNotification('Failed to save entry', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Entry';
    }
}

function resetEditor() {
    document.getElementById('entryTitle').value = '';
    contentBlocks = [];
    blockCounter = 0;
    document.getElementById('contentBlocks').innerHTML = '';
    addTextBlock();
    updateWordCount();
    showNotification('New entry started');
}

// ============================================
// MODALS
// ============================================

function openAttachmentModal() { document.getElementById('attachmentModal').classList.add('active'); }
function closeAttachmentModal() { document.getElementById('attachmentModal').classList.remove('active'); }
function selectImage() { document.getElementById('imageInput').click(); }
function selectVideo() { document.getElementById('videoInput').click(); }
function selectDocument() { document.getElementById('documentInput').click(); }
function selectBgImage() { document.getElementById('bgImageInput').click(); }
function openFontCustomizer() { document.getElementById('fontModal').classList.add('active'); }
function closeFontModal() { document.getElementById('fontModal').classList.remove('active'); }
function changeFont(fontName) {
    currentFont = fontName;
    document.documentElement.style.setProperty('--editor-font', fontName);
    document.querySelectorAll('.font-option').forEach(opt => {
        opt.classList.remove('active');
        if (opt.dataset.font === fontName) opt.classList.add('active');
    });
    showNotification(`Font changed to ${fontName}`);
}
function openThemeSelector() { document.getElementById('themeModal').classList.add('active'); }
function closeThemeModal() { document.getElementById('themeModal').classList.remove('active'); }
function changeTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-option').forEach(opt => {
        opt.classList.remove('active');
        if (opt.dataset.theme === theme) opt.classList.add('active');
    });
    showNotification(`Theme changed to ${theme}`);
}
function openBackgroundSelector() { document.getElementById('backgroundModal').classList.add('active'); }
function closeBackgroundModal() { document.getElementById('backgroundModal').classList.remove('active'); }
function setBackground(bg) { if (bg === 'none') { const bgElement = document.getElementById('entryBackground'); if (bgElement) bgElement.style.backgroundImage = 'none'; showNotification('Background removed'); } closeBackgroundModal(); }
function openTimeCapsule() {
    document.getElementById('timeCapsuleModal').classList.add('active');
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('capsuleDate').min = today;
    if (timeCapsuleDate) document.getElementById('capsuleDate').value = timeCapsuleDate;
}
function closeTimeCapsuleModal() { document.getElementById('timeCapsuleModal').classList.remove('active'); }
function saveTimeCapsule() {
    const date = document.getElementById('capsuleDate').value;
    if (date) {
        timeCapsuleDate = date;
        const formattedDate = new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        showNotification(`Time capsule set for ${formattedDate}`);
        closeTimeCapsuleModal();
    } else {
        showNotification('Please select a date', 'error');
    }
}
function closeAllModals() {
    closeAttachmentModal();
    closeFontModal();
    closeTimeCapsuleModal();
    closeThemeModal();
    closeBackgroundModal();
}

// ============================================
// UI UTILITIES
// ============================================

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    if (sidebar) sidebar.classList.toggle('collapsed');
    if (mainContent) mainContent.classList.toggle('expanded');
}

function showNotification(message, type = 'success') {
    const notif = document.getElementById('notification');
    if (!notif) return;
    notif.textContent = message;
    notif.className = `notification ${type} show`;
    setTimeout(() => notif.classList.remove('show'), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// INITIALIZATION ON LOAD
// ============================================

window.addEventListener('DOMContentLoaded', init);
console.log('✨ Dashboard initialized successfully!');
