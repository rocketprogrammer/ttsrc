#ifndef NXGRAPHICSWINDOW_H
#define NXGRAPHICSWINDOW_H

#include "pandabase.h"

#include "nxGraphicsPipe.h"
#include "graphicsWindow.h"

namespace libnx {
#include <switch.h>
}

class nxGraphicsWindow : public GraphicsWindow {
public:
  nxGraphicsWindow(GraphicsEngine *engine, GraphicsPipe *pipe,
                    const string &name,
                    const FrameBufferProperties &fb_prop,
                    const WindowProperties &win_prop,
                    int flags,
                    GraphicsStateGuardian *gsg,
                    GraphicsOutput *host);
  virtual ~nxGraphicsWindow();

  virtual bool begin_frame(FrameMode mode, Thread *current_thread);
  virtual void end_frame(FrameMode mode, Thread *current_thread);
  virtual void begin_flip();
  
  virtual void process_events();
  
protected:
  virtual void close_window();
  virtual bool open_window();

private:
  EGLDisplay _egl_display;
  EGLSurface _egl_surface;
  
  libnx::NWindow* _win;
  libnx::PadState _pad;
  libnx::s32 _touchcount;

public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    GraphicsWindow::init_type();
    register_type(_type_handle, "nxGraphicsWindow",
                  GraphicsWindow::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
  static TypeHandle _type_handle;
};

#endif
