"""Compute angles and coordinates."""

import math


def find_ang(xy1, xy2):
    """
    Find orientation of the vector linking x1, y1 to x2, y2.

    Note: this is 180d different from the vector linking x2,y2 to x1,y1.
    Validated: 03/04/19.
    """
    x1 = xy1[0]
    y1 = xy1[1]

    x2 = xy2[0]
    y2 = xy2[1]

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        print('Error: the two points can not be the same')
        return 0

    # 1st quadrant
    if dx >= 0 and dy >= 0:
        if dx != 0:
            rad = math.atan(abs(dy/dx))
            ang_raw = math.degrees(rad)
        else:
            ang_raw = 90
        # print('1st quadrant')
        # print(ang_raw)

    # 2nd quadrant
    elif dx < 0 and dy >= 0:
        if dy != 0:
            rad = math.atan(abs(dx/dy))
            ang_raw = math.degrees(rad) + 90
        else:
            ang_raw = 180
        # print('2nd quadrant')
        # print(ang_raw)

    # 3rd quadrant
    if dx < 0 and dy < 0:
        # print('3rd quadrant')
        rad = math.atan(abs(dy/dx))
        ang_raw = math.degrees(rad) + 180
        # print(rad)
        # print(ang_raw)
    # 4nd quadrant
    if dx >= 0 and dy < 0:
        # print('4th quadrant')
        rad = math.atan(abs(dx/dy))
        ang_raw = math.degrees(rad) + 270
        # print(rad)
        # print(ang_raw)

    ang = ang_raw % 360

    return ang


def find_dx(x, ang, distance):
    """
    Find change in x coordinate.

    Used in find_loc.
    Validated: 03/04/19.
    """
    if ang < 0 or ang >= 360:
        ang = norm_ang(ang)

    # 1st quadrant
    if ang >= 0 and ang < 90:
        dx = distance * math.cos(math.radians(ang))

    # 2nd quadrant
    elif ang >= 90 and ang < 180:
        dx = 0 - distance * math.sin(math.radians(ang - 90))

    # 3rd quadrant
    elif ang >= 180 and ang < 270:
        dx = 0 - distance * math.cos(math.radians(ang - 180))

    # 4th quadrant
    elif ang >= 270 and ang < 360:
        dx = distance * math.sin(math.radians(ang - 270))

    return dx


def find_dy(y, ang, distance):
    """
    Find change in y coordinate.

    Used in find_loc.
    Validated: 03/04/19.
    """
    if ang < 0 or ang >= 360:
        ang = norm_ang(ang)

    # 1st quadrant
    if ang >= 0 and ang < 90:
        dy = distance*math.sin(math.radians(ang))

    # 2nd quadrant
    elif ang >= 90 and ang < 180:
        dy = distance*math.cos(math.radians(ang - 90))

    # 3rd quadrant
    elif ang >= 180 and ang < 270:
        dy = 0 - distance*math.sin(math.radians(ang - 180))

    # 4th quadrant
    elif ang >= 270 and ang < 360:
        dy = 0 - distance*math.cos(math.radians(ang - 270))

    return dy


def find_loc(xy, ang, distance):
    """
    Given a point and an angle, find the new point.

    Used in all sorts of loc calculations.
    - x: current x coordinate
    - y: current y coordinate
    - ang: ang between current and new loc
    - distance between current and new loc

    Validated: 03/04/19
    """
    dx = find_dx(xy[0], ang, distance)
    dy = find_dy(xy[1], ang, distance)
    new_loc = xy[0] + dx, xy[1] + dy

    return new_loc


def norm_ang(ang_raw):
    """
    Arithmetics for angles.

    Validated: 03/05/19
    """
    if ang_raw >= 360:
        ang = ang_raw % 360
    elif ang_raw < 0:
        ang = 360 + (ang_raw % -360)
    else:
        ang = ang_raw

    return ang


def get_distance(loc1, loc2):
    """
    Get distance between two points.

    Validated: 03/05/19
    """
    distance = math.sqrt((loc1[0]-loc2[0])**2 + (loc1[1]-loc2[1])**2)
    return distance


def normalize(x, in_min=0, in_max=255, out_min=-5, out_max=5):
    """
    Normalize a list of numbers betwen 0-255.

    Right now it's really just scaling.
    """
    if x < in_min or x > in_max:
        print("Error: input exceed input range")
        raise
    scaled_x = (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

    return scaled_x
