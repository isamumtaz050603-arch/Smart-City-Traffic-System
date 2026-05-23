import tkinter as tk
import random
import math


class Vehicle:
    def __init__(self, vid, path, vtype, color, canvas_id):
        self.id = vid
        self.path = path
        self.type = vtype
        self.color = color
        self.canvas_id = canvas_id
        self.segment = 0
        self.progress = 0.0
        self.start = path[0]
        self.end = path[-1]


class SmartCityApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart City Traffic System")
        self.root.geometry("1200x700")

        self.canvas = tk.Canvas(self.root, bg="#87CEEB")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = {}
        self.edges = []
        self.vehicles = []
        self.vehicle_id = 0

        self.create_map()
        self.draw_roads()
        self.create_buttons()
        self.create_info_panel()

        self.root.after(60, self.update)
        self.root.mainloop()

    
    def create_map(self):
        letters = "ABCDEFGHIJKLMNOP"
        idx = 0
        for r in range(4):
            for c in range(4):
                self.nodes[letters[idx]] = (200 + c * 250, 150 + r * 150)
                idx += 1

        for r in range(4):
            for c in range(4):
                i = r * 4 + c
                if c < 3:
                    self.edges.append((letters[i], letters[i + 1]))
                if r < 3:
                    self.edges.append((letters[i], letters[i + 4]))

    
    def create_buttons(self):
        frame = tk.Frame(self.root)
        frame.place(x=10, y=10)

        tk.Button(frame, text="Spawn Car",
                  width=15, bg="#3498db", fg="white",
                  command=self.spawn_car).pack(pady=5)

        tk.Button(frame, text="Emergency",
                  width=15, bg="#e74c3c", fg="white",
                  command=self.spawn_emergency).pack(pady=5)

    def create_info_panel(self):
        panel = tk.Frame(self.root, bg="#1e1e2e", bd=3, relief="ridge")
        panel.place(relx=1.0, rely=1.0, anchor="se", x=-15, y=-15)

        tk.Label(panel, text="Active Vehicles",
                 bg="#1e1e2e", fg="white",
                 font=("Arial", 12, "bold")).pack(padx=10, pady=5)

        self.vehicle_info = tk.StringVar()
        self.vehicle_info.set("None")

        tk.Label(panel, textvariable=self.vehicle_info,
                 bg="#1e1e2e", fg="#00ff88",
                 font=("Consolas", 10),
                 justify="left").pack(padx=10, pady=5)

    
    def draw_roads(self):
        for a, b in self.edges:
            x1, y1 = self.nodes[a]
            x2, y2 = self.nodes[b]

            self.canvas.create_line(x1, y1, x2, y2,
                                    width=26, fill="#3498db")
            self.canvas.create_line(x1, y1, x2, y2,
                                    width=4, fill="#f1c40f", dash=(20, 12))

        for n, (x, y) in self.nodes.items():
            self.canvas.create_oval(x-30, y-30, x+30, y+30,
                                    fill="#f1c40f", outline="black", width=3)
            self.canvas.create_text(x, y, text=n,
                                    fill="white", font=("Arial", 16, "bold"))

    
    def get_path(self, start, end):
        path = [start]
        sx, sy = self.nodes[start]
        ex, ey = self.nodes[end]
        cur = start

        while (sx, sy) != (ex, ey):
            for n, (nx, ny) in self.nodes.items():
                if nx == sx and abs(ny - sy) == 150 and abs(ny - ey) < abs(sy - ey):
                    cur = n
                    break
                if ny == sy and abs(nx - sx) == 250 and abs(nx - ex) < abs(sx - ex):
                    cur = n
                    break
            sx, sy = self.nodes[cur]
            if cur not in path:
                path.append(cur)

        return path

    
    def spawn_car(self):
        self.spawn_vehicle("normal")

    def spawn_emergency(self):
        self.spawn_vehicle("emergency")

    def spawn_vehicle(self, vtype):
        start, end = random.sample(list(self.nodes.keys()), 2)
        path = self.get_path(start, end)

        color = "#e74c3c" if vtype == "emergency" else random.choice(
            ["#3498db", "#f1c40f", "#9b59b6"]
        )

        x, y = self.nodes[start]
        size = 16 if vtype == "emergency" else 12

        cid = self.canvas.create_oval(
            x-size, y-size, x+size, y+size,
            fill=color, outline="white", width=2
        )

        v = Vehicle(self.vehicle_id, path, vtype, color, cid)
        self.vehicle_id += 1

        self.canvas.tag_raise(cid)
        self.vehicles.append(v)
        self.update_info_panel()

   
    def move_vehicle(self, v):
        if v.segment >= len(v.path) - 1:
            return False

        a, b = v.path[v.segment], v.path[v.segment + 1]
        x1, y1 = self.nodes[a]
        x2, y2 = self.nodes[b]

        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return False

        offset = 8 if v.type == "normal" else 12
        px, py = -dy / length * offset, dx / length * offset

        v.progress += 0.015
        x = x1 + v.progress * dx + px
        y = y1 + v.progress * dy + py

        size = 16 if v.type == "emergency" else 12
        self.canvas.coords(v.canvas_id,
                           x-size, y-size,
                           x+size, y+size)

        if v.progress >= 1:
            v.progress = 0
            v.segment += 1

        return True

    
    def update_info_panel(self):
        if not self.vehicles:
            self.vehicle_info.set("None")
            return

        lines = []
        for v in self.vehicles:
            lines.append(f"#{v.id:<2} {v.type.upper():<9} {v.start} → {v.end}")
        self.vehicle_info.set("\n".join(lines))

    
    def update(self):
        for v in self.vehicles[:]:
            if not self.move_vehicle(v):
                self.canvas.delete(v.canvas_id)
                self.vehicles.remove(v)
                self.update_info_panel()

        self.root.after(60, self.update)


if __name__ == "__main__":
    SmartCityApp()
