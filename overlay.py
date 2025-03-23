import threading

import win32gui

from pyray import *

from structures import *


class Overlay:
    def __init__(self,
            window_name: str,
            name_size: int=36,
            name_color: tuple[int, int, int, int]=(255, 255, 255, 255),
            lines_color: tuple[int, int, int, int]=(255, 255, 255, 255),
            bbox_color: tuple[int, int, int, int]=(255, 255, 255, 255)) -> None:
        
        self.name_size = name_size
        self.name_color = name_color
        
        self.hp_green_color = (20, 240, 20, 255)
        self.hp_red_color = (240, 20, 20, 255)
        self.lines_color = lines_color
        self.bbox_color = bbox_color
        
        self.running = True
        self.target_window_hwnd = win32gui.FindWindow(None, window_name)
        
        self.__lines = []
        self.__bboxes = []
        self.__texts = []
        self.__polygons = []
        self.__triangles = []
        self.__circles = []
        
        self.__set_config()
        init_window(640, 480, f'{window_name} overlay')

        threading.Thread(target=self.__thr, daemon=False).start()
    
    
    def add_lines(self, lines: list[tuple[int, int, int, int]]) -> None:
        self.__lines.extend(lines)
    
    
    def add_bbox(self, bboxes: list[tuple[int, int, int, int]]) -> None:
        self.__bboxes.extend(bboxes)
    
    
    def add_texts(self, texts: list[tuple[str, int, int]]) -> None:
        self.__texts.extend(texts)
        
    
    def add_polygons(self, polygons: list[Vec4Vecs2]) -> None:
        self.__polygons.extend(polygons)
    
    
    def add_triangles(self, triangles: list[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int, int, int]]) -> None:
        self.__triangles.extend(triangles)
    
    
    def add_circle(self, circles: list) -> None:
        self.__circles.extend(circles)
    
    
    def __set_config(self) -> None:
        set_target_fps(0)
        set_config_flags(ConfigFlags.FLAG_WINDOW_UNDECORATED)
        set_config_flags(ConfigFlags.FLAG_WINDOW_MOUSE_PASSTHROUGH)
        set_config_flags(ConfigFlags.FLAG_WINDOW_TRANSPARENT)
        set_config_flags(ConfigFlags.FLAG_WINDOW_TOPMOST)
    
    
    def __get_window_info(self):
        win_info = WINDOWINFO()
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowInfo(self.target_window_hwnd, ctypes.byref(win_info))
        ctypes.windll.user32.GetClientRect(self.target_window_hwnd, ctypes.byref(rect))
        return (win_info.rcClient.left, win_info.rcClient.top, rect.right, rect.bottom)
    
    
    def __thr(self) -> None:
        prev = (0, 0, 0, 0)
        while self.running:
            x, y, w, h = self.__get_window_info()
            if (x, y, w, h) != prev:
                set_window_position(x, y)
                set_window_size(w, h)
                prev = (x, y, w, h)
                
    
    def draw_polygon(self, vec: Vec4Vecs2, color: tuple) -> None:
        draw_triangle(
            (vec.pt2.x, vec.pt2.y),
            (vec.pt1.x, vec.pt1.y),
            (vec.pt3.x, vec.pt3.y),
            color
        )

        draw_triangle(
            (vec.pt4.x, vec.pt4.y),
            (vec.pt2.x, vec.pt2.y),
            (vec.pt3.x, vec.pt3.y),
            color
        )
    
    
    def draw(self) -> None:
        begin_drawing()

        clear_background((0, 0, 0, 0))
        
        
        for line, color, width in self.__lines:
            draw_line_ex(
                line[:2],
                line[2:],
                width,
                color
            )
            
        for bbox in self.__bboxes:
            draw_rectangle(
                *bbox,
                self.bbox_color
            )
        
        for text, x, y, size in self.__texts:
            draw_text(
                text,
                x, y,
                size,
                self.name_color
            )
        
        
        for polygon, color in self.__polygons:
            self.draw_polygon(
                polygon,
                color
            )
        
        
        for pts, color in self.__triangles:
            draw_triangle(
                *pts,
                color
            )
        
        for pos, color in self.__circles:
            draw_circle(
                *pos,
                5,
                color
            )

        draw_fps(3, 3)
        end_drawing()
        
        self.__lines = []
        self.__bboxes = []
        self.__texts = []
        self.__polygons = []
        self.__triangles = []
        self.__circles = []