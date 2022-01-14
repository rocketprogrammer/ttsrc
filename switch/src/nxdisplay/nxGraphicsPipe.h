// Filename: nxGraphicsPipe.h
// Created by:  pro-rsoft (21May09)
//
////////////////////////////////////////////////////////////////////
//
// PANDA 3D SOFTWARE
// Copyright (c) Carnegie Mellon University.  All rights reserved.
//
// All use of this software is subject to the terms of the revised BSD
// license.  You should have received a copy of this license along
// with this source code in a file named "LICENSE."
//
////////////////////////////////////////////////////////////////////

#ifndef NXGRAPHICSPIPE_H
#define NXGRAPHICSPIPE_H

#include "pandabase.h"
#include "graphicsWindow.h"
#include "graphicsPipe.h"
#include "lightMutex.h"
#include "lightReMutex.h"

#include "glgsg.h"

#include <EGL/egl.h>
#include <EGL/eglext.h> // EGL extensions

class FrameBufferProperties;

class nxGraphicsWindow;

////////////////////////////////////////////////////////////////////
//       Class : nxGraphicsPipe
// Description : This graphics pipe represents the interface for
//               creating OpenGL ES graphics windows on an X-based
//               (e.g. Unix) client.
////////////////////////////////////////////////////////////////////
class nxGraphicsPipe : public GraphicsPipe {
public:
  nxGraphicsPipe(const string &display = string());
  virtual ~nxGraphicsPipe();

  virtual string get_interface_name() const;
  static PT(GraphicsPipe) pipe_constructor();
  
  virtual PreferredWindowThread get_preferred_window_thread() const;

protected:
  virtual PT(GraphicsOutput) make_output(const string &name,
                                         const FrameBufferProperties &fb_prop,
                                         const WindowProperties &win_prop,
                                         int flags,
                                         GraphicsEngine *engine,
                                         GraphicsStateGuardian *gsg,
                                         GraphicsOutput *host,
                                         int retry,
                                         bool &precertify);
										 
private:
  EGLDisplay _egl_display;

public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    GraphicsPipe::init_type();
    register_type(_type_handle, "nxGraphicsPipe",
                  GraphicsPipe::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
  static TypeHandle _type_handle;

  friend class nxGraphicsWindow;
  
};

#endif
