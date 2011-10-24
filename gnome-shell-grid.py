#!/usr/bin/env python
import Xlib
import Xlib.display

from Xlib import X, XK, Xutil

import gtk
import wnck

PANEL_HEIGHT = 26

def close(a, b):
    v = sum((x-y)**2 for (x, y) in zip(a, b))
    print v
    return v < 200

def cycle(func):
    def wrapper((width, height), window_size):
        possible_positions = func((width, height))
        for i, pos in enumerate(possible_positions):
            if close(pos, window_size):
                break
        return possible_positions[(i + 1) % len(possible_positions)]
    return wrapper
    

def top((width, height), window_size):
    return 0, 0, width, height / 2

@cycle
def top_right((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(width-cycle, 0, cycle, height)
            for cycle in width_cycle]

def right((width, height), window_size):
    return width / 2, 0, width / 2, height

@cycle
def bottom_right((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(width-cycle, height, cycle, height)
            for cycle in width_cycle]

def bottom((width, height), window_size):
    return 0, height / 2, width, height / 2

@cycle
def bottom_left((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(0, height, cycle, height)
            for cycle in width_cycle]

def left((width, height), window_size):
    return 0, 0, width / 2, height

@cycle
def top_left((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(0, 0, cycle, height)
            for cycle in width_cycle]

# send_event and reset are from PyTyle
def send_event(root, win, ctype, data, mask=None):
    data = (data + ([0] * (5 - len(data))))[:5]
    ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype,
                                           data=(32, (data)))
    root.send_event(ev, event_mask=X.SubstructureRedirectMask)

def reset(display, win):
    win.set_wm_normal_hints(
        flags = Xutil.PWinGravity,
        win_gravity = X.NorthWestGravity)
    atom = lambda s: display.intern_atom(s)
    send_event(display.screen().root, win, atom("_NET_WM_STATE"),
               [0, atom("_NET_WM_STATE_MAXIMIZED_VERT"),
                atom("_NET_WM_STATE_MAXIMIZED_HORZ")])
    display.flush()
    
MODIFIER_MASK = X.Mod1Mask | X.ControlMask | X.ShiftMask # Ctrl-Alt

KEYMAP = {
    XK.XK_k: top,
    XK.XK_i: top_right,
    XK.XK_l: right,
    XK.XK_m: bottom_right,
    XK.XK_j: bottom,
    XK.XK_n: bottom_left,
    XK.XK_h: left,
    XK.XK_u: top_left,
    }

def run_idle():
    while gtk.events_pending():
        gtk.main_iteration()
    
def main():
    display = Xlib.display.Display()
    root = display.screen().root
    screen = wnck.screen_get_default()
    screen.force_update()
    (root_width, root_height) = (screen.get_width(),
                                 screen.get_height() - PANEL_HEIGHT)

    for keysym in KEYMAP:
        root.grab_key(display.keysym_to_keycode(keysym), MODIFIER_MASK, True,
                      X.GrabModeAsync, X.GrabModeAsync)
    while True:
        event = root.display.next_event()
        run_idle()
        if event.type == X.KeyRelease:
            run_idle()
            w = screen.get_active_window()
            func = KEYMAP[display.keycode_to_keysym(event.detail, 0)]
            x, y, width, height = w.get_geometry()
            y -= PANEL_HEIGHT
            g = func((root_width, root_height), (x, y, width, height))
            print w.get_name(), (x, y, width, height), g
            w.set_geometry(0, 15, g[0], g[1], g[2], g[3])
            run_idle()


if __name__ == "__main__":
    main()
