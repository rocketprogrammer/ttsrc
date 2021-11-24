#include "nxGraphicsWindow.h"
#include "nxGraphicsStateGuardian.h"
#include "config_nxdisplay.h"
#include "nxGraphicsPipe.h"

#include "pStatTimer.h"

#include "graphicsPipe.h"
#include "mouseButton.h"

TypeHandle nxGraphicsWindow::_type_handle;

nxGraphicsWindow::
nxGraphicsWindow(GraphicsEngine *engine, GraphicsPipe *pipe,
                  const string &name,
                  const FrameBufferProperties &fb_prop,
                  const WindowProperties &win_prop,
                  int flags,
                  GraphicsStateGuardian *gsg,
                  GraphicsOutput *host) :
    GraphicsWindow(engine, pipe, name, fb_prop, win_prop, flags, gsg, host)
{
    nxGraphicsPipe *nx_pipe;
    DCAST_INTO_V(nx_pipe, _pipe);
    _egl_display = nx_pipe->_egl_display;
    _egl_surface = 0;
    _win = 0;
    _touchcount = 0;
    
    GraphicsWindowInputDevice device = GraphicsWindowInputDevice::pointer_and_keyboard(this, "keyboard_mouse");
    add_input_device(device);
}

nxGraphicsWindow::
~nxGraphicsWindow() {
}

bool nxGraphicsWindow::
begin_frame(FrameMode mode, Thread *current_thread) {
  PStatTimer timer(_make_current_pcollector, current_thread);

  begin_frame_spam(mode);
  if (_gsg == (GraphicsStateGuardian *)NULL) {
    return false;
  }

  nxGraphicsStateGuardian *nxgsg;
  DCAST_INTO_R(nxgsg, _gsg, false);
  {
    if (eglGetCurrentDisplay() == _egl_display &&
        eglGetCurrentSurface(EGL_READ) == _egl_surface &&
        eglGetCurrentSurface(EGL_DRAW) == _egl_surface &&
        eglGetCurrentContext() == nxgsg->_context) {
      // No need to make the context current again.  Short-circuit
      // this possibly-expensive call.
    } else {
      // Need to set the context.
      if (!eglMakeCurrent(_egl_display, _egl_surface, _egl_surface, nxgsg->_context)) {
        printf("eglMakeCurrent failed\n");
      }
    }
  }

  // Now that we have made the context current to a window, we can
  // reset the GSG state if this is the first time it has been used.
  // (We can't just call reset() when we construct the GSG, because
  // reset() requires having a current context.)
  nxgsg->reset_if_new();

  if (mode == FM_render) {
    // begin_render_texture();
    clear_cube_map_selection();
  }

  _gsg->set_current_properties(&get_fb_properties());
  return _gsg->begin_frame(current_thread);
}

void nxGraphicsWindow::
end_frame(FrameMode mode, Thread *current_thread) {
  end_frame_spam(mode);
  nassertv(_gsg != (GraphicsStateGuardian *)NULL);

  if (mode == FM_render) {
    // end_render_texture();
    copy_to_textures();
  }

  _gsg->end_frame(current_thread);

  if (mode == FM_render) {
    trigger_flip();
    if (_one_shot) {
      prepare_for_deletion();
    }
    clear_cube_map_selection();
  }
}

void nxGraphicsWindow::
begin_flip() {
    if (_gsg != (GraphicsStateGuardian *)NULL) {
        eglSwapBuffers(_egl_display, _egl_surface);
    }
}

bool nxGraphicsWindow::
open_window() {    
    nxGraphicsPipe *nx_pipe;
    DCAST_INTO_R(nx_pipe, _pipe, false);
    
    // GSG Creation/Initialization
    nxGraphicsStateGuardian *nxgsg;
    if (_gsg == 0) {
    // There is no old gsg.  Create a new one.
        nxgsg = new nxGraphicsStateGuardian(_engine, _pipe, NULL);
        nxgsg->choose_pixel_format(_fb_properties, _egl_display, false, false);
        _gsg = nxgsg;
    } else {
        // If the old gsg has the wrong pixel format, create a
        // new one that shares with the old gsg.
        DCAST_INTO_R(nxgsg, _gsg, false);
        if (!nxgsg->get_fb_properties().subsumes(_fb_properties)) {
            nxgsg = new nxGraphicsStateGuardian(_engine, _pipe, nxgsg);
            nxgsg->choose_pixel_format(_fb_properties, _egl_display, false, false);
            _gsg = nxgsg;
        }
    }
    
    _win = libnx::nwindowGetDefault();
    
    // Create an EGL window surface
    _egl_surface = eglCreateWindowSurface(_egl_display, nxgsg->_fbconfig, _win, nullptr);    
    if (!_egl_surface) {
        printf("eglCreateWindowSurface failed\n");
        return false;
    }
    
    if (!eglMakeCurrent(_egl_display, _egl_surface, _egl_surface, nxgsg->_context)) {
        printf("eglMakeCurrent failed\n");
    }
    
    // Configure our supported input layout: a single player with standard controller styles,
    // then initialize the gamepad
    libnx::padConfigureInput(1, libnx::HidNpadStyleSet_NpadStandard);
    libnx::padInitializeDefault(&_pad);
    
    // Initialize touchscreen
    libnx::hidInitializeTouchScreen();
    
    nxgsg->reset_if_new();
    _fb_properties = nxgsg->get_fb_properties();
    return true;
}

void nxGraphicsWindow::
close_window() {
    printf("close_window()\n");
}

void nxGraphicsWindow::
process_events() {
    GraphicsWindow::process_events();
    
    if (_win == NULL)
        return;
    
    if (libnx::appletMainLoop()) {
        libnx::padUpdate(&_pad);
        
        libnx::HidTouchScreenState state={0};
        if (libnx::hidGetTouchScreenStates(&state, 1)) {
            if (state.count == 0 && _touchcount != 0) {
                _input_devices[0].button_up(MouseButton::button(0));
                _input_devices[0].set_pointer_out_of_window();
                
            } else if (state.count == 1) {
                if (_touchcount != 1)
                    _input_devices[0].button_down(MouseButton::button(0));
                
                libnx::HidTouchState touch = state.touches[0];
                _input_devices[0].set_pointer_in_window(touch.x, touch.y);
            }
            
            _touchcount = state.count;
        }
        
        libnx::u64 kDown = libnx::padGetButtonsDown(&_pad);
        if (kDown & libnx::HidNpadButton_Left) {
            _input_devices[0].button_down(KeyboardButton::left());
        }
        if (kDown & libnx::HidNpadButton_Up) {
            _input_devices[0].button_down(KeyboardButton::up());
        }
        if (kDown & libnx::HidNpadButton_Right) {
            _input_devices[0].button_down(KeyboardButton::right());
        }
        if (kDown & libnx::HidNpadButton_Down) {
            _input_devices[0].button_down(KeyboardButton::down());
        }
        if (kDown & libnx::HidNpadButton_A) {
            _input_devices[0].button_down(KeyboardButton::control());
        }
        if (kDown & libnx::HidNpadButton_X) {
            _input_devices[0].button_down(KeyboardButton::del());
        }
        if (kDown & libnx::HidNpadButton_L) {
            _input_devices[0].button_down(KeyboardButton::home());
        }
        if (kDown & libnx::HidNpadButton_R) {
            _input_devices[0].button_down(KeyboardButton::end());
        }
        if (kDown & libnx::HidNpadButton_Y) {
            _input_devices[0].button_down(KeyboardButton::escape());
        }
        if (kDown & libnx::HidNpadButton_StickR) {
            _input_devices[0].button_down(KeyboardButton::tab());
        }
        
        libnx::u64 kUp = libnx::padGetButtonsUp(&_pad);
        if (kUp & libnx::HidNpadButton_Left) {
            _input_devices[0].button_up(KeyboardButton::left());
        }
        if (kUp & libnx::HidNpadButton_Up) {
            _input_devices[0].button_up(KeyboardButton::up());
        }
        if (kUp & libnx::HidNpadButton_Right) {
            _input_devices[0].button_up(KeyboardButton::right());
        }
        if (kUp & libnx::HidNpadButton_Down) {
            _input_devices[0].button_up(KeyboardButton::down());
        }
        if (kUp & libnx::HidNpadButton_A) {
            _input_devices[0].button_up(KeyboardButton::control());
        }
        if (kUp & libnx::HidNpadButton_X) {
            _input_devices[0].button_up(KeyboardButton::del());
        }
        if (kUp & libnx::HidNpadButton_L) {
            _input_devices[0].button_up(KeyboardButton::home());
        }
        if (kUp & libnx::HidNpadButton_R) {
            _input_devices[0].button_up(KeyboardButton::end());
        }
        if (kUp & libnx::HidNpadButton_Y) {
            _input_devices[0].button_up(KeyboardButton::escape());
        }
        if (kUp & libnx::HidNpadButton_StickR) {
            _input_devices[0].button_up(KeyboardButton::tab());
        }
        
    } else {
        close_window();
        
    }
}