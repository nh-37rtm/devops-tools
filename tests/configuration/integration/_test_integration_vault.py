
import os

import sys

import logging

import hvac

from configuration.env_config_loader import EnvConfigLoader
from configuration.vault_config_loader import VaultConfigLoader
from model.model_vault_conf import VaultConf

from tests.configuration.sets.test_model import vaultAuthModel, TestSplunkModel, TestvaultAuthModel


logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s %(message)s')
os.environ['REQUESTS_CA_BUNDLE'] = "/etc/ssl/certs/"


def test_environement_variable_set() -> None:

    assert 'DEVOPS_CORE_TEST_vault_ROLE_ID' in os.environ, \
        'DEVOPS_CORE_TEST_vault_ROLE_ID environment variable should be set'
    assert 'DEVOPS_CORE_TEST_vault_SECRET_ID' in os.environ, \
        'DEVOPS_CORE_TEST_vault_SECRET_ID environment variable should be set'
    assert 'DEVOPS_CORE_TEST_vault_URL' in os.environ, \
        'DEVOPS_CORE_TEST_vault_URL environment variable should be set'

def test_conection_vault() -> None:
    """The Test simply try to connect to vault using the hprod.vault.mycompany.fr url"""
    # https://confluence.mycompany.fr/display/DIAMM/6.3+-+vault+sur+DataOps
    # Authentication
    client = hvac.Client(
        url=os.environ['DEVOPS_CORE_TEST_vault_URL']
    )

    client.auth.approle.login(
        role_id=os.environ['DEVOPS_CORE_TEST_vault_ROLE_ID'],
        secret_id=os.environ['DEVOPS_CORE_TEST_vault_SECRET_ID'],
    )

    print(client.is_authenticated())

    # Reading a secret
    read_response = client.secrets.kv.read_secret_version(
        raise_on_deleted_version = True, # avoid deprecation warning
        path='qualif/app/devops_appli_jenkins', mount_point= "secret/devops")
    
    assert(read_response is not None)


def test_env_to_vault_auth() -> None:
    """The test load from prefixed DEVOPS_CORE_TEST_vault_ environment variables in a dict with the format : { role_id: xxx, secret_id: xxx, url: xxx }
       all DEVOPS_CORE_TEST_vault_ROLE_ID, DEVOPS_CORE_TEST_vault_URL and DEVOPS_CORE_TEST_vault_SECRET_ID  environment variables should be defined
    """

    loader = EnvConfigLoader(vaultAuthModel, os.environ, 'DEVOPS_CORE_TEST_vault_')
    kys_auth = loader.load_config()

    client = hvac.Client(url= kys_auth.url)

    client.auth.approle.login( role_id= kys_auth.role_id, secret_id= kys_auth.secret_id )
    print(client.is_authenticated())

    assert(kys_auth is not None)


def test_env_to_vault_auth_2() -> None:

    # secrets_path = ['qualif/app/devops_appli_jenkins', 'qualif/app/splunk_zst/enclave_zhb' ]
    secrets_path = ['qualif/app/devops_appli_jenkins' ]

    loader = EnvConfigLoader(vaultAuthModel, os.environ, 'DEVOPS_CORE_TEST_vault_')
    kys_auth = loader.load_config()

    vault_conf = VaultConf(
            mount_point='secret/devops',
            **kys_auth.dict()) # this line should pass the 3 arguments loaded in environment role_id, secret_id and url

    # conf_loader = VaultConfigLoader(TestSplunkModel, vault_conf, secrets_path)
    # splunk_secrets = conf_loader.load_config()

    loader = VaultConfigLoader(dict, vault_conf, secrets_path)
    secrets = loader.load_config()

    assert secrets is not None

def test_env_to_vault_auth_3() -> None:

    # secrets_path = ['qualif/app/devops_appli_jenkins', 'qualif/app/splunk_zst/enclave_zhb' ]
    secrets_path = ['qualif/app/devops_appli_jenkins' ]

    vault_conf = VaultConf(
            mount_point='secret/devops',
            role_id = os.environ['DEVOPS_CORE_TEST_vault_ROLE_ID'],
            secret_id = os.environ['DEVOPS_CORE_TEST_vault_SECRET_ID'],
            url= os.environ['DEVOPS_CORE_TEST_vault_URL'])

    # conf_loader = VaultConfigLoader(TestSplunkModel, vault_conf, secrets_path)
    # splunk_secrets = conf_loader.load_config()

    loader = VaultConfigLoader(dict, vault_conf, secrets_path)
    secrets = loader.load_config()

    assert secrets is not None
    