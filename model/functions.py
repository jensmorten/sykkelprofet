
import numpy as np

def compute_feels_like(temp, wind_speed):
    """
    Wind chill formula (Environment Canada) for temp < 10°C.
    For temp >= 10°C, returns the raw temperature.
    Wind speed should be in m/s; formula expects km/h.
    """
    wind_kmh = wind_speed * 3.6  # Convert m/s to km/h
    wind_chill = (
        13.12
        + 0.6215 * temp
        - 11.37 * np.power(np.maximum(wind_kmh, 1), 0.16)
        + 0.3965 * temp * np.power(np.maximum(wind_kmh, 1), 0.16)
    )
    return np.where(temp < 10, wind_chill, temp)