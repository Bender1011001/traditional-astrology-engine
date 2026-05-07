import os
from unittest.mock import MagicMock, mock_open, patch


from src.engine.email_service import render_template, send_email


@patch("requests.post")
@patch.dict(
    os.environ,
    {"SENDGRID_API_KEY": "test_key", "SENDER_EMAIL": "test@example.com"},
    clear=True,
)
def test_send_email_sendgrid_success(mock_post):
    """Test send_email using mocked SendGrid API."""
    mock_post.return_value.status_code = 202

    result = send_email("user@example.com", "Test Subject", "<h1>Hello</h1>")

    assert result is True
    mock_post.assert_called_once()

    # Check payload
    call_args = mock_post.call_args
    assert call_args[1]["headers"]["Authorization"] == "Bearer test_key"
    assert (
        call_args[1]["json"]["personalizations"][0]["to"][0]["email"]
        == "user@example.com"
    )
    assert "unsubscribe" in call_args[1]["json"]["content"][0]["value"].lower()


@patch("requests.post")
@patch.dict(os.environ, {"SENDGRID_API_KEY": "test_key"}, clear=True)
def test_send_email_sendgrid_failure(mock_post):
    """Test send_email returning False on SendGrid failure."""
    mock_post.return_value.status_code = 401
    mock_post.return_value.text = "Unauthorized"

    result = send_email("user@example.com", "Test Subject", "<h1>Hello</h1>")

    assert result is False


@patch("src.engine.email_service.smtplib.SMTP")
@patch.dict(
    os.environ,
    {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "user",
        "SMTP_PASS": "pass",
    },
    clear=True,
)
def test_send_email_smtp_success(mock_smtp):
    """Test send_email using mocked SMTP."""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    result = send_email(
        "user@example.com", "Test Subject", "<h1>Hello</h1>", b"fake_pdf_data"
    )

    assert result is True
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user", "pass")
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


@patch.dict(os.environ, {}, clear=True)
def test_send_email_no_provider():
    """Test send_email without configured providers."""
    result = send_email("user@example.com", "Subject", "Content")
    assert result is False


def test_render_template():
    """Test rendering an email template with basic replacing."""
    template_content = "Hello {{ name }}, your total is {{total}}."

    with patch("builtins.open", mock_open(read_data=template_content)):
        with patch("src.engine.email_service.os.path.join") as mock_join:
            mock_join.return_value = "dummy.html"
            result = render_template("test.html", {"name": "Alice", "total": "5.00"})

            assert "Hello Alice" in result
            assert "your total is 5.00" in result
