// Filename: lodNode.I
// Created by:  drose (06Mar02)
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



////////////////////////////////////////////////////////////////////
//     Function: LODNode::Constructor
//       Access: Published
//  Description:
////////////////////////////////////////////////////////////////////
INLINE LODNode::
LODNode(const string &name) :
  PandaNode(name)
{
  set_cull_callback();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Copy Constructor
//       Access: Protected
//  Description:
////////////////////////////////////////////////////////////////////
INLINE LODNode::
LODNode(const LODNode &copy) :
  PandaNode(copy),
  _cycler(copy._cycler)
{
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::add_switch
//       Access: Published
//  Description: Adds a switch range to the LODNode.  This implies
//               that the corresponding child node has been parented
//               to the node.
//
//               The sense of in vs. out distances is as if the object
//               were coming towards you from far away: it switches
//               "in" at the far distance, and switches "out" at the
//               close distance.  Thus, "in" should be larger than
//               "out".
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
add_switch(float in, float out) {
  nassertv(in >= out);

  CDWriter cdata(_cycler);
  cdata->_switch_vector.push_back(Switch(in, out));
  cdata->check_limits();

  if (cdata->_num_shown != 0) {
    mark_internal_bounds_stale();
  }
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::set_switch
//       Access: Published
//  Description: Changes the switching range of a particular child of
//               the LODNode.  See add_switch().
////////////////////////////////////////////////////////////////////
INLINE bool LODNode::
set_switch(int index, float in, float out) {
  nassertr(in >= out, false);

  CDWriter cdata(_cycler);
  nassertr(index >= 0 && index < (int)cdata->_switch_vector.size(), false);
  cdata->_switch_vector[index].set_range(in, out);
  cdata->check_limits();

  if (cdata->_num_shown != 0) {
    mark_internal_bounds_stale();
  }

  return true;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::clear_switches
//       Access: Published
//  Description: Removes the set of switching ranges for the LODNode,
//               presumably in conjunction with removing all of its
//               children.  See add_switch().
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
clear_switches() {
  CDWriter cdata(_cycler);
  cdata->_switch_vector.clear();
  cdata->_lowest = 0;
  cdata->_highest = 0;

  if (cdata->_num_shown != 0) {
    mark_internal_bounds_stale();
  }
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_num_switches
//       Access: Published
//  Description: Returns the number of switch ranges added to the
//               LODNode.  This should correspond to the number of
//               children of the node in order for the LODNode to
//               function correctly.
////////////////////////////////////////////////////////////////////
INLINE int LODNode::
get_num_switches() const {
  CDReader cdata(_cycler);
  return cdata->_switch_vector.size();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_lod_scale
//       Access: Published
//  Description: Returns the multiplier for lod distances
////////////////////////////////////////////////////////////////////
INLINE float LODNode::
get_lod_scale() const {
  CDReader cdata(_cycler);
  return cdata->_lod_scale;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::set_lod_scale
//       Access: Published
//  Description: Sets the multiplier for lod distances. A higher 
//               value means you'll see farther switchs than normal
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
set_lod_scale(float value) {
  CDWriter cdata(_cycler);
  cdata->_lod_scale = value;
}


////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_in
//       Access: Published
//  Description: Returns the "in" distance of the indicated switch
//               range.  This should be larger than the "out" distance
//               of the same range.
////////////////////////////////////////////////////////////////////
INLINE float LODNode::
get_in(int index) const {
  CDReader cdata(_cycler);
  nassertr(index >= 0 && index < (int)cdata->_switch_vector.size(), 0.0);
  return cdata->_switch_vector[index].get_in();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_out
//       Access: Published
//  Description: Returns the "out" distance of the indicated switch
//               range.  This should be smaller than the "in" distance
//               of the same range.
////////////////////////////////////////////////////////////////////
INLINE float LODNode::
get_out(int index) const {
  CDReader cdata(_cycler);
  nassertr(index >= 0 && index < (int)cdata->_switch_vector.size(), 0.0);
  return cdata->_switch_vector[index].get_out();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_lowest_switch
//       Access: Published
//  Description: Returns the index number of the child with the lowest
//               level of detail; that is, the one that is designed to
//               be seen from the farthest away.  This is usually the
//               first child, but it is not necessarily so.
////////////////////////////////////////////////////////////////////
INLINE int LODNode::
get_lowest_switch() const {
  CDReader cdata(_cycler);
  return cdata->_lowest;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_highest_switch
//       Access: Published
//  Description: Returns the index number of the child with the highest
//               level of detail; that is, the one that is designed to
//               be seen from the closest to the camera.  This is
//               usually the last child, but it is not necessarily so.
////////////////////////////////////////////////////////////////////
INLINE int LODNode::
get_highest_switch() const {
  CDReader cdata(_cycler);
  return cdata->_highest;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::force_switch
//       Access: Published
//  Description: Forces the LODNode to show the indicated level
//               instead of the level that would normally be shown
//               based on the distance from the camera.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
force_switch(int index) {
  CDWriter cdata(_cycler);
  cdata->_force_switch = index;
  cdata->_got_force_switch = true;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::clear_force_switch
//       Access: Published
//  Description: Undoes the effect of a previous call to
//               force_switch() and releases the LODNode to once again
//               display the normal level.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
clear_force_switch() {
  CDWriter cdata(_cycler);
  cdata->_got_force_switch = false;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::set_center
//       Access: Published
//  Description: Specifies the center of the LOD.  This is the point
//               that is compared to the camera (in camera space) to
//               determine the particular LOD that should be chosen.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
set_center(const LPoint3f &center) {
  CDWriter cdata(_cycler);
  cdata->_center = center;

  if (cdata->_num_shown != 0) {
    mark_internal_bounds_stale();
  }
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::get_center
//       Access: Published
//  Description: Returns the center of the LOD.  This is the point
//               that is compared to the camera (in camera space) to
//               determine the particular LOD that should be chosen.
////////////////////////////////////////////////////////////////////
INLINE const LPoint3f &LODNode::
get_center() const {
  CDReader cdata(_cycler);
  return cdata->_center;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::is_any_shown
//       Access: Published
//  Description: Returns true if any switch has been shown with
//               show_switch(), indicating the LODNode is in debug
//               show mode; or false if it is in the normal mode.
////////////////////////////////////////////////////////////////////
INLINE bool LODNode::
is_any_shown() const {
  CDReader cdata(_cycler);
  return (cdata->_num_shown != 0);
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::consider_verify_lods
//       Access: Protected
//  Description: To be called internally when the node is rendered,
//               this will raise an assertion if verify-lods is
//               configured true, and verify_child_bounds() returns
//               false.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::
consider_verify_lods(CullTraverser *trav, CullTraverserData &data) {
#ifndef NDEBUG
  if (verify_lods) {
    do_auto_verify_lods(trav, data);
  }
#endif  // NDEBUG
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::CData::Constructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE LODNode::CData::
CData() :
  _center(0.0f, 0.0f, 0.0f),
  _lowest(0),
  _highest(0),
  _got_force_switch(false),
  _force_switch(0),
  _num_shown(0),
  _lod_scale(1)
{
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::CData::Copy Constructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE LODNode::CData::
CData(const LODNode::CData &copy) :
  _center(copy._center),
  _switch_vector(copy._switch_vector),
  _lowest(copy._lowest),
  _highest(copy._highest),
  _bounds_seq(UpdateSeq::old()),
  _got_force_switch(copy._got_force_switch),
  _force_switch(copy._force_switch),
  _num_shown(copy._num_shown),
  _lod_scale(copy._lod_scale)
{
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::Constructor
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE LODNode::Switch::
Switch(float in, float out) : 
  _shown(false),
  _bounds_seq(UpdateSeq::old()),
  _verify_ok(false)
{
  set_range(in, out);
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::get_in
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE float LODNode::Switch::
get_in() const {
  return _in;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::get_out
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE float LODNode::Switch::
get_out() const {
  return _out;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::set_range
//       Access: Public
//  Description:
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
set_range(float in, float out) {
  _in = in;
  _out = out;
  clear_ring_viz();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::in_range
//       Access: Public
//  Description: Returns true if the indicated distance is within the
//               range for the LOD.
////////////////////////////////////////////////////////////////////
INLINE bool LODNode::Switch::
in_range(float dist) const {
  return (dist >= _out && dist < _in);
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::in_range_2
//       Access: Public
//  Description: Returns true if the indicated distance squared is
//               within the range for the LOD.  (The distance value is
//               understood to be the square of the distance from the
//               camera to the object.)
////////////////////////////////////////////////////////////////////
INLINE bool LODNode::Switch::
in_range_2(float dist2) const {
  return (dist2 >= _out * _out && dist2 < _in * _in);
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::rescale
//       Access: Public
//  Description: Scales the switching distances by the indicated factor.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
rescale(float factor) {
  _in *= factor;
  _out *= factor;
  clear_ring_viz();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::is_shown
//       Access: Public
//  Description: Returns true if show() has been called.
////////////////////////////////////////////////////////////////////
INLINE bool LODNode::Switch::
is_shown() const {
  return _shown;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::show
//       Access: Public
//  Description: Shows this ring in debug mode using the indicated
//               color.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
show(const Colorf &color) {
  _shown = true;
  _show_color = color;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::hide
//       Access: Public
//  Description: Undoes a previous call to show().
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
hide() {
  _shown = false;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::get_ring_viz
//       Access: Public
//  Description: Returns a PandaNode suitable for rendering the ring
//               associated with this switch.
////////////////////////////////////////////////////////////////////
INLINE PandaNode *LODNode::Switch::
get_ring_viz() const {
  if (_ring_viz.is_null()) {
    ((Switch *)this)->compute_ring_viz();
  }

  return _ring_viz;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::get_spindle_viz
//       Access: Public
//  Description: Returns a PandaNode suitable for rendering the center
//               spindle of the LODNode, in the color of this switch.
////////////////////////////////////////////////////////////////////
INLINE PandaNode *LODNode::Switch::
get_spindle_viz() const {
  if (_spindle_viz.is_null()) {
    ((Switch *)this)->compute_spindle_viz();
  }

  return _spindle_viz;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::get_viz_model_state
//       Access: Public
//  Description: Returns a RenderState suitable for drawing the
//               visible children of this switch level when the
//               show_switch() debugging mode is enabled.
////////////////////////////////////////////////////////////////////
INLINE const RenderState *LODNode::Switch::
get_viz_model_state() const {
  if (_viz_model_state.is_null()) {
    ((Switch *)this)->compute_viz_model_state();
  }

  return _viz_model_state;
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::write_datagram
//       Access: Public
//  Description: Writes the contents of the Switch out to the
//               datagram, presumably in preparation to writing to a
//               Bam file.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
write_datagram(Datagram &destination) const {
  destination.add_float32(_in);
  destination.add_float32(_out);
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::read_datagram
//       Access: Public
//  Description: Reads the contents of the Switch from the datagram,
//               presumably in response to reading a Bam file.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
read_datagram(DatagramIterator &source) {
  _in = source.get_float32();
  _out = source.get_float32();
}

////////////////////////////////////////////////////////////////////
//     Function: LODNode::Switch::clear_ring_viz
//       Access: Private
//  Description: Resets the internal cache values for the ring and
//               spindle viz, and related pointers, for the
//               set_switch() debugging mode.
////////////////////////////////////////////////////////////////////
INLINE void LODNode::Switch::
clear_ring_viz() {
  _ring_viz.clear();
  _spindle_viz.clear();
  _viz_model_state.clear();
  _bounds_seq = UpdateSeq::old();
}
