
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
    options = {
        "enable-wchar_t" : ["yes", "no"],
        "enable-unichar" : ["yes", "no"],
        "enable-cfstring" : ["yes", "no"],
        "with-logchar" : ["utf-8", "wchar_t", "unichar"],
        "with-charset" : ["utf-8", "iso-8859-1", "usascii", "ebcdic", "auto"],
        "with-SMTP" : ["libesmtp", "no"],
        "with-ODBC" : ["unixODBC", "iODBC", "Microsoft", "no"]
    }
    default_options = "enable-wchar_t=yes", "enable-unichar=no", "enable-cfstring=no", "with-logchar=utf-8", "with-charset=auto", "with-SMTP=no", "with-ODBC=no"
    lib_name = "logging-log4cxx-" + version.replace('.', '_')
    exports_sources = ["CMakeLists.txt", "*.cmake",]
    generators = "cmake"

    def requirements(self):
        self.requires.add("apache-apr/1.6.3@jgsogo/stable")
        self.requires.add("apache-apr-util/1.6.1@jgsogo/stable")

    def source(self):
        tools.get("https://github.com/apache/logging-log4cxx/archive/v{version}.tar.gz".format(version=self.version.replace(".", "_")))

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.definitions["APR_ALTLOCATION"] = self.deps_cpp_info["apache-apr"].rootpath
            cmake.definitions["APRUTIL_ALTLOCATION"] = self.deps_cpp_info["apache-apr-util"].rootpath
            cmake.configure()
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            args = ['--prefix', self.package_folder,
                    '--with-apr={}'.format(os.path.join(self.deps_cpp_info["apache-apr"].rootpath)),
                    ]
            for key, value in self.options.items():
                args += " --" + key + "=" + value

            env_build.configure(configure_dir=self.lib_name,
                                args=args,
                                build=False)  # TODO: Workaround for https://github.com/conan-io/conan/issues/2552
            env_build.make()
            env_build.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
