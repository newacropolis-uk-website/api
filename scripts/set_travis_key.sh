if [[ -z "${TRAVIS_TAG}" ]]; then
  echo 'no'
else
  echo "using live key" 
  export TRAVIS_KEY=$TRAVIS_KEY_live
fi
