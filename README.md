# conan-apache-log4cxx
A [Conan](https://conan.io) package recipe for [Apache log4cxx](https://logging.apache.org/log4cxx/latest_stable/)

The latest tagged release of log4cxx was released several years ago and no longer compiles on the latest versions of gcc (or clang).
This recipe packages the unreleased version 0.11.0 of the library and includes a patch which resolves a compilation error in
src/test/cpp/helpers/transcodertestcase

This package is published on the public conan.io repository as apache-log4cxx/0.11.0-rev+1788752@mkovalchik/stable and has been
tested with gcc 6.3.1 x86_64-pc-linux-gnu
