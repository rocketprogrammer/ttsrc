#include "nxAudioCursor.h"

namespace libnx {
    #include <switch.h>
}

#include "virtualFileSystem.h"

TypeHandle NxAudioCursor::_type_handle;

NxAudioCursor::
NxAudioCursor(NxAudio *src) :
    MovieAudioCursor(src)
{    
    _audio_rate = 48000;
    _audio_channels = 2;
    _can_seek = true;
    _can_seek_fast = true;
    VirtualFileSystem *vfs = VirtualFileSystem::get_global_ptr();

    Filename name = Filename::binary_filename(src->_filename);
    name.set_extension("raw");
    
    _file = vfs->open_read_file(name, true);
    
    _file->seekg(0, ios::end);
    _length = _file->tellg() / (48000.0 * 4.0);
    printf("length %f\n", _length);
    _file->seekg(0, ios::beg);
}

NxAudioCursor::
~NxAudioCursor()
{
    VirtualFileSystem *vfs = VirtualFileSystem::get_global_ptr();
    vfs->close_read_file(_file);
}

void NxAudioCursor::
seek(double t)
{
    // 48000 hz, 16 bits (2 bytes), 2 channels
    _last_seek = t;
    _file->clear();
    _file->seekg(t * 48000 * 2 * 2, ios::beg);
    _samples_read = 0;
}

void NxAudioCursor::
read_samples(int n, PN_int16 *data)
{
    memset(data, 0, n * 4);
    _file->clear();
    _file->read((char*)data, n * 2 * 2); // 2 channels, 2 bytes
    _samples_read += n;
}