#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from xml.dom import minidom
import xml.etree.cElementTree as ET
from tkinter import filedialog as fd
from PIL import Image, ImageFilter, ImageTk
import math
from utils import *

radius = 3
width = 1200
height = 500

class MyPolygon(object):
    def __init__(self, points, points_ids, canvas):
        self.point_radius = radius
        self.canvas = canvas

        self.points = points.copy()
        self.initial_points = []

        for point in self.points:
            self.initial_points.append([point[0], point[1]])

        self.boundary_points = self.get_boundary_points(self.initial_points)
        print(self.boundary_points)

        self.count = len(points)

        self.lines_ids = []

        self.points_ids = points_ids.copy()

        self.draw_lines()
        self.draw_points()

        self.scale = 1

        self.angle = 0

        self.center = 0
        self.calculate_center()

    def get_boundary_points(self, points):
        n = len(points)
        min_point = points[0]
        result = []

        for i in range(1,n):
            if points[i][1] == min_point[1] and  min_point[0] > points[i][0]:
                min_point = points[i]
            elif points[i][1] > min_point[1]:
                min_point = points[i]

        result.append(min_point)

        far_point = None
        point = min_point
        while far_point is not min_point:
            p1 = None
            for p in points:
                if p is point:
                    continue
                else:
                    p1 = p
                    break
            far_point = p1

            for p2 in points:
                if p2 is point or p2 is p1:
                    continue
                else:
                    direction = get_orientation(point, far_point, p2)
                    if direction > 0:
                        far_point = p2
            point = far_point
            result.append(far_point)
        return result[:len(result)-1]

    def draw_lines(self):
        for line in self.lines_ids:
            self.canvas.delete(line)

        self.lines_ids = []

        for point_id in range(self.count):
            self.lines_ids.append(self.canvas.create_line(self.points[point_id][0],
                           self.points[point_id][1],
                           self.points[(point_id + 1) % self.count][0],
                           self.points[(point_id + 1) % self.count][1]))

    def draw_points(self):
        for point in self.points_ids:
            self.canvas.delete(point)

        self.points_ids = []

        for point_id in range(self.count):
            self.points_ids.append(self.canvas.create_oval(
                self.points[point_id][0] - self.point_radius,
                self.points[point_id][1] - self.point_radius,
                self.points[point_id][0] + self.point_radius,
                self.points[point_id][1] + self.point_radius,
                outline="#0000FF",
                fill="#0000FF",
                tags=("point")
            ))
        
        for point_id in range(len(self.boundary_points)):
            self.canvas.create_oval(
                self.boundary_points[point_id][0] - self.point_radius,
                self.boundary_points[point_id][1] - self.point_radius,
                self.boundary_points[point_id][0] + self.point_radius,
                self.boundary_points[point_id][1] + self.point_radius,
                outline="green",
                fill="green",
                tags=("point")
            )

    def set_vertex(self, id, point):
        self.points[id] = point.copy()

        self.draw_lines()
        self.draw_points()

    def is_intersection(self, point):
        for i in range(self.count):
            x_condition = self.points[i][0] - self.point_radius <= point[0] and self.points[i][0] + self.point_radius >= point[0]
            y_condition = self.points[i][1] - self.point_radius <= point[1] and self.points[i][1] + self.point_radius >= point[1]

            if x_condition and y_condition:
                return i

        return -1

    def get_points(self):
        return self.points

    def set_scale(self, scale):
        if scale == self.scale:
            return

        new_points = []
        new_initial_points = []

        for i in range(len(self.points)):
            x_offset = (self.points[i][0] - self.center[0]) * scale / self.scale
            y_offset = (self.points[i][1] - self.center[1]) * scale / self.scale

            new_points.append([self.center[0] + x_offset, self.center[1] + y_offset])

        for i in range(len(self.initial_points)):
            x_offset = (self.initial_points[i][0] - self.center[0]) * scale / self.scale
            y_offset = (self.initial_points[i][1] - self.center[1]) * scale / self.scale

            new_initial_points.append([self.center[0] + x_offset, self.center[1] + y_offset])

        self.initial_points = new_initial_points
        self.points = new_points
        self.scale = scale

        self.calculate_center()

        self.draw_lines()
        self.draw_points()

    def rotation(self, angle):
        self.angle = angle
        for i in range(self.count):
            self.points[i][0] = self.center[0] + (self.initial_points[i][0] - self.center[0]) * math.cos(angle) - (
                    self.initial_points[i][1] - self.center[1]) * math.sin(angle)
            self.points[i][1] = self.center[1] + (self.initial_points[i][0] - self.center[0]) * math.sin(
                angle) + (self.initial_points[i][1] - self.center[1]) * math.cos(angle)

        self.draw_lines()
        self.draw_points()

    def calculate_center(self):
        summa_x = 0
        summa_y = 0

        for i in range(self.count):
            summa_x += self.points[i][0]
            summa_y += self.points[i][1]

        self.center = [summa_x // self.count, summa_y // self.count]


class Example(Frame):
    def __init__(self, parent):
        self.bg_id = -1
        self.point_radius = radius

        Frame.__init__(self, parent)

        self.polygons = []

        # True - Кликаем точки А и Б, False - Создаем полигон
        self.mode = False
        self.points = []
        self.points_ids = []
        self.matrix = []

        self.canvas = Canvas(width=width, height=height, background="bisque")
        # self.canvas.pack(fill="both", expand=True)
        self.canvas.grid(row=0, column=0, columnspan=3)


        self.scale = Scale(parent, digits=3,command=self.change_scale, orient=HORIZONTAL, length=550, from_=0.25, to=2,
                           tickinterval=0.25, resolution=0.05, label="Масштаб")
        self.scale.set(1)

        self.rotation = Scale(parent, digits=3, command=self.rotate, orient=HORIZONTAL, length=550, from_=-180,
                           to=180,
                           tickinterval=30, resolution=1, label="Поворот")

        self.entry = Entry(parent, width=20,bd=3)

        self.loading = Button(parent, text="Import Polygon", command= self.import_polygons, width=20, height=2)
        self.loadImage = Button(parent, text="Open IMG", command= self.open_image, width=20, height=2)
<<<<<<< HEAD
        self.findPath = Button(parent, text="Find path", command= self.find_path, width=20, height=2)
=======
        self.export = Button(parent, text="Export Polygons", command= self.export_polygons, width=20, height=2)
>>>>>>> export_xml

        self.entry.grid(row=1, column=0, sticky=W)
        self.loading.grid(row=1, column=1, sticky=W)
        self.export.grid(row=3, column=1, sticky=W)
        self.scale.grid(row=2, column=0, columnspan=2, sticky=W)
        self.loadImage.grid(row=2, column=1, sticky=W)
        self.rotation.grid(row=3, column=0, columnspan=2, sticky=W)
        self.findPath.grid(row=1, column=5, sticky=W)

        # self.entry.pack()
        # self.scale.pack()
        # self.rotation.pack()
        # self.loading.pack()
        # self.loadImage.pack()


        self._drag_data = {"x": 0, "y": 0, "item": None, "id": -1, "is_poly": False, "poly_id": -1}

        self.canvas.tag_bind("point", "<ButtonPress-3>", self.drag_start)
        self.canvas.tag_bind("point", "<ButtonRelease-3>", self.drag_stop)
        self.canvas.tag_bind("point", "<B3-Motion>", self.drag)
        self.canvas.bind("<ButtonPress-2>", self.finish_poly)
        self.canvas.bind("<Button-1>", self.create_point)

    def finish_poly(self, event):
        if len(self.points) > 2:
            self.create_poly(self.points, self.points_ids)

            self.points = []
            self.points_ids = []

    def create_point(self, event):
        """Create a token at the given coordinate in the given color"""
        color = "#00FF00" if self.mode else "#0000FF"

        self.points.append([event.x, event.y, color])
        self.points_ids.append(self.canvas.create_oval(
            event.x - self.point_radius,
            event.y - self.point_radius,
            event.x + self.point_radius,
            event.y + self.point_radius,
            outline=color,
            fill=color,
            tags=("point")
        ))

    def create_poly(self, points, points_ids):
        if len(points) > 2:
            current_poly = MyPolygon(points, points_ids, self.canvas)

            self.polygons.append(current_poly)

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        id = self.canvas.find_closest(event.x, event.y)[0]

        if self.bg_id != id:
            self._drag_data["item"] = id
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

            if self.is_intersection([event.x, event.y]) != -1:
                self._drag_data["id"] = self.is_intersection([event.x, event.y])
                self._drag_data["is_poly"] = False
            else:
                self._drag_data["is_poly"] = True
                for poly_id in range(len(self.polygons)):
                    point_id = self.polygons[poly_id].is_intersection([event.x, event.y])

                    if point_id > -1:
                        self._drag_data["poly_id"] = poly_id
                        self._drag_data["id"] = point_id
                        break

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        if self._drag_data["is_poly"]:
            self.polygons[self._drag_data["poly_id"]].set_vertex(self._drag_data["id"], [event.x, event.y])
        else:
            self.points[self._drag_data["id"]][0] = event.x
            self.points[self._drag_data["id"]][1] = event.y

        self._drag_data["item"] = None
        self._drag_data["id"] = -1
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["is_poly"] = False
        self._drag_data["poly_id"] = -1

    def drag(self, event):
        """Handle dragging of an object"""
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        self.canvas.move(self._drag_data["item"], delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        if self._drag_data["is_poly"]:
            self.polygons[self._drag_data["poly_id"]].get_points()[self._drag_data["id"]] = [event.x, event.y]
            self.polygons[self._drag_data["poly_id"]].draw_lines()
        else:
            self.points[self._drag_data["id"]][0] = event.x
            self.points[self._drag_data["id"]][1] = event.y

    # Algorithm 

    def find_path(self):
        def intersection(polygons, edge):
            for polygon in polygons:
                length = len(polygon.points)
                for point_id in range(length):
                    line = [polygon.points[point_id], polygon.points[(point_id + 1) % length]]
                    if (line_intersect(edge, line)):
                        return False
            return True
        
        def distance(point1, point2):
            return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        
        all_points = [self.points[0]]
        for polygon in self.polygons:
            all_points += polygon.points
        all_points += [self.points[1]]

        print(self.points)
        
        length = len(all_points)
        matrix = [[10 ** 10 for column in range(length)]  
                    for row in range(length)]

        for point_id in range(length):
            for point_id2 in range(point_id, length):
                if (intersection(self.polygons, [all_points[point_id], all_points[point_id2]])):
                    print('intersect')
                    matrix[point_id2][point_id] = distance(all_points[point_id], all_points[point_id2])
                    matrix[point_id][point_id2] = matrix[point_id2][point_id]

        print(matrix)

        def dijkstra(start, n, w):
            INF = 10 ** 10
            dist = [INF] * n
            dist[start] = 0
            prev = [None] * n
            used = [False] * n
            min_dist = 0
            min_vertex = start
            while min_dist < INF:
                i = min_vertex 
                used[i] = True 
                for j in range(n): 
                    if dist[i] + w[i][j] < dist[j]: 
                        dist[j] = dist[i] + w[i][j]
                        prev[j] = i
                min_dist = INF
                for j in range(n):
                    if not used[j] and dist[j] < min_dist:
                        min_dist = dist[j]
                        min_vertex = j
            path = []
            while j is not None:
                path.append(j)
                j = prev[j]
            path = path[::-1]
            print(path)
            return path

        res = dijkstra(0, length, matrix)

        for i in res:
            self.canvas.create_oval(
            all_points[i][0] - self.point_radius,
            all_points[i][1] - self.point_radius,
            all_points[i][0] + self.point_radius,
            all_points[i][1] + self.point_radius,
            outline="red",
            fill="red",
            tags=("point")
            )
        
        for i in range(len(res)-1):
            right_index = (i + 1) % len(res)
            self.canvas.create_line(all_points[res[i]][0],
                all_points[res[i]][1],
                all_points[res[right_index]][0],
                all_points[res[right_index]][1],
                fill="red")


    # TODO: Refactor?
    def is_intersection(self, point):
        for i in range(len(self.points)):
            x_condition = self.points[i][0] - self.point_radius <= point[0] and self.points[i][0] + self.point_radius >= point[0]
            y_condition = self.points[i][1] - self.point_radius <= point[1] and self.points[i][1] + self.point_radius >= point[1]

            if x_condition and y_condition:
                return i

        return -1

    def change_scale(self, event):
        if self.entry.get():
            self.polygons[int(self.entry.get())].set_scale(float(event))

    def rotate(self, event):
        if self.entry.get():
            self.polygons[int(self.entry.get())].rotation(math.pi * int(event) / 180)

    def open_image(self):
        path = fd.askopenfilename()

        openUserImage = Image.open(path)

        userImage = ImageTk.PhotoImage(openUserImage)

        self.canvas.image = userImage
        self.bg_id = self.canvas.create_image(width // 2, height // 2, image=userImage, tags=["image"])
        self.canvas.tag_lower("image")

    def import_polygons(self):
        color = "#0000FF"

        file_name = fd.askopenfilename()
        tree = ET.ElementTree(file=file_name)

        for polygon in tree.getroot():
            points = []
            points_ids = []
            for point in polygon:
                points.append([int(point.attrib['x']), int(point.attrib['y']), color])
                points_ids.append(self.canvas.create_oval(
                    int(point.attrib['x']) - self.point_radius,
                    int(point.attrib['y']) - self.point_radius,
                    int(point.attrib['x']) + self.point_radius,
                    int(point.attrib['y']) + self.point_radius,
                    outline=color,
                    fill=color,
                    tags=("point")
                ))

            self.create_poly(points, points_ids)
    def export_polygons(self):
        file_name = fd.asksaveasfilename()
        root = ET.Element("polygons")
        for _polygon in self.polygons:
            polygon = ET.Element("polygon")
            root.append(polygon)
            for _point in _polygon.points:
                point = ET.SubElement(polygon, "point")
                point.attrib['x'] = str(_point[0])
                point.attrib['y'] = str(_point[1])
        tree = ET.ElementTree(root)
        tree.write(file_name)

if __name__ == "__main__":
    print(line_intersect([[1,2], [3,4]], [[1,3], [3,5]]))
    print(line_intersect([[3,4], [1,2]], [[4,5], [1,2]]))
    print(line_intersect([[0,0], [5,5]], [[0,5], [5,0]]))
    print(line_intersect([[5,5], [0,0]], [[0,5], [5,0]]))
    root = Tk()
    r = Example(root)
    # Example(root).pack(fill="both", expand=True)
    r.grid()
    root.mainloop()
