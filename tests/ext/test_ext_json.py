
import os
import json
from unittest.mock import Mock
from cement.ext.ext_json import JsonConfigHandler
from cement.utils.test import TestApp
from cement.utils import fs

CONFIG_PARSED = dict(
    section=dict(
        subsection=dict(
            list=['item1', 'item2', 'item3', 'item4'],
            key='value'),
        key1='ok1',
        key2='ok2',
    ),
)


CONFIG = fs.join(os.path.dirname(__file__), '..',
                 'data', 'config', 'config.json')


class JsonApp(TestApp):
    class Meta:
        extensions = ['json']
        output_handler = 'json'
        config_handler = 'json'
        config_files = [CONFIG]
        argv = ['-o', 'json']
        meta_defaults = {'output.json': {'overridable': True}}


def test_json():
    with JsonApp() as app:
        app.run()
        res = app.render(dict(foo='bar'))
        json_res = json.dumps(dict(foo='bar'))
        assert res == json_res


def test_has_section():
    with JsonApp() as app:
        assert app.config.has_section('section')


def test_keys():
    with JsonApp() as app:
        assert 'subsection' in app.config.keys('section')


def test_parse_file_bad_path():
    JsonConfigHandler._parse_file = Mock()
    with JsonApp(config_files=['./some_bogus_path']):
        assert not JsonConfigHandler._parse_file.called


def test_parse_file():
    with JsonApp() as app:
        assert app.config.get('section', 'key1') == 'ok1'
        assert app.config.get_section_dict('section') == \
            CONFIG_PARSED['section']


def test_handler_override_options_is_none():
    class MyApp(JsonApp):
        class Meta:
            core_handler_override_options = {}
            handler_override_options = {}
            argv = []

    with MyApp() as app:
        app.run()
        app.render(dict(foo='bar'))


def test_get_dict():
    with JsonApp() as app:
        _config = app.config.get_dict()
        assert _config['log.logging']['level'] == 'INFO'
