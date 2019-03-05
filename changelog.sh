#!/usr/bin/env sh
MERGE_PREFIX="Merge pull request"

if [ ! -z "$TRAVIS_TAG" ]
then
    TRAVIS_COMMIT_RANGE="$(git describe --abbrev=0 --tags $TRAVIS_TAG^)..$TRAVIS_TAG"
fi

GIT_COMMIT_LOG="$(git log --reverse --format='%h: %s (by %cn)' $TRAVIS_COMMIT_RANGE)"


echo " <b>Changelog for TelegramCompanion</b>${NEWLINE}"

printf '%s\n' "$GIT_COMMIT_LOG" | while IFS= read -r line
do
  echo "- ${line}"
done
echo "${NEWLINE}"
echo "https://github.com/nitanmarcel/TelegramCompanion/compare/$TRAVIS_COMMIT_RANGE"
