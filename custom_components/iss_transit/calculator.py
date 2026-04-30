import urllib.request
import ephem
from datetime import datetime, timedelta, timezone
import logging
import math

_LOGGER = logging.getLogger(__name__)

def fetch_iss_tle():
    """Fetch the latest ISS TLE from Celestrak."""
    url = "https://celestrak.org/NORAD/elements/stations.txt"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        lines = response.read().decode('utf-8').splitlines()
    
    for i in range(len(lines)):
        if "ISS" in lines[i] or "ZARYA" in lines[i]:
            return lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()
    raise ValueError("ISS TLE not found")

def calculate_transits(lat, lon, elevation):
    """Calculate transits using the robust PyEphem library."""
    try:
        name, line1, line2 = fetch_iss_tle()
        iss = ephem.readtle(name, line1, line2)
    except Exception as e:
        _LOGGER.error("Failed to fetch TLE: %s", e)
        return {}

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = elevation
    observer.compute_pressure()

    sun = ephem.Sun()
    moon = ephem.Moon()
    
    # We must operate in strict UTC datetime objects for HA compatibility
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=21)

    def find_next(target):
        current_time = now
        
        while current_time < end_time:
            observer.date = current_time
            iss.compute(observer)
            
            if math.degrees(iss.alt) > 0:
                target.compute(observer)
                sep = math.degrees(ephem.separation((iss.az, iss.alt), (target.az, target.alt)))
                
                if sep < 5.0:
                    fine_time = current_time - timedelta(minutes=1)
                    fine_end = current_time + timedelta(minutes=1)
                    
                    min_sep = float('inf')
                    best_time = None
                    
                    while fine_time < fine_end:
                        observer.date = fine_time
                        iss.compute(observer)
                        target.compute(observer)
                        
                        f_sep = math.degrees(ephem.separation((iss.az, iss.alt), (target.az, target.alt)))
                        if f_sep < min_sep:
                            min_sep = f_sep
                            best_time = fine_time
                            
                        fine_time += timedelta(seconds=0.5)
                        
                    if min_sep < 0.8 and best_time is not None:
                        observer.date = best_time
                        iss.compute(observer)
                        
                        # FORMATTING FIX: Ensure strict HA-compatible UTC ISO string
                        # e.g., 2026-05-20T01:58:27+00:00
                        time_str = best_time.replace(microsecond=0).isoformat()
                        
                        return {
                            "time": time_str,
                            "separation_degrees": round(min_sep, 4),
                            "altitude": round(math.degrees(iss.alt), 1),
                            "azimuth": round(math.degrees(iss.az), 1)
                        }
                    
                    current_time += timedelta(minutes=10)
                    continue
            
            current_time += timedelta(minutes=1)
            
        return None

    return {
        "sun": find_next(sun),
        "moon": find_next(moon)
    }
