====================
Iterative Work Queue
====================

.. image:: https://travis-ci.org/klmitch/workq.svg?branch=master
    :target: https://travis-ci.org/klmitch/workq

In programming, there are some problems with recursive algorithms.
One of them is the stack: each recursion adds a new frame to the
stack.  This can be mitigated using tail recursion, but tail recursion
isn't always possible.  A second problem is loops: consider loading a
series of files which contain an "include" instruction, where one of
the files contains an "include" for itself or for another file which
contains an "include" for it.

One good solution for these problems is to recast the recursive
algorithm as an iterative one.  A ``WorkQueue`` is a tool for doing
exactly this; it is an iterator for work items, where work items may
be added to the queue during iteration.  A ``WorkQueue`` also has
support for tracking items that have been added to the queue before,
eliminating the loop problem by simply ignoring duplicates.

Basic Usage
===========

The basic usage of a ``WorkQueue`` is very simple--one simply
initializes it with a sequence of work items, then iterates over the
items, adding new items as necessary::

    wq = workq.WorkQueue([item])
    for item in wq:
        # Do work

        # Add one item to the queue
        wq.add(new_item)

        # Alternatively, add a sequence of items to the queue
        wq.extend(new_items)

Each item added to the queue is tracked, and attempts to add an item
that has already been added will simply be ignored.  This can be
disabled by passing ``unique=False`` to the ``WorkQueue`` constructor.
If the work items are not hashable, or must be kept unique based on
some property of the item (e.g., an instance attribute), then pass a
``key`` callable to the ``WorkQueue`` constructor; this callable will
be called with one argument--the work item--and must return the key
corresponding to that item.

Work Counts
===========

The length of a ``WorkQueue`` object is the number of work items still
in the queue.  A ``WorkQueue`` also keeps track of the total number of
work items that have been added to it; this count can be accessed
through the ``count`` property.  Finally, the number of items that
have been worked can be accessed through the ``worked`` property.  As
an example::

    >>> wq = workq.WorkQueue(['a', 'b'])
    >>> next(wq)
    'a'
    >>> wq.add('c')
    >>> len(wq)
    2
    >>> wq.count
    3
    >>> wq.worked
    1

Work Item Uniqueness
====================

A ``WorkQueue`` object uses a Python ``set`` to track the items that
have previously been added, to prevent duplications.  This isn't
required for every application, and some applications may have a large
number of work items, or even a never-ending stream of them.  To
accommodate this, the ``unique`` keyword argument may be passed to the
``WorkQueue`` constructor with a value of ``False``; this will disable
using the ``set`` and keep memory usage under control.

Another problem with using ``set`` is that some work items may not be
hashable, or the objects may be distinct when the work that they
represent is not.  To accommodate this, use the ``key`` keyword
argument to the ``WorkQueue`` constructor; this identifies a callable,
similar to the ``key`` parameters of ``sort()`` and ``sorted()``,
which is passed the work item and returns a key to use with the
``set``.  This can also be used to keep memory usage under control, by
allowing the ``set`` to store, say, a short string, rather than a
large object.
