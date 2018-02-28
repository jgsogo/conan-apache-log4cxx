
from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild
from conans.errors import ConanException
from conans.tools import os_info, SystemPackageTool
import os


# TODO: Credit to this http://www.thalesians.com/finance/index.php/Knowledge_Base/CPP/log4cxx

class Apachelog4cxxConan(ConanFile):
    name = "apache-log4cxx"
    version = "0.10.0"

    license = "Apache-2.0"
    url = "https://github.com/mkovalchik/conan-apache-log4cxx"
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
    lib_name = name + "-" + version
    exports_sources = "*.patch"

    def configure(self):
        if self.settings.arch == "x86_64":
            raise ConanException("x64 fails :/")

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires.add("apache-apr/1.5.2@jgsogo/testing")

    def source(self):
        file_ext = ".tar.gz" if not self.settings.os == "Windows" else ".zip"
        tools.get("http://archive.apache.org/dist/logging/log4cxx/{version}/{name}-{version}{ext}".format(name=self.name, version=self.version, ext=file_ext))
        #tools.unzip(self.lib_name + file_ext)
        tools.patch(base_path=self.lib_name, patch_file="apache-log4cxx-win2012.patch")
        #tools.patch(base_path=self.lib_name, patch_file="char_widening.patch")

        if self.settings.os == "Windows":
            apr_version = "1.3.8" # "1.2.11"
            apr_util_version = "1.3.9"  # "1.2.10"
            tools.get("http://archive.apache.org/dist/apr/apr-{apr_version}-win32-src.zip".format(apr_version=apr_version))
            os.rename('apr-{apr_version}'.format(apr_version=apr_version), 'apr')
            tools.get("http://archive.apache.org/dist/apr/apr-util-{apr_util_version}-win32-src.zip".format(apr_util_version=apr_util_version))
            os.rename('apr-util-{apr_util_version}'.format(apr_util_version=apr_util_version), 'apr-util')

    def build(self):
        if self.settings.os == "Windows":
            tools.replace_in_file(os.path.join("apr-util", "include", "apu.hw"),
                                  "#define APU_HAVE_APR_ICONV      1",
                                  "#define APU_HAVE_APR_ICONV      0")
            tools.replace_in_file(os.path.join("apr-util", "include", "apr_ldap.hw"),
                                  "#define APR_HAS_LDAP		    1",
                                  "#define APR_HAS_LDAP		    0")
            with tools.chdir(self.lib_name):
                self.run("configure")
                # self.run("configure-aprutil")
                msbuild = MSBuild(self)
                try:
                    msbuild.build(os.path.join("projects", "log4cxx.dsw"), upgrade_project=True)
                    # Previous line fails (because it prompts with an error)
                except Exception as e:
                    print("Try again: {}".format(e))
                    msbuild.build(os.path.join("projects", "log4cxx.sln"), upgrade_project=False)
        else:
            configure_command = "configure"
            configure_command += " --prefix=" + os.getcwd()
            configure_command += " --with-apr=" + self.deps_cpp_info["apache-apr"].rootpath

            for key, value in self.options.items():
                configure_command += " --" + key + "=" + value

            with tools.chdir(self.lib_name):
                env_build = AutoToolsBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
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
