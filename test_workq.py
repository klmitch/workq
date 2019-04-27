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

import pytest

import workq


class TestWorkQueue(object):
    def test_init_base(self, mocker):
        mock_extend = mocker.patch.object(workq.WorkQueue, 'extend')
        wq = workq.WorkQueue(['a', 'b', 'c'])

        assert wq._work == collections.deque()
        assert wq._seen == set()
        assert wq._count == 0
        assert wq._unique is True
        assert wq._key is None
        mock_extend.assert_called_once_with(['a', 'b', 'c'])

    def test_init_alt(self, mocker):
        mock_extend = mocker.patch.object(workq.WorkQueue, 'extend')
        wq = workq.WorkQueue(['a', 'b', 'c'], False, 'key')

        assert wq._work == collections.deque()
        assert wq._seen == set()
        assert wq._count == 0
        assert wq._unique is False
        assert wq._key == 'key'
        mock_extend.assert_called_once_with(['a', 'b', 'c'])

    def get_queue(self, mocker, items=None, seen=None, unique=True, key=None):
        with mocker.patch.object(workq.WorkQueue, 'extend'):
            wq = workq.WorkQueue([], unique, key)

        if items:
            wq._work.extend(items)
            wq._count = len(items)
        if seen:
            wq._seen |= seen

        return wq

    def test_len_empty(self, mocker):
        wq = self.get_queue(mocker)

        assert len(wq) == 0

    def test_len_nonempty(self, mocker):
        wq = self.get_queue(mocker, items=['a', 'b', 'c'])

        assert len(wq) == 3

    def test_bool_empty(self, mocker):
        wq = self.get_queue(mocker)

        assert not wq

    def test_bool_nonempty(self, mocker):
        wq = self.get_queue(mocker, items=['a', 'b', 'c'])

        assert wq

    def test_iter(self, mocker):
        wq = self.get_queue(mocker)

        result = iter(wq)

        assert result == wq

    def test_next(self, mocker):
        wq = self.get_queue(mocker, items=['a', 'b'])

        result1 = wq.__next__()

        assert result1 == 'a'

        result2 = wq.__next__()

        assert result2 == 'b'

        with pytest.raises(StopIteration):
            wq.__next__()

    def test_add_nonunique(self, mocker):
        wq = self.get_queue(mocker, unique=False)

        wq.add('a')
        wq.add('a')
        wq.add('a')

        assert wq._work == collections.deque(['a', 'a', 'a'])
        assert wq._seen == set()
        assert wq._count == 3

    def test_add_unique_nokey(self, mocker):
        wq = self.get_queue(mocker)

        wq.add('a')
        wq.add('b')
        wq.add('a')
        wq.add('c')
        wq.add('b')

        assert wq._work == collections.deque(['a', 'b', 'c'])
        assert wq._seen == set(['a', 'b', 'c'])
        assert wq._count == 3

    def test_add_unique_withkey(self, mocker):
        wq = self.get_queue(mocker, key=lambda x: x.key)
        a1 = mocker.Mock(key='a')
        b1 = mocker.Mock(key='b')
        a2 = mocker.Mock(key='a')
        c1 = mocker.Mock(key='c')
        b2 = mocker.Mock(key='b')

        wq.add(a1)
        wq.add(b1)
        wq.add(a2)
        wq.add(c1)
        wq.add(b2)

        assert wq._work == collections.deque([a1, b1, c1])
        assert wq._seen == set(['a', 'b', 'c'])
        assert wq._count == 3

    def test_extend(self, mocker):
        mock_add = mocker.patch.object(workq.WorkQueue, 'add')
        wq = workq.WorkQueue([])

        wq.extend(['a', 'b', 'c', 'd'])

        mock_add.assert_has_calls([
            mocker.call('a'),
            mocker.call('b'),
            mocker.call('c'),
            mocker.call('d'),
        ])

    def test_count(self, mocker):
        wq = self.get_queue(mocker)
        wq._count = 5

        assert wq.count == 5

    def test_worked(self, mocker):
        wq = self.get_queue(mocker, items=['a', 'b', 'c'])
        wq._count += 2

        assert wq.worked == 2


class TestWorkQueueFunction(object):
    def test_basic(self, mocker):
        files = {
            'f1': mocker.Mock(includes=['f1', 'f2', 'f3']),
            'f2': mocker.Mock(includes=['f1', 'f3', 'f4']),
            'f3': mocker.Mock(includes=[]),
            'f4': mocker.Mock(includes=['f5']),
            'f5': mocker.Mock(includes=[]),
        }

        wq = workq.WorkQueue(['f1'])

        worked = []
        for fn in wq:
            worked.append(fn)

            fobj = files[fn]

            wq.extend(fobj.includes)

        assert worked == ['f1', 'f2', 'f3', 'f4', 'f5']
