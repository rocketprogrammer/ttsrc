#include "config_nxdisplay.h"
#include "nxGraphicsPipe.h"
#include "nxGraphicsWindow.h"
#include "nxGraphicsStateGuardian.h"
#include "graphicsPipeSelection.h"
#include "pandaSystem.h"

Configure(config_nxdisplay);

ConfigureFn(config_nxdisplay) {
  init_libnxdisplay();
}

void
init_libnxdisplay() {
  static bool initialized = false;
  if (initialized) {
    return;
  }
  initialized = true;

  nxGraphicsPipe::init_type();
  nxGraphicsWindow::init_type();
  nxGraphicsStateGuardian::init_type();

  GraphicsPipeSelection *selection = GraphicsPipeSelection::get_global_ptr();
  selection->add_pipe_type(nxGraphicsPipe::get_class_type(),
                           nxGraphicsPipe::pipe_constructor);

  PandaSystem *ps = PandaSystem::get_global_ptr();
  ps->set_system_tag("OpenGL ES 2", "window_system", "NX");
}
