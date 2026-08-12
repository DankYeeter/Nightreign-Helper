"""Nightreign Helper GUI."""

# Shown in the window title and the environment check, so that a bug report
# names a build rather than "the latest one". The release workflow checks this
# against the tag it is building and fails if the two disagree.
#
# KEEP THIS IN STEP WITH WHAT SHIPS. The rule, so it does not have to be
# rediscovered: bump the patch digit for a hotfix (1.0.1), the middle one when
# a feature or a corrected number lands (1.1.0), and tag only what matches.
# Nothing has been released before 1.0.0, so everything built up to that tag is
# part of it rather than an increment on it.
__version__ = "1.1.0"
