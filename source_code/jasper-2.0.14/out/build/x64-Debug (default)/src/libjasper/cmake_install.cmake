# Install script for directory: C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/out/install/x64-Debug (default)")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY OPTIONAL FILES "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/out/build/x64-Debug (default)/src/libjasper/jasper.lib")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE SHARED_LIBRARY FILES "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/out/build/x64-Debug (default)/src/libjasper/jasper.dll")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/jasper" TYPE FILE FILES
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_cm.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/out/build/x64-Debug (default)/src/libjasper/include/jasper/jas_config.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_debug.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_dll.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_fix.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_getopt.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_icc.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_image.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_init.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_malloc.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_math.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jasper.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_seq.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_stream.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_string.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_tmr.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_tvp.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_types.h"
    "C:/Users/José Silva/Desktop/jasper-2.0.14/jasper-2.0.14/src/libjasper/include/jasper/jas_version.h"
    )
endif()

