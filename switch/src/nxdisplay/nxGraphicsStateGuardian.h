#ifndef NXGRAPHICSSTATEGUARDIAN_H
#define NXGRAPHICSSTATEGUARDIAN_H

#include "pandabase.h"
#include "nxGraphicsPipe.h"

////////////////////////////////////////////////////////////////////
//       Class : nxGraphicsStateGuardian
// Description : A tiny specialization on GLES2GraphicsStateGuardian
//               to add some egl-specific information.
////////////////////////////////////////////////////////////////////
class nxGraphicsStateGuardian : public GLESGraphicsStateGuardian {
public:
  INLINE const FrameBufferProperties &get_fb_properties() const;
  void get_properties(FrameBufferProperties &properties,
             bool &pbuffer_supported, bool &pixmap_supported,
                               bool &slow, EGLConfig config);
  void choose_pixel_format(const FrameBufferProperties &properties,
         EGLDisplay display, bool need_pbuffer, bool need_pixmap);

  nxGraphicsStateGuardian(GraphicsEngine *engine, GraphicsPipe *pipe,
         nxGraphicsStateGuardian *share_with);

  virtual ~nxGraphicsStateGuardian();

  virtual void reset();

  bool egl_is_at_least_version(int major_version, int minor_version) const;

  EGLContext _share_context;
  EGLContext _context;
  EGLDisplay _egl_display;
  EGLConfig _fbconfig;
  FrameBufferProperties _fbprops;

protected:
  virtual void query_gl_version();
  virtual void get_extra_extensions();
  virtual void *do_get_extension_func(const char *prefix, const char *name);

private:
  int _egl_version_major, _egl_version_minor;

public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    GLESGraphicsStateGuardian::init_type();
    register_type(_type_handle, "nxGraphicsStateGuardian",
                  GLESGraphicsStateGuardian::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
  static TypeHandle _type_handle;
};

#include "nxGraphicsStateGuardian.I"

#endif
