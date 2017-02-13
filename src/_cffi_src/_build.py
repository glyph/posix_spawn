from cffi import FFI

import os


def maker():
    """
    Generate the bindings module.  Invoked by cffi's setuptools
    integration.
    """
    _cffi_src = os.path.dirname(__file__)

    ffibuilder = FFI()

    with open(os.path.join(_cffi_src, "set_source.h")) as set_source:
        ffibuilder.set_source(
            "posix_spawn._bindings",
            set_source.read())

    with open(os.path.join(_cffi_src, "cdef.h")) as cdef:
        ffibuilder.cdef(cdef.read())

    return ffibuilder
