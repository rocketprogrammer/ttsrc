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

void
init_libpandanx() {
  init_libglesgsg();
  init_libnxdisplay();
}

int
get_pipe_type_pandanx() {
  return nxGraphicsPipe::get_class_type().get_index();
}
