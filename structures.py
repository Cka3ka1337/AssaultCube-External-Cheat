import ctypes

from ctypes import wintypes


class Pointers:
    view_matrix = 0x17DFD0
    local_player = 0x18AC00
    entity_list = 0x18AC04
    player_count = 0x18AC0C


class Vec2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float)
    ]


class Vec2_int(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int)
    ]
    
    def __init__(self, x: int=0, y: int=0) -> None:
        self.x = x
        self.y = y


class Vec3(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_float),
        ('y', ctypes.c_float),
        ('z', ctypes.c_float)
    ]


class Vec4Vecs2(ctypes.Structure):
    _fields_ = [
        ('pt1', Vec2_int),
        ('pt2', Vec2_int),
        ('pt3', Vec2_int),
        ('pt4', Vec2_int)
    ]

    def __init__(self, pt1: Vec2_int, pt2: Vec2_int, pt3: Vec2_int, pt4: Vec2_int) -> None:
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3
        self.pt4 = pt4


class Guns(ctypes.Structure):
    _fields_ = [
        ('pistol', ctypes.c_int),
        ('', ctypes.c_int * 4),
        ('riffle', ctypes.c_int),
        ('', ctypes.c_int * 3),
        ('pistol_rapid', ctypes.c_float),
        ('', ctypes.c_int * 4),
        ('riffle_rapid', ctypes.c_float)
    ]


class Entity(ctypes.Structure):
    _fields_ = [
        ('', ctypes.c_int * 1),
        ('pos_cam', Vec3),
        ('vel', Vec3),
        ('move_offset', Vec3),
        ('pos', Vec3),
        ('cam_angle', Vec2),
        ('', ctypes.c_int),
        ('recoil', ctypes.c_float),
        ('', ctypes.c_int * 3),
        ('crouch_y', ctypes.c_float),
        ('crouch_y_max', ctypes.c_float),
        ('', ctypes.c_int * 37),
        ('hp', ctypes.c_int),
        ('armor', ctypes.c_int),
        ('', ctypes.c_int * 14),
        ('guns', Guns),
        ('', ctypes.c_int * 39),
        ('name', ctypes.c_byte * 16),
        ('', ctypes.c_int * 121),
        ('head_bone', Vec3)
    ]
    
    def __copy__(self):
        new_instance = Entity()
        ctypes.memmove(ctypes.byref(new_instance), ctypes.byref(self), ctypes.sizeof(Entity))
        return new_instance


class WINDOWINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcWindow', wintypes.RECT),
        ('rcClient', wintypes.RECT),
        ('dwStyle', wintypes.DWORD),
        ('dwExStyle', wintypes.DWORD),
        ('dwWindowStatus', wintypes.DWORD),
        ('cxWindowBorders', wintypes.UINT),
        ('cyWindowBorders', wintypes.UINT),
        ('atomWindowType', wintypes.ATOM),
        ('wCreatorVersion', wintypes.WORD),
    ]



def get_offset(find: str) -> None:
    fields = Entity()._fields_
    offset = 0x0

    for field in fields:
        key, data = field
        if key != find:
            size = ctypes.sizeof(data)
            offset += size
        else:
            return offset


if __name__ == '__main__':
    fields = Entity()._fields_
    find = 'guns'
    offset = 0x0

    for field in fields:
        key, data = field
        if key != find:
            size = ctypes.sizeof(data)
            offset += size
            print(key, size)
        else:
            print(hex(offset))
            break