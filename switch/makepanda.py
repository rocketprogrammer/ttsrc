import os
import shutil
import sys

sys.path.append("switch")

from makepanda_default import *

if "-t" in sys.argv:
    # threaded overrides some functions
    from makepanda_threaded import *


SKIP_DTOOL = 0
SKIP_DTOOLCONFIG = 0
SKIP_PANDAEXPRESS = 0
SKIP_PANDA = 0
SKIP_FRAMEWORK = 0
SKIP_NXDISPLAY = 0

# Base config headers 
# and parser-inc headers
CopyFiles("switch/include")
if not os.path.exists(os.path.join(INCDIR, "parser-inc")):
    shutil.copytree("dtool/src/parser-inc", os.path.join(INCDIR, "parser-inc"))

#
# DTool
#
if not SKIP_DTOOL:
    CopyHeaders("dtool/src/dtoolbase")
    CopyHeaders("dtool/src/dtoolutil")
    CopyHeaders("dtool/metalibs/dtool")
    CopyFile("dtool/src/dtoolutil/vector_src.cxx", INCDIR)

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

#
# DToolConfig
#
if not SKIP_DTOOLCONFIG:
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

#
# PandaExpress
#

if not SKIP_PANDAEXPRESS:
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

#
# Panda
#

if not SKIP_PANDA:
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

# ...skip a few...

#
# Framework
#
if not SKIP_FRAMEWORK:
    CopyHeaders("panda/src/framework")

    Library("libframework.a", [
        Compile("panda/src/framework/framework_composite.cxx", building="FRAMEWORK")
    ])

#
# OpenGL stuff
#

if not SKIP_NXDISPLAY:
    CopyFiles("panda/src/glstuff")
    CopyHeaders("panda/src/glgsg")
    CopyHeaders("panda/src/glesgsg")
    CopyHeaders("panda/src/gles2gsg")
    CopyHeaders("switch/src/nxdisplay")
    CopyHeaders("switch/metalibs/pandanx")


    Library("libglstuff.a", [
        Compile("panda/src/glstuff/glpure.cxx", opts=["gl", "nvidiacg", "cggl"])
    ])

    glgsg = [
        Compile("panda/src/glgsg/config_glgsg.cxx", building="PANDAGL"),
        Compile("panda/src/glgsg/glgsg.cxx", building="PANDAGL")
    ]

    glesgsg = [
        Compile("panda/src/glesgsg/config_glesgsg.cxx", building="PANDAGLES"),
        Compile("panda/src/glesgsg/glesgsg.cxx", building="PANDAGLES")
    ]

    gles2gsg = [
        Compile("panda/src/gles2gsg/config_gles2gsg.cxx", building="PANDAGLES2"),
        Compile("panda/src/gles2gsg/gles2gsg.cxx", building="PANDAGLES2")
    ]

    Library("libpandanx.a", [
      Compile('switch/src/nxdisplay/config_nxdisplay.cxx', building="PANDANX", opts=['gles', 'egl']),
      Compile('switch/src/nxdisplay/nxGraphicsPipe.cxx', building="PANDANX", opts=['gles', 'egl']),
      Compile('switch/src/nxdisplay/nxGraphicsWindow.cxx', building="PANDANX", opts=['gles', 'egl']),
      Compile('switch/src/nxdisplay/nxGraphicsStateGuardian.cxx', building="PANDANX", opts=['gles', 'egl']),
      *glesgsg,
      Compile('switch/metalibs/pandanx/pandanx.cxx', building="PANDANX", opts=['gles', 'egl']),
    ])


if "-t" in sys.argv:
    # Then we start the threads
    StartThreads()