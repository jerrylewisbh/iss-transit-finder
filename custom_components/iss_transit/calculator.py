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
    
    # Find ISS
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
    observer.compute_pressure() # Use standard atmosphere for refraction

    sun = ephem.Sun()
    moon = ephem.Moon()
    
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=21)

    def find_next(target):
        current_time = now
        
        while current_time < end_time:
            # We jump forward by 1 minute increments to find passes
            observer.date = current_time
            iss.compute(observer)
            
            # Check if ISS is above the horizon
            if math.degrees(iss.alt) > 0:
                target.compute(observer)
                
                # Calculate angular separation (PyEphem separation returns radians)
                sep = math.degrees(ephem.separation((iss.az, iss.alt), (target.az, target.alt)))
                
                if sep < 5.0:
                    # We found a close pass! 
                    # Drop into 0.5 second increments to find the exact minimum
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
                        
                    # If the minimum separation is less than 0.8 degrees, it's a transit
                    if min_sep < 0.8 and best_time is not None:
                        observer.date = best_time
                        iss.compute(observer)
                        return {
                            "time": best_time.isoformat(),
                            "separation_degrees": round(min_sep, 4),
                            "altitude": round(math.degrees(iss.alt), 1),
                            "azimuth": round(math.degrees(iss.az), 1)
                        }
                    
                    # Jump forward slightly so we don't re-detect the same pass
                    current_time += timedelta(minutes=10)
                    continue
            
            # Step forward by 1 minute
            current_time += timedelta(minutes=1)
            
        return None

    return {
        "sun": find_next(sun),
        "moon": find_next(moon)
    }
