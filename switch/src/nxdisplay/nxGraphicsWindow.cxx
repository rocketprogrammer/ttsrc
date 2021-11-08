#include "nxGraphicsWindow.h"
#include "nxGraphicsStateGuardian.h"
#include "config_nxdisplay.h"
#include "nxGraphicsPipe.h"

#include "pStatTimer.h"

#include "graphicsPipe.h"

namespace libnx {
#include <switch.h>
}

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
	printf("open_window()\n");
	
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
	
	libnx::NWindow* win = libnx::nwindowGetDefault();
	
	// Create an EGL window surface
	_egl_surface = eglCreateWindowSurface(_egl_display, nxgsg->_fbconfig, win, nullptr);	
	if (!_egl_surface) {
		printf("eglCreateWindowSurface failed\n");
		return false;
	}
	
    if (!eglMakeCurrent(_egl_display, _egl_surface, _egl_surface, nxgsg->_context)) {
		printf("eglMakeCurrent failed\n");
	}
	nxgsg->reset_if_new();
	_fb_properties = nxgsg->get_fb_properties();
	return true;
}

void nxGraphicsWindow::
close_window() {
	printf("close_window()\n");
}
