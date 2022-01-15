#include "nxGraphicsStateGuardian.h"
#include "config_nxdisplay.h"
#include "lightReMutexHolder.h"

TypeHandle nxGraphicsStateGuardian::_type_handle;

nxGraphicsStateGuardian::
nxGraphicsStateGuardian(GraphicsEngine *engine, GraphicsPipe *pipe,
		nxGraphicsStateGuardian *share_with) :
	GLGraphicsStateGuardian(engine, pipe)
{
	_share_context=0;
	_context=0;
	_egl_display=0;
	_fbconfig=0;

	if (share_with != (nxGraphicsStateGuardian *)NULL) {
		_prepared_objects = share_with->get_prepared_objects();
		_share_context = share_with->_context;
	}
}

nxGraphicsStateGuardian::
~nxGraphicsStateGuardian() {
	if (_context != (EGLContext)NULL) {
		if (!eglDestroyContext(_egl_display, _context)) {
			printf("eglDestroyContext context\n");
		}
		_context = (EGLContext)NULL;
	}
}


void nxGraphicsStateGuardian::
get_properties(FrameBufferProperties &properties,
		bool &pbuffer_supported, bool &pixmap_supported,
		bool &slow, EGLConfig config) {
	
	properties.clear();

	// Now update our framebuffer_mode and bit depth appropriately.
	int red_size, green_size, blue_size,
		alpha_size,
		depth_size, stencil_size, samples, surface_type, caveat;

	eglGetConfigAttrib(_egl_display, config, EGL_RED_SIZE, &red_size);
	eglGetConfigAttrib(_egl_display, config, EGL_GREEN_SIZE, &green_size);
	eglGetConfigAttrib(_egl_display, config, EGL_BLUE_SIZE, &blue_size);
	eglGetConfigAttrib(_egl_display, config, EGL_ALPHA_SIZE, &alpha_size);
	eglGetConfigAttrib(_egl_display, config, EGL_DEPTH_SIZE, &depth_size);
	eglGetConfigAttrib(_egl_display, config, EGL_STENCIL_SIZE, &stencil_size);
	eglGetConfigAttrib(_egl_display, config, EGL_SAMPLES, &samples);
	eglGetConfigAttrib(_egl_display, config, EGL_SURFACE_TYPE, &surface_type);
	eglGetConfigAttrib(_egl_display, config, EGL_CONFIG_CAVEAT, &caveat);
	int err = eglGetError();
	if (err != EGL_SUCCESS) {
        return;
	}

	pbuffer_supported = ((surface_type & EGL_PBUFFER_BIT)!=0);
	pixmap_supported =  ((surface_type & EGL_PIXMAP_BIT)!=0);
	slow = (caveat == EGL_SLOW_CONFIG);
	
	// We really want those red green blue alpha depth stencil
	if ((red_size != 8 || green_size != 8 || blue_size != 8 || alpha_size != 8 || depth_size != 24 || stencil_size != 8)) {
		return;
	}
	
	//if ((surface_type & EGL_WINDOW_BIT)==0) {
		// We insist on having a context that will support an onscreen window.
		//return;
	//}

	properties.set_back_buffers(1);
	properties.set_rgb_color(1);
	properties.set_color_bits(red_size+green_size+blue_size);
	properties.set_stencil_bits(stencil_size);
	properties.set_depth_bits(depth_size);
	properties.set_alpha_bits(alpha_size);
	properties.set_multisamples(samples);

	// Set both hardware and software bits, indicating not-yet-known.
	properties.set_force_software(1);
	properties.set_force_hardware(1);
}

void nxGraphicsStateGuardian::
choose_pixel_format(const FrameBufferProperties &properties,
		EGLDisplay display, bool need_pbuffer, bool need_pixmap) {
			
	_egl_display = display;
	_context = 0;
	_fbconfig = 0;
	_fbprops.clear();

	static const EGLint attrib_list[] = {
		EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
        EGL_RED_SIZE,     8,
        EGL_GREEN_SIZE,   8,
        EGL_BLUE_SIZE,    8,
        EGL_ALPHA_SIZE,   8,
        EGL_DEPTH_SIZE,   24,
        EGL_STENCIL_SIZE, 8,
		EGL_NONE
	};

	EGLint num_configs = 0;
	EGLConfig configs[32];
	if (!eglChooseConfig(_egl_display, attrib_list, configs, 32, &num_configs) || num_configs <= 0) {
		printf("eglChooseConfig failed\n");
		return;
	}
	
	int best_quality = 0;
	int best_result = 0;
	FrameBufferProperties best_props;

	if (configs != 0) {
		for (int i = 0; i < num_configs; ++i) {
			FrameBufferProperties fbprops;
			bool pbuffer_supported, pixmap_supported, slow;
            
			get_properties(fbprops, pbuffer_supported, pixmap_supported, slow, configs[i]);
			
			int quality = fbprops.get_quality(properties);
			if ((quality > 0)&&(slow)) quality -= 10000000;

			if (need_pbuffer && !pbuffer_supported) {
				continue;
			}
			if (need_pixmap && !pixmap_supported) {
				continue;
			}

			if (quality > best_quality) {
				best_quality = quality;
				best_result = i;
				best_props = fbprops;
			}
		}
	}

	if (best_quality > 0) {
		_fbconfig = configs[best_result];
		
		static const EGLint context_attribs[] = {
            EGL_CONTEXT_OPENGL_PROFILE_MASK_KHR, EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT_KHR,
            EGL_CONTEXT_MAJOR_VERSION_KHR, 4,
            EGL_CONTEXT_MINOR_VERSION_KHR, 3,
			EGL_NONE
		};
		_context = eglCreateContext(_egl_display, _fbconfig, _share_context, context_attribs);
		
		int err = eglGetError();
		if (_context && err == EGL_SUCCESS) {
			_fbprops = best_props;
			return;
		}
		
		// This really shouldn't happen, so I'm not too careful about cleanup.
		printf("failed to create egl context (%d)\n", err);
		_fbconfig = 0;
		_context = 0;
	}
}

void nxGraphicsStateGuardian::
reset() {
	GLGraphicsStateGuardian::reset();

	// If "Mesa" is present, assume software.  However, if "Mesa DRI" is
	// found, it's actually a Mesa-based OpenGL layer running over a
	// hardware driver.
	if (_gl_renderer.find("Mesa") != string::npos &&
			_gl_renderer.find("Mesa DRI") == string::npos) {
		// It's Mesa, therefore probably a software context.
		_fbprops.set_force_software(1);
		_fbprops.set_force_hardware(0);
	} else {
		_fbprops.set_force_hardware(1);
		_fbprops.set_force_software(0);
	}
}

bool nxGraphicsStateGuardian::
egl_is_at_least_version(int major_version, int minor_version) const {
	if (_egl_version_major < major_version) {
		return false;
	}
	if (_egl_version_minor < minor_version) {
		return false;
	}
	return true;
}

void nxGraphicsStateGuardian::
get_extra_extensions() {
	save_extensions(eglQueryString(_egl_display, EGL_EXTENSIONS));
}

void *nxGraphicsStateGuardian::
do_get_extension_func(const char *prefix, const char *name) {
	string fullname = string(prefix) + string(name);
	return (void *)eglGetProcAddress(fullname.c_str());
}
