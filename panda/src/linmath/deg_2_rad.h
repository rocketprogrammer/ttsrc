// Filename: deg_2_rad.h
// Created by:  drose (29Sep99)
//
////////////////////////////////////////////////////////////////////
//
// PANDA 3D SOFTWARE
// Copyright (c) Carnegie Mellon University.  All rights reserved.
//
// All use of this software is subject to the terms of the revised BSD
// license.  You should have received a copy of this license along
// with this source code in a file named "LICENSE."
//
////////////////////////////////////////////////////////////////////

#ifndef DEG_2_RAD_H
#define DEG_2_RAD_H

#include "pandabase.h"

#include "mathNumbers.h"

BEGIN_PUBLISH
INLINE_LINMATH double deg_2_rad( double f ) { return f * MathNumbers::deg_2_rad; }
INLINE_LINMATH double rad_2_deg( double f ) { return f * MathNumbers::rad_2_deg; }

INLINE_LINMATH float deg_2_rad( float f ) { return f * MathNumbers::deg_2_rad_f; }
INLINE_LINMATH float rad_2_deg( float f ) { return f * MathNumbers::rad_2_deg_f; }
END_PUBLISH

#endif

