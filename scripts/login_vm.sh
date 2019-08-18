if [[ -z "${TRAVIS_TAG}" ]]; then
  echo 'no'
else
  echo "using live key" 
  echo $TRAVIS_KEY | base64 --decode > travis_rsa
fi

eval "$(ssh-agent -s)"
chmod 600 travis_rsa
ssh-add travis_rsa
