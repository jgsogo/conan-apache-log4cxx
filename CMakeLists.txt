# Credit: https://github.com/jeking3/logging-log4cxx/blob/868ef36933aea5d1d248f0421db1c1016d52a820/CMakeLists.txt

cmake_minimum_required(VERSION 3.1)

set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH}" "${CMAKE_CURRENT_SOURCE_DIR}")

set(PROJECT_DESCRIPTION "Apache Logging Framework for C++")
set(PROJECT_NAME        "log4cxx")
set(PROJECT_LICENSE     "Apache Software License 2.0")
set(PROJECT_LICURL      "http://www.apache.org/licenses/LICENSE-2.0")
set(PROJECT_URL         "http://logging.apache.org/log4cxx/")

# TODO: include(ExtractVersion)
# TODO: extract_version(PROJECT_VERSION)
set(PROJECT_VERSION "0.10.0")

message(STATUS "Configuring build environment for ${PROJECT_NAME} version ${PROJECT_VERSION}")

project(${PROJECT_NAME} VERSION ${PROJECT_VERSION})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(APR)
find_package(APRUtil)

include(PlatformSpecific)

set(LOG4CXX_DIR "${CMAKE_CURRENT_SOURCE_DIR}/logging-log4cxx-0_10_0/src/main")  # TODO: Pass library source directory (needed here and in TODO before)

configure_file("${LOG4CXX_DIR}/include/log4cxx/log4cxx.hw"
  "${CMAKE_CURRENT_BINARY_DIR}/include/log4cxx/log4cxx.h"
  COPYONLY
)

configure_file("${LOG4CXX_DIR}/include/log4cxx/private/log4cxx_private.hw"
  "${CMAKE_CURRENT_BINARY_DIR}/include/log4cxx/private/log4cxx_private.h"
  COPYONLY
)

set(LOG4CXX_INCLUDE_DIRECTORIES
  ${LOG4CXX_DIR}/include
  ${CMAKE_CURRENT_BINARY_DIR}/include
  ${APR_INCLUDE_DIR}
  )

file(GLOB_RECURSE LOG4CXX_HEADERS ${LOG4CXX_DIR}/include/log4cxx/*.h)
file(GLOB_RECURSE LOG4CXX_SRC ${LOG4CXX_DIR}/cpp/*.cpp)

add_library(${PROJECT_NAME} ${LOG4CXX_SRC} ${LOG4CXX_HEADERS})
target_include_directories(${PROJECT_NAME} PUBLIC ${LOG4CXX_INCLUDE_DIRECTORIES})
target_link_libraries(${PROJECT_NAME}
  ${APR_LIBRARIES}
# odbc32
# rpcrt4
# ws2_32
)

install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

install(
  FILES "${CMAKE_CURRENT_BINARY_DIR}/include/log4cxx/log4cxx.h"
  DESTINATION "${CMAKE_INSTALL_PREFIX}/include/log4cxx/"
  PERMISSIONS OWNER_READ GROUP_READ WORLD_READ OWNER_WRITE
)

install(
  DIRECTORY "${LOG4CXX_DIR}/include/"
  DESTINATION "${CMAKE_INSTALL_PREFIX}/include/"
  DIRECTORY_PERMISSIONS OWNER_READ GROUP_READ WORLD_READ OWNER_WRITE
  FILES_MATCHING PATTERN "*.h"
                 PATTERN "*/private/*" EXCLUDE
  PERMISSIONS OWNER_READ GROUP_READ WORLD_READ OWNER_WRITE
)

#if(MSVC)
#  install (FILES "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_BUILD_TYPE}/${PROJECT_NAME}*.pdb" DESTINATION ${CMAKE_INSTALL_LIBDIR} CONFIGURATIONS Debug RelWithDebInfo)
#endif()


