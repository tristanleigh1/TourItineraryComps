import googlemaps
import math
from decimal import *

'''
    Given a list of all POIs, a start/end, and user input, calculates and returns a list of POIs that
    that will be plotted on the map as the user's route.
'''
def create_path(total_pois, start, end, walk_factor, preferences, num_destinations):
    MAX_POIS = int(num_destinations)
    # path_segments is a list of pairs of points
    path_segments = [(start, end)]
    path_pois = []
    total_pois = list(total_pois)
    path_pois_category_dictionary = {'Museums': 0.0, 'Nature': 0.0, 'Activities': 0.0, 'Landmarks': 0.0}

    count = 0
    for poi in total_pois:
        if isStartOrEnd(poi, start, end):
            total_pois.remove(poi)

    while len(path_pois) < MAX_POIS:
        poi = find_next_poi(total_pois, path_segments, walk_factor, preferences, path_pois_category_dictionary)
        path_pois.append(poi)
        total_pois.remove(poi)
        path_pois_category_dictionary[poi.category]+=1

    final_path_pois = []
    for i in range(len(path_segments)-1):
        final_path_pois.append(path_segments[i][1])
    return final_path_pois

'''
    Takes in a POI and the start and end POIs, returns True if POI is same as start or end.
    Returns False otherwise.
'''
def isStartOrEnd(poi, start, end):
    gmaps = googlemaps.Client(key='AIzaSyAhEeD2Dgvw-AAxGR9_qL7P9JlTeO-WjvM')
    # Checks if the given POI is within a small radius of the start point
    if start and abs(poi.latitude - start.latitude) < .0015 and abs(poi.longitude - start.longitude) < .0015:
        poi_geocode = gmaps.geocode(poi.address)
        # If the POI is nearby, use Google Maps to get a more accurate latitude and longitude matching the
        # start lat/lng and check if it's within even smaller radius
        if len(poi_geocode) != 0:
            poi_location = poi_geocode[0]['geometry']['location']
            if abs(float(poi_location['lat']) - float(start.latitude)) < .000001 and abs(float(poi_location['lng']) - float(start.longitude)) < .000001:
                return True
        else:
            return True
    # Checks if the given POI is within a small radius of the end point
    if end and abs(poi.latitude - end.latitude) < .0015 and abs(poi.longitude - end.longitude) < .0015:
        poi_geocode = gmaps.geocode(poi.address)
        # If the POI is nearby, use Google Maps to get a more accurate latitude and longitude matching the
        # start lat/lng and check if it's within even smaller radius
        if len(poi_geocode) != 0:
            poi_location = poi_geocode[0]['geometry']['location']
            if abs(float(poi_location['lat']) - float(end.latitude)) < .000001 and abs(float(poi_location['lng']) - float(end.longitude)) < .000001:
                return True
        else:
            return True
    return False

'''
    Given a list of all possible POIs, the current segments on the path, and user's input, calculate
    the score of each POI, adds the POI with the highest score to the path, and returns that POI.
'''
def find_next_poi(poi_list, path_segments, walk_factor, preferences, path_category_dict):
    poi_to_add = None
    seg_to_add_to = None
    min_score = float("inf")
    final_where_in_segment = ""
    for poi in poi_list:
        # Due to large number of restaurants in database, we skip adding restaurants to initial path.
        if poi.category == 'Restaurants':
            continue
        # Check to make sure we aren't adding POI that is the same as start point.
        if poi.business_name == path_segments[0][0].business_name:
            continue
        # Check to make sure we aren't adding POI that is the same as end point.
        if poi.business_name == path_segments[len(path_segments)-1][1].business_name:
            continue
        score, segment, where_in_segment = calculate_score(poi, path_segments, walk_factor, preferences, path_category_dict)
        if score < min_score:
            poi_to_add = poi
            min_score = score
            seg_to_add_to = segment
            final_where_in_segment = where_in_segment
    update_segments(path_segments, poi_to_add, seg_to_add_to, final_where_in_segment)
    return poi_to_add

'''
    Given a POI, calculate the score of this POI with respect to the user's
    input also sent in as parameters. Returns score of POI along with the
    segment it would intersect and where in the segment it should intersect.

    Equations used based on equations in original research paper that project
    was inspired by.
'''
def calculate_score(current_poi, path_segments, walk_factor, preferences, path_cat_dict):
    # empirical_coefficient is constant that helps balance importance of POI's
    # distance to path and how much it fits user's preferences
    empirical_coefficient = 0.0006
    category = current_poi.category
    popularity = current_poi.popularity
    distance_to_path = float("inf")
    closest_segment = None

    # Cast longitude and latitude to floats
    poi_longitude = float(current_poi.longitude)
    poi_latitude = float(current_poi.latitude)

    # To determine if the POI should be added in the middle of a segment or to the
    # beginning or end of a segment, we'll assume middle for now
    final_where_in_segment = "middle"
    total_preference_points = .0001 + float(preferences[0]) + float(preferences[1]) + float(preferences[2]) + float(preferences[3])
    score = float("inf")
    if current_poi.category == 'Museums':
        taste = float(preferences[0])*(.8 - path_cat_dict['Museums']* .1)/total_preference_points
    elif current_poi.category == 'Landmarks':
        taste = float(preferences[1])*(.8 - path_cat_dict['Landmarks'] * .1)/total_preference_points
    elif current_poi.category == 'Activities':
        taste = float(preferences[2])*(.8 - path_cat_dict['Activities'] * .1)/total_preference_points
    else:
        taste = float(preferences[3])*(.8 - path_cat_dict['Nature'] * .1)/total_preference_points

    walk_factor = float(walk_factor) * .75

    # Loop through every existing segment to find the closest one to add the new POI to
    for i in range(len(path_segments)):
        seg = path_segments[i]
        # Calculate closest line (Remember: latitude is x direction, longitude is y)
        x1, x2 = float(seg[0].latitude), float(seg[1].latitude)
        y1, y2 = float(seg[0].longitude), float(seg[1].longitude)
        rise = y2 - y1
        run = x2 - x1

        if rise == 0:
            # Horizontal line
            distance_to_segment = abs(y1 - poi_longitude)
            where_in_segment = "middle"
        elif run == 0:
            # Vertical line
            distance_to_segment = abs(x1 - poi_latitude)
            where_in_segment = "middle"
        else:
            # Calculate slopes and y-intercepts
            slope = rise / run
            orthogonal_slope = (run / rise) * -1.0
            y_int = y1 - (slope * x1)
            orthogonal_y_int = poi_longitude - (orthogonal_slope * poi_latitude)

            # Find where lines intersect
            intersect_x = (orthogonal_y_int - y_int) / (slope - orthogonal_slope)
            intersect_y = (slope * intersect_x) + y_int

            # Check if point of intersection is part of segment
            distance_start_to_end = ((y2 - y1)**2 + (x2-x1)**2)**(1/2)
            distance_start_to_POI = ((intersect_y - y1)**2 + (intersect_x-x1)**2)**(1/2)
            distance_POI_to_end = ((y2 - intersect_y)**2 + (x2-intersect_x)**2)**(1/2)

            # If POI should be added in the middle of segment
            if abs(distance_start_to_POI + distance_POI_to_end - distance_start_to_end) <= 0.000001:
                distance_to_segment = math.sqrt((intersect_x - poi_latitude)**2 + (intersect_y - poi_longitude)**2)
                where_in_segment = "middle"
            else:
                distance_to_start = math.sqrt((x1 - poi_latitude)**2 + (y1 - poi_longitude)**2)
                distance_to_end = math.sqrt((x2 - poi_latitude)**2 + (y2 - poi_longitude)**2)
                # If POI should be added to the beginning of the segment
                if distance_to_start < distance_to_end:
                    distance_to_segment = distance_to_start
                    # Don't add POI before Origin
                    if seg[0].category != "Origin":
                        where_in_segment = "begin"
                    else:
                        where_in_segment = "middle"
                # If POI should be added to the end of the segment
                else:
                    distance_to_segment = distance_to_end
                    # Don't add POI after Destination
                    if seg[1].category != "Destination":
                        where_in_segment = "end"
                    else:
                        where_in_segment = "middle"


       # Update the smallest distance
        if distance_to_segment < distance_to_path:
            distance_to_path = distance_to_segment
            closest_segment = seg
            final_where_in_segment = where_in_segment

    # Calculate the score
    score = float(distance_to_path) - empirical_coefficient * float(popularity) * taste * walk_factor

    return score, closest_segment, final_where_in_segment

'''
    Given the list of segments, a new POI, a segment to add it to, and where to add the new POI, updates
    given list accordingly.
'''
def update_segments(current_segments, new_poi, segment_to_add_to, where_in_segment):
    seg_index = current_segments.index(segment_to_add_to)
    if where_in_segment == "end":
        new_segment = (current_segments[seg_index][1], new_poi)
        current_segments[seg_index + 1] = (new_poi, current_segments[seg_index + 1][1])
        current_segments.insert(seg_index+1, new_segment)

    elif where_in_segment == "begin":
        new_segment = (new_poi, current_segments[seg_index][0])
        current_segments[seg_index - 1] = (current_segments[seg_index - 1][0], new_poi)
        current_segments.insert(seg_index, new_segment)
    else:
        new_segment = (current_segments[seg_index][0], new_poi)
        current_segments[seg_index] = (new_poi, current_segments[seg_index][1])
        current_segments.insert(seg_index, new_segment)
