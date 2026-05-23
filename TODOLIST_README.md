# TODO List Application with Local Storage

## Overview

A fully-featured todo list application built with Kivy and Python that stores all data locally using JSON files. Perfect for managing tasks with priorities, categories, and due dates.

## Features

### ✨ Core Features
- **Create Todos** - Add new tasks with title, description, priority, and due date
- **Edit Todos** - Modify existing todos anytime
- **Delete Todos** - Remove individual todos or all completed ones
- **Mark Complete** - Check off completed tasks
- **Local Storage** - All data saved in JSON format (todos.json)

### 🎯 Organization
- **Categories** - Organize todos by custom categories
- **Priorities** - Set tasks as Low, Medium, or High priority
- **Due Dates** - Add optional due dates to tasks
- **Filtering** - View All, Pending, or Completed todos
- **Sorting** - Sort by date or priority
- **Search** - Search todos by title or description

### 📊 Statistics & Analytics
- View overall statistics (total, completed, pending)
- Visual charts (pie chart for completion, bar chart for priorities)
- Completion rate percentage
- Category and priority breakdown

### 💾 Data Persistence
- Automatic JSON-based local storage
- No internet required
- Fast data access
- Easy to backup and share

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Kivy garden (for matplotlib backend)
python -m kivy.garden install matplotlib
```

## Usage

### Run the Application

```bash
python todolist_app.py
```

### Using the App

1. **Home Screen** - View all your todos with filters and sorting
2. **Add Todo** - Click "➕ Add Todo" to create a new task
3. **Edit Todo** - Click the ✏️ button on any todo to edit
4. **Delete Todo** - Click the 🗑️ button to remove a todo
5. **Mark Complete** - Check the checkbox to mark as done
6. **View Stats** - Click "📊 Stats" to see analytics
7. **Clear Completed** - Remove all finished tasks at once

## File Structure

```
├── todolist_app.py          # Main Kivy application
├── storage.py               # Local storage and todo management
├── todos.json               # Auto-generated data file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Storage.py API

### LocalStorage Class

```python
from storage import LocalStorage, Todo

# Initialize storage
storage = LocalStorage()

# Add a todo
todo = Todo(
    title="Buy groceries",
    description="Milk, eggs, bread",
    priority="medium",
    due_date="2026-05-25",
    category="Shopping"
)
storage.add_todo(todo)

# Get todos
all_todos = storage.get_all_todos()
pending_todos = storage.get_pending_todos()
completed_todos = storage.get_completed_todos()

# Filter by category
groceries = storage.get_todos_by_category("Shopping")

# Filter by priority
high_priority = storage.get_todos_by_priority("high")

# Search
results = storage.search_todos("buy")

# Update a todo
storage.update_todo(todo_id, title="New title", priority="high")

# Toggle completion
storage.toggle_todo(todo_id)

# Delete
storage.delete_todo(todo_id)

# Get statistics
stats = storage.get_stats()
# Returns: {
#     'total': 10,
#     'completed': 3,
#     'pending': 7,
#     'high_priority': 2,
#     'categories': 3
# }

# Get all categories
categories = storage.get_categories()

# Clear all completed todos
count_deleted = storage.clear_completed()
```

## Data Format

### todos.json Structure

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "medium",
    "due_date": "2026-05-25",
    "category": "Shopping",
    "completed": false,
    "created_at": "2026-05-23T14:30:00.000000",
    "updated_at": "2026-05-23T14:30:00.000000"
  }
]
```

## Features Breakdown

### Home Screen
- List of all todos (filtered and sorted)
- Quick statistics in header
- Filter by status (All/Pending/Completed)
- Filter by category
- Sort by date or priority
- Color-coded priority indicators
- Quick actions (edit, delete, mark complete)

### Add/Edit Screen
- Title input (required)
- Description input
- Priority selector
- Category selector
- Due date input
- Save and Cancel buttons

### Statistics Screen
- Key metrics display
- Pie chart (completion status)
- Bar chart (todos by priority)
- Completion rate percentage

## Keyboard Shortcuts

*Coming in future versions*

## Data Backup

### Manual Backup
```bash
cp todos.json todos_backup_$(date +%Y%m%d_%H%M%S).json
```

### Restore from Backup
```bash
cp todos_backup_TIMESTAMP.json todos.json
```

## Customization

### Change Storage File
```python
storage = LocalStorage("my_todos.json")
```

### Add Custom Categories
Edit or add categories directly in the todo creation form.

### Modify Priority Levels
Edit the `priority_spinner.values` in `todolist_app.py`

## Performance

- ✅ Handles 1000+ todos efficiently
- ✅ Fast JSON serialization
- ✅ Minimal memory footprint
- ✅ Instant data persistence

## Known Limitations

- Single-file storage (no database)
- No cloud sync
- No user accounts
- No multi-device sync
- Local file size limit depends on system

## Future Enhancements

- [ ] Cloud sync option
- [ ] Recurring todos
- [ ] Todo reminders
- [ ] Tags system
- [ ] Dark mode
- [ ] Export to CSV/PDF
- [ ] Undo/Redo functionality
- [ ] Keyboard shortcuts
- [ ] Multi-language support
- [ ] Voice input

## Troubleshooting

### todos.json corrupted
```bash
# Delete and restart to create a fresh file
rm todos.json
python todolist_app.py
```

### Chart not displaying
```bash
python -m kivy.garden install matplotlib
```

### App crashes on startup
```bash
# Check dependencies
pip install --upgrade -r requirements.txt
```

## License

MIT License - Feel free to use and modify

## Support

For issues or suggestions, please open an issue on GitHub.

---

**Made with ❤️ using Kivy & Python**
