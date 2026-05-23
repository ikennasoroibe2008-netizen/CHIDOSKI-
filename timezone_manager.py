from datetime import datetime
import pytz
from typing import List, Dict, Optional
import json
import os

class TimeZoneManager:
    """Manages timezones and time conversions."""
    
    # Common timezones organized by region
    PRESET_TIMEZONES = {
        'Americas': [
            'America/New_York',      # EST/EDT
            'America/Chicago',       # CST/CDT
            'America/Denver',        # MST/MDT
            'America/Los_Angeles',   # PST/PDT
            'America/Anchorage',     # AKST/AKDT
            'Pacific/Honolulu',      # HST
            'America/Toronto',       # EST/EDT (Canada)
            'America/Mexico_City',   # CST/CDT (Mexico)
            'America/Sao_Paulo',     # BRT/BRST (Brazil)
            'America/Buenos_Aires',  # ART (Argentina)
        ],
        'Europe': [
            'Europe/London',         # GMT/BST
            'Europe/Paris',          # CET/CEST
            'Europe/Berlin',         # CET/CEST
            'Europe/Madrid',         # CET/CEST
            'Europe/Rome',           # CET/CEST
            'Europe/Amsterdam',      # CET/CEST
            'Europe/Brussels',       # CET/CEST
            'Europe/Vienna',         # CET/CEST
            'Europe/Prague',         # CET/CEST
            'Europe/Moscow',         # MSK
            'Europe/Istanbul',       # EET/EEST
            'Europe/Athens',         # EET/EEST
            'Europe/Dublin',         # GMT/IST
            'Europe/Lisbon',         # WET/WEST
            'Europe/Zurich',         # CET/CEST
        ],
        'Asia': [
            'Asia/Dubai',            # GST
            'Asia/Kolkata',          # IST
            'Asia/Bangkok',          # ICT
            'Asia/Hong_Kong',        # HKT
            'Asia/Singapore',        # SGT
            'Asia/Tokyo',            # JST
            'Asia/Seoul',            # KST
            'Asia/Shanghai',         # CST
            'Asia/Manila',           # PHT
            'Asia/Jakarta',          # WIB
            'Asia/Taipei',           # CST
            'Asia/Ho_Chi_Minh',      # ICT
            'Asia/Kuala_Lumpur',     # MYT
        ],
        'Africa': [
            'Africa/Cairo',          # EET/EEST
            'Africa/Johannesburg',   # SAST
            'Africa/Lagos',          # WAT
            'Africa/Casablanca',     # WET/WEST
            'Africa/Nairobi',        # EAT
            'Africa/Accra',          # GMT
        ],
        'Australia & Oceania': [
            'Australia/Sydney',      # AEDT/AEST
            'Australia/Melbourne',   # AEDT/AEST
            'Australia/Brisbane',    # AEST
            'Australia/Perth',       # AWST
            'Australia/Adelaide',    # ACDT/ACST
            'Pacific/Auckland',      # NZDT/NZST
            'Pacific/Fiji',          # FJT/FJST
        ]
    }
    
    def __init__(self):
        self.selected_timezones: List[str] = []
        self.load_favorites()
    
    def load_favorites(self):
        """Load favorite timezones from file."""
        if os.path.exists('favorite_timezones.json'):
            try:
                with open('favorite_timezones.json', 'r') as f:
                    data = json.load(f)
                    self.selected_timezones = data.get('timezones', ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo'])
            except Exception as e:
                print(f"Error loading favorites: {e}")
                self.selected_timezones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
        else:
            self.selected_timezones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
    
    def save_favorites(self):
        """Save favorite timezones to file."""
        try:
            with open('favorite_timezones.json', 'w') as f:
                json.dump({'timezones': self.selected_timezones}, f, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")
    
    def get_all_timezones(self) -> List[str]:
        """Get all available timezones."""
        return pytz.all_timezones
    
    def get_preset_timezones(self) -> Dict[str, List[str]]:
        """Get preset timezones by region."""
        return self.PRESET_TIMEZONES
    
    def add_timezone(self, timezone: str) -> bool:
        """Add a timezone to selected list."""
        try:
            pytz.timezone(timezone)
            if timezone not in self.selected_timezones:
                self.selected_timezones.append(timezone)
                self.save_favorites()
                return True
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"Unknown timezone: {timezone}")
        return False
    
    def remove_timezone(self, timezone: str) -> bool:
        """Remove a timezone from selected list."""
        if timezone in self.selected_timezones:
            self.selected_timezones.remove(timezone)
            self.save_favorites()
            return True
        return False
    
    def get_current_time(self, timezone: str) -> Optional[datetime]:
        """Get current time in a specific timezone."""
        try:
            tz = pytz.timezone(timezone)
            return datetime.now(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            return None
    
    def get_timezone_info(self, timezone: str) -> Optional[Dict]:
        """Get detailed information about a timezone."""
        try:
            now = self.get_current_time(timezone)
            if not now:
                return None
            
            return {
                'timezone': timezone,
                'time': now,
                'utc_offset': now.strftime('%z'),
                'timezone_name': now.strftime('%Z'),
                'is_dst': bool(now.dst()),
                'dst_name': now.tzname(),
            }
        except Exception as e:
            print(f"Error getting timezone info: {e}")
            return None
    
    def format_time(self, dt: datetime, format_str: str = '%H:%M:%S') -> str:
        """Format datetime object."""
        return dt.strftime(format_str)
    
    def format_time_12h(self, dt: datetime) -> tuple:
        """Format time in 12-hour format with AM/PM."""
        time_str = dt.strftime('%I:%M:%S')
        am_pm = dt.strftime('%p')
        return time_str, am_pm
    
    def get_time_difference(self, tz1: str, tz2: str) -> Optional[int]:
        """Get time difference in hours between two timezones."""
        try:
            time1 = self.get_current_time(tz1)
            time2 = self.get_current_time(tz2)
            
            if time1 and time2:
                diff = (time2.utcoffset() - time1.utcoffset()).total_seconds() / 3600
                return int(diff)
        except Exception as e:
            print(f"Error calculating time difference: {e}")
        return None
    
    def get_sunrise_sunset(self, timezone: str, latitude: float, longitude: float) -> Optional[Dict]:
        """Get sunrise and sunset times (requires astral library)."""
        try:
            from astral import LocationInfo
            from astral.sun import sun
            
            tz = pytz.timezone(timezone)
            location = LocationInfo(timezone=timezone, latitude=latitude, longitude=longitude)
            s = sun(location.observer, date=datetime.now(tz).date(), tzinfo=tz)
            
            return {
                'sunrise': s['sunrise'],
                'sunset': s['sunset'],
                'noon': s['noon'],
            }
        except ImportError:
            print("Astral library not installed. Install with: pip install astral")
        except Exception as e:
            print(f"Error getting sunrise/sunset: {e}")
        return None
    
    def get_utc_time(self) -> datetime:
        """Get current UTC time."""
        return datetime.now(pytz.UTC)
    
    def convert_time(self, dt: datetime, from_tz: str, to_tz: str) -> Optional[datetime]:
        """Convert time from one timezone to another."""
        try:
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)
            
            # If dt is naive, assume it's in from_tz
            if dt.tzinfo is None:
                dt = from_timezone.localize(dt)
            else:
                dt = dt.astimezone(from_timezone)
            
            return dt.astimezone(to_timezone)
        except Exception as e:
            print(f"Error converting time: {e}")
        return None
    
    def is_24h_format(self) -> bool:
        """Check if system uses 24-hour format (can be customized)."""
        return True
    
    def get_timezone_abbreviation(self, timezone: str) -> Optional[str]:
        """Get timezone abbreviation (e.g., EST, PST)."""
        try:
            dt = self.get_current_time(timezone)
            if dt:
                return dt.strftime('%Z')
        except Exception as e:
            print(f"Error getting timezone abbreviation: {e}")
        return None
