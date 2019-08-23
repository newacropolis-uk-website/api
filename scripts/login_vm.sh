[[ -z "${TRAVIS_TAG}" ]] && (echo $TRAVIS_KEY | base64 --decode > travis_rsa) || echo 'no'
eval "$(ssh-agent -s)"
chmod 600 travis_rsa
ssh-add travis_rsa
