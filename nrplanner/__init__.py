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
#
# This repository is the working one; the published repository is
# DankYeeter/Nightreign-Helper. 1.1.0 was tagged there and the bump was never
# mirrored here, so this file still read 1.0.0 while 1.1.0 was in players'
# hands. Checked at the time of writing 1.1.1: every .py file under nrplanner/
# and nrdata/ is byte-identical between the two, and this line was the only
# difference. Keep them in step -- a version that disagrees with what shipped
# is worse than no version, because a bug report names a build that never
# existed.
__version__ = "1.6.0"
