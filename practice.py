from tkinter import *
from xml.dom import minidom
import xml.etree.cElementTree as ET
from tkinter import filedialog as fd
from PIL import Image, ImageFilter, ImageTk
import math

radius = 3
width = 1700
height = 700

class MyPolygon(object):
    def __init__(self, points, points_ids, canvas):
        self.point_radius = radius
        self.canvas = canvas

        self.points = points.copy()
        self.initial_points = []

        for point in self.points:
            self.initial_points.append([point[0], point[1]])

        self.count = len(points)

        self.lines_ids = []

        self.points_ids = points_ids.copy()

        self.draw_lines()
        self.draw_points()

        self.scale = 1

        self.angle = 0

        self.center = 0
        self.calculate_center()

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

        new_points = [self.points[0]]
        new_initial_points = [self.initial_points[0]]

        for i in range(len(self.points) - 1):
            x_offset = (self.points[i + 1][0] - self.points[i][0]) * scale / self.scale
            y_offset = (self.points[i + 1][1] - self.points[i][1]) * scale / self.scale

            new_points.append([new_points[i][0] + x_offset, new_points[i][1] + y_offset])

        for i in range(len(self.initial_points) - 1):
            x_offset = (self.initial_points[i + 1][0] - self.initial_points[i][0]) * scale / self.scale
            y_offset = (self.initial_points[i + 1][1] - self.initial_points[i][1]) * scale / self.scale

            new_initial_points.append([new_initial_points[i][0] + x_offset, new_initial_points[i][1] + y_offset])

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

        self.canvas = Canvas(width=width, height=height, background="bisque")
        self.canvas.pack(fill="both", expand=True)

        self.scale = Scale(parent, digits=3,command=self.change_scale, orient=HORIZONTAL, length=1000, from_=0.25, to=2,
                           tickinterval=0.25, resolution=0.05, label="Масштаб")

        self.rotation = Scale(parent, digits=3, command=self.rotate, orient=HORIZONTAL, length=1000, from_=-180,
                           to=180,
                           tickinterval=30, resolution=1, label="Поворот")

        self.entry = Entry(parent, width=20,bd=3)

        self.loading = Button(parent, text="Import Polygon", command= self.import_polygons)
        self.loadImage = Button(parent, text="Open IMG", command= self.open_image)

        self.entry.pack()
        self.scale.pack()
        self.rotation.pack()
        self.loading.pack()
        self.loadImage.pack()

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
            self.polygons[self._drag_data["poly_id"]].draw_points()
        else:
            self.points[self._drag_data["id"]][0] = event.x
            self.points[self._drag_data["id"]][1] = event.y

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

if __name__ == "__main__":
    root = Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()
