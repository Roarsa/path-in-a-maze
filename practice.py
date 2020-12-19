from tkinter import *
from xml.dom import minidom
import xml.etree.cElementTree as ET
from tkinter import filedialog as fd
from PIL import Image, ImageFilter, ImageTk
import math

class MyPolygon(object):
    def __init__(self, points, points_ids, canvas):
        self.canvas = canvas

        self.points = points.copy()
        self.initial_points = []

        for point in self.points:
            self.initial_points.append([point[0], point[1]])

        self.count = len(points)

        self.lines_ids = []

        self.points_ids = points_ids.copy()

        self.draw_lines()

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
                self.points[point_id][0] - 10,
                self.points[point_id][1] - 10,
                self.points[point_id][0] + 10,
                self.points[point_id][1] + 10,
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
            x_condition = self.points[i][0] - 10 <= point[0] and self.points[i][0] + 10 >= point[0]
            y_condition = self.points[i][1] - 10 <= point[1] and self.points[i][1] + 10 >= point[1]

            if x_condition and y_condition:
                return i

        return -1

    def get_points(self):
        return self.points

    def set_scale(self, scale):
        if scale == self.scale:
            return

        new_points = [self.points[0]]

        for i in range(len(self.points) - 1):
            x_offset = (self.points[i + 1][0] - self.points[i][0]) * scale / self.scale
            y_offset = (self.points[i + 1][1] - self.points[i][1]) * scale / self.scale

            new_points.append([new_points[i][0] + x_offset, new_points[i][1] + y_offset])

        self.points = new_points
        self.scale = scale

        self.draw_points()
        self.draw_lines()

    def rotation(self, angle):
        self.angle = angle
        for i in range(self.count):
            self.points[i][0] = self.center[0] + (self.initial_points[i][0] - self.center[0]) * math.cos(angle) - (
                    self.initial_points[i][1] - self.center[1]) * math.sin(angle)
            self.points[i][1] = self.center[1] + (self.initial_points[i][0] - self.center[0]) * math.sin(
                angle) + (self.initial_points[i][1] - self.center[1]) * math.cos(angle)

        self.draw_points()
        self.draw_lines()

    def calculate_center(self):
        summa_x = 0
        summa_y = 0

        for i in range(self.count):
            summa_x += self.points[i][0]
            summa_y += self.points[i][1]

        self.center = [summa_x // self.count, summa_y // self.count]


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.poly = None
        self.is_created_poly = False
        self.points = []
        self.points_ids = []

        self.canvas = Canvas(width=1280, height=520, background="bisque")
        self.canvas.pack(fill="both", expand=True)

        self.scale = Scale(parent, digits=3,command=self.change_scale, orient=HORIZONTAL, length=1000, from_=0.25, to=2,
                           tickinterval=0.25, resolution=0.05, label="Масштаб")

        self.rotation = Scale(parent, digits=3, command=self.rotate, orient=HORIZONTAL, length=1000, from_=-180,
                           to=180,
                           tickinterval=30, resolution=1, label="Поворот")
        self.loading = Button(parent, text="Import Polygon", command= self.import_poly)
        self.loadImage = Button(parent, text="Open IMG", command= self.openImage)
        self.loading.pack()
        self.loadImage.pack()

        self._drag_data = {"x": 0, "y": 0, "item": None, "id": -1, "is_poly": False}

        self.canvas.tag_bind("point", "<ButtonPress-3>", self.drag_start)
        self.canvas.tag_bind("point", "<ButtonRelease-3>", self.drag_stop)
        self.canvas.tag_bind("point", "<B3-Motion>", self.drag)
        self.canvas.tag_bind("point", "<ButtonPress-2>", self.create_poly)
        self.canvas.bind("<Button-1>", self.create_point)

    def create_point(self, event):
        """Create a token at the given coordinate in the given color"""
        print("Created!")
        color = "#0000FF"

        if self.is_created_poly:
            color = "#00FF00" if self.localization([event.x, event.y]) else "#FF0000"

        self.points.append([event.x, event.y, color])
        self.points_ids.append(self.canvas.create_oval(
            event.x - 10,
            event.y - 10,
            event.x + 10,
            event.y + 10,
            outline=color,
            fill=color,
            tags=("point")
        ))

    def create_poly(self, event):
        if not self.is_created_poly:
            self.is_created_poly = True

            self.poly = MyPolygon(self.points, self.points_ids, self.canvas)

            self.points = []
            self.points_ids = []

            self.scale.pack()
            self.rotation.pack()

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        if self.is_intersection([event.x, event.y]) != -1:
            self._drag_data["id"] = self.is_intersection([event.x, event.y])
            self._drag_data["is_poly"] = False
        else:
            self._drag_data["is_poly"] = True
            self._drag_data["id"] = self.poly.is_intersection([event.x, event.y])

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        if self._drag_data["is_poly"]:
            self.poly.set_vertex(self._drag_data["id"], [event.x, event.y])
        else:
            self.points[self._drag_data["id"]][0] = event.x
            self.points[self._drag_data["id"]][1] = event.y

        self._drag_data["item"] = None
        self._drag_data["id"] = -1
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["is_poly"] = False

        self.recalculate_colors()

    def drag(self, event):
        """Handle dragging of an object"""
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        self.canvas.move(self._drag_data["item"], delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        if self._drag_data["is_poly"]:
            self.poly.get_points()[self._drag_data["id"]] = [event.x, event.y]
            self.poly.draw_lines()
        else:
            self.points[self._drag_data["id"]][0] = event.x
            self.points[self._drag_data["id"]][1] = event.y

    def is_intersection(self, point):
        for i in range(len(self.points)):
            x_condition = self.points[i][0] - 10 <= point[0] and self.points[i][0] + 10 >= point[0]
            y_condition = self.points[i][1] - 10 <= point[1] and self.points[i][1] + 10 >= point[1]

            if x_condition and y_condition:
                return i

        return -1

    def localization(self, point):
        x = point[0]
        y = point[1]

        neighbors = []

        vertexes = self.poly.get_points()

        count = len(vertexes)

        for i in range(count):
            x1 = vertexes[i][0]
            x2 = vertexes[(i + 1) % count][0]
            y1 = vertexes[i][1]
            y2 = vertexes[(i + 1) % count][1]

            if y2 > y and y1 <= y or y1 > y and y2 <= y:
                neighbors.append(((x1-x2) * y + x2 * y1 - x1 * y2)/(y1 - y2))

        if len(neighbors) < 2:
            return False
        else:
            left = []
            right = []

            for i in range(len(neighbors)):
                if x > neighbors[i]:
                    left.append(neighbors[i])
                elif x < neighbors[i]:
                    right.append(neighbors[i])

            if len(left) == len(right):
                if len(left) % 2:
                    return True
                else:
                    return False
            else:
                if len(left) % 2:
                    return True

                return False

    def change_color(self, id, color):
        self.canvas.itemconfig(id, fill=color, outline=color)

    def recalculate_colors(self):
        for i in range(len(self.points)):
            predicted_color = "#00FF00" if self.localization(self.points[i]) else "#FF0000"

            if self.points[i][2] != predicted_color:
                self.change_color(self.points_ids[i], predicted_color)
                self.points[i][2] = predicted_color

    def change_scale(self, event):
        self.poly.set_scale(float(event))

        self.recalculate_colors()

    def rotate(self, event):
        self.poly.rotation(math.pi * int(event) / 180)

        self.recalculate_colors()

    def openImage(self):
        path = fd.askopenfilename()
 
        openUserImage = Image.open(path)
 
        print(openUserImage.size)
     
        userImage = ImageTk.PhotoImage(openUserImage)
     
        self.canvas.image = userImage
        self.canvas.create_image(375, 275, image=userImage)


    def import_poly(self):
        color = "#0000FF"
        file_name = fd.askopenfilename()
        tree = ET.ElementTree(file=file_name)
        root = tree.getroot()
        for child_of_root in root:
            for plygons in child_of_root:
                self.points.append([int(plygons.attrib['x']), int(plygons.attrib['y']), color])
                self.points_ids.append(self.canvas.create_oval(
                    int(plygons.attrib['x']) - 10,
                    int(plygons.attrib['y']) - 10,
                    int(plygons.attrib['x']) + 10,
                    int(plygons.attrib['y']) + 10,
                    outline=color,
                    fill=color,
                    tags=("point")
                ))
            self.poly = MyPolygon(self.points, self.points_ids, self.canvas)

if __name__ == "__main__":
    root = Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()
    
