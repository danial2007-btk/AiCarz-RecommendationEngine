from shapely.geometry import Point, Polygon

def is_within_uk_boundary(lat, lon):
    # Define the boundary coordinates
    boundary_coords = [
        (55.730067550872946, -6.044843416651095),
        (56.39978492636089, 1.8465272521310225),
        (49.6685956318405, -5.987414410408748),
        (51.02335540643392, 1.90362796372173)
    ]

    # Create a polygon from the boundary coordinates
    uk_boundary = Polygon(boundary_coords)

    # Create a point for the given latitude and longitude
    location = Point(lat, lon)

    # Check if the point is within the polygon
    return uk_boundary.contains(location)

# Example usage:
# print(is_within_uk_boundary(53.70490479524998, -1.3740088233097907))  # True for within the UK
# print(is_within_uk_boundary(40.712776, -74.005974)) # False for Outside of UK