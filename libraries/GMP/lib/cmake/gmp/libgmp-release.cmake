#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "GMP::libgmp" for configuration "Release"
set_property(TARGET GMP::libgmp APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(GMP::libgmp PROPERTIES
  IMPORTED_IMPLIB_RELEASE "${_IMPORT_PREFIX}/lib/libgmp-13.lib"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/libgmp-13.dll"
  )

list(APPEND _IMPORT_CHECK_TARGETS GMP::libgmp )
list(APPEND _IMPORT_CHECK_FILES_FOR_GMP::libgmp "${_IMPORT_PREFIX}/lib/libgmp-13.lib" "${_IMPORT_PREFIX}/bin/libgmp-13.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
