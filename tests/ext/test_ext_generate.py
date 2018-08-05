
import os
import re
from unittest.mock import Mock
from cement import TestApp, Controller, FrameworkError
from cement.utils import shell
from cement.utils.test import raises


def exists_join(*paths):
    return os.path.exists(os.path.join(*paths))


class GenerateBase(Controller):
    class Meta:
        label = 'base'


class GenerateApp(TestApp):
    class Meta:
        extensions = ['jinja2', 'yaml', 'generate', 'alarm']
        template_handler = 'jinja2'
        template_module = 'tests.data.templates'
        handlers = [GenerateBase]


def test_generate(tmp):
    argv = ['generate', 'test1', tmp.dir, '--defaults']

    with GenerateApp(argv=argv) as app:
        app.run()

        # should have everything
        assert exists_join(tmp.dir, 'take-me')
        res = open(os.path.join(tmp.dir, 'take-me'), 'r').read()
        assert res.find('bar1') >= 0
        assert res.find('bar2') >= 0
        assert res.find('BAR3') >= 0
        assert res.find('Bar4') >= 0
        assert res.find('bar5') >= 0
        assert res.find('bar6') >= 0

        # copied but not rendered
        assert exists_join(tmp.dir, 'exclude-me')
        res = open(os.path.join(tmp.dir, 'exclude-me'), 'r').read()
        assert re.match('.*foo1 => \{\{ foo1 \}\}.*', res)

        # should not have been copied
        assert not exists_join(tmp.dir, 'ignore-me')

    # test generate again to trigger already exists

    with GenerateApp(argv=argv) as app:
        with raises(AssertionError, match='Destination file already exists'):
            app.run()


def test_missing_base_controller(tmp):
    argv = ['generate', 'test1', tmp.dir, '--defaults']
    with TestApp(argv=argv, extensions=['jinja2', 'generate']) as app:
        msg = 'ext.generate extension requires an application base controller'
        with raises(FrameworkError, match=msg):
            app.run()


def test_prompt(tmp):
    argv = ['generate', 'test1', tmp.dir]

    with GenerateApp(argv=argv) as app:
        msg = "reading from stdin while output is captured"
        with raises(OSError, message=msg):
            app.run()


def test_invalid_case(tmp):
    argv = ['generate', 'test3', tmp.dir, '--defaults']

    with GenerateApp(argv=argv) as app:
        app.run()

        assert exists_join(tmp.dir, 'take-me')
        with open(os.path.join(tmp.dir, 'take-me'), 'r') as f:
            res = f.read()
            # Assert that the case was not modified
            assert 'bar1' in res


def test_invalid_variable_value(tmp):
    argv = ['generate', 'test2', tmp.dir, '--defaults']

    with GenerateApp(argv=argv) as app:
        msg = "Invalid Response (must match: '.*not-bar1.*')"
        with raises(AssertionError, message=msg):
            app.run()


def test_no_default(tmp):
    shell.Prompt.prompt = Mock(return_value='Bogus')
    argv = ['generate', 'test4', tmp.dir]

    with GenerateApp(argv=argv) as app:
        app.run()
        with open(os.path.join(tmp.dir, 'take-me'), 'r') as f:
            res = f.read()
            assert 'Bogus' in res


# coverage

def test_generate_from_template_dir(tmp):
    # argv = ['generate', 'test1', tmp.dir, '--defaults']
    os.makedirs(os.path.join(tmp.dir, 'generate'))
    with GenerateApp(template_dir=tmp.dir) as app:
        app.run()


def test_generate_default_command(tmp):
    argv = ['generate']
    with GenerateApp(argv=argv) as app:
        app.run()
