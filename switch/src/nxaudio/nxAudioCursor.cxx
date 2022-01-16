#include "nxAudioCursor.h"
#include <opus/opusfile.h>

namespace libnx {
    #include <switch.h>
}

#include "virtualFileSystem.h"

TypeHandle NxAudioCursor::_type_handle;

// This is from libnx example ; we consider we should be working
// in a same thread, so let's hope this is safe enough
static size_t opuspkt_tmpbuf_size = sizeof(libnx::HwopusHeader) + 4096*48;
static libnx::u8* opuspkt_tmpbuf;
static Mutex decode_lock("Nx Audio Lock");
    
int hw_decode(void *_ctx, OpusMSDecoder *_decoder, void *_pcm, const ogg_packet *_op, int _nsamples, int _nchannels, int _format, int _li) {
    MutexHolder holder(decode_lock);
    
    libnx::HwopusDecoder *decoder = (libnx::HwopusDecoder*)_ctx;
    libnx::HwopusHeader *hdr = NULL;
    size_t pktsize, pktsize_extra;

    libnx::Result rc = 0;
    libnx::s32 DecodedDataSize = 0;
    libnx::s32 DecodedSampleCount = 0;

    if (_format != OP_DEC_FORMAT_SHORT) return OPUS_BAD_ARG;

    pktsize = _op->bytes;//Opus packet size.
    pktsize_extra = pktsize+8;//Packet size with HwopusHeader.

    if (pktsize_extra > opuspkt_tmpbuf_size) return OPUS_INTERNAL_ERROR;

    hdr = (libnx::HwopusHeader*)opuspkt_tmpbuf;
    memset(opuspkt_tmpbuf, 0, pktsize_extra);

    hdr->size = __builtin_bswap32(pktsize);
    memcpy(&opuspkt_tmpbuf[sizeof(libnx::HwopusHeader)], _op->packet, pktsize);

    rc = libnx::hwopusDecodeInterleaved(decoder, &DecodedDataSize, &DecodedSampleCount, opuspkt_tmpbuf, pktsize_extra, (libnx::s16*)_pcm, _nsamples * _nchannels * sizeof(opus_int16));

    if (R_FAILED(rc)) return OPUS_INTERNAL_ERROR;
    
    if (DecodedDataSize != pktsize_extra || DecodedSampleCount != _nsamples) return OPUS_INVALID_PACKET;

    return 0;
}

int custom_read(istream *_stream, char *_ptr, int _nbytes)
{
    _stream->clear();
    _stream->read(_ptr, _nbytes);
    return _stream->gcount();
}

int custom_seek(istream *_stream, opus_int64 _offset, int _whence)
{
    std::ios_base::seekdir way = std::ios_base::beg;
    if (_whence == SEEK_SET)
        way = std::ios_base::beg;
    else if (_whence == SEEK_CUR)
        way = std::ios_base::cur;
    else if (_whence == SEEK_END)
        way = std::ios_base::end;
    
    _stream->clear();
    _stream->seekg(_offset, way);
    if (_stream->fail())
        return -1;
    
    return 0;
}

opus_int64 custom_tell(istream *_stream)
{
    return _stream->tellg();
}

int custom_close(istream *_stream)
{
    VirtualFileSystem *vfs = VirtualFileSystem::get_global_ptr();
    vfs->close_read_file(_stream);
    return 0;
}



NxAudioCursor::
NxAudioCursor(NxAudio *src) :
    MovieAudioCursor(src)
{    
    _opus_file = NULL;
    
    static libnx::HwopusDecoder hwdecoder = {0};
    static bool initialized = false;
    
    if (!initialized)
    {
        opuspkt_tmpbuf = (libnx::u8*)malloc(opuspkt_tmpbuf_size);
    
        libnx::Result res = libnx::hwopusDecoderInitialize(&hwdecoder, 48000, 2);
        initialized = true;
    }
    
    VirtualFileSystem *vfs = VirtualFileSystem::get_global_ptr();
    
    Filename filename = Filename::binary_filename(src->_filename);
    filename.set_extension("opus");
    
    istream *strm = vfs->open_read_file(filename, true);
    
    if (!strm)
    {
        _aborted = true;
        return;
    }
    
    const OpusFileCallbacks cb = {
        .read = (op_read_func)custom_read,
        .seek = (op_seek_func)custom_seek,
        .tell = (op_tell_func)custom_tell,
        .close = (op_close_func)custom_close
    };
    
    int error;
    _opus_file = op_open_callbacks(strm, &cb, NULL, 0, &error);
    
    if (!_opus_file)
    {
        _aborted = true;
        return;
    }
    
    op_set_decode_callback(_opus_file, hw_decode, &hwdecoder);
    
    _audio_rate = 48000;
    _audio_channels = 2;
    _can_seek = true;
    _can_seek_fast = true;
    _length = op_pcm_total(_opus_file, -1) / 48000.0;
    
}

NxAudioCursor::
~NxAudioCursor()
{
    if (_opus_file)
        op_free(_opus_file);
}

void NxAudioCursor::
seek(double t)
{
    if (!_opus_file)
        return;
    
    _last_seek = t;
    ogg_int64_t target_ts = t * 48000.0;
    int opret = op_pcm_seek(_opus_file, target_ts);
    _samples_read = 0;
}

void NxAudioCursor::
read_samples(int n, PN_int16 *data)
{
    PN_int16* end = data + n * 2;
    
    memset(data, 0, end  - data);
    if (!_opus_file)
        return;
    
    while (data < end)
    {        
        int opret = op_read(_opus_file, data, end - data, NULL);
        if (opret <= 0)
            break;
        
        data += opret * 2;
        _samples_read += opret;
    }
}