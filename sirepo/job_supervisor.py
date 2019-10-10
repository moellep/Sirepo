# -*- coding: utf-8 -*-
"""TODO(e-carlin): Doc

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern import pkcollections
from pykern import pkjson
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdp, pkdc, pkdlog, pkdexc
import aenum
import copy
import sirepo.driver
import sirepo.job
import sys
import tornado.locks


_DATA_ACTIONS = (sirepo.job.ACTION_ANALYSIS, sirepo.job.ACTION_COMPUTE)

_OPERATOR_ACTIONS = (sirepo.job.ACTION_CANCEL,)

def init():
    pkdp('job supervisor init')
    sirepo.job.init()
    sirepo.driver.init()


def terminate():
    sirepo.driver.terminate()


class _Base(PKDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = kwargs['content']
        self._handler = kwargs['handler']

    async def do(self):
        pkdp('type={} content={}', type(self), self.content)
        await self._do()


class AgentMsg(_Base):

    async def _do(self):
        pkdlog('content={}', self.content)
        d = sirepo.driver.get_instance_for_agent(self.content.agent_id)
        if not d:
            # TODO(e-carlin): handle
            pkdlog('no driver for agent_id={}', self.content.agent_id)
            return
        d.set_handler(self.handler)
        i = self.content.get('op_id')
        if not i:
            # TODO(e-carlin): op w/o id. Store the state in the job.
            return
        d.ops[i].set_result(self.content)


class _RequestState(aenum.Enum):
    CHECK_STATUS = 'check_status'
    REPLY = 'reply'
    RUN = 'run'
    RUN_PENDING = 'run_pending'


class _Job(PKDict):
    instances = PKDict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'jid' not in self:
            self.jid = self._jid_for_req(self.req)
        self.driver_kind = self.req.driver_kind
        self.uid = self.req.content.uid

    @classmethod
    async def get_compute_status(cls, req):
        """Get the status of a compute job.
        """
        #TODO(robnagler) deal with non-in-memory job state (db?)
        self = cls.instances.get(cls._jid_for_req(req))
        if not self:
            self = cls(req=req)
        d = await sirepo.driver.get_instance_for_job(self)
        r = await d.do_op(
            op=sirepo.job.OP_COMPUTE_STATUS,
            jid=self.req.compute_jid,
            run_dir=self.req.run_dir,
        )
        pkdp('111111111111111111111111111111111')
        return pkdp(r)

    @classmethod
    def _jid_for_req(cls, req):
        """Get the jid (compute or analysis) for a job from a request.
        """
        c = req.content
        if c.api in ('api_runStatus', 'api_runCancel', 'api_runSimulation'):
            return c.compute_jid
        if c.api in ('api_simulationFrame',):
            return c.analysis_jid
        raise AssertionError('unknown api={} req={}', c.api, req)


class ServerReq(_Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        c = self.content
        self._response_received = tornado.locks.Event()
        self._response = None
        self.uid = c.uid
        self._resource_class = sirepo.job
        self.driver_kind = sirepo.driver.get_kind(self)
        self.compute_jid = self.content.compute_jid
        self.run_dir = self.content.run_dir

    async def _do(self):
        c = self.content
        dispatch = {
            'api_runStatus': self._handler.write(await _Job.get_compute_status(self))
        }
        return await dispatch[c.content.api]


class Op(PKDict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result_set = tornado.locks.Event()
        self._result = None

    async def get_result(self):
        await self._result_set.wait()
        return self._result

    def set_result(self, res):
        self._result = res
        self._resul_set.set()
