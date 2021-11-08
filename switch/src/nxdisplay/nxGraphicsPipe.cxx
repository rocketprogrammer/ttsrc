#include "nxGraphicsPipe.h"
#include "nxGraphicsWindow.h"
#include "nxGraphicsStateGuardian.h"
#include "config_nxdisplay.h"
#include "frameBufferProperties.h"

TypeHandle nxGraphicsPipe::_type_handle;


nxGraphicsPipe::
nxGraphicsPipe(const string &display) {
	_supported_types = OT_window | OT_buffer | OT_texture_buffer;
	_is_valid = true;
	
	_egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
	
	if (!eglInitialize(_egl_display, NULL, NULL)) {
		printf("eglInitialize failed\n");
	}
	if (!eglBindAPI(EGL_OPENGL_ES_API)) {
		printf("eglBindAPI failed\n");
	}
}

nxGraphicsPipe::
~nxGraphicsPipe() {
	if (_egl_display) {
		if (!eglTerminate(_egl_display)) {
			printf("eglTerminate failed\n");
			return;
		}
	}
}

string nxGraphicsPipe::
get_interface_name() const {
  return "OpenGL ES (NX)";
}

PT(GraphicsPipe) nxGraphicsPipe::
pipe_constructor() {
	return new nxGraphicsPipe;
}

GraphicsPipe::PreferredWindowThread
nxGraphicsPipe::get_preferred_window_thread() const {
	return PWT_draw;
}


PT(GraphicsOutput) nxGraphicsPipe::
make_output(const string &name,
            const FrameBufferProperties &fb_prop,
            const WindowProperties &win_prop,
            int flags,
            GraphicsEngine *engine,
            GraphicsStateGuardian *gsg,
            GraphicsOutput *host,
            int retry,
            bool &precertify) {	

	printf("making output\n");
	if (!_is_valid) {
		return NULL;
	}
  
	nxGraphicsStateGuardian *nxgsg = 0;
	if (gsg != 0) {
		DCAST_INTO_R(nxgsg, gsg, NULL);
	}

	bool support_rtt;
	support_rtt = false;
	if (nxgsg) {
		support_rtt = 
			nxgsg -> get_supports_render_texture() && 
			support_render_texture;
	}

	// First thing to try: a nxGraphicsWindow
	if (retry == 0) {
		printf("trying nxgraph window\n");
		if (((flags&BF_require_parasite)!=0)||
				((flags&BF_refuse_window)!=0)||
				((flags&BF_resizeable)!=0)||
				((flags&BF_size_track_host)!=0)||
				((flags&BF_rtt_cumulative)!=0)||
				((flags&BF_can_bind_color)!=0)||
				((flags&BF_can_bind_every)!=0)) {
			return NULL;
		}
		if ((flags & BF_fb_props_optional)==0) {
			if ((fb_prop.get_aux_rgba() > 0)||
					(fb_prop.get_aux_hrgba() > 0)||
					(fb_prop.get_aux_float() > 0)) {
				return NULL;
			}
		}
		printf("returning it\n");
		return new nxGraphicsWindow(engine, this, name, fb_prop, win_prop,
									 flags, gsg, host);
	}
	

	
	if (retry == 1) {
		printf("trying gles2graf buf\n");
		if (//(!gl_support_fbo)||
				(host==0)||
				((flags&BF_require_parasite)!=0)||
				((flags&BF_require_window)!=0)) {
			return NULL;
		}
		if ((flags & BF_fb_props_optional)==0) {
			if ((fb_prop.get_indexed_color() > 0)||
					(fb_prop.get_back_buffers() > 0)||
					(fb_prop.get_accum_bits() > 0)||
					(fb_prop.get_multisamples() > 0)) {
				return NULL;
			}
		}
		// Early success - if we are sure that this buffer WILL
		// meet specs, we can precertify it.
		if ((nxgsg != 0) &&
				(nxgsg->is_valid()) &&
				(!nxgsg->needs_reset()) &&
				(nxgsg->_supports_framebuffer_object) &&
				(nxgsg->_glDrawBuffers != 0)&&
				(fb_prop.is_basic())) {
			precertify = true;
		}
		printf("returning it (graf)\n");
		return new GLESGraphicsBuffer(engine, this, name, fb_prop, win_prop,
									flags, gsg, host);
	}
	
	printf("we failed sorry\n");
	return NULL;
}