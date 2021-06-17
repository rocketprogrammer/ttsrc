// Filename: Configrc.cxx
// $Id$
//
////////////////////////////////////////////////////////////////////

#ifdef _WIN32
#include <windows.h>
#endif

#include <iostream>

// Windows may define this macro inappropriately.
#ifdef X509_NAME
#undef X509_NAME
#endif
#include <assert.h>


// hack to share enums w/installer
class SysInfo {
public:
  // MPG hack to avoid moving installer to OTP yet
  //#include "../installer/sysinfodefs.h"
    typedef enum {
        CPU_Intel,
        CPU_MIPS,
        CPU_Alpha,
        CPU_PPC,
        CPU_unknown
      } CPUType;

      typedef enum {
        OS_unknown,
        OS_Win95,
        OS_Win98,
        OS_WinMe,
        OS_WinNT,   // NT  (must come after win9x stuff, order important)
        OS_Win2000, // Win2000
        OS_WinXP,   // WinXP
        OS_WinServer2003,   // WinXP Server, essentially
        OS_WinPostXP, // newer than WinXP
      } OSType;

      typedef enum {
        GAPI_Unknown = 0,
        GAPI_OpenGL     ,
        GAPI_DirectX_3=3,
        GAPI_DirectX_5=5,
        GAPI_DirectX_6,
        GAPI_DirectX_7,
        GAPI_DirectX_8_0,
        GAPI_DirectX_8_1,
        GAPI_DirectX_9_0,
      } GAPIType;

      typedef enum {
        C_modem,
        C_network_bridge,
        C_TCPIP_telnet,
        C_RS232,
        C_unspecified,
        C_unknown
      } CommType;

      typedef enum {
        Status_Unknown,
        Status_Unsupported,
        Status_Supported,
      } GfxCheckStatus;

      typedef enum {
        UnknownVendor=0,
        _3DFX=0x121A,
        _3DLabs=0x3D3D,
        ATI=0x1002,
        Intel=0x8086,
        Matrox=0x102B,
        Nvidia=0x10DE,
        Nvidia_STB=0x12D2,
        PowerVR=0x1023,
        S3=0x5333,
        SiS=0x1039,
        Trident=0x1023,
      } GfxVendorIDs;

    #if 0
      // used to index into array of string messages used to communicate with missedReqmts.php
      typedef enum {
        Unknown,
        Intel_i810,
        NumCardTypes,
      } GfxCardType;
    #endif
};

#define _str(s) #s
#define _xstr(s) _str(s)

#ifdef _WIN32
void write_opengl_hardware_info(HKEY hKeyToontown);
#endif // _WIN32

// win32 cruft
// file existance:
// if (GetFileAttributes(strFilePath) != 0xFFFFFFFF)  return true;
// file readability:
// You HAVE to try to open the file to find out if it's openable. Since files
// can be opend for either shared or exclusive access by other processes, you
// can't just check the static permissions or attributes. To test for
// openability, Open the file for readonly|sharedaccess. This way you won't
// block any other programs from accessing it.
// executable:
// if it ends in ".exe" or ".com" then you can assume it's executable. If you
// try to createprocess on it and get an error, then it was not.


#ifdef _WIN32

#include <string>
#include <vector>
using namespace std;
typedef vector<string> StrVec;

static void
filesearch(string rootpath, string pattern, bool bRecursive, bool bSearchForDirs, bool bPrintFileInfo, StrVec &files)
{
    // typical arguments:  filesearch("C:\\temp\\mview","*",true,true,sveclist);
    WIN32_FIND_DATA current_file;

    // first find all the files in the rootpath dir that match the pattern
    string searchpathpattern = rootpath + "\\" + pattern;
    HANDLE searcher = FindFirstFile(searchpathpattern.c_str(), &current_file);
    if ( searcher == INVALID_HANDLE_VALUE)
        return;
    do {
      string fileline;

      if(bSearchForDirs) {
          // save only dirs
          if ((current_file.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) &&
              (!(current_file.cFileName[0] == '.'))) {
               fileline = rootpath + "\\" + current_file.cFileName;
               files.push_back(fileline);
          }
      } else {
          // save only files
          if(!((current_file.cFileName[0] == '.') ||
               (current_file.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY))) {
                  if(bPrintFileInfo) {
                      SYSTEMTIME stime;
                      FileTimeToSystemTime(&current_file.ftCreationTime,&stime);
                      char extra_info[100];
                      sprintf(extra_info, ", (%d/%d/%d), %d bytes",stime.wMonth,stime.wDay,stime.wYear,current_file.nFileSizeLow);
                      fileline = rootpath + "\\" + current_file.cFileName + extra_info;
                  } else {
                   fileline = rootpath + "\\" + current_file.cFileName;
                  }
                  files.push_back(fileline);
          }
      }
    } while (FindNextFile(searcher, &current_file));
    FindClose(searcher);

    if (bRecursive) {
        // then call yourself recursively on all dirs in the rootpath
        string newsearchpath = rootpath + "\\*";
        HANDLE searcher = FindFirstFile(newsearchpath.c_str(), &current_file);
        if ( searcher == INVALID_HANDLE_VALUE)
            return;
        do {
            if ( current_file.cFileName[0] == '.' ||
                !(current_file.dwFileAttributes &
                         FILE_ATTRIBUTE_DIRECTORY))
                continue;
            newsearchpath = rootpath + "\\" + current_file.cFileName;
            filesearch(newsearchpath, pattern, true, bSearchForDirs, bPrintFileInfo, files);
        } while (FindNextFile(searcher, &current_file));
        FindClose(searcher);
    }
}

// fTestInterval is in seconds
static DWORD FindCPUMhz(float fTestInterval) {
 volatile DWORD Freq, EAX_tmp, EDX_tmp;
 int mSecs=(int)(fTestInterval*1000);
 if(mSecs<1)
   return 0;
 DWORD uSecs=mSecs*1000;

 // SetThreadPriority could be temporarily used to ensure we're not swapped out
 // seems to work ok without it for now

__asm {
     RDTSC
     mov  EAX_tmp, eax
     mov  EDX_tmp, edx
 }

 Sleep(mSecs);

 __asm {
     RDTSC
     mov  ecx, uSecs
     sub  eax, EAX_tmp
     sbb  edx, EDX_tmp
     div  ecx
     mov  Freq, eax        // Freq gets the frequency in MHz
 }

  return Freq;
}
#endif

static void write_const(ostream& os) {
  // write out the stuff that we always want in the configfile
  os << "#" << endl << "# constant config settings" << endl << "#" << endl
     << endl;
  os << "chan-config-sanity-check #f" << endl;
  os << "window-title Toontown" << endl;

  // We want to detect when a window does not open, and handle it in
  // ToonBase.py. Thus we don't want ShowBase to raise an exception if
  // the window fails to open.
  os << "require-window 0" << endl;

  // Set the language
#if defined(USE_ENGLISH)
  os << "language english" << endl;
//  os << "product-name DisneyOnline-US" << endl;
#elif defined(USE_CASTILLIAN)
  os << "language castillian" << endl;
  os << "product-name ES" << endl;
#elif defined(USE_JAPANESE)
  os << "language japanese" << endl;
  os << "product-name JP" << endl;
#elif defined(USE_GERMAN)
  os << "language german" << endl;
  os << "product-name T-Online" << endl;
#elif defined(USE_PORTUGUESE)
  os << "language portuguese" << endl;
  os << "product-name BR" << endl;
#elif defined(USE_FRENCH)
  os << "language french" << endl;
  os << "product-name FR" << endl;
#else
#error Unrecognized language defined
#endif // language
#ifdef IS_OSX
  os << "icon-filename toontown_mac_icon.rgb" << endl;
#else
  os << "icon-filename toontown.ico" << endl;
#endif  // IS_OSX

  os << endl;
  os << "cull-bin shadow 15 fixed" << endl;
  os << "cull-bin ground 14 fixed" << endl;
  os << "cull-bin gui-popup 60 unsorted" << endl;
  os << "default-model-extension .bam" << endl;
  os << "plugin-path ." << endl;

  os << "# downloader settings" << endl;
  os << "decompressor-buffer-size 32768" << endl;
  os << "extractor-buffer-size 32768" << endl;
  os << "patcher-buffer-size 512000" << endl;
  os << "downloader-timeout 15" << endl;
  os << "downloader-timeout-retries 4" << endl;
  os << "downloader-disk-write-frequency 4" << endl;
  // Assume we are fast until we are told otherwise
  os << "downloader-byte-rate 125000" << endl;
  os << "downloader-frequency 0.1" << endl;
  os << "want-render2dp 1" << endl;

  os << endl;
  os << "# texture settings" << endl;
  // this setting forces a panda scale-down for all textures
  // it really should be up to the gsg to make the determination
  // if the HW can support that tex size, so comment this out for now
  // os << "max-texture-dimension 256" << endl;

  // leaving this in for the benefit of screen shots, which
  // will not be pow2 when saved
  os << "textures-power-2 down" << endl;

  os << endl;
  os << "# loader settings" << endl;
  os << "load-file-type toontown" << endl;
  os << "dc-file phase_3/etc/toon.dc" << endl;
  os << "dc-file phase_3/etc/otp.dc" << endl;
#ifdef WIN32
  os << "aux-display pandadx9" << endl;
  os << "aux-display pandadx8" << endl;
#endif
  os << "aux-display pandagl" << endl;
  os << "aux-display tinydisplay" << endl;
  os << "compress-channels #t" << endl;
  os << "display-lists 0" << endl;
  os << "text-encoding utf8" << endl;

  // We don't want DirectEntries to return unicode strings for now.
  os << "direct-wtext 0" << endl;

  os << "text-never-break-before ,.-:?!;。？！、" << endl;
  os << endl;
  os << "early-random-seed 1" << endl;

  os << "verify-ssl 0" << endl;

  os << "http-preapproved-server-certificate-filename ttown4.online.disney.com:46667 gameserver.txt" << endl;

  // For now, restrict SSL communications to the cheaper RC4-MD5
  // cipher.  This should lighten the CPU load on the gameserver.
  os << "ssl-cipher-list RC4-MD5" << endl;
  os << "paranoid-clock 1" << endl;
  os << "lock-to-one-cpu 1" << endl;
  os << "collect-tcp 1" << endl;
  os << "collect-tcp-interval 0.2" << endl;
  os << "respect-prev-transform 1" << endl;
  os << endl;
  os << "# notify settings" << endl;
  // os << "notify-level-downloader debug" << endl;
  //  os << "notify-level-DistributedBattleBldg debug" << endl;
  // os << "notify-level-express debug" << endl;
  // Turn off spam from some noisy notify cats
  os << "notify-level-collide warning" << endl;
  os << "notify-level-chan warning" << endl;
  os << "notify-level-gobj warning" << endl;
  os << "notify-level-loader warning" << endl;
  os << "notify-timestamp #t" << endl;
  os << endl;

  // Give the decompressor and extractor plenty of timeslices before
  // we get the window open.
  os << "decompressor-step-time 0.5" << endl;
  os << "extractor-step-time 0.5" << endl;
  os << endl;

  os << "# Server version" << endl;

  // default settings for ENGLISH
  // sv1.0.40.25.test
  int lang = 0, build = 25;
  char *loginType = "playToken";
#if defined(USE_CASTILLIAN)
  lang = 1;		// sv1.1.33.x
  build = 0;
  loginType = "playToken";
#elif defined(USE_JAPANESE)
  lang = 2;		// sv1.2.33.x
  build = 0;
  loginType = "playToken";
#elif defined(USE_GERMAN)
  lang = 3;		// sv1.3.33.x
  build = 0;
  loginType = "playToken";
#elif defined(USE_PORTUGUESE)
  lang = 4; 	// sv1.4.33.x
  build = 0;
  loginType = "playToken";
#elif defined(USE_FRENCH)
  lang = 5;		// sv1.5.33.x
  build = 0;
  loginType = "playToken";
#endif
  os << "server-version sv1." << lang << ".40." << build << ".test" << endl;
  //os << "server-version dev" << endl;

#ifdef IS_OSX
  os << "server-version-suffix .osx" << endl;
#else
  os << "server-version-suffix " << endl;
#endif

  os << "required-login " << loginType << endl;

  os << "server-failover 80 443" << endl;
  os << "want-fog #t" << endl;
  os << "dx-use-rangebased-fog #t" << endl;
  os << "aspect-ratio 1.333333" << endl;
  // make OnScreenDebug use a font that we're already downloading
  os << "on-screen-debug-font phase_3/models/fonts/ImpressBT.ttf" << endl;

  // The current Toontown code now supports temp-hpr-fix.
  // Welcome to the future.
  os << "temp-hpr-fix 1" << endl;

  // Japanese, Korean, and Chinese clients will like to have these
  // features enabled.
  os << "ime-aware 1" << endl;
  os << "ime-hide 1" << endl;

  // There appears to be some performance issues with using vertex
  // buffers on nvidia drivers in DX8.  Probably I've screwed
  // something up in there.  For now, turn it off; we don't really
  // need (nor can Toontown take advantage of) the potential
  // performance gains anyway.
  os << "vertex-buffers 0" << endl;
  os << "dx-broken-max-index 1" << endl;

  // Temporarily disable the use of D3DPOOL_DEFAULT until we can be
  // confident it is working properly.
  os << "dx-management 1" << endl;

  // setting to determine if new login API from new website is used or not
  os << "tt-specific-login 0" << endl;

  // We don't need Toontown to be case-sensitive on the client end.
  // Clients are sometimes known to rename their system directories
  // without regard to case.
  os << "vfs-case-sensitive 0" << endl;

  // This is designed to prevent people from wedging something on a
  // keyboard button or something in an attempt to defeat the sleep
  // timeout.  After this amount of time, with no changes in keyboard
  // state, all the keys are "released".
  os << "inactivity-timeout 180" << endl;

  // Need to turn on this option to support our broken door triggers.
  os << "early-event-sphere 1" << endl;

  // This keeps the joint hierarchies for the different LOD's of an
  // Actor separate.  Seems to be necessary for the Toons--some of the
  // naked Toons seem to have slightly different skeletons for the
  // different LOD's.
  os << "merge-lod-bundles 0" << endl;

  // Keep the frame rate from going too ridiculously high.  This is
  // mainly an issue when the video driver doesn't support video sync.
  // Limiting the frame rate helps out some of the collision issues
  // that you get with a too-high frame rate (some of our trigger
  // planes require a certain amount of interpenetration to be
  // triggered), and is also just a polite thing to do in general.
  os << "clock-mode limited" << endl
     << "clock-frame-rate 120" << endl;

  // Not using parasite_buffer to speed things up in places where
  // creating this buffer seems to cause frame rate issues such
  // as the Photo Fun game.
  os << "prefer-parasite-buffer 0" << endl;

  // This turns on In Game News
  os << "want-news-page 1" << endl;

  // Temporarily turn off IGN over HTTP due to crash
  // os << "news-over-http 0" << endl;
  // os << "news-base-dir phase_3.5/models/news/" << endl;
  // os << "news-index-filename news_index.txt" << endl;

  os << "news-over-http 1" << endl;
  // os << "in-game-news-url http://download.test.toontown.com/news/" << endl;
  os << "news-base-dir /httpNews" << endl;
  os << "news-index-filename http_news_index.txt" << endl;

  // This should now be on by default
  // os << "want-new-toonhall 1" << endl;

  // need to specify audio library to use, such as Miles or FMOD etc
  os << "audio-library-name p3miles_audio" << endl;
}

static void write_audio(ostream& os, bool sfx_active, bool music_active, float sfx_vol,
                 float music_vol) {
  os << "#" << endl << "# audio related options" << endl << "#" << endl
     << endl;
  os << "# load the loaders" << endl;
  os << "audio-loader mp3" << endl;
  os << "audio-loader midi" << endl;
  os << "audio-loader wav" << endl;


  // This just seems like a good idea.  It doesn't appear to cost too
  // much CPU, and hardware support of midi seems to be spotty.

  // but some HW midi sounds better than the SW midi, so allow it to be configured
  os << "audio-software-midi #" << (false ? "t" : "f") << endl; // TODO Settings

  os << endl;
  if (sfx_active)
    os << "# turn sfx on" << endl << "audio-sfx-active #t" << endl;
  else
    os << "# turn sfx off" << endl << "audio-sfx-active #f" << endl;
  if (music_active)
    os << "# turn music on" << endl << "audio-music-active #t" << endl;
  else
    os << "# turn music off" << endl << "audio-music-active #f" << endl;
  os << endl;
  os << "audio-master-sfx-volume " << sfx_vol << endl;
  os << "audio-master-music-volume " << music_vol << endl;
}

static void write_res(ostream& os, unsigned int x, unsigned int y) {
  os << "#\n# display resolution\n#\n\n";
  os << "win-size " << x << " " << y << endl;
}

static void write_prod(ostream& os) {
  os << "#" << endl << "# server type" << endl << "#" << endl << endl;
  os << "server-type prod" << endl;
}

static void write_dev(ostream& os) {
  os << "#" << endl << "# server type" << endl << "#" << endl << endl;
  os << "server-type dev" << endl;
}

static void write_debug(ostream& os) {
  os << "#" << endl << "# server type" << endl << "#" << endl << endl;
  os << "server-type debug" << endl;
}

// stricmp() isn't standard ANSI, although it should be.  We'll use
// our own function as a quick workaround.  This is actually
// duplicated from string_utils.cxx, which we can't link with because
// of the whole Configrc-dtool linking thing.
static int
cmp_nocase(const string &s, const string &s2) {
  string::const_iterator p = s.begin();
  string::const_iterator p2 = s2.begin();

  while (p != s.end() && p2 != s2.end()) {
    if (toupper(*p) != toupper(*p2)) {
      return (toupper(*p) < toupper(*p2)) ? -1 : 1;
    }
    ++p;
    ++p2;
  }

  return (s2.size() == s.size()) ? 0 :
    (s.size() < s2.size()) ? -1 : 1;  // size is unsigned
}

int main(int argc, char*argv[]) {

 bool bPrintHelp=false;
 bool bDontOverwriteExistingSettings=false;
 bool bWriteStdout=false;
 bool bSaveSettings=false;
 bool bSetCursor=false;
 bool bUseCustomCursor;
 bool bPickBestRes=false;
 bool bSetLowRes=false;
 bool bChangedSettings = false;
 bool bDoSetWindowedMode=false;
 bool bWindowedMode;
 bool bDoSetShowFPSMeter=false;  // dont want to change this unless user explicitly specified to
 bool bShowFPSMeter;
 bool bDoSetForceSWMidi=false;  // dont want to change this unless user explicitly specified to
 bool bForceSWMidi;

 for (int a = 1; a < argc; a++) {
    if ((argv[a] != (char*)0L) && (strlen(argv[a])>1) &&
        (argv[a][0] == '-') ||
        (argv[a][0] == '/')) {

        char *pArgStr=argv[a]+1;
        if(cmp_nocase(pArgStr,"NoOverride")==0) {
          bDontOverwriteExistingSettings=true;
        } else if(cmp_nocase(pArgStr,"save")==0) {
          bSaveSettings=true;
        } else if(cmp_nocase(pArgStr,"lowres")==0) {
          bSaveSettings=true;
          bSetLowRes=true;
        } else if(cmp_nocase(pArgStr,"fullscreen")==0) {
          bSaveSettings=true;
          bWindowedMode=false;
          bDoSetWindowedMode=true;
        } else if(cmp_nocase(pArgStr,"windowed")==0) {
          bSaveSettings=true;
          bSetLowRes=true;  // make sure window is not bigger than desktop initially
          bWindowedMode=true;
          bDoSetWindowedMode=true;
        } else if(cmp_nocase(pArgStr,"show_fps")==0) {
          bSaveSettings=true;
          bShowFPSMeter=true;
          bDoSetShowFPSMeter=true;
        } else if(cmp_nocase(pArgStr,"hide_fps")==0) {
          bSaveSettings=true;
          bShowFPSMeter=false;
          bDoSetShowFPSMeter=true;
        } else if(cmp_nocase(pArgStr,"force_sw_midi")==0) {
          bSaveSettings=true;
          bForceSWMidi=true;
          bDoSetForceSWMidi=true;
        } else if(cmp_nocase(pArgStr,"allow_hw_midi")==0) {
          bSaveSettings=true;
          bForceSWMidi=false;
          bDoSetForceSWMidi=true;
        } else if(cmp_nocase(pArgStr,"stdout")==0) {    // this is usually hidden
          bWriteStdout=true;
        } else if(cmp_nocase(pArgStr,"cursor_on")==0) {
          bSetCursor=true;
          bUseCustomCursor=true;
          bChangedSettings = true;
        } else if(cmp_nocase(pArgStr,"cursor_off")==0) {
          bSetCursor=true;
          bUseCustomCursor=false;
          bChangedSettings = true;
        } else if(cmp_nocase(pArgStr,"pickbestres")==0) {
          bPickBestRes=true;
        } else {
          cerr << "Invalid argument: " << argv[a] << endl;
          bPrintHelp=true;
        }
    } else {
       cerr << "Invalid argument: " << argv[a] << endl;
       bPrintHelp=true;
    }
  }

  bool bDoSavedSettingsExist = false;

  if (bChangedSettings && !bWriteStdout) {
    // If the user specified one of the -OGL etc. options, but not
    // -stdout, he probably meant to specifiy -save to save those
    // changes for the next run of Toontown.

    // note: NoOverride cancels the save if file 'useropt' exists
    bSaveSettings = true;
  }

  if(bPrintHelp) {
   cerr << "Syntax: configrc [options]\n";
   cerr << "Options:\n";
   cerr << "-cursor_off:  use standard windows mouse cursor\n";
   cerr << "-cursor_on:   use custom toontown mouse cursor\n";
   cerr << "-lowres:      set the startup screen resolution to 640x480\n";
   cerr << "-fullscreen:  use fullscreen mode\n";
   cerr << "-windowed:    use windowed mode\n";
   cerr << "-show_fps:    show frames/sec perf meter\n";
   cerr << "-hide_fps:    do not show frames/sec perf meter\n";
   cerr << "-force_sw_midi: force use of software-midi to play midi music\n";
   cerr << "-allow_hw_midi: allow use of midi hardware to play midi music, if it exists\n";
   cerr << "-NoOverride:  ignore new setting specifications if saved options file exists\n";

   // Let's not advertise this option; it's just for internal use and
   // telling users about it makes our config options that much easier
   // to hack
   //   cerr << "-stdout:     write new Configrc to stdout\n";

   // mostly useless to advertise since only I know what it does
   // cerr << "-pickbestres: try to pick a startup screen resolution based on vidmem size\n";


   cerr << "-save:        save settings to '" << "(none)" << "' file (default)\n";
   exit(1);
  }

  // first write out any changes to the Settings object, then translate settings to a Configrc

  // this allows the user to change out of a bad scrn resolution outside of TT

#ifdef USE_OFSTREAM
  pofstream os("Configrc");
#else
  ostream& os = cout;
#endif


  if(!bWriteStdout) {
#ifdef USE_OFSTREAM
      os.close();
#endif
      return 0;
  }

  write_const(os);
  os << endl;

  if(true) { // Settings TODO
    os << "cursor-filename toonmono.cur" << endl << endl;
    //  not using 256 color cursors right now due to common driver probs
    //  os << "win32-color-cursor phase_3/models/gui/toon.cur" << endl;
  }

  if(true) { // Settings TODO
    os << "show-frame-rate-meter #t" << endl << endl;
  }

#if 0  // This seems to crash on dual-core CPU's, and it's not worth the trouble of fixing it.
  #ifdef WIN32_VC
    float lod_stress_factor=1.0f;

    // stupid hack 1-time adjust of lod stress factor based on CPU speed to reduce close-up
    // popping on faster machines.   this is a placeholder until we do a system that adjusts
    // lod_stress_factor dynamically based on current fps

    DWORD Mhz=FindCPUMhz(0.1f);
    // lower lods are not yet designed to be viewed closer up,
    // cant increase stress to >1 yet
     if(Mhz<1000)
        lod_stress_factor=1.0f;
     else if(Mhz<1300)
        lod_stress_factor=0.7f;
     else if(Mhz<1700)
        lod_stress_factor=0.3f;
     else lod_stress_factor=0.25f;

     os << "lod-stress-factor " << lod_stress_factor << endl << endl;
  #endif
#endif  // 0

  os << "load-display pandagl" << endl;
  os << endl;

  char fs_str[2];
  fs_str[0]=(true ? 'f' : 't'); // Settings TODO windowed
  fs_str[1]='\0';
  os << "fullscreen #" << fs_str << "\n\n";

  write_audio(os, 1, 1,
              1.0, 1.0);
  os << endl;

  unsigned int xsize,ysize;
  xsize = 800;
  ysize = 600;
  write_res(os,xsize,ysize);
  os << endl;

  if(bPickBestRes && !bDoSavedSettingsExist) {
      // right now pickbestres only works for dx9, so in case we switch to dx8/ogl we need to write
      // a win-size res as normal.

      // for now behavior is 'no-override' by default,
      // if file 'useropt' already exists, dont want to override a saved res in that
      os << "pick-best-screenres #t\n\n";
  }

  write_prod(os); // write_dev or write_debug
#ifdef USE_OFSTREAM
  os.close();
#endif

  return 0;
}
