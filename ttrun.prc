#
# constant config settings
#

chan-config-sanity-check #f
window-title Toontown
require-window 0
language english
icon-filename resources/toontown.ico

cull-bin shadow 15 fixed
cull-bin ground 14 fixed
cull-bin gui-popup 60 unsorted
default-model-extension .bam
#plugin-path .
# downloader settings
decompressor-buffer-size 32768
extractor-buffer-size 32768
patcher-buffer-size 512000
downloader-timeout 15
downloader-timeout-retries 4
downloader-disk-write-frequency 4
downloader-byte-rate 125000
downloader-frequency 0.1
want-render2dp 1

# texture settings
textures-power-2 down

# loader settings
load-file-type toontown
dc-file phase_3/etc/toon.dc
dc-file phase_3/etc/otp.dc
aux-display pandadx9
aux-display pandadx8
aux-display pandagl
aux-display tinydisplay
compress-channels #t
display-lists 0
text-encoding utf8
direct-wtext 0
text-never-break-before ,.-:?!;。？！、

early-random-seed 1
verify-ssl 0
http-preapproved-server-certificate-filename ttown4.online.disney.com:46667 gameserver.txt
#ssl-cipher-list RC4-MD5
paranoid-clock 1
lock-to-one-cpu 1
collect-tcp 1
collect-tcp-interval 0.2
respect-prev-transform 1

# notify settings
notify-level warning
default-directnotify-level warning
notify-level-collide warning
notify-level-chan warning
notify-level-gobj warning
notify-level-loader warning

notify-timestamp #t

decompressor-step-time 0.5
extractor-step-time 0.5

# Server version
server-version dev
server-version-suffix 
required-login playToken
server-failover 80 443
want-fog #t
dx-use-rangebased-fog #t
aspect-ratio 1.333333
on-screen-debug-font phase_3/models/fonts/ImpressBT.ttf
temp-hpr-fix 1
ime-aware 1
ime-hide 1
vertex-buffers 0
dx-broken-max-index 1
dx-management 1
tt-specific-login 1
vfs-case-sensitive 0
inactivity-timeout 180
early-event-sphere 1
merge-lod-bundles 0
clock-mode limited
clock-frame-rate 120
prefer-parasite-buffer 0
want-news-page 0
news-over-http 1
news-base-dir /httpNews
news-index-filename http_news_index.txt
audio-library-name p3miles_audio

cursor-filename resources/toonmono.cur

show-frame-rate-meter #t

load-display pandagl

fullscreen #f

#
# audio related options
#

# load the loaders
audio-loader mp3
audio-loader midi
audio-loader wav
audio-software-midi #f

# turn sfx on
audio-sfx-active #t
# turn music on
audio-music-active #t

audio-master-sfx-volume 1
audio-master-music-volume 1

#
# display resolution
#

win-size 800 600

#
# server type
#

server-type prod

#
# custom
#
color-bits 8 8 8
alpha-bits 8
default-server-constants 1
fake-playtoken test
game-server 127.0.0.1
want-magic-words 1