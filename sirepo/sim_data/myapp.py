# -*- coding: utf-8 -*-
u"""simulation data operations

:copyright: Copyright (c) 2019 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from __future__ import absolute_import, division, print_function
from pykern.pkdebug import pkdc, pkdlog, pkdp
import sirepo.sim_data


class SimData(sirepo.sim_data.SimDataBase):

    @classmethod
    def fixup_old_data(cls, data):
        cls._init_models(data.models)

    @classmethod
    def _compute_job_fields(cls, data):
        return [
            data.report,
            'dog',
        ]

    @classmethod
    def _lib_files(cls, *args, **kwargs):
        return []