import os
import sys
try:
    import distributed.protocol as _dp
except ImportError:
    def register_distributed_serializer(cls):
        pass
else:
    from distributed.utils import has_keyword

    def register_distributed_serializer(cls):
        _dp.register_serialization(cls, _serialize, _deserialize)

    def _serialize(df, context=None):
        def _serialize_imp(df, context=None):
            def do_serialize(x):
                return _dp.serialize(x, context=context)

            def call_with_context(meth, x, *args):
                if has_keyword(meth, 'context'):
                    return meth(x, context=context)
                else:
                    return meth(x)

            header, frames = call_with_context(df.serialize, do_serialize)
            assert 'reconstructor' not in header
            meth_deserial = getattr(type(df), 'deserialize')
            header['reconstructor'] = do_serialize(meth_deserial)
            return header, frames

        return _serialize_imp(df, context=context)

    def _deserialize(header, frames):
        reconstructor = _dp.deserialize(*header['reconstructor'])
        assert reconstructor is not None, 'None {}'.format(header['type'])
        return reconstructor(_dp.deserialize, header, frames)


def _parse_transfer_context(context):
    from distributed.comm.addressing import parse_host_port, parse_address

    def parse_it(x):
        return parse_host_port(parse_address(x)[1])

    if 'recipient' in context and 'sender' in context:
        rechost, recport = parse_it(context['recipient'])
        senhost, senport = parse_it(context['sender'])
        same_node = rechost == senhost
        same_process = same_node and recport == senport
    else:
        same_node, same_process = False, False
    return same_node, same_process


_CONFIG_USE_IPC = bool(int(os.environ.get("DASK_GDF_USE_IPC", "1")))


def should_use_ipc(context):
    if not _CONFIG_USE_IPC:
        return False
    if not sys.platform.startswith('linux'):
        return False
    if context is None:
        return False
    same_node, same_process = _parse_transfer_context(context)
    return bool(same_node)
