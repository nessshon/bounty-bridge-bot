import os

from libcloud.storage.base import StorageDriver
from libcloud.storage.providers import get_driver
from libcloud.storage.types import ContainerDoesNotExistError, Provider
from sqlalchemy_file.storage import StorageManager

from ..config import UPLOADS_DIR


def get_or_create_container(driver: StorageDriver, container_name: str):
    try:
        return driver.get_container(container_name)
    except ContainerDoesNotExistError:
        """This will just create a new directory inside the base directory for local storage."""
        return driver.create_container(container_name)


def configure_storage():
    os.makedirs(UPLOADS_DIR, 0o777, exist_ok=True)
    cls = get_driver(Provider.LOCAL)
    driver = cls(UPLOADS_DIR)
    StorageManager.add_storage("image", get_or_create_container(driver, "img"))
    StorageManager.add_storage("json", get_or_create_container(driver, "json"))
