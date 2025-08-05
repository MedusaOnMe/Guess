from geopy.distance import geodesic
import math

def compute_score(true_coords, guess_coords):
    dist = geodesic(true_coords, guess_coords).km
    score = int(5000 * math.exp(-dist / 200))
    return dist, score
