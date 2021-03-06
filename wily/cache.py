"""
A module for working with the .wily/ cache directory

This API is not intended to be public and should not be consumed directly.
The API in this module is for archivers and commands to work with the local cache

TODO: Version .wily/ cache folders?
TODO: Validate that if wily config specifies alternative directory
  that all commands work
"""

import shutil
import pathlib
import json
from wily.archivers import ALL_ARCHIVERS
from wily import logger


def exists(config):
    """
    Check whether the .wily/ directory exists

    :return: Whether the .wily directory exists
    :rtype: ``boolean``
    """
    return (
        pathlib.Path(config.cache_path).exists()
        and pathlib.Path(config.cache_path).is_dir()
    )


def create(config):
    """
    Create a wily cache
    
    :return: The path to the cache
    :rtype: ``str``
    """
    if exists(config):
        logger.debug("Wily cache exists, skipping")
        return
    logger.debug(f"Creating wily cache {config.cache_path}")
    pathlib.Path(config.cache_path).mkdir()
    return config.cache_path


def clean(config):
    """
    Delete a wily cache
    """
    if not exists(config):
        logger.debug("Wily cache does not exist, skipping")
        return
    shutil.rmtree(config.cache_path)
    logger.debug("Deleted wily cache")


def store(config, archiver, revision, stats):
    """
    Store a revision record within an archiver folder
    
    :param archiver: The name of the archiver type (e.g. 'git')
    :type  archiver: ``str``
    
    :param revision: The revision ID
    :type  revision: ``str``
    
    :param stats: The collected data
    :type  stats: ``dict``
    
    :return: The path to the created file
    :rtype: ``str``
    """
    root = pathlib.Path(config.cache_path) / archiver.name
    if not root.exists():
        logger.debug("Creating wily cache")
        root.mkdir()

    logger.debug(f"Creating {revision.key} output")
    filename = root / (revision.key + ".json")
    with open(filename, "w") as out:
        out.write(json.dumps(stats, indent=2))
    return filename


def store_index(config, archiver, index):
    """
    Store an archiver's index record for faster search
    
    :param archiver: The name of the archiver type (e.g. 'git')
    :type  archiver: ``str``
    
    :param index: The archiver index record
    :type  index: ``dict``
    """
    root = pathlib.Path(config.cache_path) / archiver.name

    if not root.exists():
        root.mkdir()
        logger.debug("Created archiver directory")

    with (root / "index.json").open("w") as out:
        out.write(json.dumps(index, indent=2))
    logger.debug(f"Creating index output")


def list_archivers(config):
    """
    List the names of archivers with data
 
    :return: A list of archiver names
    :rtype: ``list`` of ``str``
    """
    root = pathlib.Path(config.cache_path)
    result = []
    for archiver in ALL_ARCHIVERS:
        if (root / archiver.name).exists():
            result.append(archiver.name)
    return result


def get_history(config, archiver):
    """
    Get a list of revisions for a given archiver
    
    :param archiver: The name of the archiver type (e.g. 'git')
    :type  archiver: ``str``

    :return: A ``list`` of ``dict``
    """
    root = pathlib.Path(config.cache_path) / archiver
    revisions = []
    for i in root.iterdir():
        if i.name.endswith(".json"):
            with i.open("r") as rev_f:
                revision_data = json.load(rev_f)
                revisions.append(revision_data)
    return revisions


def get_index(config, archiver):
    """
    Get the contents of the archiver index file
    
    :param archiver: The name of the archiver type (e.g. 'git')
    :type  archiver: ``str``
    
    :return: The index data
    :rtype: ``dict``
    """
    root = pathlib.Path(config.cache_path) / archiver
    with (root / "index.json").open("r") as index_f:
        index = json.load(index_f)
    return index


def get(config, archiver, revision):
    """
    Get the data for a given revision
    
    :param archiver: The name of the archiver type (e.g. 'git')
    :type  archiver: ``str``
    
    :param revision: The revision ID
    :type  revision: ``str``
    
    :return: The data record for that revision
    :rtype: ``dict``
    """
    root = pathlib.Path(config.cache_path) / archiver
    # TODO : string escaping!!!
    with (root / f"{revision}.json").open("r") as rev_f:
        index = json.load(rev_f)
    return index
