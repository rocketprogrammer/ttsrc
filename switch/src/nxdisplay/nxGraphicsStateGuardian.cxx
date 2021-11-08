#include "nxGraphicsStateGuardian.h"
#include "config_nxdisplay.h"
#include "lightReMutexHolder.h"

TypeHandle nxGraphicsStateGuardian::_type_handle;

nxGraphicsStateGuardian::
nxGraphicsStateGuardian(GraphicsEngine *engine, GraphicsPipe *pipe,
		nxGraphicsStateGuardian *share_with) :
	GLESGraphicsStateGuardian(engine, pipe)
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
		printf("failed to get egl config attrib\n");
	}

	pbuffer_supported = ((surface_type & EGL_PBUFFER_BIT)!=0);
	pixmap_supported =  ((surface_type & EGL_PIXMAP_BIT)!=0);
	slow = (caveat == EGL_SLOW_CONFIG);
	
	printf("stencil color %d %d %d alpha %d depth %d stencil %d\n", red_size, green_size, blue_size, alpha_size, depth_size, stencil_size);
	// We really want those red green blue alpha depth stencil
	if ((red_size != 8 || green_size != 8 || blue_size != 8 || alpha_size != 8 || depth_size != 24 || stencil_size != 8)) {
		printf("Ignoring one of the configs\n");
		return;
	}
	
	if ((surface_type & EGL_WINDOW_BIT)==0) {
		// We insist on having a context that will support an onscreen window.
		return;
	}

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
		EGL_RENDERABLE_TYPE, EGL_OPENGL_ES_BIT,
		EGL_SURFACE_TYPE, EGL_DONT_CARE,
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
	
	printf("num_configs %d\n", num_configs);

	if (configs != 0) {
		for (int i = 0; i < num_configs; ++i) {
			FrameBufferProperties fbprops;
			bool pbuffer_supported, pixmap_supported, slow;
			printf("testing config\n");
			get_properties(fbprops, pbuffer_supported, pixmap_supported, slow, configs[i]);
			
			int quality = fbprops.get_quality(properties);
			if ((quality > 0)&&(slow)) quality -= 10000000;

			if (need_pbuffer && !pbuffer_supported) {
				continue;
			}
			if (need_pixmap && !pixmap_supported) {
				continue;
			}
			
			printf("nice %d > %d\n", quality, best_quality);

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
			EGL_CONTEXT_CLIENT_VERSION, 1,
			EGL_NONE
		};
		_context = eglCreateContext(_egl_display, _fbconfig, _share_context, context_attribs);
		
		int err = eglGetError();
		if (_context && err == EGL_SUCCESS) {
			_fbprops = best_props;
			return;
		}
		
		// This really shouldn't happen, so I'm not too careful about cleanup.
		printf("failed to create egl context\n");
		_fbconfig = 0;
		_context = 0;
	}
	printf("no usable pixel fmt\n");
}

void nxGraphicsStateGuardian::
reset() {
	GLESGraphicsStateGuardian::reset();

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
query_gl_version() {
	GLESGraphicsStateGuardian::query_gl_version();

	// Calling eglInitialize on an already-initialized display will
	// just provide us the version numbers.
	printf("eglInitialize(_egl_display, &_egl_version_major, &_egl_version_minor)\n");
	if (!eglInitialize(_egl_display, &_egl_version_major, &_egl_version_minor)) {
		printf("failed to get ver num\n");
	}
	
	printf("gl version %d.%d\n", _egl_version_major, _egl_version_minor);
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
