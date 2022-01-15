#ifndef NXAUDIOCURSOR_H
#define NXAUDIOCURSOR_H
#ifdef __SWITCH__

#include "pandabase.h"
#include "namable.h"
#include "texture.h"
#include "pointerTo.h"

#include "nxAudio.h"

class NxAudioCursor : public MovieAudioCursor {
  friend class NxAudio;

PUBLISHED:
  NxAudioCursor(NxAudio *src);
  virtual ~NxAudioCursor();
  virtual void seek(double offset);
  
public:
  virtual void read_samples(int n, PN_int16 *data);
  
protected:
  istream* _file;
  
  
public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    TypedWritableReferenceCount::init_type();
    register_type(_type_handle, "NxAudioCursor",
                  MovieAudioCursor::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
  static TypeHandle _type_handle;
};

#endif // __SWITCH__
#endif // NX_AUDIO.H
