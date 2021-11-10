// Filename: pandanx.cxx
// Created by:  pro-rsoft (8Jun09)
//
////////////////////////////////////////////////////////////////////

#include "pandanx.h"

#include "config_glesgsg.h"

#include "config_nxdisplay.h"
#include "nxGraphicsPipe.h"

// By including checkPandaVersion.h, we guarantee that runtime
// attempts to load libpandagles.so/.dll will fail if they inadvertently
// link with the wrong version of libdtool.so/.dll.

#include "checkPandaVersion.h"

////////////////////////////////////////////////////////////////////
//     Function: init_libpandagles
//  Description: Initializes the library.  This must be called at
//               least once before any of the functions or classes in
//               this library can be used.  Normally it will be
//               called by the static initializers and need not be
//               called explicitly, but special cases exist.
////////////////////////////////////////////////////////////////////
void
init_libpandanx() {
  init_libglesgsg();
  init_libnxdisplay();
}

////////////////////////////////////////////////////////////////////
//     Function: get_pipe_type_pandagles
//  Description: Returns the TypeHandle index of the recommended
//               graphics pipe type defined by this module.
////////////////////////////////////////////////////////////////////
int
get_pipe_type_pandanx() {
  return nxGraphicsPipe::get_class_type().get_index();
}
