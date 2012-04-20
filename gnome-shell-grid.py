#!/usr/bin/env python
import Xlib
import Xlib.display

from Xlib import X, XK, Xutil

import gtk
import wnck

PANEL_HEIGHT = 26

def unmaximize(func):
    def wrapper(w, *args):
        if w.is_maximized():
            w.unmaximize()
        return func(*args)
    return wrapper

def close(a, b):
    v = sum((x-y)**2 for (x, y) in zip(a, b))
    return v < 200

def cycle(func):
    def wrapper(w, (width, height), window_size):
        possible_positions = func((width, height))
        for i, pos in enumerate(possible_positions):
            if close(pos, window_size):
                break
        return possible_positions[(i + 1) % len(possible_positions)]
    return wrapper

def full(w, (width, height), window_size):
    w.maximize()
    return 0, 0, width, height

@unmaximize
def top((width, height), window_size):
    return 0, 0, width, height / 2

@cycle
@unmaximize
def top_right((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(width-cycle, 0, cycle, height)
            for cycle in width_cycle]

@unmaximize
def right((width, height), window_size):
    return width / 2, 0, width / 2, height

@cycle
@unmaximize
def bottom_right((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(width-cycle, height, cycle, height)
            for cycle in width_cycle]

@unmaximize
def bottom((width, height), window_size):
    return 0, height / 2, width, height / 2

@cycle
@unmaximize
def bottom_left((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(0, height, cycle, height)
            for cycle in width_cycle]

@unmaximize
def left((width, height), window_size):
    return 0, 0, width / 2, height

@cycle
@unmaximize
def top_left((width, height)):
    height = height / 2
    width_cycle = [width / 2, int(width / 1.5), width / 3]
    return [(0, 0, cycle, height)
            for cycle in width_cycle]

def check_num_lock(*args):
    display = Xlib.display.Display()
    gkc = display.get_keyboard_control()
    if gkc.led_mask & 2 == 2:
        print 'WARNING: NumLock is on; your bindings may not work.'

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

KEY_MODIFIER_MASK = X.Mod1Mask | X.ControlMask | X.ShiftMask # Ctrl-Alt-Shift
PAD_MODIFIER_MASK = X.Mod1Mask | X.ControlMask # Ctrl-Alt
KEYMAP = {
    XK.XK_KP_5: full,
    XK.XK_k: top,
    XK.XK_KP_8: top,
    XK.XK_i: top_right,
    XK.XK_KP_9: top_right,
    XK.XK_l: right,
    XK.XK_KP_6: right,
    XK.XK_m: bottom_right,
    XK.XK_KP_3: bottom_right,
    XK.XK_j: bottom,
    XK.XK_KP_2: bottom,
    XK.XK_n: bottom_left,
    XK.XK_KP_1: bottom_left,
    XK.XK_h: left,
    XK.XK_KP_4: left,
    XK.XK_u: top_left,
    XK.XK_KP_7: top_left,
    XK.XK_Num_Lock: check_num_lock,
    }

def run_idle():
    while gtk.events_pending():
        gtk.main_iteration()

def main():
    display = Xlib.display.Display()
    root = display.screen().root
    root.change_attributes(event_mask = X.KeyReleaseMask)
    screen = wnck.screen_get_default()
    screen.force_update()
    (root_width, root_height) = (screen.get_width(),
                                 screen.get_height() - PANEL_HEIGHT)

    for keysym in KEYMAP:
        if keysym == XK.XK_Num_Lock:
            modifier_mask = 0
        elif keysym < XK.XK_KP_1:
            modifier_mask = KEY_MODIFIER_MASK
        else:
            modifier_mask = PAD_MODIFIER_MASK
        root.grab_key(display.keysym_to_keycode(keysym), modifier_mask, True,
                      X.GrabModeAsync, X.GrabModeAsync)

    check_num_lock()
    while True:
        event = root.display.next_event()
        run_idle()
        if event.type == X.KeyRelease:
            run_idle()
            (root_width, root_height) = (screen.get_width(),
                                         screen.get_height() - PANEL_HEIGHT)
            w = screen.get_active_window()
            for i in range(4):
                try:
                    func = KEYMAP[display.keycode_to_keysym(event.detail, i)]
                    break
                except KeyError:
                    continue
            else:
                raise
            x, y, width, height = w.get_geometry()
            y -= PANEL_HEIGHT
            g = func(w, (root_width, root_height), (x, y, width, height))
            if g is not None:
                print w.get_name(), (x, y, width, height), g
                w.set_geometry(0, 15, g[0], g[1], g[2], g[3])
            run_idle()


if __name__ == "__main__":
    main()
