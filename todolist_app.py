from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.image import Image
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
import matplotlib.pyplot as plt
from storage import Todo, LocalStorage

class TodoListApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = LocalStorage()
        self.current_filter = 'all'  # all, pending, completed
        self.current_category = 'All'
        self.current_sort = 'date'  # date, priority
    
    def build(self):
        self.title = 'TODO List - Local Storage'
        self.icon = 'icon.png'
        
        sm = ScreenManager()
        
        # Home/Main screen
        home_screen = HomeScreen(name='home')
        home_screen.app = self
        sm.add_widget(home_screen)
        
        # Add todo screen
        add_screen = AddTodoScreen(name='add')
        add_screen.app = self
        sm.add_widget(add_screen)
        
        # Edit todo screen
        edit_screen = EditTodoScreen(name='edit')
        edit_screen.app = self
        sm.add_widget(edit_screen)
        
        # Stats screen
        stats_screen = StatsScreen(name='stats')
        stats_screen.app = self
        sm.add_widget(stats_screen)
        
        return sm

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.todo_buttons = []
        self.refresh_timer = None
    
    def on_enter(self):
        self.refresh_ui()
        self.refresh_timer = Clock.schedule_interval(lambda dt: self.refresh_ui(), 1)
    
    def on_leave(self):
        if self.refresh_timer:
            self.refresh_timer.cancel()
    
    def refresh_ui(self):
        """Refresh the todo list display."""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header_layout = BoxLayout(size_hint_y=0.12, spacing=10, orientation='vertical')
        title_layout = BoxLayout(size_hint_y=0.6, spacing=10)
        title_layout.add_widget(Label(text='📝 TODO List', bold=True, font_size='24sp'))
        
        stats = self.app.storage.get_stats()
        stats_text = f"Total: {stats['total']} | ✓ {stats['completed']} | ⏳ {stats['pending']}"
        title_layout.add_widget(Label(text=stats_text, size_hint_x=0.6, font_size='10sp'))
        header_layout.add_widget(title_layout)
        
        # Filter and sort controls
        controls_layout = BoxLayout(size_hint_y=0.4, spacing=5)
        
        filter_spinner = Spinner(
            text=self.app.current_filter.capitalize(),
            values=('All', 'Pending', 'Completed'),
            size_hint_x=0.33
        )
        filter_spinner.bind(text=self.on_filter_change)
        controls_layout.add_widget(filter_spinner)
        
        category_spinner = Spinner(
            text=self.app.current_category,
            values=tuple(self.app.storage.get_categories() or ['General']),
            size_hint_x=0.33
        )
        category_spinner.bind(text=self.on_category_change)
        controls_layout.add_widget(category_spinner)
        
        sort_spinner = Spinner(
            text=self.app.current_sort.capitalize(),
            values=('Date', 'Priority'),
            size_hint_x=0.34
        )
        sort_spinner.bind(text=self.on_sort_change)
        controls_layout.add_widget(sort_spinner)
        
        header_layout.add_widget(controls_layout)
        layout.add_widget(header_layout)
        
        # Get filtered todos
        todos = self.get_filtered_todos()
        todos = self.sort_todos(todos)
        
        # Todos list
        scroll = ScrollView(size_hint_y=0.7)
        todos_layout = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=(5, 5))
        todos_layout.bind(minimum_height=todos_layout.setter('height'))
        
        if todos:
            for todo in todos:
                todo_layout = self.create_todo_item(todo)
                todos_layout.add_widget(todo_layout)
        else:
            todos_layout.add_widget(Label(text='✨ No todos yet!', size_hint_y=None, height=50, font_size='16sp'))
        
        scroll.add_widget(todos_layout)
        layout.add_widget(scroll)
        
        # Action buttons
        action_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        add_btn = Button(text='➕ Add Todo')
        add_btn.bind(on_press=self.go_to_add)
        action_layout.add_widget(add_btn)
        
        stats_btn = Button(text='📊 Stats')
        stats_btn.bind(on_press=self.go_to_stats)
        action_layout.add_widget(stats_btn)
        
        clear_btn = Button(text='🗑️ Clear Done')
        clear_btn.bind(on_press=self.clear_completed)
        action_layout.add_widget(clear_btn)
        
        layout.add_widget(action_layout)
        
        self.add_widget(layout)
    
    def create_todo_item(self, todo: Todo) -> BoxLayout:
        """Create a UI element for a todo item."""
        todo_layout = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=(5, 5))
        todo_layout.canvas.before.clear()
        
        # Priority color indicator
        priority_colors = {'high': (1, 0.4, 0.4, 1), 'medium': (1, 0.8, 0.4, 1), 'low': (0.4, 1, 0.4, 1)}
        from kivy.graphics import Color, Rectangle
        with todo_layout.canvas.before:
            Color(*priority_colors.get(todo.priority, (0.9, 0.9, 0.9, 1)))
            Rectangle(size=todo_layout.size, pos=todo_layout.pos)
        
        # Checkbox
        checkbox = CheckBox(active=todo.completed, size_hint_x=0.1)
        checkbox.bind(active=lambda x, y, tid=todo.id: self.toggle_todo(tid))
        todo_layout.add_widget(checkbox)
        
        # Todo info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        title_text = f"{'✓ ' if todo.completed else ''}{todo.title}"
        if todo.completed:
            title_text = f"[s]{title_text}[/s]"
        
        title_label = Label(text=title_text, markup=True, size_hint_y=0.5, font_size='12sp')
        info_layout.add_widget(title_label)
        
        meta_text = f"[{todo.category}] {todo.priority.upper()}"
        if todo.due_date:
            meta_text += f" | Due: {todo.due_date}"
        meta_label = Label(text=meta_text, size_hint_y=0.5, font_size='9sp')
        info_layout.add_widget(meta_label)
        
        todo_layout.add_widget(info_layout)
        
        # Action buttons
        edit_btn = Button(text='✏️', size_hint_x=0.1)
        edit_btn.bind(on_press=lambda x, tid=todo.id: self.go_to_edit(tid))
        todo_layout.add_widget(edit_btn)
        
        delete_btn = Button(text='🗑️', size_hint_x=0.1)
        delete_btn.bind(on_press=lambda x, tid=todo.id: self.delete_todo(tid))
        todo_layout.add_widget(delete_btn)
        
        return todo_layout
    
    def get_filtered_todos(self) -> list:
        """Get todos based on current filter and category."""
        if self.app.current_filter == 'completed':
            todos = self.app.storage.get_completed_todos()
        elif self.app.current_filter == 'pending':
            todos = self.app.storage.get_pending_todos()
        else:
            todos = self.app.storage.get_all_todos()
        
        if self.app.current_category != 'All':
            todos = [t for t in todos if t.category == self.app.current_category]
        
        return todos
    
    def sort_todos(self, todos: list) -> list:
        """Sort todos based on current sort option."""
        if self.app.current_sort == 'priority':
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            return sorted(todos, key=lambda t: priority_order.get(t.priority, 2))
        else:  # date
            return sorted(todos, key=lambda t: t.created_at, reverse=True)
    
    def on_filter_change(self, spinner, text):
        """Handle filter change."""
        self.app.current_filter = text.lower()
        self.refresh_ui()
    
    def on_category_change(self, spinner, text):
        """Handle category change."""
        self.app.current_category = text
        self.refresh_ui()
    
    def on_sort_change(self, spinner, text):
        """Handle sort change."""
        self.app.current_sort = text.lower()
        self.refresh_ui()
    
    def toggle_todo(self, todo_id: str):
        """Toggle todo completion."""
        self.app.storage.toggle_todo(todo_id)
        self.refresh_ui()
    
    def delete_todo(self, todo_id: str):
        """Delete a todo with confirmation."""
        popup = Popup(title='Delete Todo?', size_hint=(0.8, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Are you sure you want to delete this todo?'))
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def confirm_delete(x):
            self.app.storage.delete_todo(todo_id)
            self.refresh_ui()
            popup.dismiss()
        
        yes_btn = Button(text='Yes, Delete')
        yes_btn.bind(on_press=confirm_delete)
        btn_layout.add_widget(yes_btn)
        
        no_btn = Button(text='Cancel')
        no_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(no_btn)
        
        layout.add_widget(btn_layout)
        popup.content = layout
        popup.open()
    
    def clear_completed(self, instance):
        """Clear all completed todos."""
        popup = Popup(title='Clear Completed?', size_hint=(0.8, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Delete all completed todos?'))
        
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        def confirm_clear(x):
            count = self.app.storage.clear_completed()
            self.refresh_ui()
            popup.dismiss()
        
        yes_btn = Button(text=f'Yes, Clear')
        yes_btn.bind(on_press=confirm_clear)
        btn_layout.add_widget(yes_btn)
        
        no_btn = Button(text='Cancel')
        no_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(no_btn)
        
        layout.add_widget(btn_layout)
        popup.content = layout
        popup.open()
    
    def go_to_add(self, instance):
        """Navigate to add todo screen."""
        self.manager.current = 'add'
    
    def go_to_edit(self, todo_id: str):
        """Navigate to edit todo screen."""
        edit_screen = self.manager.get_screen('edit')
        edit_screen.todo_id = todo_id
        self.manager.current = 'edit'
    
    def go_to_stats(self, instance):
        """Navigate to stats screen."""
        self.manager.current = 'stats'

class AddTodoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.08, spacing=10)
        header.add_widget(Label(text='➕ Add New Todo', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Form
        form_layout = BoxLayout(orientation='vertical', size_hint_y=0.8, spacing=10)
        
        # Title
        form_layout.add_widget(Label(text='Title *', size_hint_y=0.1, bold=True))
        self.title_input = TextInput(hint_text='Enter todo title', multiline=False, size_hint_y=0.1)
        form_layout.add_widget(self.title_input)
        
        # Description
        form_layout.add_widget(Label(text='Description', size_hint_y=0.1, bold=True))
        self.description_input = TextInput(hint_text='Enter description', multiline=True, size_hint_y=0.15)
        form_layout.add_widget(self.description_input)
        
        # Priority
        form_layout.add_widget(Label(text='Priority', size_hint_y=0.1, bold=True))
        self.priority_spinner = Spinner(
            text='Medium',
            values=('Low', 'Medium', 'High'),
            size_hint_y=0.1
        )
        form_layout.add_widget(self.priority_spinner)
        
        # Category
        form_layout.add_widget(Label(text='Category', size_hint_y=0.1, bold=True))
        categories = self.app.storage.get_categories() or ['General']
        self.category_spinner = Spinner(
            text=categories[0],
            values=tuple(categories + ['New Category']),
            size_hint_y=0.1
        )
        form_layout.add_widget(self.category_spinner)
        
        # Due Date
        form_layout.add_widget(Label(text='Due Date (YYYY-MM-DD)', size_hint_y=0.1, bold=True))
        self.due_date_input = TextInput(hint_text='Optional', multiline=False, size_hint_y=0.1)
        form_layout.add_widget(self.due_date_input)
        
        layout.add_widget(form_layout)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        save_btn = Button(text='✓ Save')
        save_btn.bind(on_press=self.save_todo)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='✕ Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def save_todo(self, instance):
        """Save the new todo."""
        title = self.title_input.text.strip()
        if not title:
            self.show_error('Title is required!')
            return
        
        category = self.category_spinner.text
        if category == 'New Category':
            category = 'General'
        
        todo = Todo(
            title=title,
            description=self.description_input.text,
            priority=self.priority_spinner.text.lower(),
            due_date=self.due_date_input.text if self.due_date_input.text else None,
            category=category
        )
        
        self.app.storage.add_todo(todo)
        self.go_back(None)
    
    def show_error(self, message):
        """Show error popup."""
        popup = Popup(title='Error', size_hint=(0.8, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message))
        close_btn = Button(text='OK', size_hint_y=0.3)
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        popup.content = layout
        popup.open()
    
    def go_back(self, instance):
        """Go back to home screen."""
        self.manager.current = 'home'

class EditTodoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.todo_id = None
    
    def on_enter(self):
        if not self.todo_id:
            self.manager.current = 'home'
            return
        
        todo = self.app.storage.get_todo(self.todo_id)
        if not todo:
            self.manager.current = 'home'
            return
        
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.08, spacing=10)
        header.add_widget(Label(text='✏️ Edit Todo', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Form
        form_layout = BoxLayout(orientation='vertical', size_hint_y=0.8, spacing=10)
        
        # Title
        form_layout.add_widget(Label(text='Title *', size_hint_y=0.1, bold=True))
        self.title_input = TextInput(text=todo.title, multiline=False, size_hint_y=0.1)
        form_layout.add_widget(self.title_input)
        
        # Description
        form_layout.add_widget(Label(text='Description', size_hint_y=0.1, bold=True))
        self.description_input = TextInput(text=todo.description, multiline=True, size_hint_y=0.15)
        form_layout.add_widget(self.description_input)
        
        # Priority
        form_layout.add_widget(Label(text='Priority', size_hint_y=0.1, bold=True))
        self.priority_spinner = Spinner(
            text=todo.priority.capitalize(),
            values=('Low', 'Medium', 'High'),
            size_hint_y=0.1
        )
        form_layout.add_widget(self.priority_spinner)
        
        # Category
        form_layout.add_widget(Label(text='Category', size_hint_y=0.1, bold=True))
        categories = self.app.storage.get_categories() or ['General']
        self.category_spinner = Spinner(
            text=todo.category,
            values=tuple(categories),
            size_hint_y=0.1
        )
        form_layout.add_widget(self.category_spinner)
        
        # Due Date
        form_layout.add_widget(Label(text='Due Date (YYYY-MM-DD)', size_hint_y=0.1, bold=True))
        self.due_date_input = TextInput(text=todo.due_date or '', multiline=False, size_hint_y=0.1)
        form_layout.add_widget(self.due_date_input)
        
        layout.add_widget(form_layout)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        save_btn = Button(text='✓ Save')
        save_btn.bind(on_press=self.save_todo)
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='✕ Cancel')
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def save_todo(self, instance):
        """Save the edited todo."""
        title = self.title_input.text.strip()
        if not title:
            self.show_error('Title is required!')
            return
        
        self.app.storage.update_todo(
            self.todo_id,
            title=title,
            description=self.description_input.text,
            priority=self.priority_spinner.text.lower(),
            due_date=self.due_date_input.text if self.due_date_input.text else None,
            category=self.category_spinner.text
        )
        
        self.go_back(None)
    
    def show_error(self, message):
        """Show error popup."""
        popup = Popup(title='Error', size_hint=(0.8, 0.3))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message))
        close_btn = Button(text='OK', size_hint_y=0.3)
        close_btn.bind(on_press=popup.dismiss)
        layout.add_widget(close_btn)
        popup.content = layout
        popup.open()
    
    def go_back(self, instance):
        """Go back to home screen."""
        self.manager.current = 'home'

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Label(text='📊 Statistics', bold=True, font_size='18sp'))
        back_btn = Button(text='← Back', size_hint_x=0.2)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        layout.add_widget(header)
        
        # Stats
        stats = self.app.storage.get_stats()
        
        stats_layout = GridLayout(cols=2, size_hint_y=0.3, spacing=10, padding=10)
        
        stats_items = [
            ('📌 Total Todos', str(stats['total'])),
            ('✓ Completed', str(stats['completed'])),
            ('⏳ Pending', str(stats['pending'])),
            ('🔴 High Priority', str(stats['high_priority'])),
            ('📂 Categories', str(stats['categories'])),
            ('⏁ Completion Rate', f"{int((stats['completed']/max(stats['total'], 1))*100)}%"),
        ]
        
        for label, value in stats_items:
            item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=50)
            item_layout.add_widget(Label(text=label, size_hint_y=0.5, bold=True))
            item_layout.add_widget(Label(text=value, size_hint_y=0.5, font_size='16sp'))
            stats_layout.add_widget(item_layout)
        
        layout.add_widget(stats_layout)
        
        # Chart
        chart_layout = BoxLayout(size_hint_y=0.6)
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
            
            # Pie chart
            sizes = [stats['completed'], stats['pending']]
            labels = ['Completed', 'Pending']
            colors = ['#4CAF50', '#FFC107']
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Completion Status')
            
            # Bar chart
            priorities = ['High', 'Medium', 'Low']
            counts = [
                len(self.app.storage.get_todos_by_priority('high')),
                len(self.app.storage.get_todos_by_priority('medium')),
                len(self.app.storage.get_todos_by_priority('low'))
            ]
            ax2.bar(priorities, counts, color=['#FF6B6B', '#FFC107', '#4CAF50'])
            ax2.set_title('Todos by Priority')
            ax2.set_ylabel('Count')
            
            plt.tight_layout()
            
            canvas = FigureCanvasKivyAgg(fig)
            chart_layout.add_widget(canvas)
        except Exception as e:
            chart_layout.add_widget(Label(text=f'Error loading chart: {str(e)}'))
        
        layout.add_widget(chart_layout)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        back_btn2 = Button(text='← Back')
        back_btn2.bind(on_press=self.go_back)
        btn_layout.add_widget(back_btn2)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        """Go back to home screen."""
        self.manager.current = 'home'

if __name__ == '__main__':
    TodoListApp().run()
