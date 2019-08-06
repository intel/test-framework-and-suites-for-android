"""
Copyright (C) 2018 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.


SPDX-License-Identifier: Apache-2.0
"""

import __builtin__

import Queue
import hashlib
import shutil
import threading
import traceback
import json
import os

from os import path
from functools import wraps

SysErrors = __builtin__.OSError, __builtin__.IOError,
try:
    # noinspection PyUnresolvedReferences
    SysErrors += __builtin__.WindowsError,
except (ImportError, AttributeError):
    pass

# Maximum over buffer before resetting Cache
# on un-linking successive exceptions
# ie. 1024 ** 2 * 256 -> 256MB
# Default: 0
AllowedOverBuffer = 0
Debug = 0


def synchronous(lock=threading.RLock()):
    """
    Decorator allowing calls to methods of a class to be synchronized using a global lock.

    :param lock: the lock (Any objects handling acquire and release methods)
    :type lock: threading.Lock | threading.RLock

    .. note :: For thread safety this would normally be a Re-entrant Lock. (:class:`threading.RLock`)
        if instance-based is used, 'lock_name' must refer to some kind of lock with methods acquire and release.

    """
    def synced(func):
        @wraps(func)
        def synchronizer(self, *args, **kwargs):
            with lock:
                return func(self, *args, **kwargs)
        return synchronizer
    return synced


def compute_file_hash(file_path, alg='md5'):
    """
    Computes the file's Hash based on specified algorithms and its given path

    Supported algorithms::

        * md5

    :param file_path: the file path from which to get hash
    :type file_path: str

    :param alg: used algorithm (MD5, SHA{1, 2, ...}, CRC, ...)
    :type alg: str

    :return: the file's hash according desired algorithm
    :rtype: str

    """
    if alg == 'md5':
        md5_obj = hashlib.md5()
        block_size = 65536
        # read chunk by chunk for big file
        with open(file_path, 'r+b') as f:
            for block in iter(lambda: f.read(block_size), ""):
                md5_obj.update(block)
        local_md5 = md5_obj.hexdigest()
        file_hash = local_md5

    else:
        raise NotImplementedError("ALGORITHM {0} NOT IMPLEMENTED!".format(alg))
    return file_hash


class IPriorityQueue(Queue.PriorityQueue):

    """
    Iterable :mod:`Queue.PriorityQueue`

    """

    # Defines a sentinel raising StopIteration,
    # preventing further Queue processing
    _sentinel = object()

    def __iter__(self):
        """
        Implements iteration over :mod:`Queue.PriorityQueue` capability

        :return: the queue as an Iterator
        :rtype: Iterator

        """
        return iter(self.get, self._sentinel)

    def close(self):
        """
        Queueing the sentinel,
        then ending further Queue processing by raising StopIteration

        """
        self.put(self._sentinel)


class CachedEntry(object):

    """
    A cache entry, representing the Cached Resource itself.

    .. note:: Any access to its data (instance's attributes) is **thread-safe**.

    Any attribute might be created on the fly (not defined in __init__)::
        :language: python

        entry = CacheEntry('myKey', '/uri/to/it', any_needed_data_as_attribute='toto')
        # Add ``any_needed_data_as_attribute`` as entry's attribute
        print(entry.any_needed_data_as_attribute)  # >>> 'toto'
        # or on the fly
        entry.my_other_needed_data_attribute = 'my_important_data'

    .. note:: inner methods, which control instance attribute's access are synchronized:

        * :meth:`__getattr__`
        * :meth:`__setattr__`
        * :meth:`__delattr__`

    """

    @synchronous()
    def __str__(self):
        """
        The Object's String, Unicode or Representation

        :return: instance's value
        """
        if Debug:
            return json.dumps(self.__dict__, indent=3)
        return str(self.value)

    __unicode__ = __repr__ = __str__

    def __init__(self, key, value, **options):
        """
        Initialize a CachedEntry instance.
        Any attribute's (r/w) access is thread safe

        :param key: CachedEntry's unique key
        :type key: str

        :param value: CachedEntry's associated value
        :type value: object

        :param options: any extra attributes name/value pair
        :type options: dict

        """
        # The 2 mandatory attributes
        self.key, self.value = key, value
        # Map as instance attribute any passed kwargs dict
        if options:
            [setattr(self, a, v) for a, v in options.iteritems()]

    @synchronous()
    def __cmp__(self, other):
        """
        Defines the IPriorityQueue<CacheEntry>() priority

        :param other: self
        :type other: CachedEntry

        :return: Instances Comparison
        :rtype: int

        """
        return 1

    @synchronous()
    def __getattr__(self, attr):
        """
        We override this method just to add Thread-Safety behavior
        on any instance's attribute read-access.

        :param attr: attribute's name
        :type attr: str

        :return: The matching attribute
        :rtype: object

        """
        if attr in self.__dict__:
            return self.__dict__[attr]
        raise AttributeError(attr)

    @synchronous()
    def __setattr__(self, attr, value):
        """
        We override this method just to add Thread-Safety behavior
        on any instance's attribute write-access.

        :param attr:
        :type attr: str

        :param value:
        :type value: object

        """
        return object.__setattr__(self, attr, value)

    @synchronous()
    def __delattr__(self, attr):
        return object.__delattr__(self, attr)

    @synchronous()
    def update(self, **values):
        """
        Implements this method in SubClass if you like to add some Updating logic

        :param values: extra values passed as kwargs,
                       if some updated value are already computed

        """
        raise NotImplementedError('update() not implemented!')


class CachedArtifact(CachedEntry):

    """
    Represent a cached Artifactory's artifact.

    """

    @property
    def timestamp(self):
        """
        Gets the Artifact's timestamp based on its value

        :return: Artifact's timestamp
        :rtype: int

        """
        if not self.__timestamp:
            self.__timestamp = int(os.stat(str(self.value)).st_mtime)
        return self.__timestamp

    @property
    def size(self):
        """
        Gets the Artifact's size (in bytes) based on its value

        :return: Artifact's size
        :rtype: int

        """
        if not self.__size:
            self.__size = os.stat(str(self.value)).st_size
        return self.__size

    @property
    def hash(self):
        """
        Gets the Artifact's hash based on its value

        :return: Artifact's hash
        :rtype: str

        """
        if not self.__hash:
            self.__hash = compute_file_hash(str(self.value))
        return self.__hash

    @synchronous()
    def update(self, **values):
        """
        Override

        Implement Timestamp, Size and Hash update.

        :param values: Must map either ``timestamp``, ``size`` or ``hash`` attribute
        :type values: dict

        .. note:: ``values`` mapping example

            file_path = '/some/path/'
            t = os.stat(file_path).st_mtime
            size = os.stat(file_path).st_size

            self.update(timestamp=t, size=size hash=already_computed_hash)

            # Or,

            self.update(size=size), ...

        """
        self.__timestamp = values.get('timestamp', int(os.stat(str(self.value)).st_mtime))
        self.__size = values.get('size', os.stat(str(self.value)).st_size)
        self.__hash = values.get('hash', values.get('md5', compute_file_hash(str(self.value))))

    def __init__(self, key, value, **options):
        """
        Initialize a CachedEntry instance.
        Any attribute's (r/w) access is thread safe

        :param key: CachedEntry's unique key
        :type key: str

        :param value: CachedEntry's associated value
        :type value: object

        :param options: any extra attributes name/value pair
        :type options: dict

        """
        CachedEntry.__init__(self, key, value, **options)

        self.__timestamp = None
        self.__size = None
        self.__hash = None


class CacheManager(object):

    """
    Handles FileSystem Caching with circular buffering pattern,
    thus handling a maximum size in bytes.

    Some Convenient ways to access the CacheManager instance as a dict have been implemented::
        :language: python
        :linenos:

        cs = CacheManager(caching_dir='...')
        # set item
        cs['/fastboot/fastboot-img.bin'] = artifact
        # get item
        artifact = cs['/fastboot/fastboot-img.bin']
        # contains item
        if '/fastboot/fastboot-img.bin' in cs:
        # all iter<xxx>() methods
        for artifact_name, artifact_obj in cs.iteritems():
            ...

        # ...

    """

    class Error(Exception):

        """
        Inner Base Exception Class

        """

    # Defines the CachedEntry factory
    Entry = None

    @property
    @synchronous()
    def logger(self):
        """
        Accessor for private __logger attribute

        :return: The Logger
        :rtype: logging.Logger | StdLogger

        """
        return self.__logger

    @property
    def caching_dir(self):
        """
        Accessor for private __caching_dir attribute

        :return: The Caching directory path
        :rtype: str

        """
        return self.__caching_dir

    @property
    def max_size_in_bytes(self):
        """
        Accessor for private __max_size_in_bytes attribute

        :return: The Maximum size in bytes allowed for the Cache
        :rtype: int

        """
        return self.__max_size_in_bytes

    @property
    @synchronous()
    def is_limited(self):
        """
        Tells if we've got a maximum Cache size
        If the value is -1, the Cache is unlimited

        :return: Whether or not we have Cache size limitation
        :rtype: bool

        """
        return self.max_size_in_bytes != -1

    @property
    @synchronous()
    def current_size(self):
        """
        Centralized thread-safe property for the private __current_cache_size attribute

        :return: The Current size in bytes of the Cache
        :rtype: int

        """
        return self.__current_cache_size

    @property
    @synchronous()
    def _cache(self):
        """
        Centralized thread-safe property for the private __cache attribute

        :return: The inner Cache structure
        :rtype: dict

        """
        return self.__cache

    @property
    @synchronous()
    def _queue(self):
        """
        Centralized thread-safe property for the private __queue attribute

        :return: The inner Priority Queue
        :rtype: IPriorityQueue

        """
        return self.__queue

    @synchronous()
    def reset(self):
        """
        Clear all Cache, in memory and physically

        """
        # Clearing previous Cache
        self.__cache.clear()
        self.__queue.close()

        self.__cache = {}
        self.__queue = IPriorityQueue()
        self.__current_cache_size = 0

        try:
            shutil.rmtree(self.caching_dir)
        except (shutil.Error, shutil.WindowsError, SysErrors):
            self.logger.error(traceback.format_exc())

    @staticmethod
    def get_key(key):
        """
        Override this method if you need to handle process of passed key

        :param key:
        :type key: str

        :return: the processed key if implemented
        :rtype: str

        """
        return key

    @synchronous()
    def get(self, key, default=None):
        """
        Gets the matching CachedEntry based on given key or None

        :param key: cached entry's key
        :type key: str

        :param default: The default value to be returned if key not found
        :type default: object

        :return: the matching cached entry or None
        :rtype: CachedEntry or None

        """
        return self._cache.get(self.get_key(key), default)

    @synchronous()
    def add(self, key, value):
        """
        Add an Entry to the Cache if not already there

        * Create the Entry from given key/value pair
        * Append created Entry to inner IPriorityQueue
        * Update Cache current size based on created Entry
        * Flush Entries from cache (if needed based on MAX_CACHE_SIZE)
        * Set created Entry into Cache
        * Returns created Entry instance

        :param key: entry's key
        :type key: str

        :param value: entry's value
        :type value: object

        :return: Created Entry
        :rtype: CachedEntry


        .. todo:: Merge Cache Dict & IPriorityQueue into one Class which must keep:

                    * Uniqueness of each item
                    * Thread-safety
                    * Priority flushing, based on timestamp or whatever ``priority`` attribute

        """
        key = self.get_key(key)

        if key not in self._cache:
            entry = self.Entry(key, value)
            size = entry.size

            # If the Size of a single artifact exceeds the MAXIMUM CACHE SIZE, we raise
            if self.is_limited and size > self.max_size_in_bytes:
                raise self.Error('The artifact\'s size is {0} bytes exceeds the MAXIMUM CACHE SIZE, which is {1} bytes!'
                                 ' Please adjust, consequently your '
                                 'Bench Configuration with an appropriated Value!'.format(size, self.max_size_in_bytes))

            # Considering Current size plus the item to be added
            if self.is_limited and self.current_size + size > self.max_size_in_bytes:
                self._flush(size)

            # CacheManager is fine to accept the new element
            # Adding it to the Queue and Cache dict.
            self._queue.put((entry.timestamp, entry))
            self._cache[key] = entry

            # Updating the current size with the new added item
            self._update_current_size(size)

        return self._cache[key]

    def fill(self, entries):
        """
        Fills the Cache from given entries list

        :param entries: a list of entries
        :type entries: tuple | list

        .. code-block:: python
            :linenos:

            entries = ['/entry/one', '/entry/two', ...]
            self.fill(entries)

        """
        for entry in entries:
            self.add(entry, path.join(self.__caching_dir, entry))

    def iteritems(self):
        """
        Implementation of :mod:`dict.iteritems` facility

        :return: Inner Cache dict.iteritems() method
        :rtype: Iterable generator

        """
        return self._cache.iteritems()

    def iterkeys(self):
        """
        Implementation of :mod:`dict.iterkeys` facility

        :return: Inner Cache dict.iterkeys() method
        :rtype: Iterable generator

        """
        return self._cache.iterkeys()

    def itervalues(self):
        """
        Implementation of :mod:`dict.itervalues` facility

        :return: Inner Cache dict.itervalues() method
        :rtype: Iterable generator

        """
        return self._cache.itervalues()

    def __len__(self):
        """
        Implements the facility to use `len` on the CacheManager

        :return: Cache artifacts count
        :rtype: int

        """
        return self._cache.__len__()

    count = length = __len__

    def __iter__(self):
        """
        Implements `in` operator behavior

        :return: An iterable of Cache artifacts
        :rtype: iterable

        """
        return self._cache.__iter__()

    def __contains__(self, key):
        """
        Overrides `[]` operator behavior

        :param key: the CachedEntry's key
        :type key: str

        :return: Whether or not the given key is contained in Cache
        :rtype: bool

        """
        return self.get_key(key) in self._cache

    def __getitem__(self, key):
        """
        Overrides `[]` operator behavior

        :param key: the CachedEntry's key
        :type key: str

        :return: CachedEntry matching given key
        :rtype: CachedEntry

        :raise: AttributeError

        """
        return self._cache[self.get_key(key)]

    def __setitem__(self, key, value):
        """
        Overrides `[]` operator behavior

        :param key: the CachedEntry's key
        :type key: str

        :param value: the CachedEntry's value
        :type value: object

        """
        self.add(key, value)

    def __delitem__(self, key):
        """
        Overrides `[]` operator behavior

        :param key: the CachedEntry's key
        :type key: str

        """
        del self._cache[self.get_key(key)]

    # Initializing

    def __init__(self, caching_dir, logger, max_size_in_bytes=1024 ** 3):
        """
        Initialises a Caching instance, with a maximum size in bytes,
        which has for default value 1GB.

        :param caching_dir: Path to the Caching directory
        :type caching_dir: str

        :param max_size_in_bytes: The maximum Cached size in bytes
        :type max_size_in_bytes: int

        """
        if max_size_in_bytes < 0:
            raise self.Error('Invalid parameter! The `MAX_CACHE_SIZE` must be a POSITIVE value!')

        self.__logger = logger

        caching_dir = path.normpath(path.abspath(path.expanduser(caching_dir)))
        # We ensure cache's directory creation!
        if not path.isdir(caching_dir):
            try:
                os.makedirs(caching_dir)
            except SysErrors:
                self.logger.error(traceback.format_exc())

        self.__caching_dir = caching_dir
        self.__max_size_in_bytes = max_size_in_bytes if max_size_in_bytes > 0 else -1

        # Initializing
        self.__cache = {}
        self.__queue = IPriorityQueue()
        self.__current_cache_size = 0

        # Used to load only Cache if the needed
        self._loaded = 0

    @synchronous()
    def _update_current_size(self, size_in_bytes, inc=1):
        """
        Update Cache's current size (in bytes) by
        either incrementing or decrementing given entry computed size.

        :param inc: increment or decrement
        :type size_in_bytes: int

        :param size_in_bytes: Entry size in bytes
        :type inc: int | bool

        """
        if inc:
            self.__current_cache_size += int(size_in_bytes)
        else:
            self.__current_cache_size -= int(size_in_bytes)

    @synchronous()
    def _flush(self, *more):
        """
        Override this method in order to implement better flushing logic (ie. MAX SIZE IN BYTES, ...).

        **DEFAULT BEHAVIOR**: all content is cleared

        """
        self.reset()

    @synchronous()
    def _load(self):
        """
        Loads existing Cache based on ``caching_dir`` property

        * Walks through the caching directory and add all found artifacts.

        """
        def build_valid_artifact_name(root, sub=None):
            """
            Builds a well-formed Artifact's name

            Like so::

                for given root path: `~/.acs/cache/Videos/mp4/artifact1.mp4`
                and a given length to substitute corresponding to Caching root directory path: `~/.acs/cache`

                the Artifactory's name output should be: **/Videos/mp4/artifact1.mp4**

            :param root: the root path
            :type root: str

            :param sub: the length to substitute from root
            :type sub: int

            :return: a well-formed artifact's name
            :rtype: str

            """
            prefix = root[sub:] if sub else root
            # here the comprehension list is used to ensure there's no empty element (if x)
            # As we don't want to get for instance a path build like so `//my/artifact/key`
            parts = [x for x in prefix.replace('\\', '/').split('/') if x]
            return '/'.join(parts)

        for root, dirs, files in os.walk(self.caching_dir):
            for art in files:
                a_name = build_valid_artifact_name(root, len(self.caching_dir))
                self.add('{0}/{1}'.format(a_name, art), path.normpath('{0}/{1}'.format(root, art)))


class ArtifactoryCacheManager(CacheManager):

    """
    Artifactory Cache System

    """

    # CachedEntry SubClass handling some more data
    Entry = CachedArtifact

    @staticmethod
    def get_key(key):
        """
        Here we want to ensure uniqueness of the key

        :param key:
        :type key: str

        :return: the processed key if implemented
        :rtype: str

        """
        if '\\' in key:
            key = key.replace('\\', '/')
        cleaned_parts = [part for part in key.split('/') if part]
        return '/'.join(cleaned_parts)

    @synchronous()
    def add(self, key, value=None):
        """
        Add an Entry to the Cache if not already there

        * Create the Entry from given key/value pair
        * Append created Entry to inner IPriorityQueue
        * Update Cache current size based on created Entry
        * Flush Entries from cache (if needed based on MAX_CACHE_SIZE)
        * Set created Entry into Cache
        * Returns created Entry instance

        :param key: entry's key
        :type key: str

        :param value: entry's value
        :type value: object

        :return: Created Entry
        :rtype: CachedEntry

        """
        if not value:
            lazy_value = path.normpath('{0}{1}{2}'.format(self.caching_dir, os.sep, key))
            if path.isfile(lazy_value):
                value = lazy_value
            else:
                raise ArtifactoryCacheManager.Error('You must pass a valid Artifact value! ({0})'.format(value))
        return CacheManager.add(self, key, value)

    @synchronous()
    def get(self, key, default=None):
        """
        Gets the matching CachedArtifact based on given key or None

        :param key: cached entry's key
        :type key: str

        :param default: The default value to be returned if key not found
        :type default: object

        :return: the matching cached entry or None
        :rtype: CachedArtifact or None

        """
        # We load the Cache, only if we need it,
        if not self._loaded:
            self._load()
            self._loaded = 1

        entry = default
        key = self.get_key(key)
        try:
            entry = self._cache[key]
        except KeyError:
            # We adopt lazy caching, if the key is not in Cache,
            # then we check that the lazy value is or not an existing artifact
            # if so, we add the Artifact to the Cache and return it
            lazy_value = path.normpath(path.join(self.caching_dir, key))
            if path.isfile(lazy_value):
                entry = self.add(key, lazy_value)
        return entry

    @synchronous()
    def _flush(self, *more):
        """
        Compute Cache entry/ies which should be flushed from Cache,
        according MAXIMUM SIZE of Cache defined in ``BenchConfig``.

        * Oldest entry/ies are removed first to free up enough space for the new entry
        * Update Cache current size

        :param more: More size to be considered
        :type more: tuple | list of int convertible value

        """
        final_size = self.current_size
        if more:
            for extra_size in more:
                try:
                    final_size += int(extra_size)
                except ValueError:
                    self.logger.error('Only `int` are accepted as *more extra-args')

        while final_size > self.max_size_in_bytes:
            priority, oldest = self._queue.get()
            # self.logger.warning('Artifact(priority={1}): {0}'.format(oldest, priority))
            key, value, size = oldest.key, oldest.value, oldest.size
            if path.isfile(value):
                try:
                    os.unlink(value)
                    self._update_current_size(size, inc=0)
                    final_size -= size
                    del self._cache[key]
                    del oldest
                except (SysErrors, KeyError) as exc:
                    self.logger.error(traceback.format_exc())
                    # if we go up cache maximum size and cache AllowedOverBuffer we reset all cache
                    if isinstance(exc, SysErrors) and self.current_size > (self.max_size_in_bytes + AllowedOverBuffer):
                        self.reset()
