#!/usr/bin/env bash
ffmpeg -y -framerate 30 -i frames/frame_%04d.png -i drone_tour.wav \
  output.mp4

  # -vf "setsar=1:1,noise=alls=2:allf=t,format=yuv420p" \
  # -c:v libx264 -preset slow -crf 16 \
  # -x264-params "aq-mode=3:aq-strength=0.8" \
  # -profile:v high -level:v 5.1 -maxrate 24M -bufsize 48M \
  # -r 30 -g 90 -keyint_min 90 -sc_threshold 0 \
  # -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  # -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart output.mp4
