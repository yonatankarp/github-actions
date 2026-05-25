#!/bin/bash

# Script to update a tag to the latest commit on the current branch:
# Parameters:
# - Tag name (e.g. "v1")

git tag -d "$1"
git push --delete origin "$1"
git tag "$1"
git push origin "$1"
