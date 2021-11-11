import os
import shutil
import sys

sys.path.append("switch")

from makepanda_default import *

if "-t" in sys.argv:
    # threaded overrides some functions
    from makepanda_threaded import *


#########################################
# Base config headers 
# and parser-inc headers
#########################################
CopyIncludeFiles("switch/include")
if not os.path.exists(os.path.join(INCDIR, "parser-inc")):
    shutil.copytree("dtool/src/parser-inc", os.path.join(INCDIR, "parser-inc"))


#########################################
# DTool
#########################################

CopyHeaders("dtool/src/dtoolbase")
CopyHeaders("dtool/src/dtoolutil")
CopyHeaders("dtool/metalibs/dtool")
CopyFileTo("dtool/src/dtoolutil/vector_src.cxx", INCDIR)

Library("libdtool.a", [
    # dtool/src/dtoolbase
    Compile("dtool/src/dtoolbase/dtoolbase_composite1.cxx", building="DTOOL"),
    Compile("dtool/src/dtoolbase/dtoolbase_composite2.cxx", building="DTOOL"),
    Compile("dtool/src/dtoolbase/lookup3.c", building="DTOOL"),
    Compile("dtool/src/dtoolbase/indent.cxx", building="DTOOL"),

    # dtool/src/dtoolutil
    Compile("dtool/src/dtoolutil/gnu_getopt.c", building="DTOOL"),
    Compile("dtool/src/dtoolutil/gnu_getopt1.c", building="DTOOL"),
    Compile("dtool/src/dtoolutil/dtoolutil_composite.cxx", building="DTOOL"),
    
    Compile("dtool/metalibs/dtool/dtool.cxx", building="DTOOL")
])


#########################################
# DToolConfig
#########################################

CopyHeaders("dtool/src/cppparser")
CopyHeaders("dtool/src/prc")
CopyHeaders("dtool/src/dconfig")
CopyHeaders("dtool/src/interrogatedb")
CopyHeaders("dtool/metalibs/dtoolconfig")
CopyHeaders("dtool/src/pystub")
CopyHeaders("dtool/src/interrogate")
CopyHeaders("dtool/src/test_interrogate")

Library("libdtoolconfig.a", [
    Compile("dtool/src/prc/prc_composite.cxx", building="DTOOLCONFIG"),
    Compile("dtool/src/dconfig/dconfig_composite.cxx", building="DTOOLCONFIG"),
    Compile("dtool/src/interrogatedb/interrogatedb_composite.cxx", building="DTOOLCONFIG"),
    
    # dtool/metalibs/dtoolconfig
    Compile("dtool/metalibs/dtoolconfig/pydtool.cxx", building="DTOOLCONFIG"),
    Compile("dtool/metalibs/dtoolconfig/dtoolconfig.cxx", building="DTOOLCONFIG")
])

Library("libpystub.a", [
    Compile("dtool/src/pystub/pystub.cxx", building="DTOOLCONFIG")
])


#########################################
# PandaExpress
#########################################
CopyHeaders("panda/src/pandabase")
CopyHeaders("panda/src/express")
CopyHeaders("panda/src/downloader")
CopyHeaders("panda/metalibs/pandaexpress")

Library("libpandaexpress.a", [
    Compile("panda/src/pandabase/pandabase.cxx", building="PANDAEXPRESS"),
    
    # panda/src/express
    Compile("panda/src/express/express_composite1.cxx", building="PANDAEXPRESS", opts=["zlib"]),
    Compile("panda/src/express/express_composite2.cxx", building="PANDAEXPRESS", opts=["zlib"]),
    Interrogate("libexpress.in", 
        module="pandaexpress", library="libexpress",
        srcdir="panda/src/express", files=["*.h", "*_composite.cxx"],
        building="PANDAEXPRESS", opts=["zlib"]
    ),
    
    # panda/src/downloader
    Compile("panda/src/downloader/downloader_composite.cxx", building="PANDAEXPRESS", opts=["zlib"]),
    Interrogate("libdownloader.in", 
        module="pandaexpress", library="libdownloader",
        srcdir="panda/src/downloader", files=["*.h", "*_composite.cxx"],
        building="PANDAEXPRESS", opts=["zlib"]
    ),
    
    # panda/metalibs/pandaexpress
    Compile("panda/metalibs/pandaexpress/pandaexpress.cxx", building="PANDAEXPRESS", opts=["zlib"]),
    Module("libpandaexpress_module.o", module="pandaexpress", library="libpandaexpress", files=[
        "libdownloader.in",
        "libexpress.in"
    ])
])


#########################################
# Panda
#########################################

CopyHeaders("panda/src/pipeline")
CopyHeaders("panda/src/putil")
CopyHeaders("panda/src/audio")
CopyHeaders("panda/src/event")
CopyHeaders("panda/src/linmath")
CopyHeaders("panda/src/mathutil")
CopyHeaders("panda/src/gsgbase")
CopyHeaders("panda/src/pnmimage")
CopyHeaders("panda/src/nativenet")
CopyHeaders("panda/src/net")
CopyHeaders("panda/src/pstatclient")
CopyHeaders("panda/src/gobj")
CopyHeaders("panda/src/lerp")
CopyHeaders("panda/src/pgraphnodes")
CopyHeaders("panda/src/pgraph")
CopyHeaders("panda/src/cull")
CopyHeaders("panda/src/chan")
CopyHeaders("panda/src/char")
CopyHeaders("panda/src/dgraph")
CopyHeaders("panda/src/display")
CopyHeaders("panda/src/device")
CopyHeaders("panda/src/pnmtext")
CopyHeaders("panda/src/text")
CopyHeaders("panda/src/movies")
CopyHeaders("panda/src/grutil")
CopyHeaders("panda/src/tform")
CopyHeaders("panda/src/collide")
CopyHeaders("panda/src/parametrics")
CopyHeaders("panda/src/pgui")
CopyHeaders("panda/src/pnmimagetypes")
CopyHeaders("panda/src/recorder")
CopyHeaders("panda/src/vrpn")
CopyHeaders("panda/metalibs/panda")

Library("libpanda.a", [
    # panda/src/pipeline
    Compile("panda/src/pipeline/pipeline_composite.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pipeline/contextSwitch.c", building="PANDA", opts=[]),
    Interrogate("libpipeline.in", 
        module="panda", library="libpipeline",
        srcdir="panda/src/pipeline", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/putil
    Compile("panda/src/putil/putil_composite1.cxx", building="PANDA", opts=["zlib"]),
    Compile("panda/src/putil/putil_composite2.cxx", building="PANDA", opts=["zlib"]),
    Interrogate("libputil.in", 
        module="panda", library="libputil",
        srcdir="panda/src/putil", files=["*.h", "*_composite.cxx"], skip=["test_bam.h"],
        building="PANDA", opts=["zlib"]
    ),
    
    # panda/src/audio
    Compile("panda/src/audio/audio_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libaudio.in", 
        module="panda", library="libaudio",
        srcdir="panda/src/audio", files=["audio.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/event
    Compile("panda/src/event/event_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libevent.in", 
        module="panda", library="libevent",
        srcdir="panda/src/event", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/linmath
    Compile("panda/src/linmath/linmath_composite.cxx", building="PANDA", opts=[]),
    Interrogate("liblinmath.in", 
        module="panda", library="liblinmath",
        srcdir="panda/src/linmath", files=["*.h", "*_composite.cxx"], skip=["lmat_oops_src.h", "cast_to_double.h", "lmat_ops.h", "cast_to_float.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/mathutil
    Compile("panda/src/mathutil/mathutil_composite.cxx", building="PANDA", opts=["fftw"]),
    Interrogate("libmathutil.in", 
        module="panda", library="libmathutil",
        srcdir="panda/src/mathutil", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=["fftw"]
    ),
    
    # panda/src/gsgbase
    Compile("panda/src/gsgbase/gsgbase_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libgsgbase.in", 
        module="panda", library="libgsgbase",
        srcdir="panda/src/gsgbase", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pnmimage
    Compile("panda/src/pnmimage/pnmimage_composite.cxx", building="PANDA", opts=["zlib"]),
    Interrogate("libpnmimage.in", 
        module="panda", library="libpnmimage",
        srcdir="panda/src/pnmimage", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=["zlib"]
    ),
    
    # panda/src/nativenet
    Compile("panda/src/nativenet/nativenet_composite1.cxx", building="PANDA", opts=[]),
    Interrogate("libnativenet.in", 
        module="panda", library="libnativenet",
        srcdir="panda/src/nativenet", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/net
    Compile("panda/src/net/net_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libnet.in", 
        module="panda", library="libnet",
        srcdir="panda/src/net", files=["*.h", "*_composite.cxx"], skip=["datagram_ui.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pstatclient
    Compile("panda/src/pstatclient/pstatclient_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libpstatclient.in", 
        module="panda", library="libpstatclient",
        srcdir="panda/src/pstatclient", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/gobj
    Compile("panda/src/gobj/gobj_composite1.cxx", building="PANDA", opts=["nvidiacg", "zlib", "squish"]),
    Compile("panda/src/gobj/gobj_composite2.cxx", building="PANDA", opts=["nvidiacg", "zlib", "squish"]),
    Interrogate("libgobj.in", 
        module="panda", library="libgobj",
        srcdir="panda/src/gobj", files=["*.h", "*_composite.cxx"], skip=["cgfx_states.h"],
        building="PANDA", opts=["nvidiacg", "zlib", "squish"]
    ),
    
    # panda/src/lerp
    Compile("panda/src/lerp/lerp_composite.cxx", building="PANDA", opts=[]),
    Interrogate("liblerp.in", 
        module="panda", library="liblerp",
        srcdir="panda/src/lerp", files=["*.h", "*_composite.cxx"], skip=["lerpchans.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pgraphnodes
    Compile("panda/src/pgraphnodes/pgraphnodes_composite1.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pgraphnodes/pgraphnodes_composite2.cxx", building="PANDA", opts=[]),
    Interrogate("libpgraphnodes.in", 
        module="panda", library="libpgraphnodes",
        srcdir="panda/src/pgraphnodes", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pgraph
    Compile("panda/src/pgraph/nodePath.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pgraph/pgraph_composite1.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pgraph/pgraph_composite2.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pgraph/pgraph_composite3.cxx", building="PANDA", opts=[]),
    Compile("panda/src/pgraph/pgraph_composite4.cxx", building="PANDA", opts=[]),
    Interrogate("libpgraph.in", 
        module="panda", library="libpgraph",
        srcdir="panda/src/pgraph", files=["*.h", "*_composite.cxx", "nodePath.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/cull
    Compile("panda/src/cull/cull_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libcull.in", 
        module="panda", library="libcull",
        srcdir="panda/src/cull", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/chan
    Compile("panda/src/chan/chan_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libchan.in", 
        module="panda", library="libchan",
        srcdir="panda/src/chan", files=["*.h", "*_composite.cxx"], skip=["movingPart.h", "animChannelFixed.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/char
    Compile("panda/src/char/char_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libchar.in", 
        module="panda", library="libchar",
        srcdir="panda/src/char", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/dgraph
    Compile("panda/src/dgraph/dgraph_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libdgraph.in", 
        module="panda", library="libdgraph",
        srcdir="panda/src/dgraph", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/display
    Compile("panda/src/display/display_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libdisplay.in", 
        module="panda", library="libdisplay",
        srcdir="panda/src/display", files=["*.h", "*_composite.cxx"], skip=["renderBuffer.h"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/device
    Compile("panda/src/device/device_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libdevice.in", 
        module="panda", library="libdevice",
        srcdir="panda/src/device", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pnmtext
    # !! only possible because we have freetype
    Compile("panda/src/pnmtext/pnmtext_composite.cxx", building="PANDA", opts=["freetype"]),
    Interrogate("libpnmtext.in", 
        module="panda", library="libpnmtext",
        srcdir="panda/src/pnmtext", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=["freetype"]
    ),
    
    # panda/src/text
    Compile("panda/src/text/text_composite.cxx", building="PANDA", opts=["zlib", "freetype"]),
    Interrogate("libtext.in", 
        module="panda", library="libtext",
        srcdir="panda/src/text", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=["zlib", "freetype"]
    ),
    
    # panda/src/movies
    Compile("panda/src/movies/movies_composite1.cxx", building="PANDA", opts=['ffmpeg']),
    Interrogate("libmovies.in", 
        module="panda", library="libmovies",
        srcdir="panda/src/movies", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=['ffmpeg']
    ),
    
    # panda/src/grutil
    Compile("panda/src/grutil/multitexReducer.cxx", building="PANDA", opts=["ffmpeg"]),
    Compile("panda/src/grutil/grutil_composite1.cxx", building="PANDA", opts=["ffmpeg"]),
    Compile("panda/src/grutil/grutil_composite2.cxx", building="PANDA", opts=["ffmpeg"]),
    Interrogate("libgrutil.in", 
        module="panda", library="libgrutil",
        srcdir="panda/src/grutil", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=["ffmpeg"]
    ),
    
    # panda/src/tform
    Compile("panda/src/tform/tform_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libtform.in", 
        module="panda", library="libtform",
        srcdir="panda/src/tform", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/collide
    Compile("panda/src/collide/collide_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libcollide.in", 
        module="panda", library="libcollide",
        srcdir="panda/src/collide", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/parametrics
    Compile("panda/src/parametrics/parametrics_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libparametrics.in", 
        module="panda", library="libparametrics",
        srcdir="panda/src/parametrics", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pgui
    Compile("panda/src/pgui/pgui_composite.cxx", building="PANDA", opts=[]),
    Interrogate("libpgui.in", 
        module="panda", library="libpgui",
        srcdir="panda/src/pgui", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/pnmimagetypes
    Compile("panda/src/pnmimagetypes/pnmimagetypes_composite.cxx", building="PANDA", opts=["png", "zlib", "jpeg", "tiff"]),
    
    # panda/src/recorder
    Compile("panda/src/recorder/recorder_composite.cxx", building="PANDA", opts=[]),
    Interrogate("librecorder.in", 
        module="panda", library="librecorder",
        srcdir="panda/src/recorder", files=["*.h", "*_composite.cxx"],
        building="PANDA", opts=[]
    ),
    
    # panda/src/vrpn
        # We don't have VRPN so we're not doing it
    
    # panda/src/dxml
        # dxml is missing so we're not doing it
    
    # panda/metalibs/panda
    Compile("panda/metalibs/panda/panda.cxx", building="PANDA", opts=["png", "zlib", "jpeg", "tiff", "ffmpeg", "zlib", "freetype", "nvidiacg", "squish", "fftw"]),
    Module("libpanda_module.o", module="panda", library="libpanda", files=[
        "librecorder.in",
        "libpgraphnodes.in",
        "libpgraph.in",
        "libcull.in",
        "libgrutil.in",
        "libchan.in",
        "libpstatclient.in",
        "libchar.in",
        "libcollide.in",
        "libdevice.in",
        "libdgraph.in",
        "libdisplay.in",
        "libpipeline.in",
        "libevent.in",
        "libgobj.in",
        "libgsgbase.in",
        "liblinmath.in",
        "libmathutil.in",
        "libparametrics.in",
        "libpnmimage.in",
        "libtext.in",
        "libtform.in",
        "liblerp.in",
        "libputil.in",
        "libaudio.in",
        "libnativenet.in",
        "libnet.in",
        "libpgui.in",
        "libmovies.in"
    ], opts=["png", "zlib", "jpeg", "tiff", "ffmpeg", "zlib", "freetype", "nvidiacg", "squish", "fftw"])
])


#########################################
# PandaSkel
#########################################

CopyHeaders("panda/src/skel")

Library("libpandaskel.a", [
    # panda/src/skel
    Compile("panda/src/skel/skel_composite.cxx", building="PANDASKEL"),
    Interrogate("libskel.in", 
        module="pandaskel", library="libskel",
        srcdir="panda/src/skel", files=["*.h", "*_composite.cxx"],
        building="PANDASKEL"
    ),
    
    Module("libpandaskel_module.o", module="pandaskel", library="libpandaskel", files=[
        "libskel.in"
    ])
])


#########################################
# PandaFx
#########################################

CopyHeaders("panda/src/distort")
CopyHeaders("panda/src/effects")
CopyHeaders("panda/metalibs/pandafx")

Library("libpandafx.a", [
    # panda/src/distort
    Compile("panda/src/distort/distort_composite.cxx", building="PANDAFX"),
    Interrogate("libdistort.in", 
        module="pandafx", library="libdistort",
        srcdir="panda/src/distort", files=["*.h", "*_composite.cxx"],
        building="PANDAFX"
    ),
    
    # panda/src/effects
    Compile("panda/src/effects/effects_composite.cxx", building="PANDAFX"),
    Interrogate("libeffects.in", 
        module="pandafx", library="libeffects",
        srcdir="panda/src/effects", files=["*.h", "*_composite.cxx"],
        building="PANDAFX"
    ),
    
    # panda/metalibs/pandafx
    Compile("panda/metalibs/pandafx/pandafx.cxx", building="PANDAFX"),
    Module("libpandafx_module.o", module="pandafx", library="libpandafx", files=[
        "libdistort.in",
        "libeffects.in"
    ])
])


#########################################
# OpenAL
#########################################

# todo


#########################################
# Framework
#########################################

CopyHeaders("panda/src/framework")

Library("libframework.a", [
    Compile("panda/src/framework/framework_composite.cxx", building="FRAMEWORK")
])


#########################################
# NxDisplay
#########################################

CopyIncludeFiles("panda/src/glstuff")
#CopyHeaders("panda/src/glgsg")
CopyHeaders("panda/src/glesgsg")
#CopyHeaders("panda/src/gles2gsg")
CopyHeaders("switch/src/nxdisplay")
CopyHeaders("switch/metalibs/pandanx")


#Library("libglstuff.a", [
#    Compile("panda/src/glstuff/glpure.cxx", opts=["gl", "nvidiacg", "cggl"])
#])

#glgsg = [
#    Compile("panda/src/glgsg/config_glgsg.cxx", building="PANDAGL"),
#    Compile("panda/src/glgsg/glgsg.cxx", building="PANDAGL")
#]

glesgsg = [
    Compile("panda/src/glesgsg/config_glesgsg.cxx", building="PANDAGLES"),
    Compile("panda/src/glesgsg/glesgsg.cxx", building="PANDAGLES")
]

#gles2gsg = [
#    Compile("panda/src/gles2gsg/config_gles2gsg.cxx", building="PANDAGLES2"),
#    Compile("panda/src/gles2gsg/gles2gsg.cxx", building="PANDAGLES2")
#]

Library("libpandanx.a", [
  Compile('switch/src/nxdisplay/config_nxdisplay.cxx', building="PANDANX", opts=['gles', 'egl']),
  Compile('switch/src/nxdisplay/nxGraphicsPipe.cxx', building="PANDANX", opts=['gles', 'egl']),
  Compile('switch/src/nxdisplay/nxGraphicsWindow.cxx', building="PANDANX", opts=['gles', 'egl']),
  Compile('switch/src/nxdisplay/nxGraphicsStateGuardian.cxx', building="PANDANX", opts=['gles', 'egl']),
  *glesgsg,
  Compile('switch/metalibs/pandanx/pandanx.cxx', building="PANDANX", opts=['gles', 'egl']),
])


#########################################
# PandaOde
#########################################

# Unfortunately the ode header is not correct,
# so we're disabling ode for now

CopyHeaders("panda/src/ode")
CopyHeaders("panda/metalibs/pandaode")

Library("libpandaode.a", [
    # panda/src/ode
    Compile("panda/src/ode/pode_composite1.cxx", building="PANDAODE", opts=["ode"]),
    Compile("panda/src/ode/pode_composite2.cxx", building="PANDAODE", opts=["ode"]),
    Compile("panda/src/ode/pode_composite3.cxx", building="PANDAODE", opts=["ode"]),
    Interrogate("libpandaode.in", 
        module="pandaode", library="libpandaode",
        srcdir="panda/src/ode", files=["*.h", "*_composite.cxx"], skip=["odeConvexGeom.h", "odeHeightFieldGeom.h", "odeHelperStructs.h"],
        building="PANDAODE", opts=["ode"]
    ),
    
    # panda/metalibs/pandaode
    Compile("panda/metalibs/pandaode/pandaode.cxx", building="PANDAODE", opts=["ode"]),
    Module("libpandaode_module.o", module="pandaode", library="libpandaode", files=[
        "libpandaode.in",
    ])
])



#########################################
# PandaPhysics
#########################################
CopyHeaders("panda/src/physics")
CopyHeaders("panda/src/particlesystem")
CopyHeaders("panda/metalibs/pandaphysics")

Library("libpandaphysics.a", [
    # panda/src/physics
    Compile("panda/src/physics/physics_composite.cxx", building="PANDAPHYSICS"),
    Interrogate("libphysics.in", 
        module="pandaphysics", library="libphysics",
        srcdir="panda/src/physics", files=["*.h", "*_composite.cxx"], skip=["forces.h"],
        building="PANDAPHYSICS"
    ),
    
    # panda/src/particlesystem
    Compile("panda/src/particlesystem/particlesystem_composite.cxx", building="PANDAPHYSICS"),
    Interrogate("libparticlesystem.in", 
        module="pandaphysics", library="libparticlesystem",
        srcdir="panda/src/particlesystem", files=["*.h", "*_composite.cxx"], skip=["orientedParticle.h", "orientedParticleFactory.h", "particlefactories.h", "emitters.h", "particles.h"],
        building="PANDAPHYSICS"
    ),
    
    # panda/metalibs/pandaphysics
    Compile("panda/metalibs/pandaphysics/pandaphysics.cxx", building="PANDAPHYSICS"),
    Module("libpandaphysics_module.o", module="pandaphysics", library="libpandaphysics", files=[
        "libphysics.in",
        "libparticlesystem.in",
    ])
])


#########################################
# Direct
#########################################

CopyHeaders("direct/src/directbase")
CopyHeaders("direct/src/dcparser")
CopyHeaders("direct/src/deadrec")
CopyHeaders("direct/src/distributed")
CopyHeaders("direct/src/interval")
CopyHeaders("direct/src/http")
CopyHeaders("direct/src/motiontrail")
CopyHeaders("direct/src/showbase")
CopyHeaders("direct/metalibs/direct")

Library("libdirect.a", [
    # direct/src/directbase
    Compile("direct/src/directbase/directbase.cxx", building="DIRECT", opts=["python"]),
    
    # direct/src/dcparser
    Compile("direct/src/dcparser/dcParser.yxx", prefix="dcyy", building="DIRECT"),
    Compile("direct/src/dcparser/dcLexer.lxx", prefix="dcyy", building="DIRECT"),
    Compile("direct/src/dcparser/dcparser_composite.cxx", building="DIRECT"),
    Interrogate("libdcparser.in",
        module="direct", library="libdcparser",
        srcdir="direct/src/dcparser", files=["*.h", "*_composite.cxx"], skip=["dcParser.h", "dcmsgtypes.h"],
        building="DIRECT"
    ),
    
    # direct/src/deadrec
    Compile("direct/src/deadrec/deadrec_composite.cxx", building="DIRECT"),
    Interrogate("libdeadrec.in",
        module="direct", library="libdeadrec",
        srcdir="direct/src/deadrec", files=["*.h", "*_composite.cxx"],
        building="DIRECT"
    ),
    
    # direct/src/distributed
    Compile("direct/src/distributed/config_distributed.cxx", building="DIRECT"),
    Compile("direct/src/distributed/cConnectionRepository.cxx", building="DIRECT"),
    Compile("direct/src/distributed/cDistributedSmoothNodeBase.cxx", building="DIRECT"),
    Interrogate("libdistributed.in",
        module="direct", library="libdistributed",
        srcdir="direct/src/distributed", files=["*.h", "*.cxx"],
        building="DIRECT"
    ),
    
    # direct/src/interval
    Compile("direct/src/interval/interval_composite.cxx", building="DIRECT"),
    Interrogate("libinterval.in",
        module="direct", library="libinterval",
        srcdir="direct/src/interval", files=["*.h", "*_composite.cxx"],
        building="DIRECT"
    ),
    
    # direct/src/http
    Compile("direct/src/http/http_composite1.cxx", building="DIRECT"),
    Interrogate("libhttp.in",
        module="direct", library="libhttp",
        srcdir="direct/src/http", files=["*.h", "*_composite1.cxx"],
        building="DIRECT"
    ),
    
    # direct/src/motiontrail
    Compile("direct/src/motiontrail/cMotionTrail.cxx", building="DIRECT"),
    Compile("direct/src/motiontrail/config_motiontrail.cxx", building="DIRECT"),
    Interrogate("libmotiontrail.in",
        module="direct", library="libmotiontrail",
        srcdir="direct/src/motiontrail", files=["*.h", "*.cxx"],
        building="DIRECT"
    ),
    
    # direct/src/showbase
    Compile("direct/src/showbase/showBase.cxx", building="DIRECT"),
    Interrogate("libshowbase.in",
        module="direct", library="libshowbase",
        srcdir="direct/src/showbase", files=["*.h", "showBase.cxx"],
        building="DIRECT"
    ),
    
    # direct/metalibs/direct
    Compile("direct/metalibs/direct/direct.cxx", building="DIRECT"),
    Module("libdirect_module.o", module="direct", library="libdirect", files=[
        "libdcparser.in",
        "libshowbase.in",
        "libdeadrec.in",
        "libhttp.in",
        "libmotiontrail.in",
        "libdistributed.in",
        "libinterval.in"
    ])
])
        

#########################################
# OTP
#########################################

CopyHeaders("otp/src/otpbase", INCDIR_OTP)
CopyHeaders("otp/src/nametag", INCDIR_OTP)
CopyHeaders("otp/src/navigation", INCDIR_OTP)
CopyHeaders("otp/src/movement", INCDIR_OTP)
CopyHeaders("otp/src/configrc", INCDIR_OTP)
CopyHeaders("otp/src/secure", INCDIR_OTP)
CopyHeaders("otp/metalibs/otp", INCDIR_OTP)

Library("libotp.a", [
    # otp/src/otpbase
    Compile("otp/src/otpbase/otpbase.cxx", building="OTP", opts=["otp"]),
    
    # otp/src/nametag
    Compile("otp/src/nametag/nametag_composite1.cxx", building="OTP", opts=["otp"]),
    Compile("otp/src/nametag/nametag_composite2.cxx", building="OTP", opts=["otp"]),
    Interrogate("libnametag.in",
        module="otp", library="libnametag",
        srcdir="otp/src/nametag", files=["*.h", "*_composite1.cxx", "*_composite2.cxx"],
        building="OTP", opts=["otp"],
    ),
    
    # otp/src/navigation
    Compile("otp/src/navigation/navigation_composite1.cxx", building="OTP", opts=["otp"]),
    Interrogate("libnavigation.in",
        module="otp", library="libnavigation",
        srcdir="otp/src/navigation", files=["*.h", "*_composite1.cxx"],
        building="OTP", opts=["otp"],
    ),
    
    # otp/src/movement
    Compile("otp/src/movement/config_movement.cxx", building="OTP", opts=["otp"]),
    Compile("otp/src/movement/cMover.cxx", building="OTP", opts=["otp"]),
    Compile("otp/src/movement/cImpulse.cxx", building="OTP", opts=["otp"]),
    Compile("otp/src/movement/cMoverGroup.cxx", building="OTP", opts=["otp"]),
    Interrogate("libmovement.in",
        module="otp", library="libmovement",
        srcdir="otp/src/movement", files=["*.h", "*.cxx"],
        building="OTP", opts=["otp"],
    ),
    
    # otp/src/configrc
    Compile("otp/src/configrc/settingsFile.cxx", building="OTP", opts=["otp"]),
    Interrogate("libsettings.in",
        module="otp", library="libsettings",
        srcdir="otp/src/configrc", files=["settingsFile.h"],
        building="OTP", opts=["otp"],
    ),
    
    # otp/src/secure
    Compile("otp/src/secure/get_fingerprint.cxx", building="OTP", opts=["otp", "zlib"]),
    Compile("otp/src/secure/loadClientCertificate.cxx", building="OTP", opts=["otp", "zlib"]),
    Interrogate("libsecure.in",
        module="otp", library="libsecure",
        srcdir="otp/src/secure", files=["loadClientCertificate.cxx", "loadClientCertificate.h", "get_fingerprint.h", "get_fingerprint.cxx"],
        building="OTP", opts=["otp", "zlib"],
    ),
    
    # otp/metalibs/otp
    Compile("otp/metalibs/otp/otp.cxx", building="OTP", opts=["otp"]),
    Module("libotp_module.o", module="otp", library="libotp", files=[
        "libnametag.in",
        "libnavigation.in",
        "libmovement.in",
        "libsettings.in",
        "libsecure.in"
    ])
])


#########################################
# Toontown
#########################################

CopyHeaders("toontown/src/toontownbase", INCDIR_TOONTOWN)
CopyHeaders("toontown/src/dna", INCDIR_TOONTOWN)
CopyHeaders("toontown/src/pets", INCDIR_TOONTOWN)
CopyHeaders("toontown/src/suit", INCDIR_TOONTOWN)

Library("libtoontown.a", [
    # toontown/src/toontownbase
    Compile("toontown/src/toontownbase/toontownbase.cxx", building="TOONTOWN", opts=["toontown"]),
    
    # toontown/src/dna
    Compile("toontown/src/dna/dnaLoader_composite1.cxx", building="TOONTOWN", opts=["toontown"]),
    Compile("toontown/src/dna/dnaLoader_composite2.cxx", building="TOONTOWN", opts=["toontown"]),
    Compile("toontown/src/dna/parser.yxx", building="TOONTOWN", opts=["toontown"], prefix="dnayy"),
    Compile("toontown/src/dna/lexer.lxx", building="TOONTOWN", opts=["toontown"], prefix="dnayy", dashi=True),
    Interrogate("libdna.in",
        module="toontown", library="libdna",
        srcdir="toontown/src/dna", files=["*.h", "*_composite1.cxx", "*_composite2.cxx"],
        building="TOONTOWN", opts=["toontown"],
    ),
    
    # toontown/src/pets
    Compile("toontown/src/pets/config_pets.cxx", building="TOONTOWN", opts=["toontown", "otp"]),
    Compile("toontown/src/pets/cPetBrain.cxx", building="TOONTOWN", opts=["toontown", "otp"]),
    Compile("toontown/src/pets/cPetChase.cxx", building="TOONTOWN", opts=["toontown", "otp"]),
    Compile("toontown/src/pets/cPetFlee.cxx", building="TOONTOWN", opts=["toontown", "otp"]),
    Interrogate("libpets.in",
        module="toontown", library="libpets",
        srcdir="toontown/src/pets", files=["*.h", "*.cxx"],
        building="TOONTOWN", opts=["toontown", "otp"],
    ),
    
    # toontown/src/suit
    Compile("toontown/src/suit/suit_composite1.cxx", building="TOONTOWN", opts=["toontown"]),
    Interrogate("libsuit.in",
        module="toontown", library="libsuit",
        srcdir="toontown/src/suit", files=["*.h", "*_composite1.cxx"],
        building="TOONTOWN", opts=["toontown"],
    ),
    
    # (module)
    Module("libtoontown_module.o", module="toontown", library="libtoontown", files=[
        "libdna.in",
        "libpets.in",
        "libsuit.in"
    ])
])


#########################################
# Python (lib, pandac, direct)
#########################################

def walk(root, curpath=[]):
    for file in os.listdir(os.path.join(root, *curpath)):
        path = os.path.join(root, *curpath, file)
        if os.path.isdir(path):
            yield from walk(root, curpath + [file])
        
        elif os.path.isfile(path):
            yield curpath, file
            
# blank __init__ for reference
open(os.path.join(TMPDIR, "__init__.py"), "w").close()


if False:
    doPyFile = lambda src, dst: Compile(src, dst + "c")
else:
    doPyFile = lambda src, dst: CopyFile(src, dst)


# python
for path, file in walk("thirdparty/switch-python/Lib"):
    if file.endswith(".py"):
        if path and (path[0] in ("test", "unittest", "lib-tk", "lib2to3", "msilib", "idlelib",
                                 "hotshot", "ensurepip", "distutils", "multiprocessing", "sqlite3")
                     or path[0].startswith("plat-")):
            continue
            
        doPyFile(
            os.path.join("thirdparty/switch-python/Lib", *path, file),
            os.path.join(PYTHON_LIB, *path, file)
        )
        
        
# pandac
#   modules we have built:
pandacModules = ("libpandaexpress", "libpanda",
                 "libpandaskel", "libpandafx",
                 "libpandaphysics", "libpandaode", "libdirect",
                 "libotp", "libtoontown")
                 
#   extension map
pandacExtensions = {
    "libpanda": ["Mat3", "NodePath", "NodePathCollection", "VBase3", "VBase4"],
    "libdirect": ["CInterval"],
    "libpandaegg": ["EggGroupNode", "EggPrimitive"],
    "libpandaexpress": ["Ramfile", "StreamReader"], # "HTTPChannel" but we don't have OPENSSL
    "libpandaode": ["OdeBody", "OdeGeom", "OdeJoint", "OdeSpace"]
}

#   pandac/PandaModules.py
with open(os.path.join(TMPDIR, "PandaModules.py"), "w") as pmfile:
    for module in pandacModules:
        pmfile.write("from " + module + "Modules import *\n")
        
        # pandac/lib...Modules.py
        with open(os.path.join(TMPDIR, module + "Modules.py"), "w") as mfile:
            mfile.write("from extension_native_helpers import *\n")
            mfile.write("from " + module + " import *\n\n")
            for extension in pandacExtensions.get(module, ()):
                with open(os.path.join("direct/src/extensions_native/" + extension + "_extensions.py"), "r") as efile:
                    mfile.write(efile.read())
                    
                mfile.write("\n\n")
                
        doPyFile(os.path.join(TMPDIR, module + "Modules.py"), os.path.join(PANDAC, module + "Modules.py"))
    
doPyFile(os.path.join(TMPDIR, "PandaModules.py"), os.path.join(PANDAC, "PandaModules.py"))
doPyFile(os.path.join(TMPDIR, "__init__.py"), os.path.join(PANDAC, "__init__.py"))
doPyFile("direct/src/extensions_native/extension_native_helpers.py", os.path.join(PANDAC, "extension_native_helpers.py"))


# direct
doPyFile(os.path.join(TMPDIR, "__init__.py"), os.path.join(DIRECT, "__init__.py"))
for path, file in walk("direct/src"):
    if path and path[0] == "extensions":
        continue
        
    if file.endswith(".py"):
        doPyFile(
            os.path.join("direct/src", *path, file),
            os.path.join(DIRECT, *path, file)
        )


if "-t" in sys.argv:
    # Then we start the threads
    StartThreads()