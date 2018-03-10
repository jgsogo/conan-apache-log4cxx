
from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild, CMake
from conans.errors import ConanException
from conans.tools import os_info, SystemPackageTool
import os


class Apachelog4cxxConan(ConanFile):
    name = "apache-log4cxx"
    version = "0.10.0"

    license = "Apache-2.0"
    url = "https://github.com/jgsogo/conan-apache-log4cxx"
    settings = "os", "compiler", "build_type", "arch"
    # TODO: Options here https://logging.apache.org/log4cxx/latest_stable/building/autotools.html
    options = {
        "shared": [True, False],
        "enable-wchar_t": ["yes", "no"],
        "enable-unichar": ["yes", "no"],
        "enable-cfstring": ["yes", "no"],
        "with-logchar": ["utf-8", "wchar_t", "unichar"],
        "with-charset": ["utf-8", "iso-8859-1", "usascii", "ebcdic", "auto"],
        "with-SMTP": ["libesmtp", "no"],
        "with-ODBC": ["unixODBC", "iODBC", "Microsoft", "no"]
    }
    default_options = "enable-wchar_t=yes", "enable-unichar=no", "enable-cfstring=no", "with-logchar=utf-8", "with-charset=auto", "with-SMTP=no", "with-ODBC=no", "shared=True"
    lib_name = "logging-log4cxx-" + version.replace('.', '_')
    exports_sources = ["CMakeLists.txt", "*.cmake", "*.patch"]
    generators = "cmake"

    def requirements(self):
        self.requires.add("apache-apr/1.6.3@jgsogo/stable")
        self.requires.add("apache-apr-util/1.6.1@jgsogo/stable")

    def source(self):
        tools.get("https://github.com/apache/logging-log4cxx/archive/v{version}.tar.gz".format(version=self.version.replace(".", "_")))

    def patch(self):
        if self.settings.os == "Windows":
            tools.patch(base_path=self.lib_name, patch_file="apache-log4cxx-win2012.patch")
            tools.replace_in_file(os.path.join(self.lib_name, 'src', 'main', 'cpp', 'stringhelper.cpp'),
                                  "#include <apr.h>",
                                  "#include <apr.h>\n#include <iterator>")
        else:
            tools.patch(base_path=self.lib_name, patch_file="log4cxx-1-gcc.4.4.patch")
            tools.patch(base_path=self.lib_name, patch_file="log4cxx-5-gcc6-fix-narrowing-conversion.patch")
            tools.replace_in_file(os.path.join(self.lib_name, 'src', 'main', 'include', 'log4cxx', 'private', 'Makefile.am'),
                                  "privateinc_HEADERS= $(top_builddir)/src/main/include/log4cxx/private/*.h log4cxx_private.h",
                                  "privateinc_HEADERS= $(top_builddir)/src/main/include/log4cxx/private/*.h")
            tools.replace_in_file(os.path.join(self.lib_name, 'src', 'main', 'include', 'log4cxx', 'Makefile.am'),
                                  "log4cxxinc_HEADERS= $(top_srcdir)/src/main/include/log4cxx/*.h log4cxx.h",
                                  "log4cxxinc_HEADERS= $(top_srcdir)/src/main/include/log4cxx/*.h")

    def build(self):
        self.patch()
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.definitions["APR_ALTLOCATION"] = self.deps_cpp_info["apache-apr"].rootpath
            cmake.definitions["APRUTIL_ALTLOCATION"] = self.deps_cpp_info["apache-apr-util"].rootpath
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            cmake.configure()
            cmake.build()
            cmake.install()
        else:
            with tools.chdir(self.lib_name):
                self.run("./autogen.sh")

            env_build = AutoToolsBuildEnvironment(self)
            args = ['--prefix', self.package_folder,
                    '--with-apr={}'.format(os.path.join(self.deps_cpp_info["apache-apr"].rootpath)),
                    '--with-apr-util={}'.format(os.path.join(self.deps_cpp_info["apache-apr-util"].rootpath)),
                    ]
            for key, value in self.options.items():
                if key != 'shared':
                    args += ["--{}={}".format(key, value), ]

            env_build.configure(configure_dir=self.lib_name,
                                host=self.settings.arch,
                                args=args)
            env_build.make()
            env_build.make(args=['install'])

    def package(self):
        self.copy("*.h", dst="include", src=os.path.join('src', 'main', 'include'), keep_path=True)
        self.copy("*.h", dst="include", src=os.path.join(self.lib_name, 'src', 'main', 'include'), keep_path=True)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = tools.collect_libs(self)
        else:
            self.cpp_info.libs = tools.collect_libs(self) + ["odbc32", "mswsock", ]
            self.cpp_info.defines = ["LOG4CXX_STATIC", ]
