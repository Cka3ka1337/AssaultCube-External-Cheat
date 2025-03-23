import pymem

from pymem.ptypes import RemotePointer

from structures import *


class Memory:
    def __init__(self, target_process_name: str) -> None:
        self.mem = pymem.Pymem(target_process_name)
    
    
    def get_local_player(self) -> Entity:
        entity = RemotePointer(
            self.mem.process_handle,
            self.mem.base_address + Pointers.local_player
        ).value
        
        return entity
        
    
    def get_players_count(self) -> int:
        return self.mem.read_int(
            self.mem.base_address + Pointers.player_count
        )
    
    
    def get_entity_list(self) -> list:
        entity_list_ptr = RemotePointer(
            self.mem.process_handle,
            self.mem.base_address + Pointers.entity_list
        ).value
        
        count = self.get_players_count()
        
        entity_list = self.mem.read_ctype(
            entity_list_ptr,
            (ctypes.c_int * count)()
        )
        
        return entity_list[1:]

    
    def read_entity(self, entity_ptr: int) -> Entity:
        entity = self.mem.read_ctype(
            entity_ptr,
            Entity()
        )
        
        return entity

    
    def get_view_matrix(self) -> None:
        return self.mem.read_ctype(
            self.mem.base_address + Pointers.view_matrix,
            (ctypes.c_float * 16)()
        )
    
    
    def write_entity(self, entity_ptr: int, entity: Entity) -> Entity:
        return self.mem.write_ctype(
            entity_ptr,
            entity
        )
    
    
    def set_cam_angle(self, ptr: int, yaw: float, pitch: float) -> None:
        yaw_offset = get_offset('cam_angle')
        pitch_offset = get_offset('cam_angle') + 0x4

        self.mem.write_float(ptr + yaw_offset, float(yaw))
        self.mem.write_float(ptr + pitch_offset, float(pitch))


    def skip_fire_delay(self, ptr: int) -> None:
        pistol = get_offset('guns') + 0x4 * 9
        riffle = pistol + 0x4 * 5

        self.mem.write_float(ptr + pistol, 0.0)
        self.mem.write_float(ptr + riffle, 0.0)
    
    
    def decode_name(self, name: bytes) -> str:
        return ''.join(map(lambda e: chr(e) if e else '', bytes(name)))


    def w2s(self, mtx, pos: Vec3, win_size: tuple[int, int]) -> Vec2_int:
        clip = Vec3()
        ndc = Vec2()
        res = Vec2_int()
        

        clip.x = (mtx[0] * pos.x) + (mtx[4] * pos.y) + (mtx[8] * pos.z) + mtx[12]
        clip.y = (mtx[1] * pos.x) + (mtx[5] * pos.y) + (mtx[9] * pos.z) + mtx[13]
        clip.z = (mtx[2] * pos.x) + (mtx[6] * pos.y) + (mtx[10] * pos.z) + mtx[14]
        clip.w = (mtx[3] * pos.x) + (mtx[7] * pos.y) + (mtx[11] * pos.z) + mtx[15]
        
        if clip.z < 0:
            return None
        
        
        ndc.x = clip.x / clip.w
        ndc.y = clip.y / clip.w
        
        res.x = int((win_size[0] / 2 * ndc.x) + (ndc.x + win_size[0] / 2))
        res.y = int(-(win_size[1] / 2 * ndc.y) + (ndc.y + win_size[1] / 2))


        return res


'''

AssaultCube

x 0 4 8 12
y 1 5 9 13
z = (matrix[3] * pos.x) + (matrix[7] * pos.y) + (matrix[11] * pos.z) + matrix[15]

[0, 4,  8, 12]
[1, 5,  9, 13]
[2, 6, 10, 14] # Для наклонов и тп
[3, 7, 11, 15]
'''