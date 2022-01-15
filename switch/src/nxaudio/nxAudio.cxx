#ifdef __SWITCH__

#include "nxAudio.h"
#include "nxAudioCursor.h"

TypeHandle NxAudio::_type_handle;

NxAudio::
NxAudio(const Filename &name) :
  MovieAudio(name)
{
  _filename = name;
}

NxAudio::
~NxAudio() {
}

PT(MovieAudioCursor) NxAudio::
open() {
  PT(NxAudioCursor) result = new NxAudioCursor(this);
  return (MovieAudioCursor*)result;
}

////////////////////////////////////////////////////////////////////

#endif // __SWITCH__
