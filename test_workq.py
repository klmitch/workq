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
import unittest

import mock

import workq


class WorkQueueTest(unittest.TestCase):
    @mock.patch.object(workq.WorkQueue, 'extend')
    def test_init_base(self, mock_extend):
        wq = workq.WorkQueue(['a', 'b', 'c'])

        self.assertEqual(wq._work, collections.deque())
        self.assertEqual(wq._seen, set())
        self.assertEqual(wq._count, 0)
        self.assertEqual(wq._unique, True)
        self.assertEqual(wq._key, None)
        mock_extend.assert_called_once_with(['a', 'b', 'c'])

    @mock.patch.object(workq.WorkQueue, 'extend')
    def test_init_alt(self, mock_extend):
        wq = workq.WorkQueue(['a', 'b', 'c'], False, 'key')

        self.assertEqual(wq._work, collections.deque())
        self.assertEqual(wq._seen, set())
        self.assertEqual(wq._count, 0)
        self.assertEqual(wq._unique, False)
        self.assertEqual(wq._key, 'key')
        mock_extend.assert_called_once_with(['a', 'b', 'c'])

    def get_queue(self, items=None, seen=None, unique=True, key=None):
        with mock.patch.object(workq.WorkQueue, 'extend'):
            wq = workq.WorkQueue([], unique, key)

        if items:
            wq._work.extend(items)
            wq._count = len(items)
        if seen:
            wq._seen |= seen

        return wq

    def test_len_empty(self):
        wq = self.get_queue()

        self.assertEqual(len(wq), 0)

    def test_len_nonempty(self):
        wq = self.get_queue(items=['a', 'b', 'c'])

        self.assertEqual(len(wq), 3)

    def test_bool_empty(self):
        wq = self.get_queue()

        self.assertFalse(wq)

    def test_bool_nonempty(self):
        wq = self.get_queue(items=['a', 'b', 'c'])

        self.assertTrue(wq)

    def test_iter(self):
        wq = self.get_queue()

        result = iter(wq)

        self.assertEqual(result, wq)

    def test_next(self):
        wq = self.get_queue(items=['a', 'b'])

        result1 = wq.__next__()

        self.assertEqual(result1, 'a')

        result2 = wq.__next__()

        self.assertEqual(result2, 'b')

        self.assertRaises(StopIteration, wq.__next__)

    def test_add_nonunique(self):
        wq = self.get_queue(unique=False)

        wq.add('a')
        wq.add('a')
        wq.add('a')

        self.assertEqual(wq._work, collections.deque(['a', 'a', 'a']))
        self.assertEqual(wq._seen, set())
        self.assertEqual(wq._count, 3)

    def test_add_unique_nokey(self):
        wq = self.get_queue()

        wq.add('a')
        wq.add('b')
        wq.add('a')
        wq.add('c')
        wq.add('b')

        self.assertEqual(wq._work, collections.deque(['a', 'b', 'c']))
        self.assertEqual(wq._seen, set(['a', 'b', 'c']))
        self.assertEqual(wq._count, 3)

    def test_add_unique_withkey(self):
        wq = self.get_queue(key=lambda x: x.key)
        a1 = mock.Mock(key='a')
        b1 = mock.Mock(key='b')
        a2 = mock.Mock(key='a')
        c1 = mock.Mock(key='c')
        b2 = mock.Mock(key='b')

        wq.add(a1)
        wq.add(b1)
        wq.add(a2)
        wq.add(c1)
        wq.add(b2)

        self.assertEqual(wq._work, collections.deque([a1, b1, c1]))
        self.assertEqual(wq._seen, set(['a', 'b', 'c']))
        self.assertEqual(wq._count, 3)

    @mock.patch.object(workq.WorkQueue, 'add')
    def test_extend(self, mock_add):
        wq = self.get_queue()

        wq.extend(['a', 'b', 'c', 'd'])

        mock_add.assert_has_calls([
            mock.call('a'),
            mock.call('b'),
            mock.call('c'),
            mock.call('d'),
        ])

    def test_count(self):
        wq = self.get_queue()
        wq._count = 5

        self.assertEqual(wq.count, 5)

    def test_worked(self):
        wq = self.get_queue(items=['a', 'b', 'c'])
        wq._count += 2

        self.assertEqual(wq.worked, 2)


class WorkQueueFunctionTest(unittest.TestCase):
    def test_basic(self):
        files = {
            'f1': mock.Mock(includes=['f1', 'f2', 'f3']),
            'f2': mock.Mock(includes=['f1', 'f3', 'f4']),
            'f3': mock.Mock(includes=[]),
            'f4': mock.Mock(includes=['f5']),
            'f5': mock.Mock(includes=[]),
        }

        wq = workq.WorkQueue(['f1'])

        worked = []
        for fn in wq:
            worked.append(fn)

            fobj = files[fn]

            wq.extend(fobj.includes)

        self.assertEqual(worked, ['f1', 'f2', 'f3', 'f4', 'f5'])
