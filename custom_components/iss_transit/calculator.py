from skyfield.api import load, wgs84
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

def calculate_transits(lat, lon, elevation):
    """Calculate the next real ISS transits for the Sun and Moon (NumPy-Free)."""
    ts = load.timescale()
    
    # Load required data
    try:
        eph = load('de421.bsp')
        sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
        
        stations_url = 'https://celestrak.org/NORAD/elements/stations.txt'
        satellites = load.tle_file(stations_url)
        iss = {s.name: s for s in satellites}['ISS (ZARYA)']
    except Exception as e:
        _LOGGER.error("Failed to load astronomical data: %s", e)
        return {}

    observer_pos = wgs84.latlon(lat, lon, elevation_m=elevation)
    observer = earth + observer_pos
    
    # Search window: 21 days
    t0 = ts.now()
    t1 = ts.from_datetime(t0.utc_datetime() + timedelta(days=21))

    def find_next(target):
        # COARSE SEARCH: Step every 10 seconds.
        # Done via a standard Python loop to avoid NumPy segfaults.
        current_t = t0
        step_days = 10.0 / 86400.0  # 10 seconds
        
        found_coarse = None
        
        while current_t.tt < t1.tt:
            # 1. Check if ISS is visible (altitude > 0)
            astrometric_iss = (iss - observer_pos).at(current_t)
            alt, _, _ = astrometric_iss.altaz()
            
            if alt.degrees > 0:
                # 2. Check separation
                astrometric_target = observer.at(current_t).observe(target).apparent()
                sep = astrometric_iss.separation_from(astrometric_target).degrees
                
                if sep < 5.0:
                    found_coarse = current_t
                    break # Break on first close pass
            
            # Step forward
            current_t = ts.tt_jd(current_t.tt + step_days)
            
        if not found_coarse:
            return None
            
        # FINE SEARCH: Step every 0.1 seconds around the coarse find
        fine_start = ts.tt_jd(found_coarse.tt - (30.0 / 86400.0))
        fine_end = ts.tt_jd(found_coarse.tt + (30.0 / 86400.0))
        fine_step = 0.1 / 86400.0
        
        current_fine = fine_start
        min_sep = float('inf')
        best_t = None
        
        while current_fine.tt < fine_end.tt:
            a_iss = (iss - observer_pos).at(current_fine)
            a_target = observer.at(current_fine).observe(target).apparent()
            sep = a_iss.separation_from(a_target).degrees
            
            if sep < min_sep:
                min_sep = sep
                best_t = current_fine
                
            current_fine = ts.tt_jd(current_fine.tt + fine_step)
            
        # Evaluate final result
        if min_sep < 0.8 and best_t is not None:
            final_a_iss = (iss - observer_pos).at(best_t)
            final_alt, final_az, _ = final_a_iss.altaz()
            return {
                "time": best_t.utc_iso(),
                "separation_degrees": round(float(min_sep), 4),
                "altitude": round(float(final_alt.degrees), 1),
                "azimuth": round(float(final_az.degrees), 1)
            }
            
        return None

    return {
        "sun": find_next(sun),
        "moon": find_next(moon)
    }
