import colorsys

from math import *
from time import *

from win32api import GetAsyncKeyState
from win32con import VK_SPACE

from overlay import *
from memory import *
from structures import *


def handle_lines(local_ent, view_mtx, sc_w, sc_h, my_history=[]) -> None:
    lines = []
    if len(my_history) == 0:
        my_history.extend([local_ent.pos for _ in range(360)])
    
    my_history.insert(0, local_ent.pos)
    my_history.pop()

    for i in range(len(my_history) - 1):
        r, g, b = map(lambda e: int(e * 255), colorsys.hsv_to_rgb(i / 360, 0.6, 1))
        
        pos1 = mem.w2s(view_mtx, my_history[i], win_size=(sc_w, sc_h))
        pos2 = mem.w2s(view_mtx, my_history[i + 1], win_size=(sc_w, sc_h))
        
        if pos1 is None or pos2 is None:
            continue
        
        lines.append(
            ((pos1.x, pos1.y, pos2.x, pos2.y), (r, g, b, 255), 3)
        )
        
    overlay.add_lines(
        lines
    )


def aimbot(ents_ptrs, local_ent, local_ent_ptr):
    best = None
    
    for ent in [mem.read_entity(ent_ptr) for ent_ptr in ents_ptrs]:
        if ent.hp <= 0:
            continue
        
        if ent.head_bone.x + ent.head_bone.y + ent.head_bone.z == -3.0:
            continue
        
        x = ent.head_bone.x - local_ent.pos_cam.x
        y = ent.head_bone.y - local_ent.pos_cam.y
        z = ent.head_bone.z - local_ent.pos_cam.z
        
        angle_yaw = degrees(atan2(y, x)) % -360
        
        distance = sqrt(x ** 2 + y ** 2)
        angle_pitch = degrees(atan2(z, distance))
        
        local_ent.cam_angle.x = abs(local_ent.cam_angle.x - 360) - 90
        local_ent.cam_angle.x = (local_ent.cam_angle.x - 90) % -360
        
        mem.set_cam_angle(local_ent_ptr, (angle_yaw + 90) % 360, angle_pitch)
        break


def main():
    offset = 0
    count = 36
    last_jump = perf_counter()
    last_fire = perf_counter()
    
    while True:
        offset += 0.5 # rgb offset
        
        sc_w, sc_h = get_screen_width(), get_screen_height()
        
        local_ent_ptr = mem.get_local_player()
        local_ent = mem.read_entity(local_ent_ptr)
        view_mtx = mem.get_view_matrix()
        ents_ptrs = mem.get_entity_list()

        

        change = False
        if local_ent.hp != 1337:
            local_ent.hp = 1337
            change = True
            
        if local_ent.armor != 1337:
            local_ent.armor = 1337
            change = True
        
        if local_ent.guns.pistol != 1337 or local_ent.guns.riffle != 1337:
            local_ent.guns.pistol = 1337
            local_ent.guns.riffle = 1337
            change = True
        
        if GetAsyncKeyState(VK_SPACE):
            if local_ent.move_offset.z > -0.00030332275390625 and local_ent.move_offset.z < 0.001:
                if perf_counter() - last_jump > 0.3:
                    mem.mem.write_float(local_ent_ptr + get_offset('vel') + 0x8, 2.0)
                    last_jump = perf_counter()
        
        if round(local_ent.recoil, 3) != 0:
            if perf_counter() - last_fire > 0.05:
                if local_ent.guns.riffle_rapid or local_ent.guns.pistol_rapid:
                    mem.skip_fire_delay(local_ent_ptr)
                    last_fire = perf_counter()
                    
            local_ent.recoil = -0.8

        if change:
            mem.write_entity(local_ent_ptr, local_ent)
        
        
        handle_lines(local_ent, view_mtx, sc_w, sc_h)
        if GetAsyncKeyState(0x1):
            aimbot(ents_ptrs, local_ent, local_ent_ptr)


        
        for ent in [mem.read_entity(ent_ptr) for ent_ptr in ents_ptrs]:
            ent.pos_cam.z += (ent.pos_cam.z - ent.pos.z) * 0.18 # Назову это эмпирической формулой, а не костылём)
            if ent.hp <= 0:
                continue


            ################################# head circle
            head_pos = mem.w2s(view_mtx, ent.head_bone, win_size=(sc_w, sc_h))
            if head_pos:
                if ent.head_bone.x == -1.0 and ent.head_bone.y == -1.0:
                    head_pos = None
                else:
                    overlay.add_circle([((head_pos.x, head_pos.y), (255, 255, 255, 255))])
            ################################# head circle

            
            ################################# Bbox
            lines = []
            for x, y in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
                ent_copy = ent.__copy__()
                
                ent_copy.pos.x += x
                ent_copy.pos.y += y
                ent_copy.pos_cam.x += x
                ent_copy.pos_cam.y += y
            
                pos_top = mem.w2s(view_mtx, ent_copy.pos_cam, win_size=(sc_w, sc_h))
                pos_bottom = mem.w2s(view_mtx, ent_copy.pos, win_size=(sc_w, sc_h))
                if pos_bottom is None or pos_top is None:
                    continue

                lines.append(((pos_bottom.x, pos_bottom.y, pos_top.x, pos_top.y), overlay.lines_color, 1))

            if lines:
                for i in range(4):
                    x1, y1, x2, y2, = lines[i - 1][0]
                    xx1, yy1, xx2, yy2 = lines[i][0]
                
                    lines.append(
                        ((x1, y1, xx1, yy1), overlay.lines_color, 1)
                    )
                    lines.append(
                        ((x2, y2, xx2, yy2), overlay.lines_color, 1)
                    )
            ################################# Bbox

            
            ################################# Name
            pos_top = mem.w2s(view_mtx, ent.pos_cam, win_size=(sc_w, sc_h))
            pos_bottom = mem.w2s(view_mtx, ent.pos, win_size=(sc_w, sc_h))
            if pos_top is None or pos_bottom is None:
                continue
            

            name = f'{str(mem.decode_name(ent.name))} - {ent.hp}'
            distance = int(sqrt((local_ent.pos.x - ent.pos.x) ** 2 + (local_ent.pos.y - ent.pos.y) ** 2))
            size = int(23 * (10 / (distance + 1 * 10**10)))
            overlay.add_texts(
                [(
                    name,
                    pos_top.x - measure_text(name, size) // 2,
                    pos_top.y - int(size * 1.5),
                    size
                )]
            )
            ################################# Name
            
            
            ################################# Health line
            ent_copy = ent.__copy__()
            scale = ent.hp / 100
            world_height = ent_copy.pos_cam.z - ent_copy.pos.z
            ent_copy.pos_cam.z -= world_height - world_height * scale
            
            pos_top_copy = mem.w2s(view_mtx, ent_copy.pos_cam, win_size=(sc_w, sc_h))
            pos_bottom_copy = mem.w2s(view_mtx, ent_copy.pos, win_size=(sc_w, sc_h))
            if pos_bottom_copy is None or pos_top_copy is None:
                continue
            
            lines.append(((pos_bottom.x, pos_bottom.y, pos_top.x, pos_top.y), overlay.hp_red_color, 1))
            lines.append(((pos_bottom_copy.x, pos_bottom_copy.y, pos_top_copy.x, pos_top_copy.y), overlay.hp_green_color, 1))
            ################################# Health line
            
            
            ################################# Line To Head
            if head_pos:
                lines.append(
                    ((sc_w // 2, 0, head_pos.x, head_pos.y), overlay.lines_color, 1)
                )
            else:
                # ent.pos_cam.z += (ent.pos_cam.z - ent.pos.z) * 0.18
                lines.append(
                    ((sc_w // 2, 0, pos_top.x, pos_top.y), overlay.lines_color, 1)
                )
            ################################# Line To Head
            
            
            if head_pos:
            ################################# China hat
                for angle in range(count):
                    ent_copy = ent.__copy__()
                    
                    # First
                    r, g, b = map(lambda e: int(e * 255), colorsys.hsv_to_rgb((((angle * (360 / count)) + offset) % 360) / 360, 0.6, 1))
                    x, y = cos(radians(angle * (360 / count))), sin(radians(angle * (360 / count)))
                    ent_copy.head_bone.x += x
                    ent_copy.head_bone.y += y
                    pos_top_copy = mem.w2s(view_mtx, ent_copy.head_bone, win_size=(sc_w, sc_h))
                    if pos_top_copy is None:
                        continue
                    
                    
                    # Two
                    ent_copy = ent.__copy__()
                    
                    angle += 1
                    x, y = cos(radians(angle * (360 / count))), sin(radians(angle * (360 / count)))
                    
                    ent_copy.head_bone.x += x
                    ent_copy.head_bone.y += y
                    pos_top_copy_next = mem.w2s(view_mtx, ent_copy.head_bone, win_size=(sc_w, sc_h))
                    if pos_top_copy_next is None:
                        continue
                    
                    
                    # Center
                    ent_copy = ent.__copy__()
                    ent_copy.head_bone.z += 0.5
                    head_pos = mem.w2s(view_mtx, ent_copy.head_bone, win_size=(sc_w, sc_h))
                    if head_pos is None:
                        continue
                    
                    lines.append(
                        ((pos_top_copy.x, pos_top_copy.y, head_pos.x, head_pos.y), (r, g, b, 255), 1)
                    )
                    
                    overlay.add_triangles(
                        [
                            (
                                (
                                    (head_pos.x, head_pos.y),
                                    (pos_top_copy.x, pos_top_copy.y),
                                    (pos_top_copy_next.x, pos_top_copy_next.y)
                                ),
                                (r, g, b, 200)
                            ),
                        ]
                    )
            ################################# China hat
                
                
            overlay.add_lines(
                lines
            )

        overlay.draw()



if __name__ == '__main__':
    overlay = Overlay(
        window_name='AssaultCube',
        lines_color=(230, 230, 230, 230)
    )
    mem = Memory('ac_client.exe')
    main()
    
    