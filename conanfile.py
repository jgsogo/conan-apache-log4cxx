from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.tools import os_info, SystemPackageTool
import os

class Apachelog4cxxConan(ConanFile):
    name = "apache-log4cxx"
    revision = "1788752"
    version = "0.11.0-rev+" + revision
    license = "Apache-2.0"
    url = "https://github.com/mkovalchik/conan-apache-log4cxx"
    settings = "os", "compiler", "build_type", "arch"
    requires = "apache-apr/1.5.2@mkovalchik/stable"
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
    lib_name = name + "-" + version
    exports_sources = "char_widening.patch"

    def source(self):
        if os_info.is_linux:
            installer = SystemPackageTool()
            installer.install("subversion")

        self.run('svn checkout -r ' + self.revision + " http://svn.apache.org/repos/asf/incubator/log4cxx/trunk " + self.lib_name)
        if not self.settings.os == "Windows":
            with tools.chdir(self.lib_name):
                self.run("./autogen.sh")
        tools.patch(base_path=self.lib_name, patch_file="char_widening.patch")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            configure_command = "./configure"
            if self.settings.os == "Windows":
                configure_command += ".bat"
            
            configure_command += " --prefix=" + os.getcwd()
            configure_command += " --with-apr=" + self.deps_cpp_info["apache-apr"].rootpath

            for key,value in self.options.items():
                configure_command += " --" + key + "=" + value

            with tools.chdir(self.lib_name):
                self.run(configure_command)
                self.run("make -j " + str(max(tools.cpu_count() - 1, 1)))
                self.run("make check")
                self.run("make install ")

    def package(self):
        self.copy("*.so*", dst="lib", src="lib", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)
        self.copy("*.h", dst="include", src="include", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["log4cxx"]
