import pkgutil

from cffi import FFI


ffi = FFI()

ffi.cdef(pkgutil.get_data('posix_spawn', 'c/cdef.h'))

lib = ffi.verify(pkgutil.get_data('posix_spawn', 'c/verify.h'))

__all__ = ('lib', 'ffi')
