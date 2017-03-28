#!/bin/bash
# IMPORTANT: Make sure this uses unix-style line-endings!
base_dir=/usr/src/larsethia

cd ${base_dir}

# Cleanup running things
rm server/portal.pid || true
rm server/server.pid || true

# Make sure our database is ready
evennia migrate || true

# Run server in blocking mode
evennia -i start
