if [[ -z "${TRAVIS_TAG}" ]]; then
  echo "using preview key"
  export TRAVIS_KEY=$TRAVIS_KEY_preview
else
  echo "using live key" 
  export TRAVIS_KEY=$TRAVIS_KEY_live
fi
