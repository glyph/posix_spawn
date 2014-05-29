import pkgutil

from cffi import FFI


ffi = FFI()

ffi.cdef(pkgutil.get_data('posix_spawn', 'c/cdef.h').decode('ascii'))

lib = ffi.verify(pkgutil.get_data('posix_spawn', 'c/verify.h').decode('ascii'))

__all__ = ('lib', 'ffi')
