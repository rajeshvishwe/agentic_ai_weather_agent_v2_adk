"""
Global pytest configuration for the Weather Intelligence Agent test suite.

This module configures the native operating-system certificate trust store
before application modules create HTTPS clients.

The project uses truststore so that integration tests accessing external HTTPS
services, including Open-Meteo, use the macOS system certificate store.
"""

import truststore


truststore.inject_into_ssl()