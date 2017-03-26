#!/bin/sh
# IMPORTANT: Make sure this uses unix-style line-endings!

# Cleanup running things
rm server/portal.pid || true
rm server/server.pid || true

# Make sure our database is ready
evennia migrate || true

# Run server in blocking mode
evennia -i start
