import base64
import json
import logging
import os
import sys
import time

# Instances of this class are used to define and obtain all configuration
# values in this solution.  These are typically obtained at runtime via
# environment variables.
#
# This class also implements encryption and decryption using a symmetric-key
# configured with environment variable ENCRYPTION_SYMMETRIC_KEY.
#
# Chris Joakim, Microsoft


class ConfigService:

    @classmethod
    def envvar(cls, name: str, default: str = "") -> str:
        """
        Return the value of the given environment variable name,
        or the given default value."""
        if name in os.environ:
            return os.environ[name].strip()
        return default

    @classmethod
    def int_envvar(cls, name: str, default: int = -1) -> int:
        """
        Return the int value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = os.environ[name].strip()
            try:
                return int(value)
            except Exception as e:
                logging.error(
                    "int_envvar error for name: {} -> {}; returning default.".format(
                        name, value
                    )
                )
                return default
        return default

    @classmethod
    def float_envvar(cls, name: str, default: float = -1.0) -> float:
        """
        Return the float value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = os.environ[name].strip()
            try:
                return float(value)
            except Exception as e:
                logging.error(
                    "float_envvar error for name: {} -> {}; returning default.".format(
                        name, value
                    )
                )
                return default
        return default

    @classmethod
    def boolean_envvar(cls, name: str, default: bool) -> bool:
        """
        Return the boolean value of the given environment variable name,
        or the given default value.
        """
        if name in os.environ:
            value = str(os.environ[name]).strip().lower()
            if value == "true":
                return True
            elif value == "t":
                return True
            elif value == "yes":
                return True
            elif value == "y":
                return True
            else:
                return False
        return default

    @classmethod
    def boolean_arg(cls, flag: str) -> bool:
        """Return a boolean indicating if the given arg is in the command-line."""
        for arg in sys.argv:
            if arg == flag:
                return True
        return False

    @classmethod
    def defined_environment_variables(cls) -> dict:
        """
        Return a dict with the defined environment variable names and descriptions
        """
        d = dict()
        d["COSMOSDB_NOSQL_URI"] = "The URI of your Cosmos DB NoSQL account"
        d["COSMOSDB_NOSQL_AUTH_MECHANISM"] = (
            "The Cosmos DB NoSQL authentication mechanism; key or rbac"
        )
        d["COSMOSDB_NOSQL_KEY"] = "The key of your Cosmos DB NoSQL account"
        d["COSMOSDB_NOSQL_DB"] = "Your Cosmos DB NoSQL database name"
        d["COSMOSDB_NOSQL_CONTAINER"] = "Your Cosmos DB NoSQL container name"
        d["LOG_LEVEL"] = (
            "a python logging standard-lib level name: notset, debug, info, warning, error, or critical"
        )
        return d


    @classmethod
    def log_defined_env_vars(cls):
        """Log the defined  environment variables as JSON"""
        keys = sorted(cls.defined_environment_variables().keys())
        selected = dict()
        for key in keys:
            value = cls.envvar(key)
            selected[key] = value
        logging.info(
            "log_defined_env_vars: {}".format(
                json.dumps(selected, sort_keys=True, indent=2)
            )
        )

    @classmethod
    def print_defined_env_vars(cls):
        """print() the defined environment variables as JSON"""
        keys = sorted(cls.defined_environment_variables().keys())
        selected = dict()
        for key in keys:
            value = cls.envvar(key)
            selected[key] = value
        print(
            "print_defined_env_vars: {}".format(
                json.dumps(selected, sort_keys=True, indent=2)
            )
        )

    @classmethod
    def cosmosdb_nosql_uri(cls) -> str:
        return cls.envvar("COSMOSDB_NOSQL_URI", None)


    @classmethod
    def cosmosdb_nosql_auth_mechanism(cls) -> str:
        return cls.envvar("COSMOSDB_NOSQL_AUTH_MECHANISM", "key").lower()

    @classmethod
    def cosmosdb_nosql_key(cls) -> str:
        return cls.envvar("COSMOSDB_NOSQL_KEY", None)

    @classmethod
    def cosmosdb_nosql_database(cls) -> str:
        return cls.envvar("COSMOSDB_NOSQL_DB", None)

    @classmethod
    def cosmosdb_nosql_container(cls) -> str:
        return cls.envvar("COSMOSDB_NOSQL_CONTAINER", None)



    @classmethod
    def epoch(cls) -> float:
        """Return the current epoch time, as time.time()"""
        return time.time()

    @classmethod
    def verbose(cls, override_flags: list = None) -> bool:
        """Return a boolean indicating if --verbose or -v is in the command-line."""
        flags = ["--verbose", "-v"] if override_flags is None else override_flags
        # true_value if condition else false_value
        for arg in sys.argv:
            for flag in flags:
                if arg == flag:
                    return True
        return False
