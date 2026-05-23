# Digital Clock - Multi Timezone Application

A beautiful, feature-rich digital clock application that displays the current time in multiple timezones simultaneously. Perfect for tracking time across different regions worldwide.

## Features

### 🕐 Clock Display
- Real-time updates (refreshes every 500ms)
- Multiple timezone clocks displayed simultaneously
- 24-hour and 12-hour (AM/PM) format options
- Digital clock display with HH:MM:SS format
- Timezone name, abbreviation, and UTC offset
- Date display with full weekday and month names

### 🌍 Timezone Management
- Add/remove timezones easily
- Pre-organized timezones by region:
  - Americas (New York, Los Angeles, Toronto, Mexico City, São Paulo, etc.)
  - Europe (London, Paris, Berlin, Moscow, Istanbul, etc.)
  - Asia (Dubai, Tokyo, Hong Kong, Singapore, Bangkok, etc.)
  - Africa (Cairo, Johannesburg, Lagos, etc.)
  - Australia & Oceania (Sydney, Melbourne, Auckland, etc.)
- Custom timezone support
- Save favorite timezones automatically
- Default timezones: UTC, New York, London, Tokyo

### 📍 Timezone Details
- Detailed view for each timezone
- Current time in both 24h and 12h formats
- Timezone abbreviation (EST, PST, JST, etc.)
- UTC offset display
- Daylight Saving Time (DST) status
- Time difference from UTC
- Individual timezone clock removal

### ⚙️ Settings
- Time format selection (24-hour or 12-hour)
- Settings persistence
- About information

### 💾 Data Persistence
- Favorite timezones saved to JSON file
- Settings remembered between sessions
- No internet required

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install astral for sunrise/sunset times
pip install astral
```

## Usage

### Run the Application

```bash
python digital_clock_app.py
```

### Main Features

#### 🕐 Clock Screen (Main)
- View all your selected timezones
- Each timezone shows:
  - Timezone name and abbreviation
  - UTC offset
  - Current time (digital)
  - Current date
  - Quick action button to view details
- Buttons:
  - **⚙️ Settings** - Open settings
  - **➕ Manage** - Add/remove timezones

#### ➕ Timezone Manager
- Browse timezones by region
- Pre-selected popular timezones
- Add/remove timezones with one click
- Add custom timezones
- Visual indicators for selected timezones

#### 📍 Timezone Details
- Detailed information for each timezone
- Current time display
- Timezone offset and abbreviation
- DST status
- Time difference from UTC
- Option to remove timezone

#### ⚙️ Settings
- Toggle between 24-hour and 12-hour format
- View app information

## Supported Timezones

### Americas (10 timezones)
- America/New_York (EST/EDT)
- America/Chicago (CST/CDT)
- America/Denver (MST/MDT)
- America/Los_Angeles (PST/PDT)
- America/Anchorage (AKST/AKDT)
- Pacific/Honolulu (HST)
- America/Toronto (EST/EDT)
- America/Mexico_City (CST/CDT)
- America/Sao_Paulo (BRT/BRST)
- America/Buenos_Aires (ART)

### Europe (15 timezones)
- Europe/London (GMT/BST)
- Europe/Paris, Berlin, Madrid, Rome, Amsterdam, etc. (CET/CEST)
- Europe/Moscow (MSK)
- Europe/Istanbul (EET/EEST)
- And more...

### Asia (13 timezones)
- Asia/Dubai (GST)
- Asia/Kolkata (IST)
- Asia/Bangkok (ICT)
- Asia/Hong_Kong (HKT)
- Asia/Singapore (SGT)
- Asia/Tokyo (JST)
- Asia/Seoul (KST)
- And more...

### Africa (6 timezones)
- Africa/Cairo (EET/EEST)
- Africa/Johannesburg (SAST)
- Africa/Lagos (WAT)
- And more...

### Australia & Oceania (7 timezones)
- Australia/Sydney (AEDT/AEST)
- Australia/Melbourne (AEDT/AEST)
- Pacific/Auckland (NZDT/NZST)
- And more...

## File Structure

```
├── digital_clock_app.py      # Main Kivy application
├── timezone_manager.py        # Timezone management logic
├── favorite_timezones.json   # Auto-generated favorites file
└── requirements.txt          # Python dependencies
```

## API Reference

### TimeZoneManager Class

```python
from timezone_manager import TimeZoneManager

# Initialize
tm = TimeZoneManager()

# Get current time in timezone
dt = tm.get_current_time('America/New_York')

# Get timezone info
info = tm.get_timezone_info('Europe/London')
# Returns: {
#     'timezone': 'Europe/London',
#     'time': datetime object,
#     'utc_offset': '+0000',
#     'timezone_name': 'GMT',
#     'is_dst': False,
#     'dst_name': 'GMT'
# }

# Format time
formatted = tm.format_time(dt, '%H:%M:%S')

# Format 12-hour
time_str, am_pm = tm.format_time_12h(dt)

# Get time difference
diff = tm.get_time_difference('UTC', 'America/New_York')
# Returns: -5 (hours)

# Add/remove timezones
tm.add_timezone('Asia/Bangkok')
tm.remove_timezone('America/Denver')

# Get all selected timezones
selected = tm.selected_timezones

# Convert time between timezones
converted = tm.convert_time(dt, 'America/New_York', 'Europe/London')
```

## Configuration

### Default Timezones
Edit `favorite_timezones.json` to change default timezones:

```json
{
  "timezones": ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
}
```

## Time Format Examples

### 24-Hour Format
```
14:30:45
08:15:20
23:59:59
```

### 12-Hour Format
```
02:30:45 PM
08:15:20 AM
11:59:59 PM
```

## Daylight Saving Time (DST)

The application automatically handles DST:
- Displays accurate times during DST transitions
- Shows DST status in timezone details
- Abbreviations change (e.g., EST ↔ EDT)

## Advanced Features

### Time Conversion
```python
dt = datetime(2026, 5, 23, 14, 30, 0)
converted = tm.convert_time(dt, 'America/New_York', 'Asia/Tokyo')
```

### UTC Time
```python
utc_time = tm.get_utc_time()
```

### All Timezones
```python
all_tz = tm.get_all_timezones()  # Returns all pytz timezones
```

## Keyboard Shortcuts

*Coming in future versions*

## Performance

- ✅ Updates every 500ms
- ✅ Handles 50+ timezones smoothly
- ✅ Minimal CPU usage
- ✅ Fast timezone calculations

## Troubleshooting

### Timezone not recognized
```python
# Check if timezone is valid
import pytz
if 'Asia/Bangkok' in pytz.all_timezones:
    print("Valid timezone")
```

### Time not updating
- Check if app timer is running
- Restart the application
- Verify system time is correct

### DST not showing correctly
- Ensure system timezone is set correctly
- Update system to latest timezone database

## Future Enhancements

- [ ] Analog clock display option
- [ ] World map with timezone visualization
- [ ] Meeting planner for multiple timezones
- [ ] Alarm for specific timezones
- [ ] Sunrise/sunset times (requires astral library)
- [ ] Timezone comparison tool
- [ ] Clock themes and customization
- [ ] System tray widget
- [ ] Voice announcement
- [ ] Weather by timezone

## Dependencies

- **Kivy** - Cross-platform GUI framework
- **pytz** - Timezone database and calculations
- **astral** (optional) - Sunrise/sunset calculations

## License

MIT License - Feel free to use and modify

## Credits

- Built with [Kivy](https://kivy.org/)
- Timezone data from [pytz](https://pypi.org/project/pytz/)

---

**🌍 Track time across the globe! Made with ❤️ using Kivy & Python**
