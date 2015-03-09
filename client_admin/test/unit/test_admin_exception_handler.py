import mock

from pulp.bindings import exceptions as bindings_exceptions
from pulp.client.admin.exception_handler import AdminExceptionHandler
from pulp.client.extensions import exceptions
from pulp.client.extensions.core import TAG_FAILURE, TAG_PARAGRAPH
from pulp.common import auth_utils
from pulp.devel.unit import base


class AdminExceptionHandlerTests(base.PulpClientTests):

    def setUp(self):
        super(AdminExceptionHandlerTests, self).setUp()

        self.handler = AdminExceptionHandler(self.prompt, self.config)

    def test_handle_authentication_failed(self):
        # Test
        self.handler._handle_authentication_failed()

        # Verify
        self.assertTrue('Authentication' in self.recorder.lines[0])
        self.assertEqual(TAG_FAILURE, self.prompt.get_write_tags()[0])
        self.assertTrue('certificate' in self.recorder.lines[2])  # skip blank line
        self.assertEqual(TAG_PARAGRAPH, self.prompt.get_write_tags()[1])

    def test_handle_permission_error(self):
        # Test
        self.handler._handle_permission_error()

        # Verify
        self.assertTrue('Permissions' in self.recorder.lines[0])
        self.assertEqual(TAG_FAILURE, self.prompt.get_write_tags()[0])
        self.assertTrue('appropriate permissions' in self.recorder.lines[2])  # skip blank line
        self.assertEqual(TAG_PARAGRAPH, self.prompt.get_write_tags()[1])

    def test_handle_invalid_username(self):
        # Test
        self.handler._handle_invalid_username()

        # Verify
        self.assertTrue('Invalid Username' in self.recorder.lines[0])
        self.assertEqual(TAG_FAILURE, self.prompt.get_write_tags()[0])

    def test_handle_unknown(self):
        # Test
        self.handler._handle_unknown()

        # Verify
        self.assertTrue('Unknown' in self.recorder.lines[0])
        self.assertEqual(TAG_FAILURE, self.prompt.get_write_tags()[0])
        self.assertTrue('server log' in self.recorder.lines[2])  # skip blank line
        self.assertEqual(TAG_PARAGRAPH, self.prompt.get_write_tags()[1])

    def test_handle_expired_client_cert(self):
        # Test
        e = bindings_exceptions.ClientCertificateExpiredException('x')
        code = self.handler.handle_expired_client_cert(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(TAG_PARAGRAPH, self.prompt.get_write_tags()[1])
        self.assertTrue('session certificate' in self.recorder.lines[2])


class AdminExceptionHandlerDispatchingTests(base.PulpClientTests):

    def setUp(self):
        super(AdminExceptionHandlerDispatchingTests, self).setUp()

        # Mock out all of the handling methods, we're just testing to see that the
        # dispatching from error code to handle method is correct
        self.handler = AdminExceptionHandler(self.prompt, self.config)
        self.handler._handle_authentication_failed = mock.MagicMock()
        self.handler._handle_invalid_username = mock.MagicMock()
        self.handler._handle_permission_error = mock.MagicMock()
        self.handler._handle_unknown = mock.MagicMock()

    def test_handle_code_failed(self):
        # Setup
        response_doc = auth_utils.generate_failure_response(auth_utils.CODE_FAILED)
        e = bindings_exceptions.PermissionsException(response_doc)

        # Test
        code = self.handler.handle_permission(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(self.handler._handle_authentication_failed.call_count, 1)

    def test_handle_code_permission(self):
        # Setup
        response_doc = auth_utils.generate_failure_response(auth_utils.CODE_PERMISSION)
        e = bindings_exceptions.PermissionsException(response_doc)

        # Test
        code = self.handler.handle_permission(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(self.handler._handle_permission_error.call_count, 1)

    def test_handle_code_invalid_ssl_cert(self):
        # Setup
        response_doc = auth_utils.generate_failure_response(auth_utils.CODE_INVALID_SSL_CERT)
        e = bindings_exceptions.PermissionsException(response_doc)

        # Test
        code = self.handler.handle_permission(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(self.handler._handle_authentication_failed.call_count, 1)

    def test_handle_code_username(self):
        # Setup
        response_doc = auth_utils.generate_failure_response(auth_utils.CODE_USER_PASS)
        e = bindings_exceptions.PermissionsException(response_doc)

        # Test
        code = self.handler.handle_permission(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(self.handler._handle_invalid_username.call_count, 1)

    def test_handle_code_unknown(self):
        # Setup
        response_doc = auth_utils.generate_failure_response('foo')
        e = bindings_exceptions.PermissionsException(response_doc)

        # Test
        code = self.handler.handle_permission(e)

        # Verify
        self.assertEqual(code, exceptions.CODE_PERMISSIONS_EXCEPTION)
        self.assertEqual(self.handler._handle_unknown.call_count, 1)
