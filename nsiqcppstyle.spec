Name:           python-nsiqcppstyle
Version:        0.5.1
Release:        1%{?dist}
Summary:        C++ style checker

License:        GPL-2
URL:            https://github.com/kunaltyagi/nsiqcppstyle
#Source:         #{url}/archive/v#{version}/nsiqcppstyle-#{version}.tar.gz
Source:         nsiqcppstyle-%{version}.tar.gz

%{?el7:AutoReqProv: no}
%undefine __pythondist_requires
%undefine __python_requires

BuildArch:      noarch

Requires: rh-python38-python(abi) = 3.8
%if 0%{?rhel} == 7
Requires: rh-python38-python(abi) = 3.8
%else
BuildRequires: pyproject-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-tomli
BuildRequires: python3-hatchling
BuildRequires: python3-tox-current-env
BuildRequires: python3-rpm-macros
%endif

%global _description %{expand:
nsiqcppstyle is one of the most customizable cpp style
checkers about.}

%description %_description

%package -n python3-nsiqcppstyle
Summary:        %{summary}

%description -n python3-nsiqcppstyle %_description

%prep
%autosetup -p1 -n nsiqcppstyle-%{version}


#generate_buildrequires
#pyproject_buildrequires -t


%build
%{?el7:/opt/rh/rh-python38/root/usr/bin/python3.8 -m build}
%{?el8:%pyproject_wheel}
%{?el9:%pyproject_wheel}
%{?fedora:%pyproject_wheel}


%install
#py3_install
#{?el7:python3.8 -m pip install -- --install-scripts=#{_bindir} --install-data=#{_datadir}}
#{?el7:#python3.8py3__python3 -m pip install --target ${RPM_BUILD_DIR}/usr}
%{?el7:/opt/rh/rh-python38/root/usr/bin/python3.8 -m pip install -I dist/*.whl --target ${RPM_BUILD_ROOT}/%python38python3_sitelib}
%{?el7:mkdir -p ${RPM_BUILD_ROOT}/usr/bin}
%{?el7:cp el7_only_bin_prog ${RPM_BUILD_ROOT}/usr/bin/nsiqcppstyle}
#{?el7:#python3.8py3_install_wheel}
#{?el7:#python38py3_install}
%{?el8:%pyproject_install}
%{?el9:%pyproject_install}
%{?fedora:%pyproject_install}

# Here, "nsiqcppstyle" is the name of the importable module.
#{?el7:python3.8 -m install --user --target $RPM_BUILD_ROOT/usr/lib/python3.8}
%{?el8:%pyproject_save_files -l nsiqcppstyle}
%{?el9:%pyproject_save_files -l nsiqcppstyle}
%{?fedora:%pyproject_save_files -l nsiqcppstyle}



#check
#tox


# Note that there is no %%files section for
# the unversioned python module, python-nsiqcppstyle.

# For python3-nsiqcppstyle, %%{pyproject_files} handles code files and %%license,
# but executables and documentation must be listed in the spec file:

%{?el7:%files -n python3-nsiqcppstyle}
%{?el8:%files -n python3-nsiqcppstyle -f %{pyproject_files}}
%{?el9:%files -n python3-nsiqcppstyle -f %{pyproject_files}}
%{?fedora:%files -n python3-nsiqcppstyle -f %{pyproject_files}}
%doc README.md
%{_bindir}/*
/opt/rh/rh-python38/root/usr/lib/python3.8/*

%changelog
