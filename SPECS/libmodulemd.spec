%global baserelease 1
%global v2_epoch 0
%global v2_major 2
%global v2_minor 13
%global v2_patch 0
%global v2_release %{baserelease}
%global libmodulemd_v2_version %{v2_major}.%{v2_minor}.%{v2_patch}
%global libmodulemd_v1_version 1.8.16
# This is trickery to ensure that the upgrade path for libmodulemd1 is always
# clean and associated with the appropriate v2 build
%global libmodulemd_v1_release %{v2_epoch}.%{v2_major}.%{v2_minor}.%{v2_patch}.%{v2_release}

Name:           libmodulemd
Version:        %{libmodulemd_v2_version}
Release:        %{baserelease}%{?dist}
Summary:        Module metadata manipulation library

License:        MIT
URL:            https://github.com/fedora-modularity/libmodulemd
Source0:        %{url}/releases/download/%{version}/modulemd-%{version}.tar.xz
Source1:        %{url}/releases/download/%{name}-%{libmodulemd_v1_version}/modulemd-%{libmodulemd_v1_version}.tar.xz
# Accept invalid, but existing 18446744073709551615 buildorder when loading
# modulemd-v2 documents, bug #1984402, proposed to the upstream
Patch0:         modulemd-2.13.0-Accept-18446744073709551615-buildorder-if-accept_ove.patch


BuildRequires:  meson >= 0.47
BuildRequires:  pkgconfig
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(yaml-0.1)
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  glib2-doc
BuildRequires:  rpm-devel
BuildRequires:  file-devel
BuildRequires:  python3-devel
BuildRequires:  python3-gobject-base
BuildRequires:  help2man

# Patches


%description
C Library for manipulating module metadata files.
See https://github.com/fedora-modularity/libmodulemd/blob/master/README.md for
more details.


%package -n python3-%{name}
Summary: Python 3 bindings for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: python3-gobject-base
Requires: %{py3_dist six}
Obsoletes: python3-modulemd < 1.3.4

%description -n python3-%{name}
Python 3 bindings for %{name}


%package devel
Summary:        Development files for libmodulemd
Requires:       %{name}%{?_isa} = %{version}-%{release}


%description devel
Development files for libmodulemd.


%package -n libmodulemd1
Summary: Compatibility package for libmodulemd 1.x
Version: %{libmodulemd_v1_version}
Release: %{libmodulemd_v1_release}
Obsoletes: libmodulemd < 2
Provides: libmodulemd = %{libmodulemd_v1_version}-%{release}
Provides: libmodulemd%{?_isa} = %{libmodulemd_v1_version}-%{release}

%description -n libmodulemd1
Compatibility library for libmodulemd 1.x


%package -n libmodulemd1-devel
Summary: Compatibility development package for libmodulemd 1.x
Version: %{libmodulemd_v1_version}
Release: %{libmodulemd_v1_release}
Requires: libmodulemd1%{?_isa} = %{libmodulemd_v1_version}-%{release}
Conflicts: %{name}-devel
Obsoletes: libmodulemd-devel < 2
Provides: libmodulemd-devel = %{libmodulemd_v1_version}-%{release}
RemovePathPostfixes: .compat


%description -n libmodulemd1-devel
Development files for libmodulemd 1.x


%package -n python3-libmodulemd1
Summary: Python 3 bindings for %{name}1
Version: %{libmodulemd_v1_version}
Release: %{libmodulemd_v1_release}
Requires: libmodulemd1 = %{libmodulemd_v1_version}-%{release}
Requires: python3-gobject-base

Obsoletes: python3-libmodulemd < 2
Provides: python3-libmodulemd = %{libmodulemd_v1_version}-%{release}

%description -n python3-libmodulemd1
Python 3 bindings for libmodulemd1


%prep
%setup -c
%setup -c -T -D -a 1
pushd modulemd-%{libmodulemd_v2_version}
%patch0 -p1
popd

%build
# Build the v1 API first
pushd modulemd-%{libmodulemd_v1_version}
%define _vpath_builddir api1
%meson -Ddeveloper_build=false
%meson_build
popd

# Build the v2 API
pushd modulemd-%{libmodulemd_v2_version}
%define _vpath_builddir api2
%meson -Ddeveloper_build=false -Dwith_manpages=enabled -Dwith_py2=false \
    -Daccept_overflowed_buildorder=true
%meson_build
popd

%check

export LC_CTYPE=C.utf8

pushd modulemd-%{libmodulemd_v1_version}
%define _vpath_builddir api1
%{__meson} test -C %{_vpath_builddir} %{?_smp_mesonflags} --print-errorlogs -t 10
popd

pushd modulemd-%{libmodulemd_v2_version}
%define _vpath_builddir api2
%{__meson} test -C %{_vpath_builddir} %{?_smp_mesonflags} --print-errorlogs -t 10
popd


%install
pushd modulemd-%{libmodulemd_v1_version}
%define _vpath_builddir api1
%meson_install
popd

pushd modulemd-%{libmodulemd_v2_version}
%define _vpath_builddir api2
%meson_install
popd

# Create a symlink for the libmodulemd1-devel package
ln -s libmodulemd.so.%{libmodulemd_v1_version} \
      %{buildroot}%{_libdir}/%{name}.so.compat


%files
%license modulemd-%{libmodulemd_v2_version}/COPYING
%doc modulemd-%{libmodulemd_v2_version}/NEWS
%doc modulemd-%{libmodulemd_v2_version}/README.md
%{_bindir}/modulemd-validator
%{_mandir}/man1/modulemd-validator.1*
%{_libdir}/%{name}.so.2*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/Modulemd-2.0.typelib


%files devel
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/modulemd-2.0.pc
%{_includedir}/modulemd-2.0/
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/Modulemd-2.0.gir
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/modulemd-2.0/


%files -n python3-%{name}
%{python3_sitearch}/gi/overrides/


%files -n python3-libmodulemd1


%files -n libmodulemd1
%license modulemd-%{libmodulemd_v1_version}/COPYING
%doc modulemd-%{libmodulemd_v1_version}/README.md
%{_bindir}/modulemd-validator-v1
%{_libdir}/%{name}.so.1*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/Modulemd-1.0.typelib


%files -n libmodulemd1-devel
%{_libdir}/%{name}.so.compat
%{_libdir}/pkgconfig/modulemd.pc
%{_includedir}/modulemd/
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/Modulemd-1.0.gir
%dir %{_datadir}/gtk-doc
%dir %{_datadir}/gtk-doc/html
%{_datadir}/gtk-doc/html/modulemd-1.0/


%changelog
* Fri Jul 09 2021 Petr Pisar <ppisar@redhat.com> - 2.13.0-1
- 2.13.0 bump (bug #1984402)

* Mon May 03 2021 Petr Pisar <ppisar@redhat.com> - 2.12.1-1
- 2.12.1 bump (bug #1894573)

* Wed May 20 2020 Stephen Gallagher <sgallagh@redhat.com> - 2.9.4-2
- Update to 2.9.4
- Drop valgrind tests from RPM build
- Resolves: RHBZ#1797749

* Tue Oct 29 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.8.2-1
- Update to versions 2.8.2 and 1.8.16
- Resolves: rhbz#1752511

* Wed Oct 23 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.5.0-4
- Improve default merging logic when dealing with third-party repos
- Resolves: rhbz#1761805

* Wed May 29 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.5.0-2
- Fix memory corruption error using Module.search_rpms() from python
- Speed up valgrind tests
- Resolves: rhbz#1714766

* Wed May 22 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.5.0-1
- Rebase to 2.5.0 and 1.8.11
- Related: rhbz#1693680

* Mon May 13 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.4.0-1
- Rebase to 2.4.0 and 1.8.10
- Resolves: rhbz#1693680

* Fri Jan 18 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-5
- Don't fail merges when default streams differ
- Resolves: rhbz#1666871

* Wed Jan 16 2019 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-4
- Include modified value when copying Defaults objects
- Resolves: rhbz#1665465

* Thu Dec 13 2018 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-3
- Keep libmodulemd1 in sync with libmodulemd

* Thu Dec 13 2018 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-2
- Fix package location of modulemd-validator

* Thu Dec 13 2018 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-1
- Update to 2.0.0 final
- Assorted fixes for validation
- Add modulemd-validator tool based on v2 code
- Fix a crash when merging defaults
- Add missing BuildRequires

* Tue Dec 11 2018 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-0.beta2
- Update to 2.0.0beta2
- Better validation of stored content during read and write operations
- ModuleIndex now returns FALSE if any subdocument fails
- Fix tests on 32-bit platforms
- Make unknown keys in YAML maps non-fatal for libmodulemd1
- Make unknown keys in YAML maps optionally fatal for libmodulemd 2.x
- Fix RPM version requirements for libmodulemd1

* Mon Dec 10 2018 Stephen Gallagher <sgallagh@redhat.com> - 2.0.0-0.beta1
- Total rewrite to 2.0 API
- Resolves: rhbz#1646436

* Thu Aug 09 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-2
- Fix backwards-incompatible API change
- Resolves: rhbz#1607083

* Tue Aug 07 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.6.2-1
- Update to 1.6.2
- Make buildorder a signed integer to match modulemd specification
- Obsolete unsupported pythonX-modulemd packages

* Fri Aug  3 2018 Florian Weimer <fweimer@redhat.com> - 1.6.1-2
- Honor %%{valgrind_arches}

* Fri Jul 20 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.6.1-1
- Update to 1.6.1
- Fix header include ordering
- Suppress empty sections from .dump() ordering

* Wed Jul 18 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.6.0-1
- Update to 1.6.0
- Adds Modulemd.ModuleStream object, deprecating Modulemd.Module
- Adds Modulemd.Translation and Modulemd.TranslationEntry objects
- Adds Modulemd.ImprovedModule object that collects streams, defaults and
  translations together
- Adds new Modulemd.index_from_*() funtions to get a hash table of
  Modulemd.ImprovedModule objects for easier searching
- Moves function documentation to the public headers
- Corrects the license headers to MIT (they were incorrectly listed as MITNFA
  in previous releases)
- Makes the "eol" field optional for Modulemd.ServiceLevel
- Clean up HTML documentation
- Fixes a type error on 32-bit systems

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sat Jun 23 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.5.2-1
- Update to libdmodulemd 1.5.2
- Don't free uninitialized memory

* Fri Jun 22 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-2
- Fix buildopts property not being initialized

* Tue Jun 19 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.5.1-1
- Update to version 1.5.1
- Re-enable build-time tests

* Mon Jun 18 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.5.0-2
- Temporarily disable build-time tests

* Mon Jun 18 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.5.0-1
- Update to version 1.5.0
- Adds support for "intents" in Modulemd.Defaults
- Adds `Modulemd.get_version()`
- Adds support for RPM whitelists in the buildopts
- Adds a new object: Modulemd.Buildopts
- Deprecates Modulemd.Module.get_rpm_buildopts()
- Deprecates Modulemd.Module.set_rpm_buildopts()
- Fixes some missing license blurbs

* Tue May 08 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.4.1-1
- Update to version 1.4.1
- Improve output from modulemd-validator
- Drop upstreamed patches

* Wed Apr 25 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.4.0-2
- Fix pointer math error
- Fix compilation failure in Fedora build system

* Wed Apr 25 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.4.0-1
- Update to version 1.4.0
- Adds new API for returning failed YAML subdocuments
- Stop emitting log messages by default (polluting consumer logs)
- Validate RPM artifacts for proper NEVRA format
- Improve the validator tool
- Drop upstreamed patch

* Mon Apr 16 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-2
- Fix serious error in modulemd-defaults emitter

* Fri Apr 13 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.3.0-1
- Update to version 1.3.0
- New Public Objects:
  * Modulemd.Prioritizer - tool to merge module defaults
- New Public Functions:
  * Modulemd.SimpleSet.is_equal()
  * Modulemd.Defaults.copy()
  * Modulemd.Defaults.merge()

* Wed Apr 04 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.2.0-1
- Update to version 1.2.0
- New Functions:
  * Modulemd.objects_from_file()
  * Modulemd.objects_from_string()
  * Modulemd.dump()
  * Modulemd.dumps()
  * Modulemd.Defaults.new_from_file()
  * Modulemd.Defaults.new_from_string()
- Deprecated Functions:
  * Modulemd.Module.new_all_from_file()
  * Modulemd.Module.new_all_from_file_ext()
  * Modulemd.Module.new_all_from_string()
  * Modulemd.Module.new_all_from_string_ext()
  * Modulemd.Module.dump_all()
  * Modulemd.Module.dumps_all()
- Bugfixes
  * Properly use G_BEGIN_DECLS and G_END_DECLS in headers
  * Assorted fixes for memory ownership in GObject Introspection

* Fri Mar 23 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-2
- Fix missing G_END_DECL from public headers

* Mon Mar 19 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.3-1
- Fix numerous memory leaks
- Drop upstreamed patch

* Thu Mar 15 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.2-1
- Update to version 1.1.2
- Revert backwards-incompatible API change
- Fix version string in pkgconfig file

* Thu Mar 15 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.1-1
- Update to version 1.1.1
- Make default stream and profiles optional
- Fixes: https://github.com/fedora-modularity/libmodulemd/issues/25
- Fixes: https://github.com/fedora-modularity/libmodulemd/issues/26
- Fixes: https://github.com/fedora-modularity/libmodulemd/issues/27

* Wed Mar 14 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.1.0-1
- Update to version 1.1.0
- Adds support for handling modulemd-defaults YAML documents
- Adds peek()/dup() routines to all object properties
- Adds Modulemd.Module.dup_nsvc() to retrieve the canonical form of the unique module identifier.
- Adds support for boolean types in the XMD section
- Revert obsoletion of pythonX-modulemd packages for now

* Tue Mar 13 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0.4-2
- Obsolete unsupported pythonX-modulemd packages

* Tue Feb 27 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.0.4-1
- Update to 1.0.4
- Rework version autodetection
- Avoid infinite loop on unparseable YAML

* Sun Feb 25 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.0.3-1
- RPM components are properly emitted when no module components exist
- Parser works around late determination of modulemd version

* Fri Feb 16 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.0.2-1
- Be more strict with certain parser edge-cases
- Replace popt argument processing with glib
- Drop upstreamed patches

* Thu Feb 15 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.0.1-2
- Handle certain unlikely format violations

* Thu Feb 15 2018 Stephen Gallagher <sgallagh@redhat.com> - 1.0.1-1
- Support modulemd v2
- Add tool to do quick validation of modulemd
- Fix memory management
- Warn and ignore unparseable sub-documents in the YAML
- Fix several memory issues detected by Coverity scan

* Tue Feb 06 2018 Stephen Gallagher <sgallagh@redhat.com> - 0.2.2-1
- Update to libmodulemd 0.2.2
- Fix numerous minor memory leaks
- Fix issues with EOL/SL dates

* Tue Feb 06 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.2.1-3
- Own appropriate directories

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.2.1-2
- Switch to %%ldconfig_scriptlets

* Fri Jan 05 2018 Stephen Gallagher <sgallagh@redhat.com> - 0.2.1-1
- Update to libmodulemd 0.2.1
- Add 'name' property for Profiles

* Thu Oct 05 2017 Stephen Gallagher <sgallagh@redhat.com> - 0.2.0-2
- Add missing BuildRequires for gtk-doc

* Thu Oct 05 2017 Stephen Gallagher <sgallagh@redhat.com> - 0.2.0-1
- Update to libmodulemd 0.2.0
- Adds gtk-doc generated documentation
- (ABI-break) Makes all optional properties accept NULL as a value to clear
  them
- (ABI-break) Modulemd.SimpleSet takes a STRV (char **) instead of a
  GLib.PtrArray
- Fixes a bug where the name was not always set for components
- Adds support for dumping YAML from the introspected API
- Includes add/remove routines for profiles

* Sat Sep 30 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.1.0-5
- Use %%_isa in Requires for main package from devel

* Mon Sep 18 2017 Stephen Gallagher <sgallagh@redhat.com> - 0.1.0-4
- Correct the license to MIT

* Mon Sep 18 2017 Stephen Gallagher <sgallagh@redhat.com> - 0.1.0-3
- Modifications requested during package review

* Fri Sep 15 2017 Stephen Gallagher <sgallagh@redhat.com> - 0.1.0-2
- First public release

