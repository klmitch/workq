# Copyright 2014 Kevin L. Mitchell
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

import six


class WorkQueue(six.Iterator):
    """
    An iterator that assists in turning a recursive algorithm into an
    iterative algorithm.  The ``WorkQueue`` is initialized with a
    sequence of items to work on, then iterates over those items.
    Work items may be added to the queue at any time, using the
    ``add()`` and ``extend()`` methods.  By default, only work items
    that have not been encountered before are added.  The length of
    the queue is the total number of items that have been added to it.
    """

    def __init__(self, items, unique=True, key=None):
        """
        Initialize a ``WorkQueue`` object.

        :param items: A sequence of items to add to the queue
                      initially.  The items may be of any type;
                      however, if they are not hashable, then either
                      ``unique`` must be ``False`` or a ``key``
                      callable must be provided.
        :param unique: If ``True``--the default--each item added to
                       the queue must be unique; any duplicate items
                       that are added to the queue will be ignored.
                       This adds the items (or their keys; see the
                       ``key`` parameter) to a set, so if memory is a
                       worry, use ``False``.
        :param key: An optional callable taking one argument.  The
                    argument will be a work item, and the result
                    should be a hashable value unique to that item.
                    This key will be added to a set, so if memory is a
                    worry, use a ``False`` value for ``unique`` or
                    select a key representation with a small memory
                    footprint.
        """

        self._work = collections.deque()
        self._seen = set()
        self._count = 0
        self._unique = unique
        self._key = key

        # Now add the items
        self.extend(items)

    def __len__(self):
        """
        Compute the number of work items still pending on the queue.

        :returns: The number of items still pending on the queue.
        """

        return len(self._work)

    def __iter__(self):
        """
        Iterate over the items in the work queue.

        :returns: The ``WorkQueue`` object.
        """

        return self

    def __next__(self):
        """
        Obtain the next item from the work queue.

        :returns: The next item of work to process.
        """

        # Is there any work left?
        if not self._work:
            raise StopIteration()

        return self._work.popleft()

    def add(self, item):
        """
        Add an item to the work queue.

        :param item: The work item to add.  An item may be of any
                     type; however, if it is not hashable, then the
                     work queue must either be initialized with
                     ``unique`` set to ``False``, or a ``key``
                     callable must have been provided.
        """

        # Are we to uniquify work items?
        if self._unique:
            key = self._key(item) if self._key else item

            # If it already has been added to the queue, do nothing
            if key in self._seen:
                return

            self._seen.add(key)

        # Add the item to the queue
        self._work.append(item)

        # We'll keep a count of the number of items that have been
        # through the queue
        self._count += 1

    def extend(self, items):
        """
        Add a sequence of items to the work queue.

        :param items: A sequence of items to add to the queue.  An
                      item may be of any type; however, if they are
                      not hashable, then the work queue must either be
                      initialized with ``unique`` set to ``False``, or
                      a ``key`` callable must have been provided.
        """

        # Just run add in a loop
        for item in items:
            self.add(item)

    @property
    def count(self):
        """
        Obtain a count of the number of items added to the work queue
        over its lifetime.
        """

        return self._count

    @property
    def worked(self):
        """
        Obtain a count of the number of items that have been worked up
        to the present time.
        """

        return self._count - len(self._work)
