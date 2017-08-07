from mock import call
import pytest

from app import create_app, get_root_path
from app.config import Development, Preview, Live


class WhenInitializingApp(object):

    @pytest.mark.parametrize("returnval,config_class", [
        ('www-preview', Preview),
        ('www-live', Live),
        ('', Development)
    ])
    def it_has_correct_environment(self, mocker, returnval, config_class):
        mocker.patch("app.get_root_path", return_value=returnval)
        mocked_config = mocker.patch("app.application.config.from_object", return_value={})
        create_app()

        assert mocked_config.called
        assert mocked_config.call_args == call(config_class)
