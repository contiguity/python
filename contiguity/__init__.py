from .main import Contiguity, Verify, EmailAnalytics, Quota, OTP, Template, Send

def login(token, debug=False):
    return Contiguity(token, debug)

__all__ = ['Contiguity', 'Send', 'Verify', 'EmailAnalytics', 'Quota', 'OTP', 'Template']
