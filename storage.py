import json
import os
from datetime import datetime
from typing import List, Optional
import uuid

class Todo:
    """Represents a single todo item."""
    def __init__(self, title: str, description: str = "", priority: str = "medium", 
                 due_date: Optional[str] = None, category: str = "General", todo_id: Optional[str] = None):
        self.id = todo_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority  # low, medium, high
        self.due_date = due_date
        self.category = category
        self.completed = False
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert todo to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date,
            'category': self.category,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Todo':
        """Create todo from dictionary."""
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'),
            category=data.get('category', 'General'),
            todo_id=data['id']
        )
        todo.completed = data.get('completed', False)
        todo.created_at = data.get('created_at', datetime.now().isoformat())
        todo.updated_at = data.get('updated_at', datetime.now().isoformat())
        return todo

class LocalStorage:
    """Manages local storage for todos using JSON files."""
    def __init__(self, storage_file: str = "todos.json"):
        self.storage_file = storage_file
        self.todos: List[Todo] = []
        self.load()
    
    def load(self):
        """Load todos from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.todos = [Todo.from_dict(item) for item in data]
            except Exception as e:
                print(f"Error loading todos: {e}")
                self.todos = []
        else:
            self.todos = []
    
    def save(self):
        """Save todos to JSON file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump([todo.to_dict() for todo in self.todos], f, indent=2)
        except Exception as e:
            print(f"Error saving todos: {e}")
    
    def add_todo(self, todo: Todo) -> Todo:
        """Add a new todo."""
        self.todos.append(todo)
        self.save()
        return todo
    
    def get_all_todos(self) -> List[Todo]:
        """Get all todos."""
        return self.todos
    
    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """Get a specific todo by ID."""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None
    
    def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """Update a todo's properties."""
        todo = self.get_todo(todo_id)
        if todo:
            for key, value in kwargs.items():
                if hasattr(todo, key):
                    setattr(todo, key, value)
            todo.updated_at = datetime.now().isoformat()
            self.save()
        return todo
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo by ID."""
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                self.todos.pop(i)
                self.save()
                return True
        return False
    
    def toggle_todo(self, todo_id: str) -> Optional[Todo]:
        """Toggle todo completion status."""
        todo = self.get_todo(todo_id)
        if todo:
            todo.completed = not todo.completed
            todo.updated_at = datetime.now().isoformat()
            self.save()
        return todo
    
    def get_todos_by_category(self, category: str) -> List[Todo]:
        """Get all todos in a category."""
        return [todo for todo in self.todos if todo.category == category]
    
    def get_todos_by_priority(self, priority: str) -> List[Todo]:
        """Get all todos with a specific priority."""
        return [todo for todo in self.todos if todo.priority == priority]
    
    def get_completed_todos(self) -> List[Todo]:
        """Get all completed todos."""
        return [todo for todo in self.todos if todo.completed]
    
    def get_pending_todos(self) -> List[Todo]:
        """Get all pending (incomplete) todos."""
        return [todo for todo in self.todos if not todo.completed]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for todo in self.todos:
            categories.add(todo.category)
        return sorted(list(categories))
    
    def clear_completed(self) -> int:
        """Delete all completed todos and return count."""
        completed_count = len(self.get_completed_todos())
        self.todos = self.get_pending_todos()
        self.save()
        return completed_count
    
    def search_todos(self, query: str) -> List[Todo]:
        """Search todos by title or description."""
        query_lower = query.lower()
        return [todo for todo in self.todos 
                if query_lower in todo.title.lower() or query_lower in todo.description.lower()]
    
    def get_stats(self) -> dict:
        """Get statistics about todos."""
        return {
            'total': len(self.todos),
            'completed': len(self.get_completed_todos()),
            'pending': len(self.get_pending_todos()),
            'high_priority': len(self.get_todos_by_priority('high')),
            'categories': len(self.get_categories())
        }
