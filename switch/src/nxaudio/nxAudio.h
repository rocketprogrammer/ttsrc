#ifndef NXAUDIO_H
#define NXAUDIO_H
#ifdef __SWITCH__

#include "movieAudio.h"

class NxAudioCursor;

class EXPCL_PANDA_MOVIES NxAudio : public MovieAudio {

PUBLISHED:
  NxAudio(const Filename &name);
  virtual ~NxAudio();
  virtual PT(MovieAudioCursor) open();

 private:
  friend class NxAudioCursor;
  
public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    TypedWritableReferenceCount::init_type();
    register_type(_type_handle, "NxAudio",
                  MovieAudio::get_class_type());
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
