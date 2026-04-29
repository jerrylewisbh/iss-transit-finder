from skyfield.api import load, wgs84
from datetime import timedelta
import logging
import numpy as np

_LOGGER = logging.getLogger(__name__)

def calculate_transits(lat, lon, elevation):
    ts = load.timescale()
    eph = load('de421.bsp')
    sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
    
    try:
        stations_url = 'https://celestrak.org/NORAD/elements/stations.txt'
        satellites = load.tle_file(stations_url)
        iss = {s.name: s for s in satellites}['ISS (ZARYA)']
    except Exception as e:
        _LOGGER.error("Failed to fetch TLE: %s", e)
        return {}

    observer_pos = wgs84.latlon(lat, lon, elevation_m=elevation)
    observer = earth + observer_pos
    
    t0 = ts.now()
    t1 = ts.from_datetime(t0.utc_datetime() + timedelta(days=21))

    def find_next(target):
        step_days = 10.0 / 86400.0 
        t_arr = ts.tt_jd(np.arange(t0.tt, t1.tt, step_days))
        
        astrometric_iss = (iss - observer_pos).at(t_arr)
        alt, _, _ = astrometric_iss.altaz()
        
        visible_idx = np.where(alt.degrees > 0)[0]
        if len(visible_idx) == 0: return None
            
        t_visible = t_arr[visible_idx]
        astrometric_iss_vis = astrometric_iss[visible_idx]
        astrometric_target_vis = observer.at(t_visible).observe(target).apparent()
        separations = astrometric_iss_vis.separation_from(astrometric_target_vis).degrees
        
        # Find local minima where separation < 5.0
        # We find indices where separation is less than 5.0
        close_mask = separations < 5.0
        close_idx = np.where(close_mask)[0]
        if len(close_idx) == 0: return None

        # Split into distinct passes (if indices jump by more than a few minutes)
        # 1 step = 10 seconds. If difference > 6 steps (1 min), it's a new pass.
        passes = np.split(close_idx, np.where(np.diff(close_idx) > 6)[0] + 1)
        
        for p_idx in passes:
            if len(p_idx) == 0: continue
            
            # Find the time of minimum separation in this pass
            pass_seps = separations[p_idx]
            min_coarse_idx = p_idx[np.argmin(pass_seps)]
            t_coarse = t_visible[min_coarse_idx]
            
            # Fine search around this coarse minimum
            fine_step = 0.1 / 86400.0
            t_fine = ts.tt_jd(np.arange(t_coarse.tt - (30/86400.0), t_coarse.tt + (30/86400.0), fine_step))
            
            astrometric_iss_fine = (iss - observer_pos).at(t_fine)
            astrometric_target_fine = observer.at(t_fine).observe(target).apparent()
            fine_separations = astrometric_iss_fine.separation_from(astrometric_target_fine).degrees
            
            min_fine_idx = np.argmin(fine_separations)
            min_sep = fine_separations[min_fine_idx]
            
            if min_sep < 0.8:
                t_event = t_fine[min_fine_idx]
                final_alt, final_az, _ = astrometric_iss_fine[min_fine_idx].altaz()
                return {
                    "time": t_event.utc_iso(),
                    "separation_degrees": round(float(min_sep), 4),
                    "altitude": round(float(final_alt.degrees), 1),
                    "azimuth": round(float(final_az.degrees), 1)
                }
            
        return None

    return {
        "sun": find_next(sun),
        "moon": find_next(moon)
    }
